import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text


class JobStatus(str, Enum):
    """Job processing status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    OCR_EXTRACTING = "ocr_extracting"
    AI_GENERATING = "ai_generating"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(SQLModel, table=True):
    """Job model for tracking resume processing status."""
    
    __tablename__ = "jobs"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_id: str = Field(unique=True, index=True, nullable=False)
    
    user_id: str = Field(index=True, nullable=False)
    
    status: JobStatus = Field(default=JobStatus.PENDING, index=True)
    
    # Processing metadata
    progress_percentage: int = Field(default=0, ge=0, le=100)
    current_stage: Optional[str] = None
    
    # Error tracking
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    error_details: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(Text))
    
    # File metadata
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Relationships
    portfolio_id: Optional[uuid.UUID] = Field(default=None, foreign_key="portfolios.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def update_status(self, status: JobStatus, stage: Optional[str] = None):
        """Update job status and optionally the current stage."""
        self.status = status
        self.current_stage = stage
        self.updated_at = datetime.utcnow()
        
    def mark_completed(self, duration: float):
        """Mark job as completed with duration."""
        self.status = JobStatus.COMPLETED
        self.progress_percentage = 100
        self.completed_at = datetime.utcnow()
        self.duration_seconds = duration
        self.updated_at = datetime.utcnow()
        
    def mark_failed(self, error_message: str, error_details: Optional[Dict[str, Any]] = None):
        """Mark job as failed with error information."""
        self.status = JobStatus.FAILED
        self.error_message = error_message
        self.error_details = error_details
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_seconds = (datetime.utcnow() - self.started_at).total_seconds()
        self.updated_at = datetime.utcnow()
