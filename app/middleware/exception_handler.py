"""
Exception Handler Middleware for FastAPI.

This module provides a global exception handler that catches all exceptions
and returns consistent error responses using the APIResponse format.

Usage:
    from app.middleware.exception_handler import add_exception_handlers
    
    app = FastAPI()
    add_exception_handlers(app)
"""

import logging
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions import (
    ShowcaseError,
    ValidationError,
    NotFoundError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
)
from app.schemas.responses import APIResponse, ErrorDetail

logger = logging.getLogger(__name__)


async def showcase_exception_handler(request: Request, exc: ShowcaseError) -> JSONResponse:
    """Handle all Showcase custom exceptions."""
    logger.warning(f"Showcase error: {exc.message}", extra={"details": exc.details})
    
    # Map exception types to HTTP status codes
    status_code = 500
    if isinstance(exc, ValidationError):
        status_code = 400
    elif isinstance(exc, NotFoundError):
        status_code = 404
    elif isinstance(exc, AuthenticationError):
        status_code = 401
    elif isinstance(exc, AuthorizationError):
        status_code = 403
    elif isinstance(exc, RateLimitError):
        status_code = 429
    
    return JSONResponse(
        status_code=status_code,
        content=APIResponse.error(
            error_type=exc.__class__.__name__,
            message=exc.message,
            details=exc.details
        ).model_dump()
    )


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    
    field = ".".join(str(loc) for loc in first_error.get("loc", []))
    message = first_error.get("msg", "Validation error")
    
    logger.warning(f"Validation error: {message}", extra={"field": field, "errors": errors})
    
    return JSONResponse(
        status_code=422,
        content=APIResponse.error(
            error_type="ValidationError",
            message=message,
            field=field,
            details={"errors": errors}
        ).model_dump()
    )


async def http_exception_handler(
    request: Request, 
    exc: StarletteHTTPException
) -> JSONResponse:
    """Handle Starlette HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error(
            error_type="HTTPError",
            message=str(exc.detail)
        ).model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    # Log the full traceback for debugging
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method}
    )
    
    # In production, don't expose internal error details
    return JSONResponse(
        status_code=500,
        content=APIResponse.error(
            error_type="InternalServerError",
            message="An unexpected error occurred. Please try again later."
        ).model_dump()
    )


def add_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI application.
    
    Args:
        app: FastAPI application instance
    
    Example:
        app = FastAPI()
        add_exception_handlers(app)
    """
    app.add_exception_handler(ShowcaseError, showcase_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered")
