"""
Generation Team - Content generation and template selection.

OPTIMIZED ARCHITECTURE:
- Uses a single "Portfolio Creator" agent to generate data (Data Injection).
- Outputs structured JSON (Pydantic) to avoid token wastage on chat/syntax.
- Selects template in the same pass or via lightweight lookup.
"""

import os
import json
from typing import Optional
from agno.agent import Agent
from agno.team import Team
from app.schemas.portfolio import PortfolioOutput
from agents.model import get_model
from agents.tools.template_tools import TemplateRegistryTools

GEMINI_MODEL = get_model()

# -------------------------------------------------------------------------
# 1. Template Selector (Lightweight)
# -------------------------------------------------------------------------
# We keep this separate but lightweight: it only sees specific metadata, 
# not the full resume, to save tokens.
template_selector = Agent(
    name="Template Selector",
    role="Select the best template ID based on user role",
    model=GEMINI_MODEL,
    tools=[TemplateRegistryTools()],
    instructions="""
    You are a precise system selector.
    
    1. Analyze the user's role and experience level.
    2. Use `find_templates_by_role` or `list_templates` to find the best match.
    3. Return ONLY the `template_id` (string) and nothing else.
    
    Example Output:
    one_temp
    """,

    markdown=False, # We want raw string if possible, or simple text
)


# -------------------------------------------------------------------------
# 2. Portfolio Creator (The Heavy Lifter)
# -------------------------------------------------------------------------
# This agent takes the Resume Data and "Injects" it into our Schema.
# It does NOT generate React code. It generates Data.

portfolio_creator = Agent(
    name="Portfolio Creator",
    role="Transform resume data into a professional portfolio structure",
    model=GEMINI_MODEL,

    instructions="""
    You are a Content Strategist for professional portfolios.
    
    Your Task:
    1. Read the provided Resume Data.
    2. Transform it into the highly structured `PortfolioOutput` format.
    3. Improve the content:
       - Write a punchy 'tagline' (5-10 words).
       - Create a 'bio_short' (elevator pitch) and 'bio_long' (professional narrative).
       - Clean up project descriptions to be impact-focused.
       - Group skills into logical categories (Languages, Frameworks, Tools).
       - Select a 'theme' (primary_color, style) that fits the role.
    
    Rules:
    - Do NOT invent facts. Use the source data.
    - If data is missing (e.g. no projects), fill with empty lists but maintain valid schema.
    - Ensure 'quality_score' reflects the completeness of the resume (0.0 to 1.0).
    """,
)

# to strictly control data flow and token usage.


# Generation Team - Wraps the agents for compatibility with Portfolio Team
generation_team = Team(
    name="Generation Team",
    description="Generate content and select template for portfolio",
    members=[portfolio_creator, template_selector],
    model=GEMINI_MODEL,
    instructions="""
    You coordinate the generation of portfolio content.
    
    1. Use Portfolio Creator to generate structured data.
    2. Use Template Selector to pick a template.
    3. Return the combined result.
    """,
)
