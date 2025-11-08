# Troubleshooting Handoff - Epic 4 UI Validation

**Date:** 2025-11-05 | **Branch:** epic-4-personalized-recommendations | **Status:** Debugging Required

## Current Situation

User is encountering errors when trying to validate the Epic 4 UI. This document provides a systematic debugging approach.

## Quick Diagnostic Commands

Run these commands first to gather information:

```bash
# 1. Check current location and branch
pwd
git branch --show-current
git status

# 2. Check if virtual environment is activated
which python
python --version

# 3. Check if API dependencies are installed
pip list | grep -E "(fastapi|uvicorn|pydantic|pyyaml)"

# 4. Check if database exists
ls -lh data/dev.db 2>/dev/null || echo "Database not found"

# 5. Check if config files exist
ls -lh spendsense/config/recommendations.yaml 2>/dev/null || echo "Recommendations config not found"
ls -lh spendsense/config/partner_offers.yaml 2>/dev/null || echo "Partner offers config not found"

# 6. Check if UI files exist
ls -lh spendsense/api/static/index.html
ls -lh spendsense/api/static/app.js
ls -lh spendsense/api/static/styles.css

# 7. Try to start API and capture error
python -m spendsense.api.main 2>&1 | head -50
```

**Please run these commands and share the output.**

## Common Errors and Solutions

### Error 1: ModuleNotFoundError

**Symptoms:**
```
ModuleNotFoundError: No module named 'spendsense'
```

**Cause:** Not in correct directory or venv not activated

**Solution:**
```bash
cd /Users/reena/gauntletai/spendsense
source venv/bin/activate
python -m spendsense.api.main
```

### Error 2: ImportError for recommendations modules

**Symptoms:**
```
ImportError: cannot import name 'ContentLibrary' from 'spendsense.recommendations'
```

**Cause:** Missing __init__.py or incomplete installation

**Solution:**
```bash
# Check if __init__.py exists
ls spendsense/recommendations/__init__.py

# If missing, create it
touch spendsense/recommendations/__init__.py

# Or reinstall in development mode
pip install -e .
```

### Error 3: FileNotFoundError for YAML configs

**Symptoms:**
```
FileNotFoundError: Recommendations file not found: spendsense/config/recommendations.yaml
```

**Cause:** Config files not in expected location

**Diagnosis:**
```bash
# Find where config files actually are
find . -name "recommendations.yaml" -o -name "partner_offers.yaml"

# Check current structure
ls -la spendsense/config/
```

**Solution:**
If files are missing, you need to create them or restore from earlier commits.

### Error 4: Database Not Found (503 Error)

**Symptoms:**
```
HTTPException: 503 - Database not available. Ingest data first.
```

**Cause:** No database file at data/dev.db

**Diagnosis:**
```bash
ls -la data/
```

**Solution:**
The database needs to be created first through the data ingestion process (Epic 1-2). For testing the UI without full data, you can create a minimal test setup (see below).

### Error 5: No Persona Assigned (404 Error)

**Symptoms:**
```
HTTPException: 404 - User user_MASKED_001 not found or no persona assigned
```

**Cause:** User doesn't exist in database or Epic 3 persona assignment hasn't run

**Diagnosis:**
```bash
# Check if database has users
sqlite3 data/dev.db "SELECT user_id FROM user_profiles LIMIT 5;" 2>/dev/null || echo "Cannot query database"
```

**Solution:** Need to run persona assignment first (Epic 3).

### Error 6: Port Already in Use

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Cause:** Port 8000 is already occupied

**Solution:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process if it's an old API server
kill -9 <PID>

# Or use a different port
uvicorn spendsense.api.main:app --port 8001
```

### Error 7: CORS or Connection Errors in Browser

**Symptoms:**
- UI loads but recommendations don't generate
- Console shows fetch errors

**Diagnosis:**
Open browser console (F12) and check for errors

**Solution:**
- Ensure API is running (check terminal)
- Try hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
- Check Network tab for failed requests

### Error 8: JavaScript Errors in Console

**Symptoms:**
```
Uncaught TypeError: Cannot read property 'addEventListener' of null
```

**Cause:** HTML elements not found

**Diagnosis:**
```bash
# Check if HTML file is correct version
grep "recommendations-form" spendsense/api/static/index.html
```

**Solution:**
Ensure you're on the correct branch with latest UI changes.

## Systematic Debugging Process

### Step 1: Verify Environment

```bash
# Location check
cd /Users/reena/gauntletai/spendsense
pwd  # Should output: /Users/reena/gauntletai/spendsense

# Branch check
git branch --show-current  # Should output: epic-4-personalized-recommendations

# Virtual environment check
source venv/bin/activate
which python  # Should point to venv/bin/python

# Dependencies check
pip list | grep fastapi  # Should show fastapi version
```

**✅ If all pass:** Environment is correct

**❌ If any fail:** Share output for diagnosis

### Step 2: Verify File Structure

```bash
# Check Epic 4 files exist
ls -la spendsense/recommendations/

# Expected files:
# - __init__.py
# - models.py
# - content_library.py
# - partner_offer_library.py
# - matcher.py
# - rationale_generator.py
# - assembler.py
# - storage.py

# Check config files
ls -la spendsense/config/

# Expected files:
# - recommendations.yaml
# - partner_offers.yaml

# Check UI files
ls -la spendsense/api/static/

# Expected files:
# - index.html
# - app.js
# - styles.css
```

**✅ If all exist:** File structure is correct

**❌ If missing:** Note which files and share

### Step 3: Run Tests

```bash
# Test Epic 4 components
pytest tests/test_assembler.py -v 2>&1 | tail -20

# If tests pass, components work
# If tests fail, there's a code issue
```

### Step 4: Try Minimal API Start

```bash
# Start API with verbose logging
python -m spendsense.api.main 2>&1 | tee api_startup.log

# Watch for:
# - Import errors
# - File not found errors
# - Database connection errors
# - Port binding errors
```

### Step 5: Test API Directly (Without UI)

```bash
# Once API is running, in a new terminal:
# Test health endpoint
curl http://localhost:8000/health

# Expected: {"status":"healthy","service":"spendsense-api"}

# Test recommendations endpoint (will fail without data, but check error)
curl "http://localhost:8000/api/recommendations/user_MASKED_001?time_window=30d&generate=true"

# Note the error message - it will indicate what's missing
```

## Minimal Test Setup (No Full Database)

If you want to test the UI without running full Epic 1-3 pipelines:

### Option A: Use Unit Tests Data

The tests use mock data. You can adapt this:

```bash
# Run Python interactive shell
python

# Then in Python:
from pathlib import Path
from spendsense.recommendations.content_library import ContentLibrary
from spendsense.recommendations.partner_offer_library import PartnerOfferLibrary

# Try to load libraries
config_dir = Path("spendsense/config")
try:
    content_lib = ContentLibrary(str(config_dir / "recommendations.yaml"))
    print(f"✅ Content library loaded: {content_lib.get_recommendation_count()} items")
except Exception as e:
    print(f"❌ Content library error: {e}")

try:
    partner_lib = PartnerOfferLibrary(str(config_dir / "partner_offers.yaml"))
    print(f"✅ Partner library loaded: {partner_lib.get_offer_count()} items")
except Exception as e:
    print(f"❌ Partner library error: {e}")
```

### Option B: Mock the Database Dependency

If database is missing, you can temporarily mock it for UI testing:

1. Edit `spendsense/api/main.py`
2. Find the recommendations endpoint (around line 825)
3. Add a mock response for testing

## Information Needed for Debugging

Please provide:

### 1. Environment Information
```bash
pwd
git branch --show-current
which python
python --version
pip list | grep -E "(fastapi|uvicorn|pydantic|pyyaml)"
```

### 2. File Structure
```bash
ls -la spendsense/recommendations/
ls -la spendsense/config/
ls -la spendsense/api/static/
ls -la data/
```

### 3. Error Output
```bash
# Try to start API and capture full error
python -m spendsense.api.main 2>&1 | head -100
```

### 4. Test Results (if applicable)
```bash
pytest tests/test_assembler.py -v 2>&1 | tail -30
```

### 5. Browser Console Errors (if UI loads)
- Open browser to http://localhost:8000
- Open Developer Tools (F12)
- Go to Recommendations tab
- Try to generate recommendations
- Share any errors from Console tab

## Quick Fixes to Try

### Fix 1: Reinstall in Development Mode
```bash
pip install -e .
```

### Fix 2: Clear Python Cache
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Fix 3: Restart Fresh
```bash
# Stop any running API servers
pkill -f "uvicorn"

# Reactivate environment
deactivate
source venv/bin/activate

# Try again
python -m spendsense.api.main
```

### Fix 4: Check for Conflicting Processes
```bash
# See what's running on port 8000
lsof -i :8000

# Kill if needed
kill -9 <PID>
```

### Fix 5: Use Alternative Port
```bash
# Try port 8001 instead
uvicorn spendsense.api.main:app --port 8001 --reload

# Then access at http://localhost:8001
```

## Escalation Path

If none of the above works, provide this information:

1. **Output from all diagnostic commands** (Step 1)
2. **Complete error message** (copy entire stack trace)
3. **File structure output** (ls commands)
4. **Last successful step** (what worked before error?)
5. **Recent changes** (did you modify any files?)

## Testing Without Full Epic 1-3 Data

If you want to test just the Epic 4 UI without full data ingestion:

### Create Minimal Mock Data

```bash
# Create minimal database for testing
cat > create_test_db.py << 'EOF'
import sqlite3
from datetime import date, datetime

# Create minimal test database
conn = sqlite3.connect('data/dev.db')
cursor = conn.cursor()

# Create user_profiles table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_profiles (
        user_id TEXT PRIMARY KEY,
        annual_income INTEGER,
        age INTEGER
    )
''')

# Create persona_assignments table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS persona_assignments (
        user_id TEXT PRIMARY KEY,
        persona_id TEXT,
        confidence REAL,
        assigned_at TEXT
    )
''')

# Insert test user
cursor.execute('''
    INSERT OR REPLACE INTO user_profiles (user_id, annual_income, age)
    VALUES ('user_MASKED_001', 50000, 30)
''')

cursor.execute('''
    INSERT OR REPLACE INTO persona_assignments
    (user_id, persona_id, confidence, assigned_at)
    VALUES ('user_MASKED_001', 'high_utilization', 0.85, ?)
''', (datetime.now().isoformat(),))

conn.commit()
conn.close()
print("✅ Test database created at data/dev.db")
EOF

python create_test_db.py
```

This creates a minimal database with one test user.

## Expected Working State

When everything works correctly:

```bash
# 1. API starts successfully
$ python -m spendsense.api.main
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000

# 2. Browser loads dashboard
http://localhost:8000
# Shows: SpendSense Dashboard with tabs

# 3. Recommendations tab works
# Click "💡 Recommendations"
# Enter: user_MASKED_001
# Click: Generate Recommendations
# Wait: 1-2 seconds
# See: 4-8 recommendation cards with personalized content

# 4. No errors in:
# - Terminal (API logs)
# - Browser console (F12)
# - Network tab (all requests succeed)
```

## Resume Next Session

To pick up debugging next time:

```bash
# Save current state
cd /Users/reena/gauntletai/spendsense
git status > debug_git_status.txt
pip list > debug_pip_list.txt
ls -laR spendsense/ > debug_file_structure.txt

# Next session:
# 1. Review these files
# 2. Check if branch matches
# 3. Share any error messages
```

## Contact Points

When seeking help, share:
1. This troubleshooting handoff document
2. Output from diagnostic commands
3. Complete error messages
4. What you've tried already
5. Last known working state

---

**Status:** Awaiting error details
**Next Step:** Run diagnostic commands and share output
**Goal:** Get API running and UI validating successfully

**Quick test:** Can you run `pytest tests/test_assembler.py -v` successfully?
If yes, the code works - just need to fix the runtime environment.
If no, there's a code issue to fix.
