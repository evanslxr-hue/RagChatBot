# UI/UX Design

## Design Principles
- **Clarity first**: Each section has a single task focus (auth, courses, PDFs, chat).
- **Progressive disclosure**: Only show PDF and chat tools after login.
- **Status visibility**: Ingestion status uses ✅/⏳ and messages provide feedback.
- **Consistency**: Uniform card layout, shared button styles, and spacing.

## 1) Login/Register
- Email + password inputs
- Buttons for login and register
- Success/error message feedback

## 2) Courses
- Create new course
- List existing courses
- Select and delete a course

## 3) PDF Library
- Upload PDF file (validated)
- Ingest PDFs for the selected course
- List PDFs with ingestion status

## 4) Chat
- Ask a question for a selected course or all courses
- Answer with citations
- Citation list displayed below the answer

## Layout Notes
- **Header**: project title, short description, and logout action.
- **Grid**: cards arranged in a responsive grid (`auto-fit`), so the UI adapts to narrow screens.
- **Primary flow**: Auth → course creation → PDF upload → ingestion → chat.
