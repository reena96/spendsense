"""
Persona registry loader and models.

Loads persona definitions from YAML configuration and provides
type-safe access to persona criteria and metadata.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from pydantic import BaseModel, Field, field_validator


class ConditionOperator(str, Enum):
    """Comparison operators for persona criteria conditions."""
    GTE = ">="
    LTE = "<="
    GT = ">"
    LT = "<"
    EQ = "=="


class LogicalOperator(str, Enum):
    """Logical operators for combining conditions."""
    AND = "AND"
    OR = "OR"


class PersonaCondition(BaseModel):
    """A single matching condition for a persona."""
    signal: str = Field(description="Signal field name from BehavioralSignal")
    operator: ConditionOperator = Field(description="Comparison operator")
    value: float = Field(description="Threshold value to compare against")
    time_window: Optional[str] = Field(
        default=None,
        description="Optional time window constraint (e.g., '30_day')"
    )

    @field_validator('signal')
    @classmethod
    def validate_signal_name(cls, v: str) -> str:
        """Validate signal name is not empty."""
        if not v or not v.strip():
            raise ValueError("Signal name cannot be empty")
        return v.strip()


class PersonaCriteria(BaseModel):
    """Matching criteria for a persona."""
    operator: LogicalOperator = Field(description="How to combine conditions (AND/OR)")
    conditions: List[PersonaCondition] = Field(description="List of matching conditions")

    @field_validator('conditions')
    @classmethod
    def validate_conditions_not_empty(cls, v: List[PersonaCondition]) -> List[PersonaCondition]:
        """Ensure at least one condition is defined."""
        if not v:
            raise ValueError("Persona must have at least one condition")
        return v


class PersonaContentTypes(BaseModel):
    """Content type recommendations for a persona."""
    education: List[str] = Field(description="Educational content topics")
    partner_offers: List[str] = Field(default_factory=list, description="Partner offer categories")


class Persona(BaseModel):
    """
    A user persona definition with matching criteria and content recommendations.

    Attributes:
        id: Unique persona identifier (snake_case)
        name: Display name
        description: Plain-language description
        priority: Prioritization rank (1 = highest priority)
        criteria: Matching criteria using behavioral signals
        focus_areas: Educational focus topics
        content_types: Recommended content categories
    """
    id: str = Field(description="Unique persona identifier")
    name: str = Field(description="Display name")
    description: str = Field(description="Plain-language description")
    priority: int = Field(ge=1, description="Prioritization rank (1 = highest)")
    criteria: PersonaCriteria = Field(description="Matching criteria")
    focus_areas: List[str] = Field(description="Educational focus topics")
    content_types: PersonaContentTypes = Field(description="Content recommendations")

    @field_validator('id')
    @classmethod
    def validate_id_snake_case(cls, v: str) -> str:
        """Validate persona ID is snake_case."""
        if not v or not v.strip():
            raise ValueError("Persona ID cannot be empty")
        if not v.islower() or ' ' in v:
            raise ValueError(f"Persona ID must be lowercase snake_case: {v}")
        return v.strip()

    @field_validator('focus_areas')
    @classmethod
    def validate_focus_areas_not_empty(cls, v: List[str]) -> List[str]:
        """Ensure at least one focus area is defined."""
        if not v:
            raise ValueError("Persona must have at least one focus area")
        return v


class PersonaRegistry(BaseModel):
    """
    Registry of all persona definitions.

    Provides type-safe access to personas and ensures all required
    personas are present with valid priority ordering.
    """
    personas: List[Persona] = Field(description="List of persona definitions")

    @field_validator('personas')
    @classmethod
    def validate_personas_not_empty(cls, v: List[Persona]) -> List[Persona]:
        """Ensure at least one persona is defined."""
        if not v:
            raise ValueError("Registry must contain at least one persona")
        return v

    @field_validator('personas')
    @classmethod
    def validate_unique_priorities(cls, v: List[Persona]) -> List[Persona]:
        """Ensure all personas have unique priorities."""
        priorities = [p.priority for p in v]
        if len(priorities) != len(set(priorities)):
            raise ValueError("All personas must have unique priority values")
        return v

    @field_validator('personas')
    @classmethod
    def validate_unique_ids(cls, v: List[Persona]) -> List[Persona]:
        """Ensure all personas have unique IDs."""
        ids = [p.id for p in v]
        if len(ids) != len(set(ids)):
            raise ValueError("All personas must have unique IDs")
        return v

    def get_persona_by_id(self, persona_id: str) -> Optional[Persona]:
        """Get persona by ID."""
        for persona in self.personas:
            if persona.id == persona_id:
                return persona
        return None

    def get_personas_by_priority(self) -> List[Persona]:
        """Get personas sorted by priority (1 = highest priority first)."""
        return sorted(self.personas, key=lambda p: p.priority)

    def get_persona_ids(self) -> List[str]:
        """Get list of all persona IDs."""
        return [p.id for p in self.personas]


# Singleton registry instance
_registry_cache: Optional[PersonaRegistry] = None


def load_persona_registry(config_path: Optional[Path] = None, force_reload: bool = False) -> PersonaRegistry:
    """
    Load persona registry from YAML configuration.

    Args:
        config_path: Path to personas.yaml file. If None, uses default location.
        force_reload: If True, reload even if cached

    Returns:
        PersonaRegistry with all persona definitions

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If YAML is malformed or validation fails
        yaml.YAMLError: If YAML parsing fails
    """
    global _registry_cache

    # Return cached registry if available
    if _registry_cache is not None and not force_reload:
        return _registry_cache

    # Determine config path
    if config_path is None:
        # Default: spendsense/config/personas.yaml
        module_dir = Path(__file__).parent.parent  # spendsense/
        config_path = module_dir / "config" / "personas.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Persona registry not found: {config_path}")

    # Load YAML
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)

    if not data or 'personas' not in data:
        raise ValueError(f"Invalid persona registry: missing 'personas' key in {config_path}")

    # Validate and create registry
    try:
        registry = PersonaRegistry(**data)
    except Exception as e:
        raise ValueError(f"Failed to validate persona registry: {e}")

    # Cache and return
    _registry_cache = registry
    return registry


def clear_registry_cache() -> None:
    """Clear the cached registry. Useful for testing."""
    global _registry_cache
    _registry_cache = None
