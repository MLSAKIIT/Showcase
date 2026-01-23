"""
Parsing Team - Resume parsing and data extraction.

This team handles:
1. OCR text extraction from uploaded files
2. Parsing text into structured data
3. Validating and cleaning data
"""

import os
from agno.agent import Agent
from agno.team import Team

# Get configured Gemini model with rate limiting
from agents.model import get_model

GEMINI_MODEL = get_model()


# OCR Agent - Extracts text from files
ocr_agent = Agent(
    name="OCR Agent",
    role="Extract text from uploaded PDF and image files",
    model=GEMINI_MODEL,
    instructions="""
    You are an OCR specialist. Your job is to extract all text from uploaded 
    resume files (PDFs, images, etc.).
    
    When given a file:
    1. Use OCR tools to extract all visible text
    2. Preserve structure where possible (sections, bullet points)
    3. Handle multiple pages if present
    4. Return the raw extracted text
    
    If text extraction fails, explain why and what can be done.
    """,
    markdown=True,
)


# Parser Agent - Converts text to structured data
parser_agent = Agent(
    name="Resume Parser Agent",
    role="Parse raw resume text into structured JSON data",
    model=GEMINI_MODEL,
    instructions="""
    You are a resume parsing expert. Your job is to convert raw resume text
    into structured JSON data.
    
    Extract the following information:
    
    {
        "name": "Full name of the person",
        "email": "Email address",
        "phone": "Phone number",
        "location": "City, Country",
        "title": "Current/Desired job title",
        "summary": "Professional summary or objective",
        "skills": ["skill1", "skill2", ...],
        "experience": [
            {
                "company": "Company name",
                "position": "Job title",
                "duration": "Start - End",
                "description": "What they did",
                "highlights": ["achievement1", ...]
            }
        ],
        "education": [
            {
                "institution": "School name",
                "degree": "Degree type",
                "field": "Field of study",
                "year": "Graduation year"
            }
        ],
        "projects": [
            {
                "name": "Project name",
                "description": "What it does",
                "technologies": ["tech1", "tech2"],
                "url": "Link if available"
            }
        ],
        "links": {
            "linkedin": "URL",
            "github": "URL",
            "portfolio": "URL"
        }
    }
    
    Handle missing information gracefully - use null or empty arrays.
    Infer job titles and skill categories where appropriate.
    """,
    markdown=True,
)


# Validator Agent - Cleans and validates data
validator_agent = Agent(
    name="Data Validator Agent",
    role="Validate and clean parsed resume data",
    model=GEMINI_MODEL,
    instructions="""
    You are a data quality specialist. Your job is to validate and clean
    parsed resume data.
    
    Validation steps:
    1. Ensure required fields exist (name, at least some skills or experience)
    2. Normalize email formats
    3. Clean and format phone numbers
    4. Remove duplicates from skills list
    5. Standardize date formats
    6. Flag any suspicious or incomplete data
    
    Quality scoring:
    - Calculate a quality score (0.0 to 1.0)
    - List any warnings or issues found
    - Suggest improvements if data is sparse
    
    Return the cleaned data with quality metrics.
    """,
    markdown=True,
)


# Parsing Team - Coordinates parsing agents
parsing_team = Team(
    name="Parsing Team",
    description="Handle resume parsing from file upload to structured data",
    members=[ocr_agent, parser_agent, validator_agent],
    model=GEMINI_MODEL,
    instructions="""
    You coordinate the parsing of uploaded resumes.
    
    Workflow:
    1. First, delegate to OCR Agent to extract text from the file
    2. Then, delegate to Resume Parser to structure the data
    3. Finally, delegate to Data Validator to clean and validate
    
    Return the final structured resume data with quality metrics.
    """,
    markdown=True,
)
