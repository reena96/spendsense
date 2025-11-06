"""
Rationale generation engine for recommendations.

Generates transparent, personalized rationales for recommendations
by replacing template placeholders with user's actual behavioral data.
"""

import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from spendsense.recommendations.models import Recommendation, PartnerOffer

logger = logging.getLogger(__name__)


@dataclass
class GeneratedRationale:
    """
    Generated rationale for a recommendation.

    Attributes:
        recommendation_id: ID of recommendation
        recommendation_type: Type (education or partner_offer)
        rationale_text: Generated rationale with data citations
        placeholders_replaced: Dict of placeholder → actual value
        data_citations: List of specific data points cited
        timestamp: When rationale was generated
    """

    recommendation_id: str
    recommendation_type: str
    rationale_text: str
    placeholders_replaced: Dict[str, Any]
    data_citations: List[str]
    timestamp: datetime


class RationaleGenerator:
    """
    Generates personalized rationales for recommendations.

    Implements rationale generation per PRD Story 4.4:
    - Uses template system with placeholders
    - Replaces placeholders with user's actual signal values
    - Cites specific data (account numbers, amounts, percentages, dates)
    - Ensures plain language (grade-8 readability)
    - Includes "because" statements with concrete data
    """

    def __init__(self):
        """Initialize rationale generator."""
        pass

    def generate_for_recommendation(
        self,
        recommendation: Recommendation,
        user_data: Dict[str, Any],
        signals: Optional[List[str]] = None,
    ) -> GeneratedRationale:
        """
        Generate rationale for educational content recommendation (PRD AC1, AC2, AC4).

        Args:
            recommendation: Recommendation with personalization_template
            user_data: User's behavioral and account data
            signals: Optional list of triggering signals

        Returns:
            GeneratedRationale with personalized text and audit trail

        Example:
            >>> rec = Recommendation(id="understand_utilization", ...)
            >>> user_data = {"credit_max_utilization_pct": 68, "account_name": "Visa ****4523"}
            >>> rationale = generator.generate_for_recommendation(rec, user_data)
            >>> print(rationale.rationale_text)
            "You're currently at 68% credit utilization on your Visa ****4523..."
        """
        template = recommendation.personalization_template or ""
        if not template:
            # Use default template if none provided
            template = self._default_education_template(recommendation)

        # Replace placeholders with actual values
        rationale_text, placeholders = self._replace_placeholders(template, user_data)

        # Extract data citations
        citations = self._extract_citations(rationale_text, placeholders)

        logger.info(
            f"Generated rationale for recommendation {recommendation.id}: "
            f"{len(placeholders)} placeholders replaced"
        )

        return GeneratedRationale(
            recommendation_id=recommendation.id,
            recommendation_type="education",
            rationale_text=rationale_text,
            placeholders_replaced=placeholders,
            data_citations=citations,
            timestamp=datetime.utcnow(),
        )

    def generate_for_offer(
        self,
        offer: PartnerOffer,
        user_data: Dict[str, Any],
        signals: Optional[List[str]] = None,
    ) -> GeneratedRationale:
        """
        Generate rationale for partner offer recommendation (PRD AC1, AC3, AC4).

        Args:
            offer: PartnerOffer with rationale_template
            user_data: User's behavioral and account data
            signals: Optional list of triggering signals

        Returns:
            GeneratedRationale with personalized text and audit trail

        Example:
            >>> offer = PartnerOffer(id="balance_transfer", rationale_template="...")
            >>> user_data = {"account_name": "Visa ****4523", "utilization_pct": 68}
            >>> rationale = generator.generate_for_offer(offer, user_data)
            >>> print(rationale.rationale_text)
            "Your Visa ****4523 is at 68% utilization. Transferring..."
        """
        template = offer.rationale_template or ""
        if not template:
            # Use default template if none provided
            template = self._default_offer_template(offer)

        # Replace placeholders with actual values
        rationale_text, placeholders = self._replace_placeholders(template, user_data)

        # Extract data citations
        citations = self._extract_citations(rationale_text, placeholders)

        logger.info(
            f"Generated rationale for offer {offer.id}: "
            f"{len(placeholders)} placeholders replaced"
        )

        return GeneratedRationale(
            recommendation_id=offer.id,
            recommendation_type="partner_offer",
            rationale_text=rationale_text,
            placeholders_replaced=placeholders,
            data_citations=citations,
            timestamp=datetime.utcnow(),
        )

    def _replace_placeholders(
        self, template: str, user_data: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """
        Replace placeholders in template with actual values (PRD AC4, AC5).

        Placeholder format: {placeholder_name}

        Formatting rules (AC5):
        - Amounts: Format as currency with commas (e.g., "$3,400")
        - Percentages: Format with % symbol (e.g., "68%")
        - Account numbers: Already masked in user_data (e.g., "****4523")
        - Dates: Format as human-readable (e.g., "Jan 15, 2025")

        Args:
            template: Template string with {placeholder} markers
            user_data: Dict of placeholder_name → value

        Returns:
            Tuple of (filled_text, placeholders_replaced_dict)
        """
        placeholders_replaced = {}
        filled_text = template

        # Find all placeholders in template
        placeholder_pattern = r"\{([^}]+)\}"
        matches = re.findall(placeholder_pattern, template)

        for placeholder_name in matches:
            if placeholder_name in user_data:
                value = user_data[placeholder_name]
                formatted_value = self._format_value(placeholder_name, value)
                filled_text = filled_text.replace(
                    f"{{{placeholder_name}}}", str(formatted_value)
                )
                placeholders_replaced[placeholder_name] = formatted_value
            else:
                # Placeholder not found in user_data - keep as is or use fallback
                logger.warning(
                    f"Placeholder '{placeholder_name}' not found in user_data"
                )
                placeholders_replaced[placeholder_name] = f"[{placeholder_name}]"

        return filled_text, placeholders_replaced

    def _format_value(self, placeholder_name: str, value: Any) -> str:
        """
        Format value based on placeholder type (PRD AC5).

        Formatting rules:
        - Money amounts: "$3,400" (commas, dollar sign)
        - Percentages: "68%" (percent sign)
        - Account numbers: Already masked (e.g., "Visa ****4523")
        - Numbers: Formatted with commas for thousands
        - Dates: Human-readable format
        - Everything else: String conversion

        Args:
            placeholder_name: Name of placeholder (hints at type)
            value: Value to format

        Returns:
            Formatted string
        """
        # Detect type from placeholder name
        lower_name = placeholder_name.lower()

        # Currency formatting
        if any(
            keyword in lower_name
            for keyword in [
                "balance",
                "amount",
                "income",
                "savings",
                "interest",
                "limit",
                "payment",
                "cost",
                "charge",
                "fee",
            ]
        ):
            if isinstance(value, (int, float)):
                return f"${value:,.0f}" if value == int(value) else f"${value:,.2f}"

        # Percentage formatting
        if any(
            keyword in lower_name
            for keyword in ["pct", "percent", "utilization", "rate", "apy", "apr"]
        ):
            if isinstance(value, (int, float)):
                return f"{value}%"

        # Months formatting
        if "months" in lower_name:
            if isinstance(value, (int, float)):
                return f"{value:.1f}" if value != int(value) else str(int(value))

        # Number formatting (with commas)
        if isinstance(value, int):
            return f"{value:,}"

        if isinstance(value, float):
            return f"{value:,.2f}"

        # Date formatting
        if isinstance(value, datetime):
            return value.strftime("%b %d, %Y")

        # String/default
        return str(value)

    def _extract_citations(
        self, rationale_text: str, placeholders: Dict[str, Any]
    ) -> List[str]:
        """
        Extract specific data citations from generated rationale (PRD AC5).

        Citations include:
        - Account numbers (masked)
        - Dollar amounts
        - Percentages
        - Dates

        Args:
            rationale_text: Generated rationale with data
            placeholders: Dict of replaced placeholders

        Returns:
            List of data citations found
        """
        citations = []

        # Extract account numbers (masked pattern: ****XXXX)
        account_pattern = r"\*{4}\d{4}"
        accounts = re.findall(account_pattern, rationale_text)
        citations.extend([f"Account: ****{acc[-4:]}" for acc in accounts])

        # Extract dollar amounts
        amount_pattern = r"\$[\d,]+(?:\.\d{2})?"
        amounts = re.findall(amount_pattern, rationale_text)
        citations.extend([f"Amount: {amt}" for amt in set(amounts)])

        # Extract percentages
        pct_pattern = r"\d+(?:\.\d+)?%"
        percentages = re.findall(pct_pattern, rationale_text)
        citations.extend([f"Percentage: {pct}" for pct in set(percentages)])

        return citations

    def _default_education_template(self, recommendation: Recommendation) -> str:
        """
        Generate default template for educational content (PRD AC6, AC8).

        Uses plain language and includes "because" statement.

        Args:
            recommendation: Recommendation without template

        Returns:
            Default template string
        """
        # Generic template with "because" statement
        return (
            f"We recommend this {recommendation.type.value} because it can help you "
            f"{recommendation.description[:50]}... "
            f"This is relevant to your current financial situation."
        )

    def _default_offer_template(self, offer: PartnerOffer) -> str:
        """
        Generate default template for partner offer (PRD AC6, AC8).

        Uses plain language and includes "because" statement.

        Args:
            offer: Partner offer without template

        Returns:
            Default template string
        """
        # Generic template with "because" statement
        return (
            f"We recommend {offer.title} because it could help with your financial goals. "
            f"{offer.description[:80]}..."
        )

    def validate_readability(self, text: str) -> Dict[str, Any]:
        """
        Validate text meets grade-8 readability (PRD AC6).

        Simple heuristics:
        - Average sentence length < 20 words
        - Average word length < 6 characters
        - No complex jargon

        Args:
            text: Text to validate

        Returns:
            Dict with readability metrics
        """
        # Split into sentences (simplified)
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        words = text.split()

        avg_sentence_length = len(words) / max(len(sentences), 1)
        avg_word_length = sum(len(w) for w in words) / max(len(words), 1)

        # Check for complex words (>10 characters)
        complex_words = [w for w in words if len(w) > 10]

        is_readable = (
            avg_sentence_length < 20
            and avg_word_length < 6
            and len(complex_words) < len(words) * 0.1  # Less than 10% complex words
        )

        return {
            "is_readable": is_readable,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "avg_word_length": round(avg_word_length, 1),
            "complex_word_count": len(complex_words),
            "complexity_ratio": round(len(complex_words) / max(len(words), 1), 2),
        }
