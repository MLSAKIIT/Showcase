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
    Uses the new Agno Teams architecture.
    """
    is_valid, error = validate_input(parsed_data)
    if not is_valid:
        logger.warning("Input validation failed: %s", error)
        raise ValidationError(error)

    try:
        logger.info("Starting portfolio generation with Agno Teams")
        
        from agents.teams.portfolio_team import portfolio_team
        import json
        
        # Format data for the team
        prompt = f"Generate a portfolio from this resume data:\n\n{json.dumps(parsed_data, indent=2)}"
        
        if config:
            prompt += f"\n\nUser preferences:\n{json.dumps(config, indent=2)}"
        
        # Run the team
        response = await portfolio_team.arun(prompt)
        
        logger.info("Portfolio generation completed successfully")
        
        # Return the response as a dict
        return {
            "success": True,
            "response": str(response),
            "parsed_data": parsed_data,
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
        
        from agents.teams.portfolio_team import portfolio_team
        import json
        
        prompt = f"""
Regenerate the '{section}' section of this portfolio:

Current portfolio:
{json.dumps(current_portfolio, indent=2)}

Preferences:
{json.dumps(preferences or {}, indent=2)}
"""
        
        response = await portfolio_team.arun(prompt)
        
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
