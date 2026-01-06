from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict

class ProjectSchema(BaseModel):
    title: str
    description: str = Field(..., min_length=50, description="AI-enhanced description")
    tech_stack: List[str]
    featured: bool = False
    link: Optional[str] = None

class HeroSchema(BaseModel):
    name: str
    tagline: str = Field(..., max_length=100)
    bio_short: str
    avatar_url: Optional[str] = None

class SkillCategory(BaseModel):
    category: str # e.g., "Languages", "Frameworks"
    items: List[str]

class ThemeSchema(BaseModel):
    primary_color: str = Field("#4A90E2", pattern="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
    style: str = "modern_tech" # options: modern_tech, minimalist, creative

class PortfolioOutput(BaseModel):
    
    hero: HeroSchema
    bio_long: str = Field(..., min_length=150)
    projects: List[ProjectSchema]
    skills: List[SkillCategory]
    theme: ThemeSchema
    
    # Metadata for the system
    quality_score: float = Field(..., ge=0, le=1.0)
    generated_at: str