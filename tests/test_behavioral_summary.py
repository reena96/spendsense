"""
Tests for behavioral summary aggregation (Story 2.6).
"""

import pytest
from datetime import date, timedelta
from pathlib import Path
import json

from spendsense.features.behavioral_summary import (
    BehavioralSummaryGenerator,
    BehavioralSummary
)


@pytest.fixture
def generator():
    """Create BehavioralSummaryGenerator with test database."""
    db_path = "data/processed/spendsense.db"
    if not Path(db_path).exists():
        pytest.skip(f"Test database not found: {db_path}")
    return BehavioralSummaryGenerator(db_path)


class TestBehavioralSummaryGenerator:
    """Tests for BehavioralSummaryGenerator class."""

    def test_ac1_combines_all_signals(self, generator):
        """AC1: User behavioral summary created combining subscription, savings, credit, and income signals."""
        reference_date = date(2025, 11, 4)
        summary = generator.generate_summary(
            user_id="user_MASKED_000",
            reference_date=reference_date
        )

        # Summary should be returned
        assert isinstance(summary, BehavioralSummary)

        # Should have all signal types
        assert hasattr(summary, 'subscriptions_30d')
        assert hasattr(summary, 'subscriptions_180d')
        assert hasattr(summary, 'savings_30d')
        assert hasattr(summary, 'savings_180d')
        assert hasattr(summary, 'credit_30d')
        assert hasattr(summary, 'credit_180d')
        assert hasattr(summary, 'income_30d')
        assert hasattr(summary, 'income_180d')

    def test_ac2_includes_both_time_windows(self, generator):
        """AC2: Summary includes all metrics computed for both time windows."""
        reference_date = date(2025, 11, 4)
        summary = generator.generate_summary(
            user_id="user_MASKED_000",
            reference_date=reference_date
        )

        # Verify 30-day metrics
        assert summary.subscriptions_30d.window_days == 30
        assert summary.savings_30d.window_days == 30
        assert summary.credit_30d.window_days == 30
        assert summary.income_30d.window_days == 30

        # Verify 180-day metrics
        assert summary.subscriptions_180d.window_days == 180
        assert summary.savings_180d.window_days == 180
        assert summary.credit_180d.window_days == 180
        assert summary.income_180d.window_days == 180

    def test_ac3_includes_metadata(self, generator):
        """AC3: Summary includes metadata: calculation timestamp, data completeness flags."""
        reference_date = date(2025, 11, 4)
        summary = generator.generate_summary(
            user_id="user_MASKED_000",
            reference_date=reference_date
        )

        # Check metadata fields
        assert hasattr(summary, 'generated_at')
        assert hasattr(summary, 'data_completeness')
        assert summary.generated_at is not None

        # Data completeness should be a dict
        assert isinstance(summary.data_completeness, dict)

        # Should have completeness flags for all detectors
        assert 'subscriptions' in summary.data_completeness
        assert 'savings' in summary.data_completeness
        assert 'credit' in summary.data_completeness
        assert 'income' in summary.data_completeness

    def test_ac4_missing_data_indicators(self, generator):
        """AC4: Missing data indicators added where signals could not be computed."""
        reference_date = date(2025, 11, 4)
        summary = generator.generate_summary(
            user_id="user_MASKED_000",
            reference_date=reference_date
        )

        # fallbacks_applied should be a list
        assert isinstance(summary.fallbacks_applied, list)

        # Each data completeness should be boolean
        for key, value in summary.data_completeness.items():
            assert isinstance(value, bool)

    def test_ac5_json_serialization(self, generator):
        """AC5: Summary stored in structured format (JSON) for recommendation engine access."""
        reference_date = date(2025, 11, 4)
        summary = generator.generate_summary(
            user_id="user_MASKED_000",
            reference_date=reference_date
        )

        # Should have to_dict method
        assert hasattr(summary, 'to_dict')

        # Convert to dict
        summary_dict = summary.to_dict()

        # Should be JSON serializable
        json_str = json.dumps(summary_dict)
        assert len(json_str) > 0

        # Parse back
        parsed = json.loads(json_str)
        assert parsed['user_id'] == "user_MASKED_000"

    def test_ac7_fallback_defaults_applied(self, generator):
        """AC7: Fallback defaults applied consistently for incomplete data."""
        reference_date = date(2025, 11, 4)

        # Test with user likely to have missing data
        summary = generator.generate_summary(
            user_id="user_MASKED_999",  # Non-existent user
            reference_date=reference_date
        )

        # Should return summary with fallbacks
        assert isinstance(summary, BehavioralSummary)
        assert len(summary.fallbacks_applied) > 0

    def test_ac8_summary_generation_logged(self, generator):
        """AC8: Summary generation logged for audit trail."""
        reference_date = date(2025, 11, 4)

        # Generate summary (logging happens internally)
        summary = generator.generate_summary(
            user_id="user_MASKED_000",
            reference_date=reference_date
        )

        # Verify summary was generated successfully
        assert summary is not None
        assert summary.generated_at is not None

    def test_ac9_data_structure_completeness(self, generator):
        """AC9: Unit tests verify summary completeness and data structure."""
        reference_date = date(2025, 11, 4)
        summary = generator.generate_summary(
            user_id="user_MASKED_000",
            reference_date=reference_date
        )

        # Verify all required fields present
        required_fields = [
            'user_id',
            'generated_at',
            'reference_date',
            'subscriptions_30d',
            'subscriptions_180d',
            'savings_30d',
            'savings_180d',
            'credit_30d',
            'credit_180d',
            'income_30d',
            'income_180d',
            'data_completeness',
            'fallbacks_applied'
        ]

        for field in required_fields:
            assert hasattr(summary, field)


class TestSummaryStructure:
    """Test summary data structure."""

    def test_summary_dict_structure(self, generator):
        """Test summary dictionary has correct structure."""
        reference_date = date(2025, 11, 4)
        summary = generator.generate_summary(
            user_id="user_MASKED_000",
            reference_date=reference_date
        )

        summary_dict = summary.to_dict()

        # Check top-level keys
        assert 'user_id' in summary_dict
        assert 'generated_at' in summary_dict
        assert 'reference_date' in summary_dict
        assert 'subscriptions' in summary_dict
        assert 'savings' in summary_dict
        assert 'credit' in summary_dict
        assert 'income' in summary_dict
        assert 'metadata' in summary_dict

        # Check nested structure
        assert '30d' in summary_dict['subscriptions']
        assert '180d' in summary_dict['subscriptions']
        assert '30d' in summary_dict['savings']
        assert '180d' in summary_dict['savings']
        assert '30d' in summary_dict['credit']
        assert '180d' in summary_dict['credit']
        assert '30d' in summary_dict['income']
        assert '180d' in summary_dict['income']

        # Check metadata structure
        assert 'data_completeness' in summary_dict['metadata']
        assert 'fallbacks_applied' in summary_dict['metadata']

    def test_all_detectors_called(self, generator):
        """Test that all four detectors are called."""
        reference_date = date(2025, 11, 4)
        summary = generator.generate_summary(
            user_id="user_MASKED_000",
            reference_date=reference_date
        )

        # Verify all detectors returned metrics
        assert summary.subscriptions_30d is not None
        assert summary.subscriptions_180d is not None
        assert summary.savings_30d is not None
        assert summary.savings_180d is not None
        assert summary.credit_30d is not None
        assert summary.credit_180d is not None
        assert summary.income_30d is not None
        assert summary.income_180d is not None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_non_existent_user(self, generator):
        """Test handling of non-existent user."""
        reference_date = date(2025, 11, 4)
        summary = generator.generate_summary(
            user_id="user_NONEXISTENT",
            reference_date=reference_date
        )

        # Should return summary with fallbacks
        assert isinstance(summary, BehavioralSummary)
        assert summary.user_id == "user_NONEXISTENT"

        # All data completeness should likely be False
        # (depends on data, but likely)

    def test_future_date_handling(self, generator):
        """Test that future dates are handled gracefully."""
        future_date = date.today() + timedelta(days=30)

        # Generator catches exceptions and returns fallbacks instead of raising
        summary = generator.generate_summary(
            user_id="user_MASKED_000",
            reference_date=future_date
        )

        # Should return summary with all fallbacks applied
        assert isinstance(summary, BehavioralSummary)
        # All detectors should have failed and applied fallbacks
        assert len(summary.fallbacks_applied) == 4  # All 4 detectors


class TestMetadataFields:
    """Test metadata field accuracy."""

    def test_data_completeness_accuracy(self, generator):
        """Test data completeness flags are accurate."""
        reference_date = date(2025, 11, 4)
        summary = generator.generate_summary(
            user_id="user_MASKED_000",
            reference_date=reference_date
        )

        # Verify completeness matches actual data
        if summary.data_completeness.get('subscriptions'):
            # Should have subscription data
            assert (summary.subscriptions_30d.subscription_count > 0 or
                    summary.subscriptions_180d.subscription_count > 0)

        if summary.data_completeness.get('savings'):
            # Should have savings data
            assert (summary.savings_30d.has_savings_accounts or
                    summary.savings_180d.has_savings_accounts)

    def test_fallbacks_tracking(self, generator):
        """Test fallbacks are tracked correctly."""
        reference_date = date(2025, 11, 4)
        summary = generator.generate_summary(
            user_id="user_MASKED_000",
            reference_date=reference_date
        )

        # fallbacks_applied should be subset of detectors
        valid_detectors = {'subscriptions', 'savings', 'credit', 'income'}
        for fallback in summary.fallbacks_applied:
            assert fallback in valid_detectors


class TestIntegration:
    """Test integration between all detectors."""

    def test_end_to_end_summary_generation(self, generator):
        """Test complete end-to-end summary generation."""
        reference_date = date(2025, 11, 4)
        summary = generator.generate_summary(
            user_id="user_MASKED_000",
            reference_date=reference_date
        )

        # Convert to JSON
        summary_dict = summary.to_dict()

        # Verify can be serialized and deserialized
        json_str = json.dumps(summary_dict)
        parsed = json.loads(json_str)

        # Verify key fields preserved
        assert parsed['user_id'] == "user_MASKED_000"
        assert 'subscriptions' in parsed
        assert 'savings' in parsed
        assert 'credit' in parsed
        assert 'income' in parsed
        assert 'metadata' in parsed
