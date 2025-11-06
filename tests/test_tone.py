"""
Tests for tone validation and language safety system (Epic 5 - Story 5.3).

Comprehensive test suite covering all acceptance criteria.
"""

import pytest
from spendsense.guardrails.tone import (
    ToneValidator,
    ToneValidationResult,
    FlaggedPhrase,
    PROHIBITED_PHRASES,
    EMPOWERING_ALTERNATIVES
)


@pytest.fixture
def tone_validator():
    """Create ToneValidator instance."""
    return ToneValidator()


# ===== AC1 & AC2: Prohibited phrase detection =====

def test_detects_overspending_phrase(tone_validator):
    """Test detection of 'overspending' prohibited phrase (AC1, AC2, AC9)."""
    text = "You've been overspending on dining out."

    result = tone_validator.validate_tone(text, text_id="test_1")

    assert result.passes_tone is False
    assert len(result.flagged_phrases) == 1
    assert result.flagged_phrases[0].phrase == "overspending"


def test_detects_bad_with_money_phrase(tone_validator):
    """Test detection of 'bad with money' phrase (AC1, AC2, AC9)."""
    text = "It seems you're bad with money management."

    result = tone_validator.validate_tone(text, text_id="test_2")

    assert result.passes_tone is False
    assert any(f.phrase == "bad with money" for f in result.flagged_phrases)


def test_detects_irresponsible_phrase(tone_validator):
    """Test detection of 'irresponsible' phrase (AC1, AC2, AC9)."""
    text = "This irresponsible spending pattern needs to change."

    result = tone_validator.validate_tone(text, text_id="test_3")

    assert result.passes_tone is False
    assert any(f.phrase == "irresponsible" for f in result.flagged_phrases)


def test_detects_multiple_prohibited_phrases(tone_validator):
    """Test detection of multiple prohibited phrases (AC2, AC9)."""
    text = "Your overspending and irresponsible choices show poor money habits."

    result = tone_validator.validate_tone(text, text_id="test_4")

    assert result.passes_tone is False
    assert len(result.flagged_phrases) >= 3  # overspending, irresponsible, poor choices


def test_case_insensitive_detection(tone_validator):
    """Test phrase detection is case-insensitive (AC2)."""
    text = "OVERSPENDING and Bad With Money are issues."

    result = tone_validator.validate_tone(text, text_id="test_5")

    assert result.passes_tone is False
    assert len(result.flagged_phrases) >= 2


def test_flagged_phrase_includes_position(tone_validator):
    """Test flagged phrases include position in text (AC2)."""
    text = "This shows overspending behavior."

    result = tone_validator.validate_tone(text, text_id="test_6")

    assert len(result.flagged_phrases) == 1
    assert result.flagged_phrases[0].position == 11  # Position of "overspending"


# ===== AC3: Empowering alternatives =====

def test_provides_empowering_alternative(tone_validator):
    """Test validator suggests empowering alternatives (AC3)."""
    text = "You've been overspending recently."

    result = tone_validator.validate_tone(text, text_id="test_7")

    assert result.flagged_phrases[0].suggestion is not None
    assert "spending more than planned" in result.flagged_phrases[0].suggestion


def test_empowering_alternative_for_bad_with_money(tone_validator):
    """Test empowering alternative for 'bad with money' (AC3)."""
    text = "You're bad with money."

    result = tone_validator.validate_tone(text, text_id="test_8")

    flagged = result.flagged_phrases[0]
    assert flagged.phrase == "bad with money"
    assert "building money management skills" in flagged.suggestion


# ===== AC4: Readability checking =====

def test_readability_grade_8_passes(tone_validator):
    """Test simple text at grade-8 level passes readability (AC4)."""
    # Simple, clear text
    text = "You can save money by cooking at home. This is a good way to reduce spending on food."

    result = tone_validator.validate_tone(text, text_id="test_9")

    if result.readability_metrics:  # textstat may not be available
        assert result.passes_readability is True
        assert result.readability_metrics.grade_level <= 8.0


def test_readability_complex_text_fails(tone_validator):
    """Test complex text exceeding grade-8 fails readability (AC4)."""
    # Complex, academic text
    text = "The implementation of comprehensive fiscal responsibility necessitates meticulous examination of expenditure patterns and judicious allocation of monetary resources through strategic prioritization methodologies."

    result = tone_validator.validate_tone(text, text_id="test_10")

    if result.readability_metrics:  # textstat may not be available
        # This text should be much higher than grade 8
        assert result.readability_metrics.grade_level > 8.0
        assert result.passes_readability is False


def test_readability_check_when_textstat_unavailable(tone_validator):
    """Test graceful handling when textstat library unavailable (AC4)."""
    # Validator should handle missing textstat gracefully
    text = "Simple text."

    result = tone_validator.validate_tone(text, text_id="test_11")

    # Should still return result even if readability metrics None
    assert result is not None
    if result.readability_metrics is None:
        # Passes readability by default if unavailable
        assert result.passes_readability is True


# ===== AC6: Failed validations logged =====

def test_failed_validation_includes_flagged_phrases(tone_validator):
    """Test failed validation logs specific flagged phrases (AC6)."""
    text = "Your irresponsible overspending is a problem."

    result = tone_validator.validate_tone(text, text_id="test_12")

    assert result.passes is False
    assert len(result.flagged_phrases) >= 2
    assert any(f.phrase == "irresponsible" for f in result.flagged_phrases)
    assert any(f.phrase == "overspending" for f in result.flagged_phrases)


# ===== AC8: Audit trail includes results =====

def test_audit_trail_structure(tone_validator):
    """Test validation result includes comprehensive audit trail (AC8)."""
    text = "This is acceptable supportive language."

    result = tone_validator.validate_tone(text, text_id="test_13")

    assert "audit_trail" in result.__dict__
    audit = result.audit_trail

    assert audit["action"] == "tone_validation"
    assert audit["text_id"] == "test_13"
    assert "passes" in audit
    assert "passes_tone" in audit
    assert "passes_readability" in audit
    assert "flagged_count" in audit
    assert "flagged_phrases" in audit
    assert "timestamp" in audit


def test_audit_trail_includes_grade_level_when_available(tone_validator):
    """Test audit trail includes readability grade level when available (AC8)."""
    text = "Simple clear text that is easy to read."

    result = tone_validator.validate_tone(text, text_id="test_14")

    if result.readability_metrics:
        assert "grade_level" in result.audit_trail
        assert isinstance(result.audit_trail["grade_level"], float)


# ===== AC9 & AC10: Acceptable language tests =====

def test_acceptable_language_passes_validation(tone_validator):
    """Test supportive, empowering language passes validation (AC10)."""
    text = "You have an opportunity to optimize your spending on dining. Building a budget could help you reach your savings goals."

    result = tone_validator.validate_tone(text, text_id="test_15")

    assert result.passes_tone is True
    assert len(result.flagged_phrases) == 0


def test_neutral_educational_language_passes(tone_validator):
    """Test neutral, educational language passes validation (AC10)."""
    text = "Consider setting up automatic transfers to savings. This strategy can help you build an emergency fund over time."

    result = tone_validator.validate_tone(text, text_id="test_16")

    assert result.passes_tone is True
    assert len(result.flagged_phrases) == 0


def test_empowering_language_passes(tone_validator):
    """Test empowering, strengths-based language passes (AC10)."""
    text = "You're making progress on your financial goals. Let's explore ways to strengthen your savings habits."

    result = tone_validator.validate_tone(text, text_id="test_17")

    assert result.passes_tone is True
    assert len(result.flagged_phrases) == 0


# ===== AC7: Manual review queue integration =====

def test_validate_recommendations_filters_problematic(tone_validator):
    """Test validation filters recommendations with problematic tone (AC5, AC7)."""
    recommendations = [
        {
            "item_id": "rec_1",
            "rationale": "Consider building an emergency fund to strengthen your financial resilience."
        },
        {
            "item_id": "rec_2",
            "rationale": "Your overspending on dining is irresponsible and needs to stop."
        },
        {
            "item_id": "rec_3",
            "rationale": "A high-yield savings account could help you reach your goals faster."
        }
    ]

    validated, all_results = tone_validator.validate_recommendations(recommendations)

    # Should filter out rec_2 (has prohibited phrases)
    assert len(validated) == 2
    assert len(all_results) == 3

    validated_ids = [r["item_id"] for r in validated]
    assert "rec_1" in validated_ids
    assert "rec_3" in validated_ids
    assert "rec_2" not in validated_ids  # Filtered out


def test_validate_recommendations_returns_all_results(tone_validator):
    """Test validation returns results for all recommendations (AC8)."""
    recommendations = [
        {"item_id": "rec_1", "rationale": "Good supportive language."},
        {"item_id": "rec_2", "rationale": "Bad with money language."}
    ]

    validated, all_results = tone_validator.validate_recommendations(recommendations)

    assert len(all_results) == 2
    assert all_results[0].passes_tone is True
    assert all_results[1].passes_tone is False


# ===== Integration scenarios =====

def test_combined_tone_and_readability_failure(tone_validator):
    """Test overall validation fails when either tone or readability fails."""
    # Complex text with prohibited phrase
    text = "The irresponsible implementation of comprehensive fiscal responsibility necessitates examination."

    result = tone_validator.validate_tone(text, text_id="test_18")

    assert result.passes_tone is False  # Has "irresponsible"
    if result.readability_metrics:
        assert result.readability_metrics.grade_level > 8.0  # Too complex
        assert result.passes is False  # Overall fails


def test_text_snippet_truncation(tone_validator):
    """Test long text is truncated in result snippet."""
    long_text = "This is a very long text " * 20  # 500+ chars

    result = tone_validator.validate_tone(long_text, text_id="test_19")

    assert len(result.text_snippet) <= 103  # 100 chars + "..."
    assert result.text_snippet.endswith("...")
