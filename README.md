# Context-Aware Campus Study Assistant (RAG Chatbot)

A full-stack final-year project using React + FastAPI + LangChain + ChromaDB + PyMuPDF + sentence-transformers + a local HuggingFace LLM. The assistant lets students upload course PDFs, ingest and embed them, and ask questions with citations.

> **Note:** Chroma persistence may reset on rebuild because free disk is not persistent on Hugging Face Spaces.

## Features
- Email/password + JWT auth
- Create/list/delete courses
- Upload PDFs per course (stored locally)
- `/api/ingest` to chunk and embed PDFs into Chroma
- `/api/chat` with course-scoped or ALL courses retrieval
- Answers include citations like `[filename.pdf, page 12]`

## Setup

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 7860
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Build & Serve React From FastAPI
```bash
cd frontend
npm install
npm run build
cd ../backend
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

## Environment Variables
Create a `.env` in the repo root (or backend) with:
```
SECRET_KEY=change-me
MODEL_NAME=google/flan-t5-base
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
CHROMA_PERSIST_DIR=./backend/data/chroma
DATABASE_URL=sqlite:///./backend/data/app.db
STORAGE_ROOT=./backend/storage
```

## Docker (HF Spaces Compatible)
Build and run locally:
```bash
docker build -t rag-chatbot .
docker run -p 7860:7860 rag-chatbot
```

## Docs
See `/docs` for architecture, data model, API docs, UI description, testing plan, report draft, and demo script.
