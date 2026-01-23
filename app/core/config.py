"""
Application configuration using Pydantic Settings.

All configuration values are loaded from environment variables with sensible defaults.
Use Field() consistently for all settings to enable validation and documentation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List, Union, Any
import json
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings use Pydantic Field for consistent validation and documentation.
    Environment variables take precedence over defaults.
    """
    
    # === Application ===
    PROJECT_NAME: str = Field(
        default="Showcase AI",
        description="Name of the application"
    )
    API_V1_STR: str = Field(
        default="/api/v1",
        description="API version prefix"
    )
    ENV: str = Field(
        default="development",
        description="Environment: development, staging, production, testing"
    )
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode (automatically set based on ENV)"
    )
    
    # === Database ===
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/showcase_db",
        description="PostgreSQL connection string"
    )
    
    # === Security ===
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT tokens. MUST be changed in production!"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="Algorithm used for JWT encoding"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60 * 24 * 8,  # 8 days
        description="Access token expiration time in minutes"
    )
    
    # === Firebase ===
    FIREBASE_SERVICE_ACCOUNT_PATH: str = Field(
        default="firebase-service-account.json",
        description="Path to Firebase service account JSON file"
    )
    
    # === Gemini AI ===
    GEMINI_API_KEY: str = Field(
        ...,  # Required field
        description="Google Gemini API key (required)"
    )
    GEMINI_VISION_MODEL: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model for vision/OCR tasks"
    )
    GEMINI_AGENT_MODEL: str = Field(
        default="gemini-1.5-pro",
        description="Gemini model for content generation"
    )
    
    # === GitHub OAuth ===
    GITHUB_CLIENT_ID: str = Field(
        default="",
        description="GitHub OAuth client ID"
    )
    GITHUB_CLIENT_SECRET: str = Field(
        default="",
        description="GitHub OAuth client secret"
    )
    
    # === CORS ===
    BACKEND_CORS_ORIGINS: Union[List[str], str] = Field(
        default=[],
        description="Allowed CORS origins (comma-separated string or JSON array)"
    )
    
    # === Redis (for Celery) ===
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for Celery task queue"
    )
    
    @field_validator("DEBUG", mode="before")
    @classmethod
    def set_debug_from_env(cls, v: Any, info) -> bool:
        """Set DEBUG based on ENV if not explicitly set."""
        if v is not None and v != "":
            return v if isinstance(v, bool) else str(v).lower() in ("true", "1", "yes")
        # Check if we can access ENV from the values
        return False
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            # Try parsing as JSON array
            if v.startswith("["):
                try:
                    return json.loads(v.replace("'", '"'))
                except json.JSONDecodeError:
                    pass
            # Parse as comma-separated
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return []
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENV == "development"
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENV == "production"
    
    def is_testing(self) -> bool:
        """Check if running in test mode."""
        return self.ENV == "testing"
    
    model_config = SettingsConfigDict(
        env_file=".env" if os.getenv("ENV") != "testing" else None,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Create settings instance
settings = Settings()

# Automatically enable DEBUG in development
if settings.ENV == "development":
    # Override DEBUG in development mode
    object.__setattr__(settings, "DEBUG", True)
