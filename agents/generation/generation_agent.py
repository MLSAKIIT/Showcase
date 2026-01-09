"""
CONTENT_GENERATOR.PY - AI Content Generation Agent (Gemini Integration)
========================================================================

PURPOSE:
This is the creative brain of the pipeline. It uses Google's Gemini LLM to generate
compelling portfolio content from the structured schema.

DATA FLOW IN:
- Portfolio schema (from schema_builder)
- User data (original preprocessed data for context)

DATA FLOW OUT:
- Complete portfolio with AI-generated content:
  * Hero tagline
  * Professional bio
  * Enhanced project descriptions
  * Section content

HOW IT WORKS:
- Uses constrained generation (not plain prompts!)
- Sends schema + strict formatting rules to Gemini
- Generates React components, Tailwind styles, config files
- Maintains consistency across all generated content
- Uses temperature control for creativity vs. accuracy balance

NOTE: THIS CODE IS AI GENERATED, YOUR WORK IS TO ANALYSIS THE CODE AND CHECK THE LOGIC AND MAKE CHANGES
     WHERE REQUIRED
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List

import google.generativeai as genai
from pydantic import ValidationError

from agents.schemas.portfolio import PortfolioOutput


class GenerationAgent:
    """
    Transforms SchemaBuilderAgent output into final portfolio content.

    Input:
      - schema: structured semantic schema from SchemaBuilderAgent
      - profile: original normalized profile data

    Output:
      - PortfolioOutput (validated, render-ready)
    """

    def __init__(self, model: str = "gemini-1.5-pro"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    async def run(
        self,
        schema: Dict[str, Any],
        profile: Dict[str, Any],
    ) -> PortfolioOutput:
        prompt = self._build_prompt(schema, profile)

        response = await asyncio.to_thread(
            self.model.generate_content,
            prompt
        )

        if not response or not response.text:
            raise RuntimeError("Gemini returned empty response")

        raw = self._extract_json(response.text)

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON from Gemini:\n{raw}") from e

        try:
            return PortfolioOutput(
                **parsed,
                generated_at=datetime.utcnow().isoformat()
            )
        except ValidationError as e:
            raise RuntimeError(
                f"Generated content failed PortfolioOutput validation:\n{e}"
            ) from e

    # ------------------------------------------------------------------
    # PROMPT ENGINE (SCHEMA-AWARE)
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        schema: Dict[str, Any],
        profile: Dict[str, Any],
    ) -> str:
        return f"""
You are an AI portfolio content generator.

You will be given:
1. A STRUCTURED SCHEMA produced by another system
2. A USER PROFILE with factual data

Your job:
Convert the schema into FINAL, polished portfolio content.

STRICT RULES:
- Output ONLY valid JSON
- No markdown, no explanations, no comments
- Do NOT change schema intent
- Do NOT invent experience, metrics, or facts
- Use schema as authoritative guidance

TARGET OUTPUT FORMAT:
{{
  "hero": {{
    "name": string,
    "tagline": string (max 100 chars),
    "bio_short": string,
    "avatar_url": null
  }},
  "bio_long": string (min 150 words),
  "projects": [
    {{
      "title": string,
      "description": string (min 50 chars),
      "tech_stack": [string],
      "featured": boolean,
      "link": null
    }}
  ],
  "skills": [
    {{
      "category": string,
      "items": [string]
    }}
  ],
  "theme": {{
    "primary_color": "#RRGGBB",
    "style": "modern_tech" | "minimalist" | "creative"
  }},
  "quality_score": number between 0 and 1
}}

SCHEMA (instructional, DO NOT MODIFY STRUCTURE):
{json.dumps(schema, indent=2)}

USER PROFILE (facts only):
{json.dumps(profile, indent=2)}

CONTENT GUIDELINES:
- Professional, confident, human
- Action-oriented language
- No clichés ("passionate", "innovative", etc.)
- Expand reference_points into natural prose
- Respect layout_hints.density for verbosity
- Highlight higher priority projects more strongly

Generate the JSON now.
"""

    # ------------------------------------------------------------------
    # UTILITIES
    # ------------------------------------------------------------------

    def _extract_json(self, text: str) -> str:
        text = text.strip()

        if text.startswith("{") and text.endswith("}"):
            return text

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            raise RuntimeError("No JSON object found in Gemini response")

        return text[start:end + 1]

    def __repr__(self) -> str:
        return f"GenerationAgent(model={self.model.model_name})"
