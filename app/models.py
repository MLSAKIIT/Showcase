"""
SQLAlchemy database models.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class JobStatus(str, enum.Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(Base):
    """Job model for tracking pipeline execution."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    error_message = Column(Text, nullable=True)
    extra_metadata = Column(JSON, nullable=True)  # Fixed: Renamed from metadata

    # Relationships
    artifacts = relationship("Artifact", back_populates="job", cascade="all, delete-orphan")
    resume = relationship("Resume", back_populates="job", uselist=False, cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="job", cascade="all, delete-orphan")


class Artifact(Base):
    """Artifact model for storing pipeline outputs."""
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    artifact_type = Column(String(100), nullable=False)  # e.g., "resume_json", "frontend_bundle", "preview"
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    extra_metadata = Column(JSON, nullable=True) # Fixed: Renamed from metadata

    # Relationships
    job = relationship("Job", back_populates="artifacts")


class Resume(Base):
    """Resume model for storing processed resume data."""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), unique=True, nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    structured_json = Column(JSON, nullable=True)  # Structured resume data
    ocr_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    job = relationship("Job", back_populates="resume")


class ChatMessage(Base):
    """Chat message model for storing AI interactions."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    role = Column(String(20), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    extra_metadata = Column(JSON, nullable=True) # Fixed: Renamed from metadata

    # Relationships
    job = relationship("Job", back_populates="chat_messages")