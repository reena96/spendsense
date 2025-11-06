"""
Partner offer library loader and accessor.

Loads partner offers from YAML configuration and provides
efficient lookup by persona, type, and eligibility checking.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import ValidationError

from spendsense.recommendations.models import PartnerOffer

logger = logging.getLogger(__name__)


class PartnerOfferLibrary:
    """
    Partner offer library loader and accessor.

    Loads partner offers from YAML file and caches them in memory
    for fast lookup and eligibility checking.

    Usage:
        library = PartnerOfferLibrary("spendsense/config/partner_offers.yaml")
        offers = library.get_by_persona("high_utilization")
        eligible = library.get_eligible_offers("high_utilization", user_data)
    """

    def __init__(self, config_path: str):
        """
        Initialize partner offer library from YAML file.

        Args:
            config_path: Path to partner offers YAML file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If YAML is invalid or offers are malformed
        """
        self.config_path = Path(config_path)
        self.offers: Dict[str, List[PartnerOffer]] = {}
        self._offer_index: Dict[str, PartnerOffer] = {}

        self._load_from_yaml()
        logger.info(
            f"Loaded {len(self._offer_index)} partner offers "
            f"for {len(self.offers)} personas"
        )

    def _load_from_yaml(self) -> None:
        """
        Load partner offers from YAML file (PRD flat structure).

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If YAML is invalid or offers are malformed
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Partner offers file not found: {self.config_path}")

        try:
            with open(self.config_path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {self.config_path}: {e}")

        # PRD structure: flat list under 'partner_offers'
        if not data or "partner_offers" not in data:
            raise ValueError("YAML must contain 'partner_offers' root key")

        offers_data = data["partner_offers"]
        if not isinstance(offers_data, list):
            raise ValueError("'partner_offers' must be a list")

        # Load all offers from flat list
        for offer_data in offers_data:
            try:
                offer = PartnerOffer(**offer_data)

                # Add to global index for ID lookup
                if offer.id in self._offer_index:
                    logger.warning(
                        f"Duplicate offer ID '{offer.id}' found (keeping first occurrence)"
                    )
                else:
                    self._offer_index[offer.id] = offer

                # Add to each persona it applies to (PRD AC4: multi-persona support)
                for persona_id in offer.personas:
                    if persona_id not in self.offers:
                        self.offers[persona_id] = []
                    self.offers[persona_id].append(offer)

            except ValidationError as e:
                logger.error(f"Invalid partner offer: {e}")
                raise ValueError(
                    f"Invalid partner offer: {offer_data.get('id', 'unknown')}"
                ) from e

        # Sort each persona's offers by priority (1=highest)
        for persona_id in self.offers:
            self.offers[persona_id].sort(key=lambda o: o.priority)

        # Validate all expected personas are present
        self._validate_persona_coverage()

    def _validate_persona_coverage(self) -> None:
        """
        Validate that all expected personas have offers (PRD AC5, AC6).

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

        missing_personas = expected_personas - set(self.offers.keys())
        if missing_personas:
            logger.warning(f"Missing partner offers for personas: {missing_personas}")

        extra_personas = set(self.offers.keys()) - expected_personas
        if extra_personas:
            logger.info(f"Found additional personas: {extra_personas}")

    def get_by_persona(self, persona_id: str) -> List[PartnerOffer]:
        """
        Get all partner offers for a persona, sorted by priority.

        Args:
            persona_id: Persona identifier (e.g., "high_utilization")

        Returns:
            List of partner offers sorted by priority (1=highest)
            Empty list if persona not found

        Example:
            >>> library = PartnerOfferLibrary("config/partner_offers.yaml")
            >>> offers = library.get_by_persona("high_utilization")
            >>> print(offers[0].title)
        """
        if persona_id not in self.offers:
            logger.warning(f"No partner offers found for persona: {persona_id}")
            return []

        return self.offers[persona_id]

    def get_by_id(self, offer_id: str) -> Optional[PartnerOffer]:
        """
        Get a specific partner offer by ID.

        Args:
            offer_id: Unique offer identifier

        Returns:
            PartnerOffer if found, None otherwise

        Example:
            >>> library = PartnerOfferLibrary("config/partner_offers.yaml")
            >>> offer = library.get_by_id("balance_transfer_chase_slate")
            >>> print(offer.title)
        """
        offer = self._offer_index.get(offer_id)
        if not offer:
            logger.debug(f"Partner offer not found: {offer_id}")
        return offer

    def get_by_type(self, offer_type: str) -> List[PartnerOffer]:
        """
        Get all partner offers of a specific type (PRD AC2).

        Args:
            offer_type: Type of offer (savings_account/credit_card/app/tool)

        Returns:
            List of offers of this type, sorted by priority

        Example:
            >>> library = PartnerOfferLibrary("config/partner_offers.yaml")
            >>> credit_cards = library.get_by_type("credit_card")
            >>> print([o.title for o in credit_cards])
        """
        matching_offers = [
            offer for offer in self._offer_index.values()
            if offer.type.value == offer_type
        ]
        matching_offers.sort(key=lambda o: o.priority)
        return matching_offers

    def check_eligibility(self, offer: PartnerOffer, user_data: dict) -> tuple[bool, List[str]]:
        """
        Check if user meets eligibility criteria for an offer (PRD AC3).

        Args:
            offer: PartnerOffer to check eligibility for
            user_data: User data dict with keys:
                - annual_income: int (annual income in dollars)
                - credit_score: int (300-850)
                - existing_accounts: List[str] (account types user has)
                - credit_utilization: int (0-100 percentage)
                - age: int (user age)
                - is_employed: bool (employment status)

        Returns:
            Tuple of (is_eligible: bool, reasons: List[str])
            reasons contains human-readable explanations for ineligibility

        Example:
            >>> library = PartnerOfferLibrary("config/partner_offers.yaml")
            >>> offer = library.get_by_id("balance_transfer_chase_slate")
            >>> user = {"annual_income": 50000, "credit_score": 700, "existing_accounts": []}
            >>> eligible, reasons = library.check_eligibility(offer, user)
            >>> print(f"Eligible: {eligible}")
        """
        ineligibility_reasons = []

        # Check minimum income requirement
        if offer.eligibility.min_income is not None:
            user_income = user_data.get("annual_income", 0)
            if user_income < offer.eligibility.min_income:
                ineligibility_reasons.append(
                    f"Minimum income requirement not met (requires ${offer.eligibility.min_income:,}, have ${user_income:,})"
                )

        # Check minimum credit score requirement
        if offer.eligibility.min_credit_score is not None:
            user_credit_score = user_data.get("credit_score", 0)
            if user_credit_score < offer.eligibility.min_credit_score:
                ineligibility_reasons.append(
                    f"Minimum credit score not met (requires {offer.eligibility.min_credit_score}, have {user_credit_score})"
                )

        # Check excluded accounts
        if offer.eligibility.excluded_accounts:
            user_accounts = user_data.get("existing_accounts", [])
            excluded_matches = set(offer.eligibility.excluded_accounts) & set(user_accounts)
            if excluded_matches:
                ineligibility_reasons.append(
                    f"User has excluded account types: {', '.join(excluded_matches)}"
                )

        # Check maximum credit utilization
        if offer.eligibility.max_credit_utilization is not None:
            user_utilization = user_data.get("credit_utilization", 0)
            if user_utilization > offer.eligibility.max_credit_utilization:
                ineligibility_reasons.append(
                    f"Credit utilization too high (max {offer.eligibility.max_credit_utilization}%, have {user_utilization}%)"
                )

        # Check minimum age
        if offer.eligibility.min_age is not None:
            user_age = user_data.get("age", 0)
            if user_age < offer.eligibility.min_age:
                ineligibility_reasons.append(
                    f"Minimum age requirement not met (requires {offer.eligibility.min_age}, have {user_age})"
                )

        # Check employment requirement
        if offer.eligibility.employment_required:
            is_employed = user_data.get("is_employed", False)
            if not is_employed:
                ineligibility_reasons.append("Employment required but user is not employed")

        is_eligible = len(ineligibility_reasons) == 0
        return is_eligible, ineligibility_reasons

    def get_eligible_offers(self, persona_id: str, user_data: dict, limit: Optional[int] = None) -> List[PartnerOffer]:
        """
        Get eligible partner offers for a persona based on user data.

        Args:
            persona_id: Persona identifier
            user_data: User data dict (see check_eligibility for required fields)
            limit: Optional maximum number of offers to return

        Returns:
            List of eligible offers sorted by priority

        Example:
            >>> library = PartnerOfferLibrary("config/partner_offers.yaml")
            >>> user = {"annual_income": 50000, "credit_score": 700, "existing_accounts": [], "age": 30}
            >>> offers = library.get_eligible_offers("high_utilization", user, limit=3)
            >>> print([o.title for o in offers])
        """
        all_offers = self.get_by_persona(persona_id)
        eligible_offers = []

        for offer in all_offers:
            is_eligible, _ = self.check_eligibility(offer, user_data)
            if is_eligible:
                eligible_offers.append(offer)
                if limit and len(eligible_offers) >= limit:
                    break

        return eligible_offers

    def get_all_personas(self) -> List[str]:
        """
        Get list of all personas with partner offers.

        Returns:
            List of persona IDs

        Example:
            >>> library = PartnerOfferLibrary("config/partner_offers.yaml")
            >>> personas = library.get_all_personas()
            >>> print(personas)
        """
        return list(self.offers.keys())

    def get_offer_count(self, persona_id: Optional[str] = None) -> int:
        """
        Get count of partner offers.

        Args:
            persona_id: Optional persona ID to count for specific persona

        Returns:
            Total count (if persona_id is None) or count for specific persona

        Example:
            >>> library = PartnerOfferLibrary("config/partner_offers.yaml")
            >>> total = library.get_offer_count()
            >>> high_util_count = library.get_offer_count("high_utilization")
        """
        if persona_id is None:
            return len(self._offer_index)

        if persona_id not in self.offers:
            return 0

        return len(self.offers[persona_id])

    def get_high_priority(self, persona_id: str, limit: int = 3) -> List[PartnerOffer]:
        """
        Get top priority partner offers for a persona.

        Args:
            persona_id: Persona identifier
            limit: Maximum number of offers to return (default 3 per PRD)

        Returns:
            Top N offers sorted by priority

        Example:
            >>> library = PartnerOfferLibrary("config/partner_offers.yaml")
            >>> top_3 = library.get_high_priority("high_utilization", limit=3)
        """
        all_offers = self.get_by_persona(persona_id)
        return all_offers[:limit]

    def __repr__(self) -> str:
        """String representation for debugging."""
        persona_counts = {p: len(offers) for p, offers in self.offers.items()}
        return f"PartnerOfferLibrary({len(self._offer_index)} total, personas={persona_counts})"


# Singleton instance for easy access
_library_instance: Optional[PartnerOfferLibrary] = None


def get_partner_offer_library(config_path: Optional[str] = None) -> PartnerOfferLibrary:
    """
    Get singleton PartnerOfferLibrary instance (PRD AC10).

    Args:
        config_path: Optional path to partner offers YAML file
                    If None, uses default path

    Returns:
        PartnerOfferLibrary instance

    Example:
        >>> from spendsense.recommendations import get_partner_offer_library
        >>> library = get_partner_offer_library()
        >>> offers = library.get_by_persona("high_utilization")
    """
    global _library_instance

    if _library_instance is None:
        if config_path is None:
            # Default path
            config_path = str(
                Path(__file__).parent.parent / "config" / "partner_offers.yaml"
            )
        _library_instance = PartnerOfferLibrary(config_path)

    return _library_instance
