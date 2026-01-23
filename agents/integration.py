"""
Integration layer between backend services and the Agno Teams agent system.

This module provides:
- Input validation
- Async + sync APIs for portfolio generation
- Bridge to the new Teams architecture
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional, Tuple
from app.schemas.portfolio import PortfolioOutput

# Logging
logger = logging.getLogger("agents.integration")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# Domain Exceptions

class PortfolioError(Exception):
    """Base exception for portfolio-related failures."""


class ValidationError(PortfolioError):
    """Raised when input validation fails."""


class GenerationError(PortfolioError):
    """Raised when portfolio generation fails."""


class ConfigurationError(PortfolioError):
    """Raised when configuration is invalid."""


# Validation

def validate_input(parsed_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Lightweight validation before running the pipeline.
    """
    if not isinstance(parsed_data, dict):
        return False, "parsed_data must be a dictionary"

    if not parsed_data.get("name") and not parsed_data.get("email"):
        return False, "At least one of 'name' or 'email' is required"

    has_core_content = any(
        parsed_data.get(key)
        for key in ("skills", "projects", "experience")
    )

    if not has_core_content:
        return False, (
            "At least one of 'skills', 'projects', or 'experience' must be provided"
        )

    return True, None


# Core Async APIs using Agno Teams

async def generate_portfolio(
    parsed_data: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate a complete portfolio configuration from parsed resume data.
    
    OPTIMIZATION:
    Uses a sequential pipeline (Data Injection) to minimize token usage.
    1. Portfolio Creator (Structured Pydantic Output)
    2. Template Selector (Lightweight text output)
    """
    is_valid, error = validate_input(parsed_data)
    if not is_valid:
        logger.warning("Input validation failed: %s", error)
        raise ValidationError(error)

    try:
        logger.info("Starting optimized portfolio generation pipeline")
        
        from agents.teams.generation_team import portfolio_creator, template_selector
        import json
        
        # 1. Generate Structured Content (Data Injection)
        # We send the raw data and get back a clean, validated Pydantic object
        logger.info("Running Step 1: Content Generation & Structuring")
        content_response = await portfolio_creator.arun(
            f"Resume Data:\n{json.dumps(parsed_data, indent=2)}\n\nUser Config:\n{json.dumps(config or {}, indent=2)}",
            response_model=PortfolioOutput
        )
        
        # The content_response.content is already a PortfolioOutput Pydantic object!
        # Access it directly.
        structured_content = content_response.content
        
        # 2. Select Template (Lightweight)
        # We only send relevant snippets to save tokens
        logger.info("Running Step 2: Template Selection")
        role_hint = parsed_data.get("job_title", "Developer")
        skills_hint = parsed_data.get("skills", [])[:5] # Top 5 skills only
        
        template_response = await template_selector.arun(
            f"Role: {role_hint}\nTop Skills: {skills_hint}\nUser Config: {config or {}}"
        )
        
        # Clean up template ID (remove markdown code blocks if any)
        selected_template_id = template_response.content.strip().replace("`", "")
        
        # 3. Apply Code Customizations (Optional - "Developer Mode")
        # If the user requested specific design/code changes, we spin up a Developer Agent
        if config and config.get("customization_prompt"):
            logger.info("Running Step 3: Code Customization (Developer Mode)")
            
            from agno.agent import Agent
            from agents.tools.code_tools import CodeModificationTools
            from agents.tools.file_tools import FileSystemTools
            
            # Initialize tools pointing to the template directory
            # In a real scenario, we'd copy the template to a build dir first
            # But for now, we assume we are editing a copy or the source if allowed
            
            developer_agent = Agent(
                name="Developer Agent",
                role="Frontend Developer",
                model=get_model(),
                tools=[CodeModificationTools(), FileSystemTools()],
                instructions=f"""
                You are an expert Frontend Developer.
                Your task is to modify the code of the selected template ('{selected_template_id}') 
                based on the user's request.
                
                User Request: "{config.get('customization_prompt')}"
                
                Guidelines:
                - Use `find_and_replace` or `update_css_variable` for safe edits.
                - Do NOT break the build.
                - Only modify style/content as requested.
                """,
            )
            
            # Execute the customization
            await developer_agent.arun(f"Apply these changes to {selected_template_id}")
            
            final_portfolio["customizations_applied"] = True

        logger.info(f"Pipeline completed. Template: {selected_template_id}")
        
        # 4. Assemble Final Result
        # Convert Pydantic model to dict
        final_portfolio = structured_content.model_dump()
        final_portfolio["template_id"] = selected_template_id
        
        # Return standard response format
        return {
            "success": True,
            "response": json.dumps(final_portfolio), # For legacy compatibility
            "parsed_data": parsed_data,
            "portfolio_data": final_portfolio # The clean data
        }

    except ValidationError:
        raise
    except Exception as exc:
        logger.exception("Portfolio generation failed")
        raise GenerationError(str(exc)) from exc


async def regenerate_section(
    current_portfolio: Dict[str, Any],
    section: str,
    preferences: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Regenerate a specific section of an existing portfolio.
    """
    if not isinstance(current_portfolio, dict):
        raise ValidationError("current_portfolio must be a dictionary")

    if not section:
        raise ValidationError("section must be provided")

    try:
        logger.info("Regenerating section: %s", section)
        
        # Import intentionally removed: using updater_agent below

        
        prompt = f"""
Regenerate the '{section}' section of this portfolio:

Current portfolio:
{json.dumps(current_portfolio, indent=2)}

Preferences:
{json.dumps(preferences or {}, indent=2)}
"""
        
        # Use a temporary generic agent for partial updates to avoid strict full-schema validation
        from agno.agent import Agent
        from agents.model import get_model
        
        updater_agent = Agent(
            model=get_model(),
            description="Update a specific section of JSON data",
            instructions="Return only the updated JSON section. No markdown, no explanations."
        )
        
        response = await updater_agent.arun(prompt)
        
        logger.info("Section '%s' regenerated successfully", section)
        return {
            "success": True,
            "section": section,
            "response": str(response),
        }

    except ValidationError:
        raise
    except Exception as exc:
        logger.exception("Section regeneration failed")
        raise GenerationError(str(exc)) from exc


async def export_portfolio(
    portfolio: Dict[str, Any],
    format: str = "json",
    config: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Export a portfolio to a supported format.
    """
    import json
    
    if not isinstance(portfolio, dict):
        raise ValidationError("portfolio must be a dictionary")

    if format not in {"json", "yaml", "html_preview"}:
        raise ValidationError(f"Unsupported export format: {format}")

    try:
        if format == "json":
            return json.dumps(portfolio, indent=2, ensure_ascii=False)
        
        elif format == "yaml":
            try:
                import yaml
                return yaml.dump(portfolio, allow_unicode=True, sort_keys=False)
            except ImportError:
                raise GenerationError("PyYAML not installed")
        
        elif format == "html_preview":
            # Simple HTML preview
            hero = portfolio.get("hero", {})
            return f"""<!DOCTYPE html>
<html>
<head><title>{hero.get('name', 'Portfolio')}</title></head>
<body>
<h1>{hero.get('name', 'Portfolio')}</h1>
<p>{hero.get('tagline', '')}</p>
</body>
</html>"""

    except Exception as exc:
        logger.exception("Portfolio export failed")
        raise GenerationError(str(exc)) from exc


# Sync Wrappers
def _run_async(coro):
    """Safe asyncio runner for sync contexts."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        return asyncio.run_coroutine_threadsafe(coro, loop).result()

    return asyncio.run(coro)


def generate_portfolio_sync(
    parsed_data: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return _run_async(generate_portfolio(parsed_data, config))


def regenerate_section_sync(
    current_portfolio: Dict[str, Any],
    section: str,
    preferences: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return _run_async(
        regenerate_section(current_portfolio, section, preferences, config)
    )


def export_portfolio_sync(
    portfolio: Dict[str, Any],
    format: str = "json",
    config: Optional[Dict[str, Any]] = None,
) -> str:
    return _run_async(export_portfolio(portfolio, format, config))
