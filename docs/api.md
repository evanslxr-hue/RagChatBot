# API दस्तावेज़ (API Docs)

Base URL: `http://localhost:7860`

## Auth
### Register
`POST /api/auth/register`
```json
{ "email": "student@uni.edu", "password": "password123" }
```

### Login
`POST /api/auth/login`
Form URL encoded:
```
username=student@uni.edu&password=password123
```
Response:
```json
{ "access_token": "...", "token_type": "bearer" }
```

## Courses
### List courses
`GET /api/courses`
Authorization: `Bearer <token>`

### Create course
`POST /api/courses`
```json
{ "name": "Data Structures" }
```

### Delete course
`DELETE /api/courses/{course_id}`

## PDFs
### Upload PDF
`POST /api/courses/{course_id}/pdfs`
Multipart form with `file` (PDF only)

### List PDFs
`GET /api/courses/{course_id}/pdfs`

### Delete PDF
`DELETE /api/pdfs/{pdf_id}`

## Ingest
`POST /api/ingest`
```json
{ "course_id": 1 }
```
or
```json
{ "pdf_ids": [1,2] }
```
Response:
```json
{ "ingested_pdfs": 2, "chunks": 120 }
```

## Chat
`POST /api/chat`
```json
{ "query": "Explain binary search", "course_id": 1, "all_courses": false }
```
Response:
```json
{
  "answer": "...",
  "citations": ["[lecture1.pdf, page 3]"]
}
```

If the answer is not found:
```json
{
  "answer": "I don't have enough information in your uploaded documents to answer that. Try uploading relevant PDFs or asking about specific pages or topics.",
  "citations": []
}
```
