# 🎯 SpendSense UI Quick Start Guide

## The UI is Running NOW! 🚀

**Open your browser to:** http://localhost:8000

The server is already running on your machine (PID: see terminal output).

## What You Can Do Right Now

### 1. Generate Profiles
- Click "Generate Profiles" tab
- Set number of users (50-100)
- Choose a seed number (for reproducibility)
- Click "Generate Profiles"
- See instant validation results

### 2. View Profiles
- Click "View Profiles" tab
- Browse all generated profiles
- Filter by persona type
- Use pagination to navigate
- See detailed financial characteristics for each user

### 3. Check Statistics
- Click "Statistics" tab
- See persona distribution charts
- View income range statistics
- Check validation status

### 4. Learn About Personas
- Click "Personas" tab
- Read about the 5 persona archetypes
- Understand behavioral patterns

### 5. Explore API
Visit http://localhost:8000/docs for interactive API documentation (Swagger UI)

## Features

✅ **Fully Functional UI** - No command line needed
✅ **Real-time Generation** - Create profiles instantly
✅ **Visual Statistics** - See distribution charts
✅ **Filter & Search** - Find profiles by persona
✅ **Responsive Design** - Works on any screen size
✅ **Extensible** - Ready for future features

## Stopping the Server

Press `Ctrl+C` in the terminal, or run:
```bash
pkill -f "uvicorn spendsense.api.main"
```

## Restarting the Server

Simply run:
```bash
./scripts/run_ui.sh
```

Or manually:
```bash
source venv/bin/activate
python -m uvicorn spendsense.api.main:app --reload --port 8000
```

## Testing Different Scenarios

### Test 1: Generate 50 profiles
1. Go to Generate Profiles tab
2. Set: num_users = 50, seed = 42
3. Click Generate
4. Go to Statistics tab - should see exactly 10 per persona

### Test 2: Reproducibility
1. Generate with seed = 999
2. Note the first profile details in View Profiles
3. Generate again with seed = 999
4. First profile should be identical

### Test 3: Filter by Persona
1. Generate 100 profiles
2. Go to View Profiles
3. Select "High Utilization" from dropdown
4. Should see only High Utilization personas (20 profiles)

### Test 4: Check Validation
1. Generate profiles
2. Go to Statistics tab
3. Each persona should be exactly 20%
4. Validation should show ✓ Passed

## Future Features

As we build future stories, new features will appear:

🔜 **Story 1.4** - Generate and view transactions
🔜 **Epic 2** - View detected behavioral signals
🔜 **Epic 3** - See persona assignments
🔜 **Epic 4** - Browse recommendations
🔜 **Epic 6** - Full operator dashboard

The UI is designed to grow with the project!

## Troubleshooting

### Can't Access http://localhost:8000
- Check server is running: `ps aux | grep uvicorn`
- Restart: `./scripts/run_ui.sh`

### No Profiles Showing
- Generate profiles first in the "Generate Profiles" tab
- Click "Refresh" in View Profiles tab

### Port Already in Use
```bash
# Use different port
python -m uvicorn spendsense.api.main:app --port 8001
# Then visit http://localhost:8001
```

## Files Created

```
spendsense/api/
├── main.py              # FastAPI backend (400+ lines)
├── static/
│   ├── index.html       # Main UI (200+ lines)
│   ├── styles.css       # Styling (400+ lines)
│   └── app.js           # JavaScript (300+ lines)
└── README.md            # Detailed API docs

run_ui.sh                # Easy start script
UI_QUICKSTART.md         # This file
```

## API Endpoints Summary

- `GET /` - Web UI
- `GET /health` - Health check
- `POST /api/generate` - Generate profiles
- `GET /api/profiles` - List profiles (with pagination)
- `GET /api/profiles/{id}` - Get specific profile
- `GET /api/stats` - Statistics
- `GET /api/personas` - Persona info
- `GET /docs` - Interactive API docs

## What's Next?

1. **Test the UI** - Generate profiles, explore features
2. **Review Story 1.3** - All acceptance criteria met
3. **Story 1.4** - Add transaction generation (we'll extend this UI)
4. **Epic 2+** - Build the recommendation engine (UI ready!)

Enjoy testing SpendSense! 🎉
