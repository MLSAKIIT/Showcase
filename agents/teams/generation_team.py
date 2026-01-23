"""
Generation Team - Content generation and template selection.

This team handles:
1. Building portfolio schema structure
2. Generating compelling content using AI
3. Selecting the best template for the user
"""

import os
from agno.agent import Agent
from agno.team import Team

from agents.tools.template_tools import TemplateRegistryTools

# Get configured Gemini model with rate limiting
from agents.model import get_model

GEMINI_MODEL = get_model()


# Schema Builder Agent
schema_agent = Agent(
    name="Schema Builder Agent",
    role="Build portfolio schema structure from parsed resume data",
    model=GEMINI_MODEL,
    instructions="""
    You are a portfolio architecture specialist. Your job is to create
    a well-structured portfolio schema from parsed resume data.
    
    Create a schema with these sections:
    
    {
        "hero": {
            "name": "User's name",
            "tagline": "Compelling professional tagline",
            "subtitle": "Current role or aspiration",
            "cta_primary": "Primary call to action",
            "cta_secondary": "Secondary call to action"
        },
        "about": {
            "title": "About section title",
            "bio": "Professional bio (2-3 paragraphs)",
            "highlights": ["Key highlight 1", "Key highlight 2", ...]
        },
        "skills": {
            "technical": [{"name": "Skill", "level": 90, "category": "Frontend"}],
            "soft": ["Communication", "Leadership", ...],
            "tools": ["VS Code", "Figma", ...]
        },
        "experience": [...],
        "projects": [...],
        "education": [...],
        "contact": {...}
    }
    
    Make the structure comprehensive but adaptable to different templates.
    """,
    markdown=True,
)


# Content Generator Agent
content_agent = Agent(
    name="Content Generator Agent",
    role="Generate compelling, professional portfolio content",
    model=GEMINI_MODEL,
    instructions="""
    You are a creative content writer specializing in professional portfolios.
    Your job is to generate engaging, impactful content.
    
    Content Guidelines:
    
    1. HERO TAGLINE:
       - 5-10 words
       - Memorable and unique
       - Highlights specialty or value proposition
       - Examples: "Crafting Experiences, One Pixel at a Time"
    
    2. PROFESSIONAL BIO:
       - 150-200 words
       - First person voice
       - Highlights journey, expertise, and passion
       - Includes personality, not just credentials
       - Ends with current focus or goals
    
    3. PROJECT DESCRIPTIONS:
       - Start with impact/result
       - Mention specific technologies
       - Include metrics when possible
       - 2-3 sentences max
    
    4. SKILL DESCRIPTIONS:
       - Group by category (Frontend, Backend, Design, etc.)
       - Include proficiency levels (1-100)
       - Add context for key skills
    
    Generate content that feels authentic and professional, not generic.
    Avoid buzzwords and clichés.
    """,
    markdown=True,
)


# Template Selector Agent
template_selector = Agent(
    name="Template Selector Agent",
    role="Select the best template based on user profile and preferences",
    model=GEMINI_MODEL,
    tools=[TemplateRegistryTools()],
    instructions="""
    You are a design consultant who selects the perfect portfolio template.
    
    Selection Criteria:
    
    1. ROLE-BASED:
       - Developers → modern-minimal, terminal-style (one_temp, seven_temp)
       - Designers → creative, visual-heavy (four_temp, eight_temp)
       - Fullstack → professional, comprehensive (two_temp, six_temp)
       - Writers/Academics → blog-style (three_temp, ten_temp)
    
    2. EXPERIENCE LEVEL:
       - Junior → simpler layouts, focus on projects
       - Senior → comprehensive, timeline-focused
       - Executive → minimal, impact-focused
    
    3. CONTENT DENSITY:
       - Many projects → gallery templates
       - Long experience → timeline templates
       - Minimal content → single-page, impactful
    
    4. USER PREFERENCES:
       - If user specifies style preferences, prioritize those
       - Consider color preferences for template matching
    
    Use the template registry tools to:
    1. List available templates
    2. Find templates by role/features
    3. Return the selected template ID with reasoning
    """,
    markdown=True,
)


# Generation Team - Coordinates content agents
generation_team = Team(
    name="Generation Team",
    description="Generate portfolio content and select optimal template",
    members=[schema_agent, content_agent, template_selector],
    model=GEMINI_MODEL,
    instructions="""
    You coordinate portfolio content generation.
    
    Workflow:
    1. Delegate to Schema Builder to create portfolio structure
    2. Delegate to Content Generator to write compelling content
    3. Delegate to Template Selector to choose the best template
    
    Return:
    - Complete portfolio schema with generated content
    - Selected template ID and reasoning
    - Any recommendations for customization
    """,
    markdown=True,
)
