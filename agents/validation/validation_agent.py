import re
from typing import List

from agents.schemas.portfolio import PortfolioOutput


class ValidationError(Exception):
    pass


class PortfolioValidator:
    """
    Validates PortfolioOutput beyond Pydantic structural checks.

    Focus:
    - Content quality
    - Reasonable length / tone
    - Placeholder detection
    - Deterministic scoring

    Pydantic already guarantees:
    - Required fields
    - Min/max lengths
    - Types
    """

    PASS_SCORE = 0.70

    PLACEHOLDER_PATTERNS = [
        r"\[.*?\]",
        r"lorem ipsum",
        r"\b(todo|fixme|tbd)\b",
        r"sample text",
        r"example\.com",
        r"your (name|project|company)",
    ]

    def validate_and_enhance(
        self,
        portfolio: PortfolioOutput,
        original_data: dict | None = None,
    ) -> dict:
        """
        Validate generated portfolio and attach validation metadata.
        """

        hero_score = self._validate_hero(portfolio.hero)
        bio_score = self._validate_bio(portfolio.bio_long)
        project_score = self._validate_projects(portfolio.projects)

        overall = (
            hero_score * 0.25 +
            bio_score * 0.35 +
            project_score * 0.40
        )

        passed = overall >= self.PASS_SCORE

        result = portfolio.model_dump()

        result["quality_score"] = round(overall, 3)
        result["validation"] = {
            "hero_score": round(hero_score, 3),
            "bio_score": round(bio_score, 3),
            "projects_score": round(project_score, 3),
            "passed": passed,
        }

        if not passed:
            raise ValidationError(
                f"Portfolio quality below threshold ({overall:.2f})"
            )

        return result

    # SECTION VALIDATORS

    def _validate_hero(self, hero) -> float:
        score = 1.0

        wc = len(hero.tagline.split())
        if wc < 6 or wc > 18:
            score -= 0.3

        if self._has_placeholders(hero.tagline):
            score -= 0.4

        if hero.bio_short and len(hero.bio_short.split()) < 20:
            score -= 0.1

        return max(score, 0.0)

    def _validate_bio(self, bio: str) -> float:
        score = 1.0

        if self._has_placeholders(bio):
            score -= 0.4

        if not self._is_first_person(bio):
            score -= 0.2

        if self._is_repetitive(bio):
            score -= 0.1

        return max(score, 0.0)

    def _validate_projects(self, projects: List) -> float:
        if not projects:
            return 0.4

        scores = []

        for p in projects:
            s = 1.0

            if self._has_placeholders(p.description):
                s -= 0.4

            if not p.tech_stack:
                s -= 0.1

            scores.append(max(s, 0.0))

        return sum(scores) / len(scores)

    # HELPERS

    def _has_placeholders(self, text: str) -> bool:
        text = text.lower()
        return any(re.search(p, text) for p in self.PLACEHOLDER_PATTERNS)

    def _is_first_person(self, text: str) -> bool:
        t = text.lower()
        return any(p in t for p in [" i ", " my ", " i'm ", " i've "])

    def _is_repetitive(self, text: str) -> bool:
        sentences = [s.strip().lower() for s in text.split(".") if s.strip()]
        return len(sentences) != len(set(sentences))
