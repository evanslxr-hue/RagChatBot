from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class CourseCreate(BaseModel):
    name: str


class CourseOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        orm_mode = True


class PDFOut(BaseModel):
    id: int
    filename: str
    ingested: bool
    uploaded_at: datetime

    class Config:
        orm_mode = True


class IngestRequest(BaseModel):
    course_id: Optional[int] = None
    pdf_ids: Optional[List[int]] = None


class ChatRequest(BaseModel):
    query: str
    course_id: Optional[int] = None
    all_courses: bool = False
    top_k: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    citations: List[str]
