"""
Tests for persona prioritization logic.

Tests selection of highest-priority persona when multiple matches occur,
edge cases, and deterministic behavior.
"""

import pytest
from datetime import datetime

from spendsense.personas.prioritizer import (
    PersonaPrioritizer,
    PersonaAssignment
)
from spendsense.personas.matcher import PersonaMatch
from spendsense.personas.registry import clear_registry_cache


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear registry cache before each test."""
    clear_registry_cache()
    yield
    clear_registry_cache()


@pytest.fixture
def prioritizer():
    """Create PersonaPrioritizer instance."""
    return PersonaPrioritizer()


@pytest.fixture
def sample_matches():
    """Create sample PersonaMatch fixtures for testing."""
    return {
        'high_utilization': PersonaMatch(
            persona_id='high_utilization',
            matched=True,
            evidence={'credit_max_utilization_pct': 60.0},
            matched_conditions=['credit_max_utilization_pct >= 50.0']
        ),
        'irregular_income': PersonaMatch(
            persona_id='irregular_income',
            matched=True,
            evidence={'income_median_pay_gap_days': 50.0},
            matched_conditions=['income_median_pay_gap_days > 45.0']
        ),
        'low_savings': PersonaMatch(
            persona_id='low_savings',
            matched=True,
            evidence={'savings_emergency_fund_months': 2.0},
            matched_conditions=['savings_emergency_fund_months < 3.0']
        ),
        'subscription_heavy': PersonaMatch(
            persona_id='subscription_heavy',
            matched=True,
            evidence={'subscription_share_pct': 0.25},
            matched_conditions=['subscription_share_pct >= 0.20']
        ),
        'cash_flow_optimizer': PersonaMatch(
            persona_id='cash_flow_optimizer',
            matched=True,
            evidence={
                'savings_emergency_fund_months': 7.0,
                'credit_max_utilization_pct': 5.0
            },
            matched_conditions=[
                'savings_emergency_fund_months >= 6.0',
                'credit_max_utilization_pct < 10.0'
            ]
        ),
        'young_professional': PersonaMatch(
            persona_id='young_professional',
            matched=True,
            evidence={'transaction_history_days': 150},
            matched_conditions=['transaction_history_days < 180']
        ),
    }


class TestPersonaPrioritizer:
    """Test PersonaPrioritizer class."""

    def test_initialization(self, prioritizer):
        """Test prioritizer initializes correctly."""
        assert prioritizer.registry is not None
        assert len(prioritizer.registry.personas) == 6

    def test_single_match(self, prioritizer, sample_matches):
        """Test prioritization with single qualifying persona."""
        matches = [
            sample_matches['low_savings'],
            PersonaMatch(persona_id='high_utilization', matched=False, evidence={}),
            PersonaMatch(persona_id='irregular_income', matched=False, evidence={}),
            PersonaMatch(persona_id='subscription_heavy', matched=False, evidence={}),
            PersonaMatch(persona_id='cash_flow_optimizer', matched=False, evidence={}),
            PersonaMatch(persona_id='young_professional', matched=False, evidence={}),
        ]

        assignment = prioritizer.prioritize_persona(matches)

        assert assignment.assigned_persona_id == 'low_savings'
        assert assignment.priority == 3
        assert assignment.all_qualifying_personas == ['low_savings']
        assert "Only qualifying persona" in assignment.prioritization_reason
        assert isinstance(assignment.assigned_at, datetime)

    def test_zero_matches(self, prioritizer):
        """Test prioritization with zero qualifying personas."""
        matches = [
            PersonaMatch(persona_id='high_utilization', matched=False, evidence={}),
            PersonaMatch(persona_id='irregular_income', matched=False, evidence={}),
            PersonaMatch(persona_id='low_savings', matched=False, evidence={}),
            PersonaMatch(persona_id='subscription_heavy', matched=False, evidence={}),
            PersonaMatch(persona_id='cash_flow_optimizer', matched=False, evidence={}),
            PersonaMatch(persona_id='young_professional', matched=False, evidence={}),
        ]

        assignment = prioritizer.prioritize_persona(matches)

        assert assignment.assigned_persona_id == 'unclassified'
        assert assignment.priority is None
        assert assignment.all_qualifying_personas == []
        assert "No qualifying personas found" in assignment.prioritization_reason


class TestPriorityOrdering:
    """Test priority-based selection logic."""

    def test_priority_1_wins_over_2(self, prioritizer, sample_matches):
        """Test Persona 1 (high_utilization) beats Persona 2 (irregular_income)."""
        matches = [
            sample_matches['high_utilization'],  # Priority 1
            sample_matches['irregular_income'],  # Priority 2
            PersonaMatch(persona_id='low_savings', matched=False, evidence={}),
            PersonaMatch(persona_id='subscription_heavy', matched=False, evidence={}),
            PersonaMatch(persona_id='cash_flow_optimizer', matched=False, evidence={}),
            PersonaMatch(persona_id='young_professional', matched=False, evidence={}),
        ]

        assignment = prioritizer.prioritize_persona(matches)

        assert assignment.assigned_persona_id == 'high_utilization'
        assert assignment.priority == 1
        assert 'high_utilization' in assignment.all_qualifying_personas
        assert 'irregular_income' in assignment.all_qualifying_personas
        assert len(assignment.all_qualifying_personas) == 2

    def test_priority_2_wins_over_3(self, prioritizer, sample_matches):
        """Test Persona 2 (irregular_income) beats Persona 3 (low_savings)."""
        matches = [
            PersonaMatch(persona_id='high_utilization', matched=False, evidence={}),
            sample_matches['irregular_income'],  # Priority 2
            sample_matches['low_savings'],  # Priority 3
            PersonaMatch(persona_id='subscription_heavy', matched=False, evidence={}),
            PersonaMatch(persona_id='cash_flow_optimizer', matched=False, evidence={}),
            PersonaMatch(persona_id='young_professional', matched=False, evidence={}),
        ]

        assignment = prioritizer.prioritize_persona(matches)

        assert assignment.assigned_persona_id == 'irregular_income'
        assert assignment.priority == 2

    def test_priority_3_wins_over_4(self, prioritizer, sample_matches):
        """Test Persona 3 (low_savings) beats Persona 4 (subscription_heavy)."""
        matches = [
            PersonaMatch(persona_id='high_utilization', matched=False, evidence={}),
            PersonaMatch(persona_id='irregular_income', matched=False, evidence={}),
            sample_matches['low_savings'],  # Priority 3
            sample_matches['subscription_heavy'],  # Priority 4
            PersonaMatch(persona_id='cash_flow_optimizer', matched=False, evidence={}),
            PersonaMatch(persona_id='young_professional', matched=False, evidence={}),
        ]

        assignment = prioritizer.prioritize_persona(matches)

        assert assignment.assigned_persona_id == 'low_savings'
        assert assignment.priority == 3

    def test_priority_4_wins_over_5(self, prioritizer, sample_matches):
        """Test Persona 4 (subscription_heavy) beats Persona 5 (cash_flow_optimizer)."""
        matches = [
            PersonaMatch(persona_id='high_utilization', matched=False, evidence={}),
            PersonaMatch(persona_id='irregular_income', matched=False, evidence={}),
            PersonaMatch(persona_id='low_savings', matched=False, evidence={}),
            sample_matches['subscription_heavy'],  # Priority 4
            sample_matches['cash_flow_optimizer'],  # Priority 5
            PersonaMatch(persona_id='young_professional', matched=False, evidence={}),
        ]

        assignment = prioritizer.prioritize_persona(matches)

        assert assignment.assigned_persona_id == 'subscription_heavy'
        assert assignment.priority == 4

    def test_priority_5_wins_over_6(self, prioritizer, sample_matches):
        """Test Persona 5 (cash_flow_optimizer) beats Persona 6 (young_professional)."""
        matches = [
            PersonaMatch(persona_id='high_utilization', matched=False, evidence={}),
            PersonaMatch(persona_id='irregular_income', matched=False, evidence={}),
            PersonaMatch(persona_id='low_savings', matched=False, evidence={}),
            PersonaMatch(persona_id='subscription_heavy', matched=False, evidence={}),
            sample_matches['cash_flow_optimizer'],  # Priority 5
            sample_matches['young_professional'],  # Priority 6
        ]

        assignment = prioritizer.prioritize_persona(matches)

        assert assignment.assigned_persona_id == 'cash_flow_optimizer'
        assert assignment.priority == 5

    def test_all_six_personas_match(self, prioritizer, sample_matches):
        """Test priority 1 wins when all 6 personas match."""
        matches = list(sample_matches.values())

        assignment = prioritizer.prioritize_persona(matches)

        assert assignment.assigned_persona_id == 'high_utilization'
        assert assignment.priority == 1
        assert len(assignment.all_qualifying_personas) == 6
        assert "6 qualifying personas" in assignment.prioritization_reason


class TestMultipleMatches:
    """Test scenarios with multiple qualifying personas."""

    def test_three_personas_match(self, prioritizer, sample_matches):
        """Test prioritization with 3 qualifying personas."""
        matches = [
            PersonaMatch(persona_id='high_utilization', matched=False, evidence={}),
            sample_matches['irregular_income'],  # Priority 2
            sample_matches['low_savings'],  # Priority 3
            sample_matches['subscription_heavy'],  # Priority 4
            PersonaMatch(persona_id='cash_flow_optimizer', matched=False, evidence={}),
            PersonaMatch(persona_id='young_professional', matched=False, evidence={}),
        ]

        assignment = prioritizer.prioritize_persona(matches)

        assert assignment.assigned_persona_id == 'irregular_income'
        assert assignment.priority == 2
        assert len(assignment.all_qualifying_personas) == 3
        assert "3 qualifying personas" in assignment.prioritization_reason
        assert 'irregular_income' in assignment.all_qualifying_personas
        assert 'low_savings' in assignment.all_qualifying_personas
        assert 'subscription_heavy' in assignment.all_qualifying_personas

    def test_two_low_priority_personas(self, prioritizer, sample_matches):
        """Test prioritization with only low-priority personas matching."""
        matches = [
            PersonaMatch(persona_id='high_utilization', matched=False, evidence={}),
            PersonaMatch(persona_id='irregular_income', matched=False, evidence={}),
            PersonaMatch(persona_id='low_savings', matched=False, evidence={}),
            PersonaMatch(persona_id='subscription_heavy', matched=False, evidence={}),
            sample_matches['cash_flow_optimizer'],  # Priority 5
            sample_matches['young_professional'],  # Priority 6
        ]

        assignment = prioritizer.prioritize_persona(matches)

        assert assignment.assigned_persona_id == 'cash_flow_optimizer'
        assert assignment.priority == 5


class TestAuditTrail:
    """Test completeness of audit trail."""

    def test_all_qualifying_personas_recorded(self, prioritizer, sample_matches):
        """Test all qualifying persona IDs are recorded."""
        matches = [
            sample_matches['high_utilization'],
            sample_matches['irregular_income'],
            sample_matches['low_savings'],
            PersonaMatch(persona_id='subscription_heavy', matched=False, evidence={}),
            PersonaMatch(persona_id='cash_flow_optimizer', matched=False, evidence={}),
            PersonaMatch(persona_id='young_professional', matched=False, evidence={}),
        ]

        assignment = prioritizer.prioritize_persona(matches)

        assert set(assignment.all_qualifying_personas) == {
            'high_utilization',
            'irregular_income',
            'low_savings'
        }

    def test_prioritization_reason_descriptive(self, prioritizer, sample_matches):
        """Test prioritization reason is descriptive."""
        matches = [
            sample_matches['high_utilization'],
            sample_matches['irregular_income'],
            PersonaMatch(persona_id='low_savings', matched=False, evidence={}),
            PersonaMatch(persona_id='subscription_heavy', matched=False, evidence={}),
            PersonaMatch(persona_id='cash_flow_optimizer', matched=False, evidence={}),
            PersonaMatch(persona_id='young_professional', matched=False, evidence={}),
        ]

        assignment = prioritizer.prioritize_persona(matches)

        # Reason should mention number of qualifying personas and priority
        assert "2 qualifying personas" in assignment.prioritization_reason
        assert "priority 1" in assignment.prioritization_reason

    def test_timestamp_present(self, prioritizer, sample_matches):
        """Test assignment timestamp is present."""
        matches = [sample_matches['low_savings']]

        assignment = prioritizer.prioritize_persona(matches)

        assert assignment.assigned_at is not None
        assert isinstance(assignment.assigned_at, datetime)


class TestDeterministicBehavior:
    """Test that prioritization is deterministic."""

    def test_same_input_same_output(self, prioritizer, sample_matches):
        """Test same input produces same output (deterministic)."""
        matches = [
            sample_matches['irregular_income'],
            sample_matches['low_savings'],
            sample_matches['subscription_heavy'],
            PersonaMatch(persona_id='high_utilization', matched=False, evidence={}),
            PersonaMatch(persona_id='cash_flow_optimizer', matched=False, evidence={}),
            PersonaMatch(persona_id='young_professional', matched=False, evidence={}),
        ]

        # Run 10 times with same input
        results = []
        for _ in range(10):
            assignment = prioritizer.prioritize_persona(matches)
            results.append(assignment.assigned_persona_id)

        # All results should be identical
        assert len(set(results)) == 1
        assert results[0] == 'irregular_income'

    def test_different_order_same_result(self, prioritizer, sample_matches):
        """Test different match order produces same result."""
        # Same matches, different order
        matches_order1 = [
            sample_matches['subscription_heavy'],
            sample_matches['low_savings'],
            sample_matches['irregular_income'],
            PersonaMatch(persona_id='high_utilization', matched=False, evidence={}),
            PersonaMatch(persona_id='cash_flow_optimizer', matched=False, evidence={}),
            PersonaMatch(persona_id='young_professional', matched=False, evidence={}),
        ]

        matches_order2 = [
            sample_matches['irregular_income'],
            sample_matches['subscription_heavy'],
            sample_matches['low_savings'],
            PersonaMatch(persona_id='high_utilization', matched=False, evidence={}),
            PersonaMatch(persona_id='cash_flow_optimizer', matched=False, evidence={}),
            PersonaMatch(persona_id='young_professional', matched=False, evidence={}),
        ]

        assignment1 = prioritizer.prioritize_persona(matches_order1)
        assignment2 = prioritizer.prioritize_persona(matches_order2)

        assert assignment1.assigned_persona_id == assignment2.assigned_persona_id
        assert assignment1.priority == assignment2.priority
        assert set(assignment1.all_qualifying_personas) == set(assignment2.all_qualifying_personas)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_only_lowest_priority_matches(self, prioritizer, sample_matches):
        """Test when only the lowest priority persona matches."""
        matches = [
            PersonaMatch(persona_id='high_utilization', matched=False, evidence={}),
            PersonaMatch(persona_id='irregular_income', matched=False, evidence={}),
            PersonaMatch(persona_id='low_savings', matched=False, evidence={}),
            PersonaMatch(persona_id='subscription_heavy', matched=False, evidence={}),
            PersonaMatch(persona_id='cash_flow_optimizer', matched=False, evidence={}),
            sample_matches['young_professional'],  # Priority 6 (lowest)
        ]

        assignment = prioritizer.prioritize_persona(matches)

        assert assignment.assigned_persona_id == 'young_professional'
        assert assignment.priority == 6
        assert "Only qualifying persona" in assignment.prioritization_reason

    def test_only_highest_priority_matches(self, prioritizer, sample_matches):
        """Test when only the highest priority persona matches."""
        matches = [
            sample_matches['high_utilization'],  # Priority 1 (highest)
            PersonaMatch(persona_id='irregular_income', matched=False, evidence={}),
            PersonaMatch(persona_id='low_savings', matched=False, evidence={}),
            PersonaMatch(persona_id='subscription_heavy', matched=False, evidence={}),
            PersonaMatch(persona_id='cash_flow_optimizer', matched=False, evidence={}),
            PersonaMatch(persona_id='young_professional', matched=False, evidence={}),
        ]

        assignment = prioritizer.prioritize_persona(matches)

        assert assignment.assigned_persona_id == 'high_utilization'
        assert assignment.priority == 1

    def test_empty_matches_list(self, prioritizer):
        """Test with empty matches list."""
        matches = []

        assignment = prioritizer.prioritize_persona(matches)

        assert assignment.assigned_persona_id == 'unclassified'
        assert assignment.priority is None
        assert assignment.all_qualifying_personas == []
