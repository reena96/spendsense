# SpendSense Web UI & API

A comprehensive web dashboard for testing and exploring SpendSense features.

## Quick Start

### Option 1: Run Script (Easiest)

```bash
# From project root
./run_ui.sh
```

Then open your browser to **http://localhost:8000**

### Option 2: Manual Start

```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
python -m uvicorn spendsense.api.main:app --reload --port 8000
```

## Features

### Current (Story 1.3)

✅ **Generate Profiles** - Create synthetic user profiles with persona-based characteristics
- Configurable number of users (50-100)
- Reproducible with seed
- Real-time validation

✅ **View Profiles** - Browse generated profiles
- Pagination
- Filter by persona
- Detailed profile information

✅ **Statistics Dashboard** - Analyze generated data
- Persona distribution charts
- Income range statistics
- Validation status

✅ **Persona Information** - Learn about the 5 persona archetypes

### Coming Soon

🔜 **Story 1.4: Transactions** - Generate and view synthetic transactions
🔜 **Epic 2: Signals** - Detect behavioral patterns
🔜 **Epic 3: Persona Assignment** - Match users to personas
🔜 **Epic 4: Recommendations** - Generate personalized recommendations
🔜 **Epic 5: Guardrails** - Consent & eligibility filtering
🔜 **Epic 6: Operator View** - Oversight and approval workflows

## API Endpoints

### Profile Generation

**POST /api/generate**
```json
{
  "num_users": 100,
  "seed": 42
}
```

**GET /api/profiles**
- Query params: `limit`, `offset`, `persona`

**GET /api/profiles/{user_id}**
- Get specific profile

**GET /api/stats**
- Get statistics and validation

**GET /api/personas**
- Get persona definitions

### Interactive API Docs

Visit **http://localhost:8000/docs** for interactive Swagger UI documentation.

## Architecture

```
spendsense/api/
├── main.py              # FastAPI application
├── static/              # Frontend assets
│   ├── index.html       # Main UI
│   ├── styles.css       # Styling
│   └── app.js           # JavaScript logic
└── README.md            # This file

Frontend:
- Vanilla JavaScript (no build tools)
- Modern CSS with CSS Grid/Flexbox
- Fully responsive design

Backend:
- FastAPI for REST API
- Pydantic for validation
- Static file serving for UI
```

## Development

### Adding New Features

When implementing new stories (e.g., Story 1.4: Transactions), add:

1. **Backend**: New endpoints in `main.py`
```python
@app.post("/api/transactions")
async def generate_transactions():
    # Implementation
    pass
```

2. **Frontend**: New tab in `index.html`
```html
<button class="tab" data-tab="transactions">Transactions</button>
<div id="transactions" class="tab-content">
    <!-- Content -->
</div>
```

3. **JavaScript**: New functions in `app.js`
```javascript
async function loadTransactions() {
    // Implementation
}
```

### Hot Reload

The server runs with `--reload` flag, so changes to Python code reload automatically.

For frontend changes (HTML/CSS/JS), just refresh your browser.

## Testing

### Manual Testing via UI

1. Start the server: `./run_ui.sh`
2. Open http://localhost:8000
3. Generate profiles with different settings
4. Explore profiles and statistics
5. Try different filters and pagination

### API Testing via curl

```bash
# Generate profiles
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"num_users": 50, "seed": 42}'

# List profiles
curl http://localhost:8000/api/profiles?limit=5

# Get stats
curl http://localhost:8000/api/stats

# Get personas
curl http://localhost:8000/api/personas
```

### API Testing via Swagger UI

Visit **http://localhost:8000/docs** and use the interactive interface.

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
python -m uvicorn spendsense.api.main:app --port 8001
```

### Virtual Environment Issues

```bash
# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### No Profiles Showing

1. Make sure you've generated profiles first (Generate Profiles tab)
2. Check that `data/synthetic/users/profiles.json` exists
3. Try refreshing the page

## Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Generates 100 profiles in ~1 second
- UI loads profiles instantly
- Pagination for smooth browsing
- No external dependencies (except FastAPI)

## Security Note

This is a development/testing interface. For production:
- Add authentication
- Add rate limiting
- Validate all inputs
- Use HTTPS
- Add CORS configuration
