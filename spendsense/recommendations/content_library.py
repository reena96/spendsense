"""
Content library loader and accessor for recommendations.

Loads recommendations from YAML configuration and provides
efficient lookup by persona and recommendation ID.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import ValidationError

from spendsense.recommendations.models import Recommendation

logger = logging.getLogger(__name__)


class ContentLibrary:
    """
    Content library loader and accessor for recommendations.

    Loads recommendations from YAML file and caches them in memory
    for fast lookup.

    Usage:
        library = ContentLibrary("spendsense/config/recommendations.yaml")
        recommendations = library.get_by_persona("low_savings")
        rec = library.get_by_id("emergency_fund_start")
    """

    def __init__(self, config_path: str):
        """
        Initialize content library from YAML file.

        Args:
            config_path: Path to recommendations YAML file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If YAML is invalid or recommendations are malformed
        """
        self.config_path = Path(config_path)
        self.recommendations: Dict[str, List[Recommendation]] = {}
        self._recommendation_index: Dict[str, Recommendation] = {}

        self._load_from_yaml()
        logger.info(
            f"Loaded {len(self._recommendation_index)} recommendations "
            f"for {len(self.recommendations)} personas"
        )

    def _load_from_yaml(self) -> None:
        """
        Load recommendations from YAML file.

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If YAML is invalid or recommendations are malformed
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Recommendations file not found: {self.config_path}")

        try:
            with open(self.config_path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {self.config_path}: {e}")

        if not data or "recommendations" not in data:
            raise ValueError("YAML must contain 'recommendations' root key")

        recommendations_data = data["recommendations"]
        if not isinstance(recommendations_data, dict):
            raise ValueError("'recommendations' must be a dictionary")

        # Load and validate each persona's recommendations
        for persona_id, recs in recommendations_data.items():
            if not isinstance(recs, list):
                raise ValueError(f"Recommendations for '{persona_id}' must be a list")

            persona_recommendations = []
            for rec_data in recs:
                try:
                    rec = Recommendation(**rec_data)
                    persona_recommendations.append(rec)

                    # Add to global index for ID lookup
                    if rec.id in self._recommendation_index:
                        existing = self._recommendation_index[rec.id]
                        logger.warning(
                            f"Duplicate recommendation ID '{rec.id}' found for personas "
                            f"(keeping first occurrence)"
                        )
                    else:
                        self._recommendation_index[rec.id] = rec

                except ValidationError as e:
                    logger.error(f"Invalid recommendation in '{persona_id}': {e}")
                    raise ValueError(
                        f"Invalid recommendation in '{persona_id}': {rec_data.get('id', 'unknown')}"
                    ) from e

            # Sort by priority (1=highest)
            persona_recommendations.sort(key=lambda r: r.priority)
            self.recommendations[persona_id] = persona_recommendations

        # Validate all expected personas are present
        self._validate_persona_coverage()

    def _validate_persona_coverage(self) -> None:
        """
        Validate that all expected personas have recommendations.

        Logs warnings for missing personas.
        """
        expected_personas = {
            "high_utilization",
            "irregular_income",
            "low_savings",
            "subscription_heavy",
            "cash_flow_optimizer",
            "young_professional",
        }

        missing_personas = expected_personas - set(self.recommendations.keys())
        if missing_personas:
            logger.warning(f"Missing recommendations for personas: {missing_personas}")

        extra_personas = set(self.recommendations.keys()) - expected_personas
        if extra_personas:
            logger.info(f"Found additional personas: {extra_personas}")

    def get_by_persona(self, persona_id: str) -> List[Recommendation]:
        """
        Get all recommendations for a persona, sorted by priority.

        Args:
            persona_id: Persona identifier (e.g., "low_savings")

        Returns:
            List of recommendations sorted by priority (1=highest)
            Empty list if persona not found

        Example:
            >>> library = ContentLibrary("config/recommendations.yaml")
            >>> recs = library.get_by_persona("low_savings")
            >>> print(recs[0].title)
            "Build Your Emergency Fund"
        """
        if persona_id not in self.recommendations:
            logger.warning(f"No recommendations found for persona: {persona_id}")
            return []

        return self.recommendations[persona_id]

    def get_by_id(self, recommendation_id: str) -> Optional[Recommendation]:
        """
        Get a specific recommendation by ID.

        Args:
            recommendation_id: Unique recommendation identifier

        Returns:
            Recommendation if found, None otherwise

        Example:
            >>> library = ContentLibrary("config/recommendations.yaml")
            >>> rec = library.get_by_id("emergency_fund_start")
            >>> print(rec.title)
            "Build Your Emergency Fund"
        """
        rec = self._recommendation_index.get(recommendation_id)
        if not rec:
            logger.debug(f"Recommendation not found: {recommendation_id}")
        return rec

    def get_all_personas(self) -> List[str]:
        """
        Get list of all personas with recommendations.

        Returns:
            List of persona IDs

        Example:
            >>> library = ContentLibrary("config/recommendations.yaml")
            >>> personas = library.get_all_personas()
            >>> print(personas)
            ["high_utilization", "low_savings", ...]
        """
        return list(self.recommendations.keys())

    def get_recommendation_count(self, persona_id: Optional[str] = None) -> int:
        """
        Get count of recommendations.

        Args:
            persona_id: Optional persona ID to count for specific persona

        Returns:
            Total count (if persona_id is None) or count for specific persona

        Example:
            >>> library = ContentLibrary("config/recommendations.yaml")
            >>> total = library.get_recommendation_count()
            >>> low_savings_count = library.get_recommendation_count("low_savings")
        """
        if persona_id is None:
            return len(self._recommendation_index)

        if persona_id not in self.recommendations:
            return 0

        return len(self.recommendations[persona_id])

    def get_by_category(self, persona_id: str, category: str) -> List[Recommendation]:
        """
        Get recommendations for a persona filtered by category.

        Args:
            persona_id: Persona identifier
            category: Recommendation category (education, action, tip, insight)

        Returns:
            List of recommendations matching category, sorted by priority

        Example:
            >>> library = ContentLibrary("config/recommendations.yaml")
            >>> actions = library.get_by_category("low_savings", "action")
            >>> print([r.title for r in actions])
        """
        all_recs = self.get_by_persona(persona_id)
        return [r for r in all_recs if r.category.value == category]

    def get_high_priority(self, persona_id: str, limit: int = 5) -> List[Recommendation]:
        """
        Get top priority recommendations for a persona.

        Args:
            persona_id: Persona identifier
            limit: Maximum number of recommendations to return

        Returns:
            Top N recommendations sorted by priority

        Example:
            >>> library = ContentLibrary("config/recommendations.yaml")
            >>> top_3 = library.get_high_priority("low_savings", limit=3)
        """
        all_recs = self.get_by_persona(persona_id)
        return all_recs[:limit]

    def get_quick_wins(self, persona_id: str) -> List[Recommendation]:
        """
        Get quick win recommendations for a persona.

        Quick wins are one-time actions or beginner-level recommendations.

        Args:
            persona_id: Persona identifier

        Returns:
            List of quick win recommendations

        Example:
            >>> library = ContentLibrary("config/recommendations.yaml")
            >>> quick_wins = library.get_quick_wins("young_professional")
        """
        all_recs = self.get_by_persona(persona_id)
        return [r for r in all_recs if r.is_quick_win]

    def __repr__(self) -> str:
        """String representation for debugging."""
        persona_counts = {p: len(recs) for p, recs in self.recommendations.items()}
        return f"ContentLibrary({len(self._recommendation_index)} total, personas={persona_counts})"


# Singleton instance for easy access
_library_instance: Optional[ContentLibrary] = None


def get_content_library(config_path: Optional[str] = None) -> ContentLibrary:
    """
    Get singleton ContentLibrary instance.

    Args:
        config_path: Optional path to recommendations YAML file
                    If None, uses default path

    Returns:
        ContentLibrary instance

    Example:
        >>> from spendsense.recommendations import get_content_library
        >>> library = get_content_library()
        >>> recs = library.get_by_persona("low_savings")
    """
    global _library_instance

    if _library_instance is None:
        if config_path is None:
            # Default path
            config_path = str(
                Path(__file__).parent.parent / "config" / "recommendations.yaml"
            )
        _library_instance = ContentLibrary(config_path)

    return _library_instance
