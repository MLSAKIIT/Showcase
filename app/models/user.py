from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """User model for storing GitHub authenticated users."""
    
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    github_id: int = Field(unique=True, index=True)
    username: str = Field(index=True)
    email: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)
    github_access_token: str = Field(default="")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserRead(SQLModel):
    """Response model for user data (excludes sensitive fields)."""
    
    id: int
    github_id: int
    username: str
    email: Optional[str]
    name: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime
