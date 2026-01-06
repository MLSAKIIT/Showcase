from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import uuid

class ResumeUploadResponse(BaseModel):
    job_id: str
    status: str = "processing"
    message: str

class ResumeDataInput(BaseModel):
    name: str = Field(..., description="Full name of the user")
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[dict] = Field(default_factory=list)
    education: List[dict] = Field(default_factory=list)
    projects: List[dict] = Field(default_factory=list)