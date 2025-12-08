"""
API dependencies and utilities.
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db


def get_database(db: Session = Depends(get_db)) -> Session:
    """Dependency for database session."""
    return db

