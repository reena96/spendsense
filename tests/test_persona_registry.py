"""
Unit tests for persona registry loader and models.
"""

import pytest
from pathlib import Path
from pydantic import ValidationError

from spendsense.personas.registry import (
    load_persona_registry,
    clear_registry_cache,
    Persona,
    PersonaCriteria,
    PersonaCondition,
    PersonaRegistry,
    ConditionOperator,
    LogicalOperator,
)


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear registry cache before each test."""
    clear_registry_cache()
    yield
    clear_registry_cache()


class TestPersonaRegistryLoading:
    """Test persona registry loading from YAML."""

    def test_load_persona_registry_success(self):
        """Test registry loads successfully from default location."""
        registry = load_persona_registry()

        assert registry is not None
        assert isinstance(registry, PersonaRegistry)
        assert len(registry.personas) > 0

    def test_load_persona_registry_caching(self):
        """Test registry is cached after first load."""
        registry1 = load_persona_registry()
        registry2 = load_persona_registry()

        # Should be the same instance (cached)
        assert registry1 is registry2

    def test_load_persona_registry_force_reload(self):
        """Test force_reload bypasses cache."""
        registry1 = load_persona_registry()
        registry2 = load_persona_registry(force_reload=True)

        # Should be different instances but equal content
        assert registry1 is not registry2
        assert registry1.model_dump() == registry2.model_dump()

    def test_load_persona_registry_file_not_found(self):
        """Test error handling when config file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_persona_registry(config_path=Path("/nonexistent/personas.yaml"))


class TestPersonaDefinitions:
    """Test all 6 persona definitions are present and valid."""

    def test_all_six_personas_present(self):
        """Test registry contains all 6 required personas."""
        registry = load_persona_registry()

        expected_personas = {
            'high_utilization',
            'irregular_income',
            'low_savings',
            'subscription_heavy',
            'cash_flow_optimizer',
            'young_professional'
        }

        actual_personas = set(registry.get_persona_ids())
        assert actual_personas == expected_personas

    def test_persona_priorities_correct(self):
        """Test personas have correct priority ordering."""
        registry = load_persona_registry()

        expected_order = [
            ('high_utilization', 1),
            ('irregular_income', 2),
            ('low_savings', 3),
            ('subscription_heavy', 4),
            ('cash_flow_optimizer', 5),
            ('young_professional', 6)
        ]

        for persona_id, expected_priority in expected_order:
            persona = registry.get_persona_by_id(persona_id)
            assert persona is not None
            assert persona.priority == expected_priority

    def test_persona_priorities_unique(self):
        """Test all personas have unique priorities."""
        registry = load_persona_registry()

        priorities = [p.priority for p in registry.personas]
        assert len(priorities) == len(set(priorities))

    def test_get_personas_by_priority_sorted(self):
        """Test personas can be retrieved sorted by priority."""
        registry = load_persona_registry()

        sorted_personas = registry.get_personas_by_priority()
        priorities = [p.priority for p in sorted_personas]

        # Should be sorted ascending (1, 2, 3, 4, 5, 6)
        assert priorities == sorted(priorities)


class TestPersonaCriteria:
    """Test persona criteria definitions."""

    def test_high_utilization_criteria(self):
        """Test high utilization persona has correct criteria."""
        registry = load_persona_registry()
        persona = registry.get_persona_by_id('high_utilization')

        assert persona is not None
        assert persona.criteria.operator == LogicalOperator.AND
        assert len(persona.criteria.conditions) >= 1

        # Should have credit utilization condition
        conditions = [c for c in persona.criteria.conditions if c.signal == 'credit_max_utilization_pct']
        assert len(conditions) == 1
        assert conditions[0].operator == ConditionOperator.GTE
        assert conditions[0].value == 50.0

    def test_irregular_income_criteria(self):
        """Test irregular income persona has correct criteria."""
        registry = load_persona_registry()
        persona = registry.get_persona_by_id('irregular_income')

        assert persona is not None
        assert persona.criteria.operator == LogicalOperator.OR

        # Should have income-related conditions
        signals = [c.signal for c in persona.criteria.conditions]
        assert 'income_median_pay_gap_days' in signals or 'income_payroll_count' in signals

    def test_low_savings_criteria(self):
        """Test low savings persona has correct criteria."""
        registry = load_persona_registry()
        persona = registry.get_persona_by_id('low_savings')

        assert persona is not None

        # Should have emergency fund condition
        conditions = [c for c in persona.criteria.conditions if c.signal == 'savings_emergency_fund_months']
        assert len(conditions) >= 1
        assert conditions[0].operator == ConditionOperator.LT
        assert conditions[0].value == 3.0

    def test_subscription_heavy_criteria(self):
        """Test subscription heavy persona has correct criteria."""
        registry = load_persona_registry()
        persona = registry.get_persona_by_id('subscription_heavy')

        assert persona is not None

        # Should have subscription share condition
        conditions = [c for c in persona.criteria.conditions if c.signal == 'subscription_share_pct']
        assert len(conditions) >= 1
        assert conditions[0].operator == ConditionOperator.GTE
        assert conditions[0].value == 0.20

    def test_cash_flow_optimizer_criteria(self):
        """Test cash flow optimizer persona has correct criteria."""
        registry = load_persona_registry()
        persona = registry.get_persona_by_id('cash_flow_optimizer')

        assert persona is not None
        assert persona.criteria.operator == LogicalOperator.AND

        # Should have both high savings AND low utilization
        signals = [c.signal for c in persona.criteria.conditions]
        assert 'savings_emergency_fund_months' in signals
        assert 'credit_max_utilization_pct' in signals

    def test_young_professional_criteria(self):
        """Test young professional persona has correct criteria."""
        registry = load_persona_registry()
        persona = registry.get_persona_by_id('young_professional')

        assert persona is not None
        assert persona.criteria.operator == LogicalOperator.OR

        # Should have transaction history or credit limit conditions
        signals = [c.signal for c in persona.criteria.conditions]
        assert 'transaction_history_days' in signals or 'credit_total_limits' in signals


class TestPersonaMetadata:
    """Test persona metadata (name, description, focus areas, content types)."""

    def test_all_personas_have_names(self):
        """Test all personas have non-empty display names."""
        registry = load_persona_registry()

        for persona in registry.personas:
            assert persona.name
            assert len(persona.name) > 0

    def test_all_personas_have_descriptions(self):
        """Test all personas have non-empty descriptions."""
        registry = load_persona_registry()

        for persona in registry.personas:
            assert persona.description
            assert len(persona.description) > 0

    def test_all_personas_have_focus_areas(self):
        """Test all personas have at least one focus area."""
        registry = load_persona_registry()

        for persona in registry.personas:
            assert persona.focus_areas
            assert len(persona.focus_areas) > 0

    def test_all_personas_have_education_content(self):
        """Test all personas have education content recommendations."""
        registry = load_persona_registry()

        for persona in registry.personas:
            assert persona.content_types.education
            assert len(persona.content_types.education) > 0

    def test_cash_flow_optimizer_has_partner_offers(self):
        """Test cash flow optimizer has partner offer recommendations."""
        registry = load_persona_registry()
        persona = registry.get_persona_by_id('cash_flow_optimizer')

        assert persona is not None
        assert persona.content_types.partner_offers
        assert len(persona.content_types.partner_offers) > 0


class TestPersonaModel:
    """Test Persona model validation."""

    def test_persona_id_must_be_lowercase(self):
        """Test persona ID must be lowercase snake_case."""
        with pytest.raises(ValidationError):
            Persona(
                id="HighUtilization",  # Invalid: not lowercase
                name="Test",
                description="Test",
                priority=1,
                criteria=PersonaCriteria(
                    operator=LogicalOperator.AND,
                    conditions=[
                        PersonaCondition(signal="test", operator=ConditionOperator.GTE, value=1.0)
                    ]
                ),
                focus_areas=["test"],
                content_types={"education": ["test"], "partner_offers": []}
            )

    def test_persona_must_have_focus_areas(self):
        """Test persona must have at least one focus area."""
        with pytest.raises(ValidationError):
            Persona(
                id="test",
                name="Test",
                description="Test",
                priority=1,
                criteria=PersonaCriteria(
                    operator=LogicalOperator.AND,
                    conditions=[
                        PersonaCondition(signal="test", operator=ConditionOperator.GTE, value=1.0)
                    ]
                ),
                focus_areas=[],  # Invalid: empty
                content_types={"education": ["test"], "partner_offers": []}
            )

    def test_persona_must_have_conditions(self):
        """Test persona criteria must have at least one condition."""
        with pytest.raises(ValidationError):
            Persona(
                id="test",
                name="Test",
                description="Test",
                priority=1,
                criteria=PersonaCriteria(
                    operator=LogicalOperator.AND,
                    conditions=[]  # Invalid: no conditions
                ),
                focus_areas=["test"],
                content_types={"education": ["test"], "partner_offers": []}
            )


class TestPersonaRegistry:
    """Test PersonaRegistry model."""

    def test_registry_get_persona_by_id(self):
        """Test retrieving persona by ID."""
        registry = load_persona_registry()

        persona = registry.get_persona_by_id('high_utilization')
        assert persona is not None
        assert persona.id == 'high_utilization'

        # Test non-existent ID
        persona = registry.get_persona_by_id('nonexistent')
        assert persona is None

    def test_registry_get_persona_ids(self):
        """Test retrieving all persona IDs."""
        registry = load_persona_registry()

        ids = registry.get_persona_ids()
        assert len(ids) == 6
        assert 'high_utilization' in ids
        assert 'young_professional' in ids
