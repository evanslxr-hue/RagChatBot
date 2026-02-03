# Data Model (ERD)

```mermaid
erDiagram
  USERS ||--o{ COURSES : owns
  USERS ||--o{ PDF_DOCUMENTS : uploads
  COURSES ||--o{ PDF_DOCUMENTS : contains

  USERS {
    int id PK
    string email
    string hashed_password
    datetime created_at
  }

  COURSES {
    int id PK
    string name
    int owner_id FK
    datetime created_at
  }

  PDF_DOCUMENTS {
    int id PK
    string filename
    string storage_path
    int course_id FK
    int owner_id FK
    datetime uploaded_at
    bool ingested
  }
```

## Data Model Notes
- PDFs are stored on disk under `storage/{user_id}/{course_id}/{pdf_id}.pdf`.
- Chroma stores chunk embeddings with metadata: user_id, course_id, pdf_id, filename, page_number.
