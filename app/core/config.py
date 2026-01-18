from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator, Field, ValidationInfo
from typing import List, Union, Any
import os
import json

class Settings(BaseSettings):
  
    PROJECT_NAME: str = "Showcase AI"
    API_V1_STR: str = "/api/v1"

    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = ENV == "development"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/showcase")

    SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
        description="Secret key for JWT tokens. Must be set in production!"
    )

    FIREBASE_SERVICE_ACCOUNT_PATH: str = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_PATH", 
        "firebase-service-account.json"
    )
  
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 

    GEMINI_API_KEY: str = Field(...)

    GEMINI_VISION_MODEL: str = os.getenv("GEMINI_VISION_MODEL", "gemini-1.5-flash")
    GEMINI_AGENT_MODEL: str = os.getenv("GEMINI_AGENT_MODEL", "gemini-1.5-pro")

    # GitHub OAuth Settings
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")

    BACKEND_CORS_ORIGINS: Union[List[str], str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("["):
                try:
                    return json.loads(v.replace("'", '"'))
                except Exception:
                    pass
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

    model_config = SettingsConfigDict(
        env_file=".env" if os.getenv("ENV") != "testing" else None,
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
