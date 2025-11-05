# SpendSense

**An explainable, consent-aware AI system that transforms Plaid-style transaction data into personalized financial education.**

## Overview

SpendSense analyzes financial transaction data to detect behavioral patterns and deliver personalized financial education recommendations. The system prioritizes transparency, user control, and ethical compliance in financial AI.

### Core Features

- **Behavioral Signal Detection**: Identifies subscription patterns, savings behavior, credit utilization, and income stability
- **Persona Assignment**: Assigns users to educational personas based on detected financial behaviors
- **Explainable Recommendations**: Every recommendation includes transparent rationales citing specific data signals
- **Consent-First**: No data processing without explicit user permission
- **Ethical Guardrails**: Mandatory validation for consent, eligibility, and tone requirements

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLite, Parquet
- **Frontend**: React 18, TypeScript, Vite, TailwindCSS
- **Testing**: pytest (backend), jest (frontend)
- **Development**: ruff (linting), black (formatting), mypy (type checking)

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- pip (Python package manager)
- npm (Node package manager)

## Quick Setup

### One-Command Setup (Recommended)

```bash
./setup.sh
```

This script will:
1. Create a Python virtual environment
2. Install all Python dependencies
3. Install frontend dependencies
4. Initialize data directories
5. Run tests to verify the setup

### Manual Setup

#### Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv

# On Mac/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

#### Frontend Setup

```bash
# Navigate to UI directory
cd spendsense/ui

# Install frontend dependencies
npm install
```

## Development Commands

### Backend

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run tests
pytest

# Run tests with coverage
pytest --cov=spendsense --cov-report=html

# Run linter
ruff check spendsense/

# Run formatter
black spendsense/

# Run type checker
mypy spendsense/

# Start API server (when implemented)
uvicorn spendsense.api.main:app --reload --port 8000
```

### Frontend

```bash
# Navigate to UI directory
cd spendsense/ui

# Start development server
npm run dev

# Run tests
npm test

# Run linter
npm run lint

# Build for production
npm run build
```

## Project Structure

```
spendsense/
├── spendsense/          # Main Python package
│   ├── ingest/          # Data loading and validation
│   ├── features/        # Signal detection and feature engineering
│   ├── personas/        # Persona assignment logic
│   ├── recommend/       # Recommendation engine
│   ├── guardrails/      # Consent, eligibility, tone checks
│   ├── ui/              # React frontend (separate from Python package)
│   ├── eval/            # Evaluation harness and metrics
│   ├── api/             # REST API endpoints
│   ├── db/              # Database models and schemas
│   └── config/          # Configuration files
├── tests/               # Test suite
│   ├── integration/     # Integration tests
│   └── e2e/             # End-to-end tests
├── data/                # Data storage
│   ├── synthetic/       # Generated CSV/JSON files
│   ├── sqlite/          # SQLite database
│   ├── parquet/         # Analytics exports
│   └── logs/            # JSON audit logs
├── docs/                # Documentation
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Testing

The project uses a testing pyramid approach:
- **~60% Unit Tests**: Individual functions and classes
- **~30% Integration Tests**: Module interactions
- **~10% E2E Tests**: Full API workflows

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=spendsense --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # Mac/Linux
# or
start htmlcov/index.html  # Windows
```

## Configuration

Configuration files are stored in `spendsense/config/` and use YAML format.

Example configuration structure:
- Persona definitions: `spendsense/config/personas.yaml`
- Content catalog: `spendsense/config/content_catalog.yaml`
- Application settings: `spendsense/config/settings.py`

## Environment Variables

Create a `.env` file in the project root (see `.env.example` for template):

```bash
# Environment
ENV=development

# Database
DATABASE_URL=sqlite:///data/sqlite/spendsense.db

# API
API_HOST=0.0.0.0
API_PORT=8000

# Operator Authentication
OPERATOR_API_KEY=change-this-in-production

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## Architecture

SpendSense uses a **modular monolith architecture** with clear module boundaries:

1. **Ingest Module**: Loads and validates Plaid-style financial data
2. **Features Module**: Detects behavioral signals from transactions
3. **Personas Module**: Assigns users to educational personas
4. **Recommend Module**: Generates personalized recommendations
5. **Guardrails Module**: Enforces ethical constraints
6. **API Module**: Exposes REST endpoints
7. **UI Module**: Operator review interface
8. **Eval Module**: System performance metrics

## Key Principles

- **Explainability over Sophistication**: Clear, transparent AI decisions
- **User Control over Automation**: Users maintain control of their data
- **Education over Sales**: Focus on learning, not product promotion
- **Fairness**: No bias in persona assignment or recommendations

## Documentation

- [Product Requirements Document](docs/prd.md)
- [Architecture Document](docs/architecture.md)
- [Epic Specifications](docs/prd/)
- [Story Files](docs/stories/)

## License

[License information to be added]

## Contact

For questions or feedback, please contact: bharris@peak6.com

---

**Note**: This is a demonstration project focused on responsible AI in financial services. Always consult a licensed financial advisor for personalized financial guidance.
