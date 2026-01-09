from pydantic import BaseModel, Field
from typing import List, Optional

class ProjectSchema(BaseModel):
    title: str
    description: str = Field(..., min_length=50)
    tech_stack: List[str]
    featured: bool = False
    link: Optional[str] = None


class HeroSchema(BaseModel):
    name: str
    tagline: str = Field(..., max_length=100)
    bio_short: str
    avatar_url: Optional[str] = None


class SkillCategory(BaseModel):
    category: str
    items: List[str]


class ThemeSchema(BaseModel):
    primary_color: str = "#4A90E2"
    style: str = "modern_tech"


class PortfolioOutput(BaseModel):
    hero: HeroSchema
    bio_long: str = Field(..., min_length=150)
    projects: List[ProjectSchema]
    skills: List[SkillCategory]
    theme: ThemeSchema
    quality_score: float
    generated_at: str
