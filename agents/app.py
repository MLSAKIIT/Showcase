"""
Showcase AI Agent Application - Agno Teams Entry Point.

This module provides the main entry point for the AI portfolio generation system
using Agno Teams architecture.

Usage:
    # As a module
    from agents.app import portfolio_team, run_portfolio_generation
    
    # Run directly
    python -m agents.app
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add agents directory to path
agents_dir = Path(__file__).resolve().parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))

# Import the portfolio team
from agents.teams.portfolio_team import portfolio_team


async def run_portfolio_generation(
    input_data: str,
    preferences: dict = None,
) -> dict:
    """
    Run the complete portfolio generation pipeline.
    
    Args:
        input_data: Raw resume text or file path
        preferences: Optional user preferences dict
        
    Returns:
        Dictionary with generation results
    """
    # Build the prompt
    prompt = f"Create a portfolio from this resume:\n\n{input_data}"
    
    if preferences:
        pref_text = "\n".join(f"- {k}: {v}" for k, v in preferences.items())
        prompt += f"\n\nUser preferences:\n{pref_text}"
    
    # Run the team
    response = await portfolio_team.arun(prompt)
    
    return {
        "success": True,
        "response": response,
    }


async def customize_portfolio(
    template_id: str,
    customizations: dict,
) -> dict:
    """
    Customize an existing template.
    
    Args:
        template_id: Template to customize
        customizations: Dict of customization requests
        
    Returns:
        Dictionary with customization results
    """
    prompt = f"""
    Customize the template '{template_id}' with these changes:
    
    {json.dumps(customizations, indent=2)}
    
    Apply all requested customizations to the template.
    """
    
    response = await portfolio_team.arun(prompt)
    
    return {
        "success": True,
        "template_id": template_id,
        "response": response,
    }


async def main():
    """Example usage of the portfolio team."""
    
    print("=" * 60)
    print("🚀 Showcase AI - Portfolio Generation System")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("   Please set it in your .env file")
        return
    
    # Sample resume data
    sample_resume = """
    JOHN DOE
    Full Stack Developer
    john.doe@email.com | github.com/johndoe | San Francisco, CA
    
    SUMMARY
    Passionate full-stack developer with 5+ years of experience building 
    scalable web applications. Expertise in React, Node.js, and cloud technologies.
    
    SKILLS
    - Frontend: React, TypeScript, Next.js, Tailwind CSS
    - Backend: Node.js, Python, PostgreSQL, Redis
    - DevOps: Docker, AWS, CI/CD, Kubernetes
    - Tools: Git, Figma, VS Code
    
    EXPERIENCE
    Senior Software Engineer | TechCorp Inc. | 2021-Present
    - Led development of customer-facing dashboard serving 100K+ users
    - Reduced page load time by 40% through performance optimization
    - Mentored team of 4 junior developers
    
    Software Engineer | StartupXYZ | 2019-2021
    - Built real-time chat system using WebSockets
    - Implemented CI/CD pipeline reducing deployment time by 60%
    
    PROJECTS
    E-Commerce Platform
    - Full-stack marketplace with React, Node.js, Stripe integration
    - Features: real-time inventory, admin dashboard, analytics
    
    Open Source Contributions
    - Contributor to React Query and Next.js
    - Built popular npm package with 5K+ downloads/week
    
    EDUCATION
    B.S. Computer Science | Stanford University | 2019
    """
    
    print("\n📄 Sample Resume Loaded")
    print("-" * 60)
    
    # Define preferences
    preferences = {
        "color_theme": "dark blue with teal accents",
        "features": ["dark mode toggle", "smooth animations"],
        "style": "modern and minimalist",
    }
    
    print("\n🎨 Preferences:")
    for key, value in preferences.items():
        print(f"   • {key}: {value}")
    
    print("\n" + "-" * 60)
    print("🤖 Starting Portfolio Generation...")
    print("-" * 60)
    
    try:
        # Run the generation
        result = await run_portfolio_generation(
            input_data=sample_resume,
            preferences=preferences,
        )
        
        print("\n✅ Generation Complete!")
        print("-" * 60)
        print("\n📋 Response:")
        print(result.get("response", "No response"))
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
