from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    courses = relationship("Course", back_populates="owner", cascade="all, delete")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="courses")
    pdfs = relationship("PDFDocument", back_populates="course", cascade="all, delete")


class PDFDocument(Base):
    __tablename__ = "pdf_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    ingested = Column(Boolean, default=False)

    course = relationship("Course", back_populates="pdfs")
