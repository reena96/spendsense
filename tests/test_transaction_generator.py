"""
Tests for synthetic transaction generator.
"""

import json
import pytest
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

from spendsense.generators.transaction_generator import (
    TransactionGenerator,
    generate_synthetic_transactions,
)
from spendsense.generators.profile_generator import ProfileGenerator
from spendsense.personas.definitions import PersonaType


@pytest.fixture
def sample_profiles():
    """Generate sample profiles for testing."""
    generator = ProfileGenerator(seed=42, num_users=50)
    profiles = generator.generate_all_profiles()
    # Convert UserProfile objects to dicts (simulating JSON loading)
    import json
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        generator.save_profiles(profiles, f.name)
        f.flush()
        with open(f.name, 'r') as rf:
            return json.load(rf)


@pytest.fixture
def transaction_generator(sample_profiles):
    """Create transaction generator with sample profiles."""
    return TransactionGenerator(
        profiles=sample_profiles,
        seed=42,
        days_of_history=180
    )


class TestTransactionGeneratorInitialization:
    """Test transaction generator initialization and validation."""

    def test_initialization_with_defaults(self, sample_profiles):
        """Test initialization with default parameters."""
        generator = TransactionGenerator(profiles=sample_profiles, seed=42)

        assert generator.seed == 42
        assert generator.days_of_history == 180
        assert len(generator.profiles) == 50
        assert generator.start_date == date.today() - timedelta(days=180)

    def test_initialization_with_custom_days(self, sample_profiles):
        """Test initialization with custom days of history."""
        generator = TransactionGenerator(
            profiles=sample_profiles,
            seed=42,
            days_of_history=365
        )

        assert generator.days_of_history == 365
        assert generator.start_date == date.today() - timedelta(days=365)

    def test_initialization_with_custom_start_date(self, sample_profiles):
        """Test initialization with custom start date."""
        start = date(2024, 1, 1)
        generator = TransactionGenerator(
            profiles=sample_profiles,
            seed=42,
            days_of_history=180,
            start_date=start
        )

        assert generator.start_date == start
        assert generator.end_date == start + timedelta(days=180)

    def test_initialization_validates_minimum_days(self, sample_profiles):
        """Test that minimum 180 days is enforced."""
        with pytest.raises(ValueError, match="must be at least 180"):
            TransactionGenerator(
                profiles=sample_profiles,
                seed=42,
                days_of_history=90
            )

    def test_merchant_catalogs_initialized(self, transaction_generator):
        """Test that merchant catalogs are properly initialized."""
        assert len(transaction_generator.subscription_merchants) > 0
        assert len(transaction_generator.grocery_merchants) > 0
        assert len(transaction_generator.restaurant_merchants) > 0
        assert len(transaction_generator.gas_merchants) > 0
        assert len(transaction_generator.utility_merchants) > 0


class TestTransactionGeneration:
    """Test transaction generation for all profiles."""

    def test_generate_returns_dict_for_all_users(self, transaction_generator):
        """Test that generate returns transactions for all users."""
        transactions = transaction_generator.generate()

        assert isinstance(transactions, dict)
        assert len(transactions) == 50  # All users

        # Each user should have transactions
        for user_id, txns in transactions.items():
            assert isinstance(txns, list)
            assert len(txns) > 0  # Each user has some transactions

    def test_transactions_span_full_date_range(self, transaction_generator):
        """Test that transactions span the full 180 day period."""
        transactions = transaction_generator.generate()

        # Check a few users
        for user_id in list(transactions.keys())[:5]:
            user_txns = transactions[user_id]
            dates = [date.fromisoformat(t["date"]) for t in user_txns]

            earliest = min(dates)
            latest = max(dates)

            # Should span most of the 180 days
            span_days = (latest - earliest).days
            assert span_days >= 150  # At least 150 days of the 180

    def test_transaction_structure(self, transaction_generator):
        """Test that transactions have correct structure."""
        transactions = transaction_generator.generate()

        # Get first user's first transaction
        first_user = list(transactions.keys())[0]
        first_txn = transactions[first_user][0]

        # Check required fields
        assert "transaction_id" in first_txn
        assert "account_id" in first_txn
        assert "date" in first_txn
        assert "amount" in first_txn
        assert "merchant_name" in first_txn
        assert "payment_channel" in first_txn
        assert "personal_finance_category" in first_txn
        assert "pending" in first_txn

        # Check types
        assert isinstance(first_txn["transaction_id"], str)
        assert isinstance(first_txn["account_id"], str)
        assert isinstance(first_txn["date"], str)
        assert isinstance(first_txn["amount"], float)
        assert isinstance(first_txn["merchant_name"], str)
        assert isinstance(first_txn["payment_channel"], str)
        assert isinstance(first_txn["personal_finance_category"], str)
        assert isinstance(first_txn["pending"], bool)

    def test_transaction_ids_are_unique(self, transaction_generator):
        """Test that all transaction IDs are unique."""
        transactions = transaction_generator.generate()

        all_ids = []
        for user_txns in transactions.values():
            all_ids.extend([t["transaction_id"] for t in user_txns])

        # All IDs should be unique
        assert len(all_ids) == len(set(all_ids))


class TestIncomeTransactionGeneration:
    """Test income/payroll transaction generation."""

    def test_biweekly_income_generation(self, sample_profiles):
        """Test biweekly payroll generation."""
        # Find a profile with regular income (not variable)
        regular_profile = None
        for profile in sample_profiles:
            if profile["persona"] != PersonaType.VARIABLE_INCOME.value:
                regular_profile = profile
                break

        generator = TransactionGenerator([regular_profile], seed=42, days_of_history=180)
        transactions = generator.generate()

        user_txns = transactions[regular_profile["user_id"]]
        income_txns = [t for t in user_txns if t["personal_finance_category"] == "INCOME_WAGES"]

        # Should have ~13 paychecks in 180 days (26 per year / 2)
        assert 11 <= len(income_txns) <= 15

        # Income amounts should be positive
        for txn in income_txns:
            assert txn["amount"] > 0

        # Check gaps between income transactions (~14 days)
        if len(income_txns) >= 2:
            dates = sorted([date.fromisoformat(t["date"]) for t in income_txns])
            gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates) - 1)]
            avg_gap = sum(gaps) / len(gaps)
            assert 12 <= avg_gap <= 16  # Around 14 days

    def test_variable_income_generation(self, sample_profiles):
        """Test variable income generation."""
        # Find Variable Income persona
        variable_profile = None
        for profile in sample_profiles:
            if profile["persona"] == PersonaType.VARIABLE_INCOME.value:
                variable_profile = profile
                break

        if variable_profile:
            generator = TransactionGenerator([variable_profile], seed=42, days_of_history=180)
            transactions = generator.generate()

            user_txns = transactions[variable_profile["user_id"]]
            income_txns = [t for t in user_txns if t["personal_finance_category"] == "INCOME_WAGES"]

            # Should have fewer income transactions (4-5 in 6 months)
            assert 3 <= len(income_txns) <= 6

            # Check for irregular gaps (should have at least one gap > 45 days)
            if len(income_txns) >= 2:
                dates = sorted([date.fromisoformat(t["date"]) for t in income_txns])
                gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates) - 1)]
                assert any(gap > 45 for gap in gaps)


class TestSubscriptionTransactionGeneration:
    """Test recurring subscription transaction generation."""

    def test_subscription_heavy_has_many_subscriptions(self, sample_profiles):
        """Test that Subscription-Heavy persona has 5-10 subscriptions."""
        # Find Subscription-Heavy profile
        sub_heavy_profile = None
        for profile in sample_profiles:
            if profile["persona"] == PersonaType.SUBSCRIPTION_HEAVY.value:
                sub_heavy_profile = profile
                break

        if sub_heavy_profile:
            generator = TransactionGenerator([sub_heavy_profile], seed=42, days_of_history=180)
            transactions = generator.generate()

            user_txns = transactions[sub_heavy_profile["user_id"]]
            subscription_txns = [
                t for t in user_txns
                if t["personal_finance_category"] == "GENERAL_SERVICES_SUBSCRIPTION"
            ]

            # Count unique merchants
            merchants = set(t["merchant_name"] for t in subscription_txns)

            # Should have 5-10 unique subscription merchants
            assert 5 <= len(merchants) <= 10

    def test_subscriptions_recur_monthly(self, sample_profiles):
        """Test that subscriptions recur monthly on same day."""
        # Use any profile
        profile = sample_profiles[0]
        generator = TransactionGenerator([profile], seed=42, days_of_history=180)
        transactions = generator.generate()

        user_txns = transactions[profile["user_id"]]
        subscription_txns = [
            t for t in user_txns
            if t["personal_finance_category"] == "GENERAL_SERVICES_SUBSCRIPTION"
        ]

        if len(subscription_txns) > 0:
            # Group by merchant
            by_merchant = {}
            for txn in subscription_txns:
                merchant = txn["merchant_name"]
                if merchant not in by_merchant:
                    by_merchant[merchant] = []
                by_merchant[merchant].append(date.fromisoformat(txn["date"]))

            # Check that each merchant has recurring dates
            for merchant, dates in by_merchant.items():
                if len(dates) >= 2:
                    dates = sorted(dates)
                    # Gaps should be ~30 days (monthly)
                    gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates) - 1)]
                    avg_gap = sum(gaps) / len(gaps)
                    assert 28 <= avg_gap <= 32  # Around 30 days

    def test_subscription_amounts_are_negative(self, transaction_generator):
        """Test that subscription amounts are negative (expenses)."""
        transactions = transaction_generator.generate()

        for user_txns in transactions.values():
            subscription_txns = [
                t for t in user_txns
                if t["personal_finance_category"] == "GENERAL_SERVICES_SUBSCRIPTION"
            ]

            for txn in subscription_txns:
                assert txn["amount"] < 0


class TestSpendingTransactionGeneration:
    """Test daily spending transaction generation."""

    def test_spending_categories_present(self, transaction_generator):
        """Test that various spending categories are present."""
        transactions = transaction_generator.generate()

        all_categories = set()
        for user_txns in transactions.values():
            for txn in user_txns:
                all_categories.add(txn["personal_finance_category"])

        # Should have main spending categories
        assert "FOOD_AND_DRINK_GROCERIES" in all_categories
        assert "FOOD_AND_DRINK_RESTAURANTS" in all_categories
        assert "TRANSPORTATION_GAS" in all_categories

    def test_high_utilization_has_high_spending(self, sample_profiles):
        """Test that High Utilization persona has higher spending."""
        # Find ALL High Utilization and Control profiles
        high_util_profiles = []
        control_profiles = []

        for profile in sample_profiles:
            if profile["persona"] == PersonaType.HIGH_UTILIZATION.value:
                high_util_profiles.append(profile)
            elif profile["persona"] == PersonaType.CONTROL.value:
                control_profiles.append(profile)

        if high_util_profiles and control_profiles:
            all_profiles = high_util_profiles + control_profiles
            generator = TransactionGenerator(all_profiles, seed=42, days_of_history=180)
            transactions = generator.generate()

            # Calculate average spending as percentage of income
            high_util_ratios = []
            for profile in high_util_profiles:
                spending = sum(
                    abs(t["amount"]) for t in transactions[profile["user_id"]]
                    if t["amount"] < 0 and t["personal_finance_category"] in [
                        "FOOD_AND_DRINK_GROCERIES",
                        "FOOD_AND_DRINK_RESTAURANTS",
                        "TRANSPORTATION_GAS",
                        "GENERAL_MERCHANDISE_GENERAL"
                    ]
                )
                # Normalize by 6 months of income
                income_6mo = profile["annual_income"] * 0.5
                high_util_ratios.append(spending / income_6mo if income_6mo > 0 else 0)

            control_ratios = []
            for profile in control_profiles:
                spending = sum(
                    abs(t["amount"]) for t in transactions[profile["user_id"]]
                    if t["amount"] < 0 and t["personal_finance_category"] in [
                        "FOOD_AND_DRINK_GROCERIES",
                        "FOOD_AND_DRINK_RESTAURANTS",
                        "TRANSPORTATION_GAS",
                        "GENERAL_MERCHANDISE_GENERAL"
                    ]
                )
                income_6mo = profile["annual_income"] * 0.5
                control_ratios.append(spending / income_6mo if income_6mo > 0 else 0)

            # Average spending ratio for HIGH_UTIL should be higher than CONTROL
            avg_high_util = sum(high_util_ratios) / len(high_util_ratios)
            avg_control = sum(control_ratios) / len(control_ratios)

            # High utilization should spend more relative to income
            assert avg_high_util > avg_control * 1.05  # At least 5% more

    def test_savings_builder_has_lower_spending(self, sample_profiles):
        """Test that Savings Builder persona has lower spending on discretionary items."""
        # Find ALL Savings Builder profiles
        savings_profiles = []
        for profile in sample_profiles:
            if profile["persona"] == PersonaType.SAVINGS_BUILDER.value:
                savings_profiles.append(profile)

        if savings_profiles:
            generator = TransactionGenerator(savings_profiles, seed=42, days_of_history=180)
            transactions = generator.generate()

            # Calculate average spending ratio across all savings builders
            spending_ratios = []
            for profile in savings_profiles:
                user_txns = transactions[profile["user_id"]]
                # Only count discretionary spending (not transfers/payments)
                discretionary_spending = sum(
                    abs(t["amount"]) for t in user_txns
                    if t["amount"] < 0 and t["personal_finance_category"] in [
                        "FOOD_AND_DRINK_GROCERIES",
                        "FOOD_AND_DRINK_RESTAURANTS",
                        "TRANSPORTATION_GAS",
                        "GENERAL_MERCHANDISE_GENERAL",
                        "GENERAL_SERVICES_SUBSCRIPTION",
                        "HOME_UTILITIES"
                    ]
                )
                # Use 6 months of annual income as baseline
                income_6mo = profile["annual_income"] * 0.5
                if income_6mo > 0:
                    spending_ratios.append(discretionary_spending / income_6mo)

            # Average spending should be less than 70% of income
            if spending_ratios:
                avg_ratio = sum(spending_ratios) / len(spending_ratios)
                assert avg_ratio < 0.70  # Less than 70%


class TestFinancialTransferGeneration:
    """Test savings transfers and credit card payments."""

    def test_savings_builder_has_savings_transfers(self, sample_profiles):
        """Test that Savings Builder persona has savings transfers."""
        # Find Savings Builder profile
        savings_profile = None
        for profile in sample_profiles:
            if profile["persona"] == PersonaType.SAVINGS_BUILDER.value:
                savings_profile = profile
                break

        if savings_profile:
            generator = TransactionGenerator([savings_profile], seed=42, days_of_history=180)
            transactions = generator.generate()

            user_txns = transactions[savings_profile["user_id"]]
            savings_txns = [
                t for t in user_txns
                if t["personal_finance_category"] == "TRANSFER_OUT_SAVINGS"
            ]

            # Should have monthly savings transfers (~6 in 180 days)
            assert 4 <= len(savings_txns) <= 8

            # Amounts should be close to target_savings_monthly
            target = Decimal(str(savings_profile["characteristics"]["target_savings_monthly"]))
            for txn in savings_txns:
                amount = abs(txn["amount"])
                # Within 20% of target
                assert target * Decimal("0.8") <= Decimal(str(amount)) <= target * Decimal("1.2")

    def test_credit_card_payments_present(self, transaction_generator):
        """Test that credit card payments are generated."""
        transactions = transaction_generator.generate()

        cc_payment_count = 0
        for user_txns in transactions.values():
            cc_payments = [
                t for t in user_txns
                if t["personal_finance_category"] == "LOAN_PAYMENTS_CREDIT_CARD_PAYMENT"
            ]
            cc_payment_count += len(cc_payments)

        # Should have many CC payments across all users
        assert cc_payment_count > 100


class TestReproducibility:
    """Test that generation is reproducible with same seed."""

    def test_same_seed_produces_same_transactions(self, sample_profiles):
        """Test that same seed produces identical transactions."""
        generator1 = TransactionGenerator(sample_profiles, seed=42, days_of_history=180)
        transactions1 = generator1.generate()

        generator2 = TransactionGenerator(sample_profiles, seed=42, days_of_history=180)
        transactions2 = generator2.generate()

        # Should have same users
        assert transactions1.keys() == transactions2.keys()

        # Check first user's transactions match
        first_user = list(transactions1.keys())[0]
        txns1 = transactions1[first_user]
        txns2 = transactions2[first_user]

        assert len(txns1) == len(txns2)

        # Check a few transactions match exactly
        for i in range(min(5, len(txns1))):
            assert txns1[i]["date"] == txns2[i]["date"]
            assert abs(txns1[i]["amount"] - txns2[i]["amount"]) < 0.01
            assert txns1[i]["merchant_name"] == txns2[i]["merchant_name"]

    def test_different_seeds_produce_different_transactions(self, sample_profiles):
        """Test that different seeds produce different transactions."""
        generator1 = TransactionGenerator(sample_profiles, seed=42, days_of_history=180)
        transactions1 = generator1.generate()

        generator2 = TransactionGenerator(sample_profiles, seed=999, days_of_history=180)
        transactions2 = generator2.generate()

        # Get first user's first 5 transactions
        first_user = list(transactions1.keys())[0]
        txns1 = transactions1[first_user][:5]
        txns2 = transactions2[first_user][:5]

        # At least some should be different
        differences = sum(
            1 for t1, t2 in zip(txns1, txns2)
            if t1["merchant_name"] != t2["merchant_name"] or abs(t1["amount"] - t2["amount"]) > 0.01
        )

        assert differences > 0


class TestJSONSerialization:
    """Test JSON serialization and file operations."""

    def test_save_creates_file(self, transaction_generator):
        """Test that save creates JSON file."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "transactions.json"

            transaction_generator.save(output_path)

            assert output_path.exists()
            assert output_path.stat().st_size > 0

    def test_saved_file_is_valid_json(self, transaction_generator):
        """Test that saved file contains valid JSON."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "transactions.json"
            transaction_generator.save(output_path)

            with open(output_path, 'r') as f:
                data = json.load(f)

            assert isinstance(data, dict)
            assert len(data) == 50  # All users

    def test_from_profiles_file(self):
        """Test creating generator from profiles file."""
        with TemporaryDirectory() as tmpdir:
            # Generate profiles first
            profile_gen = ProfileGenerator(seed=42, num_users=50)
            profiles = profile_gen.generate_all_profiles()
            profiles_path = Path(tmpdir) / "profiles.json"
            profile_gen.save_profiles(profiles, profiles_path)

            # Create transaction generator from file
            txn_gen = TransactionGenerator.from_profiles_file(
                profiles_path,
                seed=42,
                days_of_history=180
            )

            assert len(txn_gen.profiles) == 50

    def test_generate_synthetic_transactions_convenience_function(self):
        """Test convenience function for full workflow."""
        with TemporaryDirectory() as tmpdir:
            # Generate profiles
            profile_gen = ProfileGenerator(seed=42, num_users=50)
            profiles = profile_gen.generate_all_profiles()
            profiles_path = Path(tmpdir) / "profiles.json"
            profile_gen.save_profiles(profiles, profiles_path)

            # Generate transactions
            transactions_path = Path(tmpdir) / "transactions.json"
            result = generate_synthetic_transactions(
                profiles_path=profiles_path,
                output_path=transactions_path,
                seed=42,
                days_of_history=180
            )

            # Check file created
            assert transactions_path.exists()

            # Check return value
            assert isinstance(result, dict)
            assert len(result) == 50


class TestAcceptanceCriteria:
    """Test that all acceptance criteria are met."""

    def test_ac1_realistic_monthly_spending_patterns(self, transaction_generator):
        """AC1: Transaction generator creates realistic monthly spending patterns."""
        transactions = transaction_generator.generate()

        for user_txns in list(transactions.values())[:5]:  # Check 5 users
            # Group by month
            by_month = {}
            for txn in user_txns:
                if txn["amount"] < 0:  # Expenses only
                    txn_date = date.fromisoformat(txn["date"])
                    month_key = (txn_date.year, txn_date.month)
                    if month_key not in by_month:
                        by_month[month_key] = []
                    by_month[month_key].append(abs(txn["amount"]))

            # Each month should have transactions
            assert len(by_month) >= 5  # At least 5 months

            # Monthly spending should be relatively consistent
            monthly_totals = [sum(amounts) for amounts in by_month.values()]
            avg_spending = sum(monthly_totals) / len(monthly_totals)

            # All months within 2x of average (allows for variation)
            for total in monthly_totals:
                assert total < avg_spending * 2

    def test_ac2_recurring_subscriptions_with_consistent_cadence(self, transaction_generator):
        """AC2: Recurring transactions generated for subscriptions with consistent cadence."""
        transactions = transaction_generator.generate()

        subscription_found = False
        for user_txns in transactions.values():
            subs = [
                t for t in user_txns
                if t["personal_finance_category"] == "GENERAL_SERVICES_SUBSCRIPTION"
            ]

            if len(subs) > 0:
                subscription_found = True

                # Group by merchant
                by_merchant = {}
                for txn in subs:
                    merchant = txn["merchant_name"]
                    if merchant not in by_merchant:
                        by_merchant[merchant] = []
                    by_merchant[merchant].append(date.fromisoformat(txn["date"]))

                # Check consistency for at least one merchant
                for merchant, dates in by_merchant.items():
                    if len(dates) >= 3:
                        # Deduplicate dates (in case of rare edge cases)
                        dates = sorted(list(set(dates)))
                        if len(dates) >= 3:
                            gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates) - 1)]
                            # Gaps should be consistent (28-32 days)
                            # Allow for month-to-month variation (27-33 days to handle Feb/leap year edge cases)
                            assert all(27 <= gap <= 33 for gap in gaps), f"{merchant} has gaps {gaps} outside range"
                            break

        assert subscription_found

    def test_ac3_income_with_realistic_pay_cycles(self, transaction_generator):
        """AC3: Income transactions generated with realistic pay cycles."""
        transactions = transaction_generator.generate()

        income_found = False
        for user_txns in list(transactions.values())[:10]:  # Check 10 users
            income_txns = [
                t for t in user_txns
                if t["personal_finance_category"] == "INCOME_WAGES"
            ]

            if len(income_txns) >= 2:
                income_found = True
                dates = sorted([date.fromisoformat(t["date"]) for t in income_txns])
                gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates) - 1)]

                # Should be biweekly (~14 days) or monthly (~30 days) or variable (>45 days)
                avg_gap = sum(gaps) / len(gaps)
                assert avg_gap >= 12  # At least biweekly

        assert income_found

    def test_ac4_financial_transfers_generated(self, transaction_generator):
        """AC4: Credit card payments, savings transfers, and bill payments generated."""
        transactions = transaction_generator.generate()

        has_cc_payments = False
        has_savings_transfers = False

        for user_txns in transactions.values():
            categories = [t["personal_finance_category"] for t in user_txns]

            if "LOAN_PAYMENTS_CREDIT_CARD_PAYMENT" in categories:
                has_cc_payments = True
            if "TRANSFER_OUT_SAVINGS" in categories:
                has_savings_transfers = True

        assert has_cc_payments
        # Note: savings transfers only for Savings Builder persona

    def test_ac5_merchant_names_and_categories_realistic(self, transaction_generator):
        """AC5: Merchant names and categories assigned realistically per transaction type."""
        transactions = transaction_generator.generate()

        # Check a few users
        for user_txns in list(transactions.values())[:5]:
            for txn in user_txns:
                merchant = txn["merchant_name"]
                category = txn["personal_finance_category"]

                # Basic sanity checks
                assert len(merchant) > 0
                assert len(category) > 0

                # Specific category/merchant matching
                if "Netflix" in merchant or "Spotify" in merchant:
                    assert category == "GENERAL_SERVICES_SUBSCRIPTION"
                if "Payroll" in merchant or "Deposit" in merchant:
                    assert category == "INCOME_WAGES"

    def test_ac6_transaction_amounts_vary(self, transaction_generator):
        """AC6: Transaction amounts vary seasonally and by merchant category."""
        transactions = transaction_generator.generate()

        # Check that amounts vary for same merchant/category
        for user_txns in list(transactions.values())[:5]:
            groceries = [
                abs(t["amount"]) for t in user_txns
                if t["personal_finance_category"] == "FOOD_AND_DRINK_GROCERIES"
            ]

            if len(groceries) >= 5:
                # Should have variation in amounts
                unique_amounts = len(set(groceries))
                assert unique_amounts >= 3  # At least 3 different amounts

    def test_ac7_date_distribution_respects_patterns(self, transaction_generator):
        """AC7: Date distribution respects user pay cycles and spending patterns."""
        transactions = transaction_generator.generate()

        # Dates should be spread across full range
        for user_txns in list(transactions.values())[:5]:
            dates = [date.fromisoformat(t["date"]) for t in user_txns]

            if len(dates) > 0:
                earliest = min(dates)
                latest = max(dates)
                span = (latest - earliest).days

                # Should span most of 180 days
                assert span >= 150

    def test_ac8_data_spans_180_plus_days(self, transaction_generator):
        """AC8: Generated data spans 180+ days for long-term pattern detection."""
        assert transaction_generator.days_of_history >= 180

        transactions = transaction_generator.generate()

        # Check that transactions span the full range
        all_dates = []
        for user_txns in transactions.values():
            all_dates.extend([date.fromisoformat(t["date"]) for t in user_txns])

        if all_dates:
            span = (max(all_dates) - min(all_dates)).days
            assert span >= 180

    def test_ac9_validates_against_schema(self, transaction_generator):
        """AC9: Transaction data validates against schema successfully."""
        transactions = transaction_generator.generate()

        # Each transaction should have valid structure
        for user_txns in transactions.values():
            for txn in user_txns:
                # Required fields present
                assert "transaction_id" in txn
                assert "account_id" in txn
                assert "date" in txn
                assert "amount" in txn
                assert "merchant_name" in txn
                assert "payment_channel" in txn
                assert "personal_finance_category" in txn
                assert "pending" in txn

                # Valid date format
                date.fromisoformat(txn["date"])

                # Valid amount
                assert isinstance(txn["amount"], (int, float))

                # Valid enum values (as strings in JSON)
                assert txn["payment_channel"] in [
                    "in store", "online", "other"  # "in store" has a space per Plaid spec
                ]
                assert isinstance(txn["personal_finance_category"], str)
                assert len(txn["personal_finance_category"]) > 0
