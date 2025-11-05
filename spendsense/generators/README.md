# Synthetic User Profile Generator

Generates realistic synthetic user profiles with persona-based financial characteristics for testing the SpendSense recommendation engine.

## Overview

The profile generator creates 50-100 diverse user profiles, each assigned to one of 5 personas representing distinct financial behavioral patterns. Profiles include:

- **Identity**: Masked user IDs and realistic names (via Faker)
- **Financial Characteristics**: Income, credit utilization targets, savings goals, subscription counts
- **Account Structure**: Checking, savings, and credit card accounts based on persona
- **Persona Assignment**: Deterministic 20% distribution across 5 archetypes

## Personas

### 1. High Utilization
**Target Signal**: Credit utilization 60-80%

- **Income**: $40K-$80K (moderate)
- **Credit Limits**: $8K-$20K (high)
- **Savings**: Minimal ($0-$100/month)
- **Accounts**: 1 checking, 1-2 credit cards
- **Use Case**: Test debt management recommendations

### 2. Variable Income
**Target Signal**: >45 day median pay gap

- **Income**: $20K-$120K (wide range, irregular)
- **Credit Limits**: $3K-$10K (moderate)
- **Savings**: Limited ($0-$150/month)
- **Accounts**: 1 checking, 0-1 credit cards
- **Use Case**: Test budgeting for irregular income

### 3. Subscription-Heavy
**Target Signal**: ≥5 recurring merchants

- **Income**: $50K-$120K (moderate-good)
- **Credit Limits**: $5K-$15K
- **Savings**: Moderate ($100-$300/month)
- **Subscriptions**: 5-10 recurring
- **Accounts**: 1 checking, 1 savings, 1-2 credit cards
- **Use Case**: Test subscription optimization

### 4. Savings Builder
**Target Signal**: >$200/month savings

- **Income**: $60K-$200K (good-high)
- **Credit Limits**: $10K-$30K (low utilization 5-30%)
- **Savings**: Strong ($200-$1000/month)
- **Accounts**: 1 checking, 1 savings (high balance), 1-2 credit cards
- **Use Case**: Test investment and optimization

### 5. Control/Mixed
**Baseline for comparison**

- **Income**: $30K-$150K (wide range)
- **Credit**: Moderate usage (20-50%)
- **Savings**: Moderate ($50-$300/month)
- **Accounts**: Variable structure
- **Use Case**: Baseline/average user behavior

## Usage

### Command Line

```bash
# Generate 100 profiles with default settings
python -m spendsense.generators.cli

# Generate 75 profiles with custom seed
python -m spendsense.generators.cli --num-users 75 --seed 999

# Specify output path
python -m spendsense.generators.cli --output custom/path/profiles.json

# Verbose mode
python -m spendsense.generators.cli --verbose
```

### Python API

```python
from spendsense.generators import generate_synthetic_profiles

# Quick generation
profiles, validation = generate_synthetic_profiles(
    num_users=100,
    seed=42,
    output_path="data/synthetic/users/profiles.json"
)

print(f"Generated {len(profiles)} profiles")
print(f"Validation passed: {validation['valid']}")
```

### Advanced Usage

```python
from spendsense.generators import ProfileGenerator

# Create generator
gen = ProfileGenerator(seed=42, num_users=100)

# Generate profiles
profiles = gen.generate_all_profiles()

# Validate distribution
validation = gen.validate_distribution(profiles)
assert validation["valid"]

# Save profiles
gen.save_profiles(profiles, "output.json")

# Load profiles later
loaded = ProfileGenerator.load_profiles("output.json")
```

## Output Format

### Profile JSON Schema

```json
{
  "user_id": "user_MASKED_001",
  "name": "John Doe",
  "persona": "high_utilization",
  "annual_income": 65000.0,
  "characteristics": {
    "target_credit_utilization": 0.70,
    "target_savings_monthly": 50.0,
    "income_stability": "regular",
    "subscription_count_target": 3,
    "median_pay_gap_days": null
  },
  "accounts": [
    {
      "type": "depository",
      "subtype": "checking",
      "initial_balance": 2708.33
    },
    {
      "type": "credit",
      "subtype": "credit card",
      "initial_balance": 0.0,
      "limit": 15000.0
    }
  ]
}
```

### Account Types

- **type**: `depository`, `credit`, `loan` (from AccountType enum)
- **subtype**: `checking`, `savings`, `cd`, `money market`, `credit card`, `mortgage`, `student`, `personal` (from AccountSubtype enum)

### Characteristics Fields

| Field | Type | Description |
|-------|------|-------------|
| `target_credit_utilization` | float | Target credit utilization ratio (0.0-1.0) |
| `target_savings_monthly` | float | Monthly savings target in dollars |
| `income_stability` | string | `regular`, `irregular`, or `highly_irregular` |
| `subscription_count_target` | int | Number of recurring subscriptions |
| `median_pay_gap_days` | int or null | Median days between paychecks (Variable Income only) |

## Validation

The generator validates:

1. **Persona Distribution**: Each persona gets exactly 20% of users (±1% tolerance)
2. **Income Range**: Covers $20K-$200K range (with statistical tolerance)
3. **Persona Characteristics**: Each profile matches its persona's behavioral rules

Example validation output:

```python
{
  "valid": True,
  "persona_distribution": {
    "high_utilization": 20,
    "variable_income": 20,
    "subscription_heavy": 20,
    "savings_builder": 20,
    "control": 20
  },
  "persona_percentages": {
    "high_utilization": 20.0,
    "variable_income": 20.0,
    # ...
  },
  "income_range": (22000.0, 127000.0),
  "errors": []
}
```

## Reproducibility

Generation is fully deterministic with the same seed:

```python
# Same seed = identical profiles
gen1 = ProfileGenerator(seed=42)
gen2 = ProfileGenerator(seed=42)

profiles1 = gen1.generate_all_profiles()
profiles2 = gen2.generate_all_profiles()

assert profiles1[0].annual_income == profiles2[0].annual_income
assert profiles1[0].name == profiles2[0].name
```

## Integration with Story 1.2

Profiles use schemas from Story 1.2 (Synthetic Data Schema Definition):

- **AccountType, AccountSubtype enums**: spendsense/db/models.py
- **Validation**: spendsense/db/validators.py:validate_account()
- **Decimal precision**: All financial amounts use Decimal type

## File Locations

```
spendsense/
├── generators/
│   ├── profile_generator.py  # Main generator
│   ├── cli.py                # Command-line interface
│   └── README.md             # This file
├── personas/
│   └── definitions.py        # Persona definitions
└── db/
    ├── models.py             # Pydantic schemas (Story 1.2)
    └── validators.py         # Validation utilities (Story 1.2)

tests/
└── test_profile_generator.py # 58 tests

data/synthetic/users/
└── profiles.json             # Generated profiles
```

## Testing

Run the comprehensive test suite:

```bash
# All tests (58 tests)
pytest tests/test_profile_generator.py -v

# Specific test categories
pytest tests/test_profile_generator.py::TestPersonaAssignment -v
pytest tests/test_profile_generator.py::TestFinancialCharacteristics -v
pytest tests/test_profile_generator.py::TestAccountStructure -v
pytest tests/test_profile_generator.py::TestEndToEndGeneration -v
```

## Next Steps

Generated profiles will be consumed by:

- **Story 1.4**: Synthetic Transaction Data Generator
- **Story 2.x**: Behavioral Signal Detection Pipeline
- **Story 3.x**: Persona Assignment System

The persona-driven approach ensures transaction patterns will trigger expected behavioral signals for recommendation engine testing.
