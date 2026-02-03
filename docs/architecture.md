# Architecture

```mermaid
flowchart LR
  User((Student)) --> UI[React UI]
  UI -->|JWT| API[FastAPI Backend]
  API --> DB[(SQLite: users, courses, pdfs)]
  API --> FS[(Local PDF Storage)]
  API --> Chroma[(ChromaDB Persisted)]
  Chroma --> Embed[Sentence-Transformers Embeddings]
  API --> LLM[HF Local LLM (Flan-T5)]
  FS --> Ingest[PyMuPDF Extraction + Chunking]
  Ingest --> Chroma
```
