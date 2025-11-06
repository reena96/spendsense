"""
Tone validation and language safety system for SpendSense.

This module provides tone validation to ensure all recommendation text uses
supportive, non-judgmental language that empowers users rather than shaming them.

Epic 5 - Story 5.3: Tone Validation & Language Safety
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
import re
import structlog

# Configure structured logging
logger = structlog.get_logger(__name__)

# Prohibited shaming phrases (AC1)
PROHIBITED_PHRASES = {
    # Direct shaming language
    "overspending",
    "bad with money",
    "irresponsible",
    "reckless",
    "wasteful",
    "poor choices",
    "bad habits",
    "financial mistakes",
    "careless spending",
    "living beyond your means",

    # Judgmental phrases
    "you should know better",
    "obviously wrong",
    "clearly irresponsible",
    "foolish",
    "stupid decision",

    # Blame-oriented language
    "your fault",
    "you caused",
    "you're the problem",
    "if only you had",

    # Negative characterizations
    "bad at managing",
    "can't handle money",
    "don't understand finance",
    "need to learn how",
    "failing to",
}

# Empowering alternatives (AC3)
EMPOWERING_ALTERNATIVES = {
    "overspending": "spending more than planned",
    "bad with money": "building money management skills",
    "irresponsible": "opportunity to strengthen financial habits",
    "reckless": "room for more careful planning",
    "wasteful": "opportunity to optimize spending",
    "poor choices": "different choices to consider",
    "bad habits": "habits that could be adjusted",
    "financial mistakes": "learning opportunities",
    "careless spending": "spending without a plan",
    "living beyond your means": "spending exceeding income",
    "you should know better": "here's something to consider",
    "obviously wrong": "there may be a better approach",
    "clearly irresponsible": "worth reconsidering",
    "foolish": "worth thinking through",
    "your fault": "this situation",
    "you caused": "this happened",
    "if only you had": "going forward, you could",
    "bad at managing": "developing your skills in",
    "can't handle money": "growing your confidence with",
    "don't understand finance": "learning about finance",
    "need to learn how": "might find it helpful to",
    "failing to": "opportunity to",
}


@dataclass
class FlaggedPhrase:
    """
    Details about a prohibited phrase found in text.
    """
    phrase: str
    position: int
    suggestion: Optional[str] = None


@dataclass
class ReadabilityMetrics:
    """
    Readability metrics for text analysis.
    """
    grade_level: float
    passes: bool  # True if at or below grade 8


@dataclass
class ToneValidationResult:
    """
    Result of tone validation with pass/fail and flagged phrases.

    Similar to ConsentResult and EligibilityResult patterns from previous stories.
    """
    text_snippet: str  # First 100 chars for reference
    passes_tone: bool
    passes_readability: bool
    flagged_phrases: List[FlaggedPhrase]
    readability_metrics: Optional[ReadabilityMetrics]
    audit_trail: dict

    @property
    def passes(self) -> bool:
        """Overall validation passes if both tone and readability pass."""
        return self.passes_tone and self.passes_readability


class ToneValidator:
    """
    Service for validating tone and language safety in recommendation text.

    Uses dependency injection pattern following Story 5.1 and Story 5.2.
    """

    def __init__(self, max_grade_level: float = 8.0):
        """
        Initialize tone validator.

        Args:
            max_grade_level: Maximum acceptable Flesch-Kincaid grade level (default: 8.0)
        """
        self.max_grade_level = max_grade_level
        self.prohibited_phrases = PROHIBITED_PHRASES
        self.empowering_alternatives = EMPOWERING_ALTERNATIVES

    def validate_tone(self, text: str, text_id: str = "unknown") -> ToneValidationResult:
        """
        Validate tone and language safety of text (AC2, AC3, AC4, AC5).

        Performs:
        - Prohibited phrase detection (shaming language)
        - Readability checking (grade-8 reading level)

        Args:
            text: Text to validate (typically recommendation rationale)
            text_id: Identifier for the text being validated

        Returns:
            ToneValidationResult with pass/fail and flagged phrases
        """
        # Check for prohibited phrases (AC1, AC2)
        flagged_phrases = self.check_prohibited_phrases(text)
        passes_tone = len(flagged_phrases) == 0

        # Check readability (AC4)
        readability_metrics = self.check_readability(text)
        passes_readability = readability_metrics.passes if readability_metrics else True

        # Overall result
        passes = passes_tone and passes_readability

        # Build audit trail (AC8)
        audit_trail = {
            "action": "tone_validation",
            "text_id": text_id,
            "passes": passes,
            "passes_tone": passes_tone,
            "passes_readability": passes_readability,
            "flagged_count": len(flagged_phrases),
            "flagged_phrases": [f.phrase for f in flagged_phrases],
            "timestamp": datetime.utcnow().isoformat()
        }

        if readability_metrics:
            audit_trail["grade_level"] = readability_metrics.grade_level

        # Log validation failures (AC6)
        if not passes:
            logger.warning(
                "tone_validation_failed",
                text_id=text_id,
                passes_tone=passes_tone,
                passes_readability=passes_readability,
                flagged_phrases=[f.phrase for f in flagged_phrases],
                grade_level=readability_metrics.grade_level if readability_metrics else None
            )
        else:
            logger.debug(
                "tone_validation_passed",
                text_id=text_id
            )

        # Epic 6 Story 6.5: Log to audit_log table for compliance reporting
        try:
            from spendsense.services.audit_service import AuditService
            severity = "critical" if not passes_tone else ("warning" if not passes_readability else "none")
            AuditService.log_tone_validated(
                user_id="unknown",  # Tone validation may not have user context
                recommendation_id=text_id,
                passed=passes,
                detected_violations=[f.phrase for f in flagged_phrases],
                severity=severity,
                original_text=text[:200],  # First 200 chars for audit
                session=None  # Will create its own session
            )
        except Exception as e:
            # Log but don't fail tone validation if audit logging fails
            logger.warning("audit_log_failed", error=str(e), text_id=text_id)

        # Create result
        text_snippet = text[:100] + "..." if len(text) > 100 else text

        return ToneValidationResult(
            text_snippet=text_snippet,
            passes_tone=passes_tone,
            passes_readability=passes_readability,
            flagged_phrases=flagged_phrases,
            readability_metrics=readability_metrics,
            audit_trail=audit_trail
        )

    def check_prohibited_phrases(self, text: str) -> List[FlaggedPhrase]:
        """
        Check text for prohibited shaming phrases (AC1, AC2).

        Args:
            text: Text to check

        Returns:
            List of FlaggedPhrase objects with positions and suggestions
        """
        flagged = []
        text_lower = text.lower()

        for phrase in self.prohibited_phrases:
            # Case-insensitive search
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            matches = pattern.finditer(text)

            for match in matches:
                suggestion = self.empowering_alternatives.get(phrase.lower())
                flagged.append(FlaggedPhrase(
                    phrase=phrase,
                    position=match.start(),
                    suggestion=suggestion
                ))

        # Sort by position
        flagged.sort(key=lambda x: x.position)

        return flagged

    def check_readability(self, text: str) -> Optional[ReadabilityMetrics]:
        """
        Check text readability using Flesch-Kincaid grade level (AC4).

        Args:
            text: Text to check

        Returns:
            ReadabilityMetrics with grade level and pass/fail, or None if textstat unavailable
        """
        try:
            import textstat
        except ImportError:
            logger.warning("textstat_not_available", message="textstat library not installed, skipping readability check")
            return None

        # Calculate Flesch-Kincaid grade level
        grade_level = textstat.flesch_kincaid_grade(text)
        passes = grade_level <= self.max_grade_level

        return ReadabilityMetrics(
            grade_level=grade_level,
            passes=passes
        )

    def validate_recommendations(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], List[ToneValidationResult]]:
        """
        Validate tone for a list of recommendations (AC5, AC7).

        Args:
            recommendations: List of recommendation items with 'rationale' field

        Returns:
            Tuple of (validated_recommendations, all_results)
                - validated_recommendations: Only items passing validation
                - all_results: All validation results for audit trail
        """
        validated_recommendations = []
        all_results = []

        for rec in recommendations:
            rationale = rec.get("rationale", "")
            rec_id = rec.get("item_id", "unknown")

            result = self.validate_tone(rationale, text_id=rec_id)
            all_results.append(result)

            if result.passes:
                validated_recommendations.append(rec)
            else:
                # Log failure and skip (AC6, AC7)
                logger.info(
                    "recommendation_filtered_by_tone",
                    item_id=rec_id,
                    flagged_phrases=[f.phrase for f in result.flagged_phrases],
                    grade_level=result.readability_metrics.grade_level if result.readability_metrics else None
                )

        logger.info(
            "tone_validation_complete",
            total_recommendations=len(recommendations),
            passed_count=len(validated_recommendations),
            filtered_count=len(recommendations) - len(validated_recommendations)
        )

        return validated_recommendations, all_results
