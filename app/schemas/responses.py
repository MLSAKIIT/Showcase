"""
Standardized API response schemas for Showcase AI.

This module provides consistent response wrappers for all API endpoints,
ensuring uniform error handling and response structure.

Usage:
    from app.schemas.responses import APIResponse, PaginatedResponse
    
    @router.get("/items")
    async def list_items() -> APIResponse[List[Item]]:
        items = await get_items()
        return APIResponse.success(data=items)
"""

from typing import TypeVar, Generic, Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


T = TypeVar("T")


class ResponseMeta(BaseModel):
    """Metadata included in API responses."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    processing_time_ms: Optional[int] = None
    version: str = "1.0.0"


class ErrorDetail(BaseModel):
    """Detailed error information for API responses."""
    
    error_type: str = Field(..., description="Error class name")
    message: str = Field(..., description="Human-readable error message")
    field: Optional[str] = Field(None, description="Field that caused the error")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper.
    
    All API endpoints should return responses wrapped in this format
    for consistency across the application.
    """
    
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[T] = Field(None, description="Response payload")
    error: Optional[ErrorDetail] = Field(None, description="Error details if request failed")
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
    
    @classmethod
    def success(
        cls, 
        data: T, 
        request_id: Optional[str] = None,
        processing_time_ms: Optional[int] = None
    ) -> "APIResponse[T]":
        """Create a successful response."""
        return cls(
            success=True,
            data=data,
            meta=ResponseMeta(
                request_id=request_id,
                processing_time_ms=processing_time_ms
            )
        )
    
    @classmethod
    def error(
        cls, 
        error_type: str,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> "APIResponse[None]":
        """Create an error response."""
        return cls(
            success=False,
            error=ErrorDetail(
                error_type=error_type,
                message=message,
                field=field,
                details=details
            ),
            meta=ResponseMeta(request_id=request_id)
        )
    
    @classmethod
    def from_exception(
        cls, 
        exc: Exception,
        request_id: Optional[str] = None
    ) -> "APIResponse[None]":
        """Create an error response from an exception."""
        # Import here to avoid circular imports
        from app.exceptions import ShowcaseError
        
        if isinstance(exc, ShowcaseError):
            return cls.error(
                error_type=exc.__class__.__name__,
                message=exc.message,
                details=exc.details,
                request_id=request_id
            )
        
        return cls.error(
            error_type="InternalError",
            message=str(exc),
            request_id=request_id
        )


class PaginationInfo(BaseModel):
    """Pagination metadata for list responses."""
    
    page: int = Field(1, ge=1, description="Current page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")
    
    @classmethod
    def create(cls, page: int, page_size: int, total_items: int) -> "PaginationInfo":
        """Create pagination info from basic parameters."""
        total_pages = (total_items + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """Response wrapper for paginated list endpoints."""
    
    success: bool = True
    data: List[T] = Field(default_factory=list)
    pagination: PaginationInfo
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
    
    @classmethod
    def create(
        cls,
        items: List[T],
        page: int,
        page_size: int,
        total_items: int,
        request_id: Optional[str] = None
    ) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        return cls(
            data=items,
            pagination=PaginationInfo.create(page, page_size, total_items),
            meta=ResponseMeta(request_id=request_id)
        )


# Common response types for reuse
class MessageResponse(BaseModel):
    """Simple message response."""
    message: str


class JobStatusResponse(BaseModel):
    """Response for job status queries."""
    job_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    current_stage: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    """Response for health check endpoints."""
    status: str = "online"
    version: str
    engine: str
    uptime_seconds: Optional[int] = None
