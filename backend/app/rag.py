import logging
from typing import List, Tuple

import fitz
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import HuggingFacePipeline
from langchain.schema import Document
from transformers import pipeline

from .config import settings

logger = logging.getLogger(__name__)

_embeddings = None
_llm = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model_name)
    return _embeddings


def get_vectorstore():
    return Chroma(
        persist_directory=settings.chroma_persist_dir,
        embedding_function=get_embeddings(),
    )


def get_llm():
    global _llm
    if _llm is None:
        generator = pipeline(
            "text2text-generation",
            model=settings.model_name,
            max_new_tokens=256,
            temperature=0.1,
        )
        _llm = HuggingFacePipeline(pipeline=generator)
    return _llm


def extract_pdf_pages(pdf_path: str, filename: str) -> List[Tuple[int, str]]:
    doc = fitz.open(pdf_path)
    pages = []
    for page_number in range(doc.page_count):
        page = doc.load_page(page_number)
        text = page.get_text("text")
        if text.strip():
            pages.append((page_number + 1, text))
    return pages


def chunk_pages(pages: List[Tuple[int, str]]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    documents: List[Document] = []
    for page_number, text in pages:
        for chunk in splitter.split_text(text):
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={"page_number": page_number},
                )
            )
    return documents


def ingest_documents(
    pdf_path: str,
    filename: str,
    user_id: int,
    course_id: int,
    pdf_id: int,
) -> int:
    pages = extract_pdf_pages(pdf_path, filename)
    documents = chunk_pages(pages)
    for doc in documents:
        doc.metadata.update(
            {
                "user_id": user_id,
                "course_id": course_id,
                "pdf_id": pdf_id,
                "filename": filename,
            }
        )
    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents)
    vectorstore.persist()
    logger.info("Ingested %s chunks for pdf_id=%s", len(documents), pdf_id)
    return len(documents)


def format_citations(docs: List[Document]) -> List[str]:
    citations = []
    seen = set()
    for doc in docs:
        filename = doc.metadata.get("filename")
        page_number = doc.metadata.get("page_number")
        citation = f"[{filename}, page {page_number}]"
        if citation not in seen:
            seen.add(citation)
            citations.append(citation)
    return citations


def build_answer(query: str, docs: List[Document]) -> str:
    context = "\n\n".join(
        f"Source ({doc.metadata.get('filename')} p.{doc.metadata.get('page_number')}): {doc.page_content}"
        for doc in docs
    )
    prompt = (
        "You are a campus study assistant. Answer ONLY using the context. "
        "If the answer is not contained in the context, say you don't have enough information.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\nAnswer:"
    )
    llm = get_llm()
    return llm(prompt).strip()


def retrieve_context(
    query: str,
    user_id: int,
    course_id: int | None,
    top_k: int,
    all_courses: bool,
) -> List[Document]:
    vectorstore = get_vectorstore()
    filter_metadata = {"user_id": user_id}
    if course_id and not all_courses:
        filter_metadata["course_id"] = course_id
    docs = vectorstore.similarity_search(query, k=top_k, filter=filter_metadata)
    return docs
