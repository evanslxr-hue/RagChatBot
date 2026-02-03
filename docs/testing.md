# Testing Plan

## Unit Tests
- Auth: password hashing and login error handling
- Health endpoint response

## Integration Tests
- Course creation and listing
- Upload PDFs and ingest flow
- Chat response formatting

## Manual Tests
- Register, login, logout
- Create course, upload PDFs, ingest
- Ask course-scoped questions and all-courses questions

## Sample Pytest
See `backend/tests/test_health.py` for a starting example.
