from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, validator, Field
from typing import List, Union
import os

class Settings(BaseSettings):
  
    PROJECT_NAME: str = "Showcase AI"
    API_V1_STR: str = "/api/v1"

    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = ENV == "development"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/showcase")

    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 

    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")

    GEMINI_VISION_MODEL: str = os.getenv("GEMINI_VISION_MODEL", "gemini-1.5-flash")
    GEMINI_AGENT_MODEL: str = os.getenv("GEMINI_AGENT_MODEL", "gemini-1.5-pro")

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(default_factory=list)

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()