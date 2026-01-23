"""
Portfolio Master Team - Main coordinator for AI portfolio generation.

This is the top-level team that coordinates all sub-teams:
1. Parsing Team - Extract and parse resume data
2. Generation Team - Generate content and select template
3. Customization Team - Apply customizations and modifications

Usage:
    from agents.teams.portfolio_team import portfolio_team
    
    response = await portfolio_team.arun(
        "Create a portfolio from my resume with dark blue theme and animations"
    )
"""

import os
from agno.agent import Agent
from agno.team import Team

from agents.teams.parsing_team import parsing_team
from agents.teams.generation_team import generation_team
from agents.teams.customization_team import customization_team
from agents.tools.file_tools import FileSystemTools
from agents.tools.template_tools import TemplateRegistryTools

# Get configured Gemini model with rate limiting
from agents.model import get_model

GEMINI_MODEL = get_model()


# Coordinator Agent - Manages the overall workflow
coordinator_agent = Agent(
    name="Coordinator Agent",
    role="Coordinate the portfolio generation workflow",
    model=GEMINI_MODEL,
    tools=[FileSystemTools(), TemplateRegistryTools()],
    instructions="""
    You are the workflow coordinator. You manage the end-to-end 
    portfolio generation process and communicate with the user.
    
    Your responsibilities:
    1. Understand user requirements
    2. Delegate to appropriate sub-teams
    3. Track progress across teams
    4. Communicate results and next steps
    5. Handle errors gracefully
    
    Workflow:
    1. If user provides raw resume/text → delegate to Parsing Team
    2. If data is already parsed → delegate to Generation Team
    3. If user wants customizations → delegate to Customization Team
    
    Always be helpful and explain what's happening.
    """,
    markdown=True,
)


# Portfolio Master Team
portfolio_team = Team(
    name="Portfolio Master Team",
    description="Complete AI-powered portfolio generation and customization",
    members=[
        coordinator_agent,
        parsing_team,
        generation_team,
        customization_team,
    ],
    model=GEMINI_MODEL,
    instructions="""
    You are the Portfolio Master Team - a powerful AI system that creates
    stunning, customized portfolio websites from resumes.
    
    CAPABILITIES:
    
    1. RESUME PARSING:
       - Extract text from PDF/images (OCR)
       - Parse into structured data
       - Validate and clean data
    
    2. CONTENT GENERATION:
       - Build portfolio schema
       - Generate compelling content (bio, taglines, descriptions)
       - Select the best template for the user
    
    3. CUSTOMIZATION (FULL FLEXIBILITY):
       - Inject user data into templates
       - Apply any color scheme or theme
       - Add/remove features (dark mode, animations, etc.)
       - Make ANY code modifications the user requests
    
    INTERACTION STYLE:
    
    - Be proactive: Ask about preferences if unclear
    - Be creative: Suggest improvements and ideas
    - Be flexible: Handle any customization request
    - Be helpful: Explain what you're doing
    
    EXAMPLE REQUESTS YOU CAN HANDLE:
    
    - "Create a portfolio from my resume"
    - "Make it dark blue with orange accents"
    - "Add a dark mode toggle"
    - "I want a minimalist look with animations"
    - "Change the font to Inter"
    - "Add a particle background"
    - "Remove the contact form"
    - "Make the projects section a carousel"
    
    You can do ALL of this. Delegate to the right sub-teams and make it happen!
    
    WORKFLOW:
    
    For a complete generation:
    1. Delegate to Parsing Team to extract resume data
    2. Ask user about preferences (colors, features, style)
    3. Delegate to Generation Team to create content and select template
    4. Delegate to Customization Team to apply preferences
    5. Return the path to the customized portfolio
    
    For customization only:
    - Delegate directly to Customization Team
    
    Always keep the user informed of progress.
    """,
    markdown=True,
)


# Export for easy access
__all__ = ["portfolio_team"]
