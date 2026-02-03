# Project Report Draft

## Abstract
This project presents a Context-Aware Campus Study Assistant that enables students to query their course PDFs using retrieval-augmented generation (RAG) with citations. The system uses a local HuggingFace model, embeddings, and a persisted vector database to ensure privacy and reproducibility.

## Introduction
University students often struggle to quickly find answers across multiple lecture notes and handouts. This assistant provides a search-and-chat experience over uploaded documents.

## Objectives
- Provide secure authentication with JWT
- Enable course-specific document management
- Support reliable PDF ingestion and chunking
- Deliver grounded answers with citations

## Scope
The system supports PDF uploads, ingestion, and chat for a single user account at a time. It focuses on course materials and does not target web retrieval.

## Methodology
We use PyMuPDF for page extraction, LangChain for chunking and orchestration, sentence-transformer embeddings for retrieval, and a local instruction-following LLM for generation.

## System Design
The architecture follows a React frontend and FastAPI backend. SQLite stores metadata, and Chroma persists vector embeddings. JWT is used for authentication.

## Implementation
- FastAPI endpoints for auth, courses, PDFs, ingestion, and chat
- Chroma vector store with metadata filters
- HuggingFace local LLM (Flan-T5) with grounded prompting

## Results
The system returns answers with page-level citations and supports course-specific or all-course retrieval.

## Limitations
- Free hosting environments may reset Chroma persistence
- CPU inference can be slow for large PDFs

## Future Work
- Add role-based sharing of courses
- Improve summarization and citation ranking
- Add multimodal support for figures and tables

## References
- LangChain documentation
- ChromaDB documentation
- HuggingFace Transformers
