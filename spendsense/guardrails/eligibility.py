"""
Eligibility filtering system for SpendSense.

This module provides eligibility checking to ensure only appropriate product
recommendations are shown to users based on income, credit, existing accounts,
and harmful product filtering.

Epic 5 - Story 5.2: Eligibility Filtering System
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import structlog

# Configure structured logging
logger = structlog.get_logger(__name__)


# Harmful product categories to block
HARMFUL_PRODUCT_CATEGORIES = {
    "payday_loan",
    "title_loan",
    "high_fee_credit",
    "predatory_lending",
    "crypto_leverage",
    "high_risk_investment"
}


@dataclass
class EligibilityResult:
    """
    Result of eligibility check with pass/fail and reasons.

    Similar to ConsentResult and MatchingResult patterns from previous stories.
    """
    offer_id: str
    eligible: bool
    reasons: List[str]  # Reasons for pass or fail
    checks_performed: Dict[str, bool]  # Which checks passed/failed
    audit_trail: dict


class EligibilityChecker:
    """
    Service for checking offer eligibility against user data.

    Uses dependency injection pattern following Story 4.3 and Story 5.1.
    """

    def __init__(self, partner_offers: Optional[Dict[str, Any]] = None):
        """
        Initialize eligibility checker.

        Args:
            partner_offers: Optional partner offer catalog for eligibility rules
        """
        self.partner_offers = partner_offers or {}

    def check_eligibility(
        self,
        user_data: Dict[str, Any],
        offer: Dict[str, Any]
    ) -> EligibilityResult:
        """
        Check if user is eligible for a specific offer.

        Performs multiple eligibility checks:
        - Income requirements
        - Credit requirements
        - Duplicate account prevention
        - Harmful product blocking

        Args:
            user_data: User profile with income, credit, existing_accounts
            offer: Partner offer with eligibility rules

        Returns:
            EligibilityResult with pass/fail and detailed reasons
        """
        offer_id = offer.get("offer_id", "unknown")
        reasons = []
        checks = {}

        # Check 1: Income requirement (AC1)
        income_check = self.check_income_requirement(user_data, offer)
        checks["income"] = income_check["passed"]
        if not income_check["passed"]:
            reasons.append(income_check["reason"])

        # Check 2: Credit requirement (AC2)
        credit_check = self.check_credit_requirement(user_data, offer)
        checks["credit"] = credit_check["passed"]
        if not credit_check["passed"]:
            reasons.append(credit_check["reason"])

        # Check 3: Duplicate account prevention (AC3)
        duplicate_check = self.check_duplicate_accounts(user_data, offer)
        checks["duplicate"] = duplicate_check["passed"]
        if not duplicate_check["passed"]:
            reasons.append(duplicate_check["reason"])

        # Check 4: Harmful product blocking (AC4)
        harmful_check = self.check_harmful_products(offer)
        checks["harmful"] = harmful_check["passed"]
        if not harmful_check["passed"]:
            reasons.append(harmful_check["reason"])

        # Overall eligibility
        eligible = all(checks.values())

        if eligible:
            reasons.append("All eligibility checks passed")

        # Build audit trail (AC6, AC8)
        audit_trail = {
            "action": "eligibility_check",
            "offer_id": offer_id,
            "user_id": user_data.get("user_id", "unknown"),
            "eligible": eligible,
            "checks_performed": checks,
            "failure_reasons": [r for r in reasons if r != "All eligibility checks passed"],
            "timestamp": datetime.utcnow().isoformat()
        }

        # Log eligibility failures (AC6)
        if not eligible:
            logger.warning(
                "eligibility_check_failed",
                offer_id=offer_id,
                user_id=user_data.get("user_id"),
                reasons=reasons
            )
        else:
            logger.debug(
                "eligibility_check_passed",
                offer_id=offer_id,
                user_id=user_data.get("user_id")
            )

        return EligibilityResult(
            offer_id=offer_id,
            eligible=eligible,
            reasons=reasons,
            checks_performed=checks,
            audit_trail=audit_trail
        )

    def check_income_requirement(
        self,
        user_data: Dict[str, Any],
        offer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if user meets minimum income requirement (AC1).

        Args:
            user_data: Must contain 'annual_income'
            offer: Must contain 'minimum_income' if requirement exists

        Returns:
            Dict with 'passed' (bool) and 'reason' (str)
        """
        minimum_income = offer.get("minimum_income", 0)
        user_income = user_data.get("annual_income", 0)

        if minimum_income > 0 and user_income < minimum_income:
            return {
                "passed": False,
                "reason": f"Income ${user_income:,.0f} below minimum ${minimum_income:,.0f}"
            }

        return {
            "passed": True,
            "reason": "Income requirement met"
        }

    def check_credit_requirement(
        self,
        user_data: Dict[str, Any],
        offer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if user meets credit requirements (AC2).

        Uses credit score if available, otherwise uses credit utilization as proxy.

        Args:
            user_data: Must contain 'credit_score' or 'credit_utilization'
            offer: Must contain 'minimum_credit_score' if requirement exists

        Returns:
            Dict with 'passed' (bool) and 'reason' (str)
        """
        minimum_credit = offer.get("minimum_credit_score", 0)

        if minimum_credit > 0:
            user_credit = user_data.get("credit_score", 0)

            # If no credit score, use utilization as proxy
            # High utilization (>50%) suggests credit issues
            if user_credit == 0:
                credit_utilization = user_data.get("credit_utilization", 0)
                if credit_utilization > 0.5:
                    return {
                        "passed": False,
                        "reason": f"High credit utilization ({credit_utilization*100:.0f}%) suggests credit issues"
                    }
                # Allow if low/no utilization (no negative signals)
                return {
                    "passed": True,
                    "reason": "Credit signals acceptable"
                }

            if user_credit < minimum_credit:
                return {
                    "passed": False,
                    "reason": f"Credit score {user_credit} below minimum {minimum_credit}"
                }

        return {
            "passed": True,
            "reason": "Credit requirement met"
        }

    def check_duplicate_accounts(
        self,
        user_data: Dict[str, Any],
        offer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if user already has this type of account (AC3).

        Args:
            user_data: Must contain 'existing_accounts' list
            offer: Must contain 'product_id' or 'product_type'

        Returns:
            Dict with 'passed' (bool) and 'reason' (str)
        """
        existing_accounts = user_data.get("existing_accounts", [])
        offer_product_id = offer.get("product_id")
        offer_product_type = offer.get("product_type")

        # Check for exact product ID match
        if offer_product_id:
            for account in existing_accounts:
                if account.get("product_id") == offer_product_id:
                    return {
                        "passed": False,
                        "reason": f"User already has {offer_product_id}"
                    }

        # Check for product type match (e.g., user already has savings account)
        if offer_product_type:
            for account in existing_accounts:
                if account.get("product_type") == offer_product_type:
                    return {
                        "passed": False,
                        "reason": f"User already has {offer_product_type} account"
                    }

        return {
            "passed": True,
            "reason": "No duplicate accounts"
        }

    def check_harmful_products(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if offer is a harmful/predatory product (AC4).

        Args:
            offer: Must contain 'category' or 'product_type'

        Returns:
            Dict with 'passed' (bool) and 'reason' (str)
        """
        category = offer.get("category", "").lower()
        product_type = offer.get("product_type", "").lower()

        # Check against harmful products blocklist
        if category in HARMFUL_PRODUCT_CATEGORIES or product_type in HARMFUL_PRODUCT_CATEGORIES:
            return {
                "passed": False,
                "reason": f"Harmful product category blocked: {category or product_type}"
            }

        # Additional check for high APR (predatory lending indicator)
        apr = offer.get("apr", 0)
        if apr > 36:  # 36% APR is typical usury law threshold
            return {
                "passed": False,
                "reason": f"Predatory APR blocked: {apr}%"
            }

        return {
            "passed": True,
            "reason": "Not a harmful product"
        }

    def filter_eligible_offers(
        self,
        user_data: Dict[str, Any],
        offers: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], List[EligibilityResult]]:
        """
        Filter list of offers to only eligible ones (AC7).

        Args:
            user_data: User profile data
            offers: List of partner offers to check

        Returns:
            Tuple of (eligible_offers, all_results)
        """
        eligible_offers = []
        all_results = []

        for offer in offers:
            result = self.check_eligibility(user_data, offer)
            all_results.append(result)

            if result.eligible:
                eligible_offers.append(offer)

        logger.info(
            "eligibility_filtering_complete",
            total_offers=len(offers),
            eligible_count=len(eligible_offers),
            filtered_count=len(offers) - len(eligible_offers)
        )

        return eligible_offers, all_results
