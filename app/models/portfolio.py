
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON, Column

class Portfolio(SQLModel, table=True):
    __tablename__ = "portfolios"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    user_id: str = Field(index=True, nullable=False)
    job_id: str = Field(unique=True, index=True, nullable=False)
    
    full_name: str
    email: Optional[str] = None
    
    # Slug for public URLs (e.g., /public/john-doe-portfolio)
    slug: Optional[str] = Field(default=None, unique=True, index=True)
    
    # Use generic JSON for SQLite compatibility
    content: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    theme_id: str = Field(default="modern_tech")
    deployed_url: Optional[str] = None
    is_published: bool = Field(default=False, index=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
