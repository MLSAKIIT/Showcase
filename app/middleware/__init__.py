"""
Middleware package for Showcase AI.

This package contains FastAPI middleware components.
"""

from app.middleware.exception_handler import add_exception_handlers

__all__ = ["add_exception_handlers"]
