import logging
from pathlib import Path
from typing import List

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import models, schemas
from .auth import get_current_user, create_access_token, get_password_hash, verify_password
from .config import settings, ensure_directories
from .database import Base, engine, get_db
from .rag import ingest_documents, retrieve_context, build_answer, format_citations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ensure_directories()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Context-Aware Campus Study Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_build = Path("frontend/build")
if frontend_build.exists():
    app.mount("/", StaticFiles(directory=str(frontend_build), html=True), name="frontend")


@app.post("/api/auth/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = models.User(email=user.email, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/api/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/api/courses", response_model=List[schemas.CourseOut])
def list_courses(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Course).filter(models.Course.owner_id == current_user.id).all()


@app.post("/api/courses", response_model=schemas.CourseOut)
def create_course(
    course: schemas.CourseCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_course = models.Course(name=course.name, owner_id=current_user.id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@app.delete("/api/courses/{course_id}", status_code=204)
def delete_course(
    course_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = (
        db.query(models.Course)
        .filter(models.Course.id == course_id, models.Course.owner_id == current_user.id)
        .first()
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()


@app.post("/api/courses/{course_id}/pdfs", response_model=schemas.PDFOut)
def upload_pdf(
    course_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    contents = file.file.read()
    max_bytes = settings.max_pdf_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(status_code=400, detail="File too large")
    course = (
        db.query(models.Course)
        .filter(models.Course.id == course_id, models.Course.owner_id == current_user.id)
        .first()
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    pdf = models.PDFDocument(
        filename=file.filename,
        storage_path="",
        course_id=course.id,
        owner_id=current_user.id,
    )
    db.add(pdf)
    db.commit()
    db.refresh(pdf)

    storage_dir = Path(settings.storage_root) / str(current_user.id) / str(course_id)
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_path = storage_dir / f"{pdf.id}.pdf"
    storage_path.write_bytes(contents)

    pdf.storage_path = str(storage_path)
    db.commit()
    db.refresh(pdf)
    return pdf


@app.get("/api/courses/{course_id}/pdfs", response_model=List[schemas.PDFOut])
def list_pdfs(
    course_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.PDFDocument)
        .filter(
            models.PDFDocument.course_id == course_id,
            models.PDFDocument.owner_id == current_user.id,
        )
        .all()
    )


@app.delete("/api/pdfs/{pdf_id}", status_code=204)
def delete_pdf(
    pdf_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pdf = (
        db.query(models.PDFDocument)
        .filter(models.PDFDocument.id == pdf_id, models.PDFDocument.owner_id == current_user.id)
        .first()
    )
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    Path(pdf.storage_path).unlink(missing_ok=True)
    db.delete(pdf)
    db.commit()


@app.post("/api/ingest")
def ingest(
    request: schemas.IngestRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.PDFDocument).filter(models.PDFDocument.owner_id == current_user.id)
    if request.course_id:
        query = query.filter(models.PDFDocument.course_id == request.course_id)
    if request.pdf_ids:
        query = query.filter(models.PDFDocument.id.in_(request.pdf_ids))
    pdfs = query.all()
    if not pdfs:
        raise HTTPException(status_code=404, detail="No PDFs found to ingest")
    total_chunks = 0
    for pdf in pdfs:
        chunks = ingest_documents(
            pdf.storage_path,
            pdf.filename,
            current_user.id,
            pdf.course_id,
            pdf.id,
        )
        total_chunks += chunks
        pdf.ingested = True
    db.commit()
    return {"ingested_pdfs": len(pdfs), "chunks": total_chunks}


@app.post("/api/chat", response_model=schemas.ChatResponse)
def chat(
    request: schemas.ChatRequest,
    current_user: models.User = Depends(get_current_user),
):
    if request.course_id is None and not request.all_courses:
        raise HTTPException(status_code=400, detail="Select a course or enable all_courses")
    docs = retrieve_context(
        request.query,
        user_id=current_user.id,
        course_id=request.course_id,
        top_k=request.top_k or settings.top_k,
        all_courses=request.all_courses,
    )
    if not docs:
        answer = (
            "I don't have enough information in your uploaded documents to answer that. "
            "Try uploading relevant PDFs or asking about specific pages or topics."
        )
        return schemas.ChatResponse(answer=answer, citations=[])
    answer = build_answer(request.query, docs)
    citations = format_citations(docs)
    return schemas.ChatResponse(answer=answer, citations=citations)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/static/{path:path}")
async def static_files(path: str):
    if not frontend_build.exists():
        raise HTTPException(status_code=404, detail="Frontend build not found")
    return FileResponse(frontend_build / path)
