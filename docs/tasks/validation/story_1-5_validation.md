# Story 1.5 Validation - Synthetic Liability Data Generator

## Automated Checks ✅

- ✅ **Tests**: 15/15 passed in 0.14s
- ✅ **Output File**: liabilities.json created (45KB)
- ✅ **Schema Validation**: All generated data validates against Pydantic models
- ✅ **Reproducibility**: Seed-based generation confirmed working
- ✅ **API Integration**: `/api/liabilities/generate` endpoint working

## Manual Steps 🔍

**IMPORTANT:** Activate virtual environment first:
```bash
source venv/bin/activate
```

### 1. Verify Generated Data Quality

```bash
# Check liability data structure
python -c "
import json
with open('data/synthetic/liabilities/liabilities.json') as f:
    data = json.load(f)
print(f'Total users with liabilities: {len(data)}')
print(f'Sample user: {list(data.keys())[0]}')
print(json.dumps(data[list(data.keys())[0]], indent=2)[:500])
"
```

Verify:
- [ ] 100 users have liability data
- [ ] Credit cards have realistic balances and APRs
- [ ] Student loans show reasonable amounts and interest rates
- [ ] Mortgages have appropriate balances for persona income levels

### 2. Test CLI Tool

```bash
# Generate fresh data with CLI
python -m spendsense.generators.liability_cli \
  --profiles data/synthetic/users/profiles.json \
  --transactions data/synthetic/transactions/transactions.json \
  --output /tmp/test_liabilities.json \
  --num-users 10 \
  --seed 42

# Check output
ls -lh /tmp/test_liabilities.json
```

Verify:
- [ ] CLI generates liability data successfully
- [ ] Output file contains 10 users
- [ ] Same seed produces identical results on re-run

### 3. Validate Persona-Specific Behavior

```bash
# Check that different personas have appropriate debt levels
python -c "
import json
with open('data/synthetic/liabilities/liabilities.json') as f:
    liabs = json.load(f)
with open('data/synthetic/users/profiles.json') as f:
    profiles = json.load(f)

for user_id in list(liabs.keys())[:5]:
    persona = profiles[user_id]['persona']
    cc_count = len(liabs[user_id].get('credit_cards', []))
    print(f'{user_id}: {persona} -> {cc_count} credit cards')
"
```

Verify:
- [ ] Struggling personas have higher credit card utilization
- [ ] Secure personas have lower/no overdue balances
- [ ] Income levels correlate appropriately with debt amounts

**Done!** Story 1.5 ready for review.
