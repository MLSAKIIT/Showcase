"""
Unified exception hierarchy for Showcase AI.

This module provides a centralized exception hierarchy for consistent 
error handling across the entire application. All custom exceptions 
should inherit from ShowcaseError.

Usage:
    from app.exceptions import ValidationError, PipelineError
    
    if not data:
        raise ValidationError("Input data cannot be empty")
"""

from typing import Optional, Dict, Any


class ShowcaseError(Exception):
    """
    Base exception for all Showcase errors.
    
    All custom exceptions in this application should inherit from this class.
    This allows for easy catching of all application-specific errors.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to a dictionary for API responses."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


# === Input/Validation Errors ===

class ValidationError(ShowcaseError):
    """
    Raised when input validation fails.
    
    Examples:
        - Missing required fields
        - Invalid file format
        - Data type mismatches
    """
    pass


class FileValidationError(ValidationError):
    """
    Raised when file validation fails.
    
    Examples:
        - Unsupported file type
        - File too large
        - Corrupted file
    """
    
    def __init__(
        self, 
        message: str, 
        filename: Optional[str] = None,
        file_type: Optional[str] = None,
        max_size: Optional[int] = None
    ):
        details = {}
        if filename:
            details["filename"] = filename
        if file_type:
            details["file_type"] = file_type
        if max_size:
            details["max_size_bytes"] = max_size
        super().__init__(message, details)


# === Pipeline Errors ===

class PipelineError(ShowcaseError):
    """
    Raised when the AI pipeline execution fails.
    
    Examples:
        - Pipeline stage timeout
        - Agent execution failure
        - Pipeline configuration error
    """
    
    def __init__(
        self, 
        message: str, 
        stage: Optional[str] = None, 
        original_error: Optional[Exception] = None
    ):
        details = {}
        if stage:
            details["stage"] = stage
        if original_error:
            details["original_error"] = str(original_error)
        super().__init__(message, details)
        self.stage = stage
        self.original_error = original_error


class OCRError(PipelineError):
    """
    Raised when text extraction (OCR) fails.
    
    Examples:
        - PDF parsing failure
        - Image processing error
        - No text found in document
    """
    pass


class ContentGenerationError(PipelineError):
    """
    Raised when AI content generation fails.
    
    Examples:
        - LLM API error
        - Invalid response format
        - Content validation failure
    """
    pass


class SchemaError(PipelineError):
    """
    Raised when schema building or validation fails.
    
    Examples:
        - Invalid schema structure
        - Missing required schema fields
        - Schema version mismatch
    """
    pass


# === External Service Errors ===

class ExternalServiceError(ShowcaseError):
    """
    Raised when an external API call fails.
    
    Examples:
        - Gemini API error
        - Vercel deployment failure
        - GitHub API issue
    """
    
    def __init__(
        self, 
        message: str, 
        service_name: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None
    ):
        details = {"service": service_name}
        if status_code:
            details["status_code"] = status_code
        if response_body:
            details["response"] = response_body[:500]  # Truncate long responses
        super().__init__(message, details)
        self.service_name = service_name
        self.status_code = status_code


class GeminiError(ExternalServiceError):
    """Raised when Gemini API calls fail."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_body: Optional[str] = None
    ):
        super().__init__(message, "Gemini", status_code, response_body)


class RateLimitError(ExternalServiceError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(self, service_name: str, retry_after: Optional[int] = None):
        message = f"Rate limit exceeded for {service_name}"
        if retry_after:
            message += f". Retry after {retry_after} seconds."
        super().__init__(message, service_name)
        self.retry_after = retry_after


# === Database Errors ===

class DatabaseError(ShowcaseError):
    """
    Raised when database operations fail.
    
    Examples:
        - Connection failure
        - Transaction error
        - Constraint violation
    """
    pass


class NotFoundError(DatabaseError):
    """
    Raised when a requested resource is not found.
    
    Examples:
        - Job not found
        - Portfolio not found
        - User not found
    """
    
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(message, {"resource_type": resource_type, "resource_id": resource_id})


# === Authentication/Authorization Errors ===

class AuthError(ShowcaseError):
    """Base class for authentication and authorization errors."""
    pass


class AuthenticationError(AuthError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(AuthError):
    """Raised when the user lacks permission for an action."""
    pass


# === Configuration Errors ===

class ConfigurationError(ShowcaseError):
    """
    Raised when configuration is invalid or missing.
    
    Examples:
        - Missing API key
        - Invalid database URL
        - Malformed environment variable
    """
    pass
