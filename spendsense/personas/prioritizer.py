"""
Persona prioritization logic for selecting highest-priority match.

This module implements deterministic prioritization when multiple personas
match a user's behavioral signals, selecting the persona with the highest
priority (lowest priority number).
"""

from datetime import datetime
from typing import List, Optional
import logging

from pydantic import BaseModel, Field

from spendsense.personas.matcher import PersonaMatch
from spendsense.personas.registry import load_persona_registry

logger = logging.getLogger(__name__)


class PersonaAssignment(BaseModel):
    """
    Final persona assignment with audit trail.

    Attributes:
        assigned_persona_id: ID of assigned persona, or "unclassified" if no matches
        priority: Priority number of assigned persona (None if unclassified)
        all_qualifying_personas: List of all persona IDs that matched
        prioritization_reason: Human-readable explanation of selection
        assigned_at: Timestamp when assignment was made
    """
    assigned_persona_id: str = Field(description="Assigned persona ID or 'unclassified'")
    priority: Optional[int] = Field(default=None, description="Priority number (1=highest)")
    all_qualifying_personas: List[str] = Field(
        default_factory=list,
        description="All persona IDs that matched"
    )
    prioritization_reason: str = Field(description="Why this persona was selected")
    assigned_at: datetime = Field(default_factory=datetime.now, description="Assignment timestamp")


class PersonaPrioritizer:
    """
    Prioritizes persona matches to select highest-priority assignment.

    When multiple personas match a user's behavioral signals, this class
    applies deterministic prioritization rules to select the single most
    appropriate persona based on priority rankings.

    Usage:
        from spendsense.personas.matcher import PersonaMatcher

        # Get matches from matcher
        matcher = PersonaMatcher("data/processed/spendsense.db")
        matches = matcher.match_personas(behavioral_summary, date(2025, 11, 5), "30d")

        # Prioritize
        prioritizer = PersonaPrioritizer()
        assignment = prioritizer.prioritize_persona(matches)

        print(f"Assigned: {assignment.assigned_persona_id}")
        print(f"Reason: {assignment.prioritization_reason}")
        print(f"All qualifying: {assignment.all_qualifying_personas}")
    """

    def __init__(self):
        """Initialize persona prioritizer with persona registry."""
        self.registry = load_persona_registry()

    def prioritize_persona(self, matches: List[PersonaMatch]) -> PersonaAssignment:
        """
        Select highest-priority persona from list of matches.

        Args:
            matches: List of PersonaMatch objects from matcher

        Returns:
            PersonaAssignment with selected persona and audit trail

        Algorithm:
            1. Filter to only matched personas
            2. If zero matches → return "unclassified"
            3. Look up priority for each match
            4. Sort by priority (ascending: 1, 2, 3...)
            5. Select first (lowest number = highest priority)
            6. Build assignment with reasoning
        """
        # Filter to only matched personas
        qualifying_matches = [m for m in matches if m.matched]
        qualifying_persona_ids = [m.persona_id for m in qualifying_matches]

        logger.info(
            f"Prioritizing from {len(qualifying_matches)} qualifying personas: "
            f"{', '.join(qualifying_persona_ids) if qualifying_persona_ids else 'none'}"
        )

        # Handle zero matches
        if not qualifying_matches:
            logger.warning("No qualifying personas found - assigning 'unclassified' status")
            return PersonaAssignment(
                assigned_persona_id="unclassified",
                priority=None,
                all_qualifying_personas=[],
                prioritization_reason="No qualifying personas found"
            )

        # Look up priorities and sort
        persona_priorities = []
        for match in qualifying_matches:
            persona = self.registry.get_persona_by_id(match.persona_id)
            if persona is None:
                logger.error(f"Persona {match.persona_id} not found in registry")
                continue
            persona_priorities.append((match.persona_id, persona.priority))

        # Sort by priority (ascending: 1=highest, 2=second-highest, etc.)
        persona_priorities.sort(key=lambda x: x[1])

        # Check for ties (shouldn't happen - unique priorities enforced in registry)
        if len(persona_priorities) > 1 and persona_priorities[0][1] == persona_priorities[1][1]:
            logger.warning(
                f"Priority tie detected between {persona_priorities[0][0]} and {persona_priorities[1][0]} "
                f"(both priority {persona_priorities[0][1]}). This should not happen!"
            )

        # Select highest priority (first in sorted list)
        assigned_persona_id, assigned_priority = persona_priorities[0]

        # Build prioritization reason
        if len(qualifying_matches) == 1:
            reason = f"Only qualifying persona (priority {assigned_priority})"
        else:
            reason = (
                f"Highest priority match among {len(qualifying_matches)} qualifying personas "
                f"(priority {assigned_priority})"
            )

        logger.info(
            f"Selected persona: {assigned_persona_id} (priority {assigned_priority}). "
            f"Reason: {reason}"
        )

        # Return assignment
        return PersonaAssignment(
            assigned_persona_id=assigned_persona_id,
            priority=assigned_priority,
            all_qualifying_personas=qualifying_persona_ids,
            prioritization_reason=reason
        )
