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
        Load recommendations from YAML file (PRD flat structure).

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

        # PRD structure: flat list under 'educational_content'
        if not data or "educational_content" not in data:
            raise ValueError("YAML must contain 'educational_content' root key")

        recommendations_data = data["educational_content"]
        if not isinstance(recommendations_data, list):
            raise ValueError("'educational_content' must be a list")

        # Load all recommendations from flat list
        for rec_data in recommendations_data:
            try:
                rec = Recommendation(**rec_data)

                # Add to global index for ID lookup
                if rec.id in self._recommendation_index:
                    logger.warning(
                        f"Duplicate recommendation ID '{rec.id}' found (keeping first occurrence)"
                    )
                else:
                    self._recommendation_index[rec.id] = rec

                # Add to each persona it applies to (PRD AC3: multi-persona support)
                for persona_id in rec.personas:
                    if persona_id not in self.recommendations:
                        self.recommendations[persona_id] = []
                    self.recommendations[persona_id].append(rec)

            except ValidationError as e:
                logger.error(f"Invalid recommendation: {e}")
                raise ValueError(
                    f"Invalid recommendation: {rec_data.get('id', 'unknown')}"
                ) from e

        # Sort each persona's recommendations by priority (1=highest)
        for persona_id in self.recommendations:
            self.recommendations[persona_id].sort(key=lambda r: r.priority)

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

    def get_by_signal(self, signal_type: str) -> List[Recommendation]:
        """
        Get all recommendations triggered by a specific signal (PRD AC4).

        Args:
            signal_type: Signal type (e.g., "credit_utilization", "savings_balance")

        Returns:
            List of recommendations that trigger on this signal, sorted by priority

        Example:
            >>> library = ContentLibrary("config/recommendations.yaml")
            >>> recs = library.get_by_signal("credit_utilization")
            >>> print([r.title for r in recs[:3]])
        """
        matching_recs = [
            rec for rec in self._recommendation_index.values()
            if signal_type in rec.triggering_signals
        ]
        matching_recs.sort(key=lambda r: r.priority)
        return matching_recs

    def get_by_type(self, content_type: str) -> List[Recommendation]:
        """
        Get all recommendations of a specific content type (PRD AC2).

        Args:
            content_type: Type of content (article/template/calculator/video)

        Returns:
            List of recommendations of this type, sorted by priority

        Example:
            >>> library = ContentLibrary("config/recommendations.yaml")
            >>> calculators = library.get_by_type("calculator")
            >>> print([r.title for r in calculators])
        """
        matching_recs = [
            rec for rec in self._recommendation_index.values()
            if rec.type.value == content_type
        ]
        matching_recs.sort(key=lambda r: r.priority)
        return matching_recs

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
