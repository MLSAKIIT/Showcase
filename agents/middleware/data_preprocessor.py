"""
DATA_PREPROCESSOR.PY
====================

Middleware for input normalization.

Role in pipeline:
Raw resume data
    ↓
[ DataPreprocessor ]
    ↓
Clean, predictable dict → SchemaBuilderAgent
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger("agents.middleware.data_preprocessor")


class PreprocessingError(Exception):
    """Base preprocessing error."""
    pass


class InputValidationError(PreprocessingError):
    """Raised when input resume data is invalid."""
    pass


class DataPreprocessor:
    """
    Minimal, deterministic resume preprocessor.

    Responsibilities:
    - Enforce minimum viable input
    - Normalize text
    - Normalize & deduplicate skills
    - Normalize projects
    - Produce schema-safe output
    """

    SKILL_MAP = {
        "js": "JavaScript",
        "javascript": "JavaScript",
        "ts": "TypeScript",
        "py": "Python",
        "python3": "Python",
        "reactjs": "React",
        "nodejs": "Node.js",
        "django": "Django",
        "flask": "Flask",
        "fastapi": "FastAPI",
        "aws": "AWS",
        "docker": "Docker",
        "k8s": "Kubernetes",
        "git": "Git",
    }

    async def preprocess(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw resume data.

        Output is guaranteed to be:
        - dict
        - stable keys
        - safe for SchemaBuilderAgent
        """

        if not isinstance(raw, dict):
            raise InputValidationError("Resume input must be a dictionary")

        if not raw.get("name") and not raw.get("email"):
            raise InputValidationError("Missing identifier: name or email required")

        if not any(raw.get(k) for k in ("skills", "projects", "experience", "summary")):
            raise InputValidationError("Resume has no usable content")

        clean = {
            "name": self._clean_text(raw.get("name", "Portfolio")),
            "email": self._clean_email(raw.get("email")),
            "summary": self._clean_text(raw.get("summary", "")),
            "skills": self._process_skills(raw.get("skills", [])),
            "projects": self._process_projects(raw.get("projects", [])),
            "experience": raw.get("experience", []),
            "education": raw.get("education", []),
            "links": raw.get("links", {}),
        }

        logger.info(
            "Preprocessing done | skills=%d | projects=%d",
            len(clean["skills"]),
            len(clean["projects"]),
        )

        return clean

    # ---------------- helpers ---------------- #

    def _clean_text(self, text: Any) -> str:
        if not isinstance(text, str):
            return ""
        return " ".join(text.split()).strip()

    def _clean_email(self, email: Any) -> str | None:
        if not isinstance(email, str):
            return None
        email = email.strip().lower()
        return email if "@" in email else None

    def _process_skills(self, skills: Any) -> List[str]:
        if not isinstance(skills, list):
            return []

        seen = set()
        normalized: List[str] = []

        for skill in skills:
            s = str(skill).strip()
            if len(s) < 2:
                continue

            mapped = self.SKILL_MAP.get(s.lower(), s.title())
            key = mapped.lower()

            if key not in seen:
                seen.add(key)
                normalized.append(mapped)

        return normalized

    def _process_projects(self, projects: Any) -> List[Dict[str, Any]]:
        if not isinstance(projects, list):
            return []

        cleaned = []

        for idx, project in enumerate(projects, 1):
            if isinstance(project, str):
                desc = self._clean_text(project)
                if len(desc) < 10:
                    continue

                cleaned.append({
                    "title": f"Project {idx}",
                    "description": desc,
                    "technologies": [],
                })

            elif isinstance(project, dict):
                desc = self._clean_text(project.get("description", ""))
                if len(desc) < 10:
                    continue

                cleaned.append({
                    "title": self._clean_text(project.get("title", f"Project {idx}")),
                    "description": desc,
                    "technologies": self._process_skills(
                        project.get("technologies")
                        or project.get("tech_stack", [])
                    ),
                })

        return cleaned
