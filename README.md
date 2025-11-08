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
./scripts/setup.sh
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

## Running the Application

SpendSense consists of two main interfaces:

### 1. Backend API Server (Port 8000)

**Audience:** Developers, API consumers, system administrators

The FastAPI backend provides REST API endpoints and interactive Swagger documentation.

```bash
# Activate virtual environment
source venv/bin/activate

# Start API server
uvicorn spendsense.api.main:app --reload --port 8000
```

**Access:** http://localhost:8000/docs

### 2. Operator Dashboard (Port 3000)

**Audience:** Operators, compliance officers, human reviewers

React-based web interface for human oversight and quality assurance.

```bash
# Navigate to UI directory
cd spendsense/ui

# Start development server
npm run dev
```

**Access:** http://localhost:3000

---

## Dashboard Features

### Backend API (Port 8000) - Interactive Swagger UI

**Purpose:** Backend API server powering the entire SpendSense system with live API documentation.

#### Available Endpoints:

**Profile Generation**
- `POST /api/generate` - Generate synthetic user profiles (50-100 users)
- `GET /api/profiles` - List and filter profiles by persona
- `GET /api/profiles/{user_id}` - Get specific profile details
- `GET /api/stats` - Profile statistics and persona distribution

**Transaction Management**
- `POST /api/transactions/generate` - Generate realistic transaction data (180+ days)
- `GET /api/transactions` - Retrieve user transaction history
- `GET /api/transactions/stats` - Transaction statistics and category breakdown

**Liability Management**
- `POST /api/liabilities/generate` - Generate credit cards, student loans, mortgages
- `GET /api/liabilities/stats` - Liability statistics (APR rates, utilization)
- `GET /api/liabilities/user/{user_id}` - Get user liabilities

**Behavioral Signals**
- `GET /api/signals/{user_id}` - Comprehensive behavioral summary
  - Subscription patterns (recurring merchants, monthly spend)
  - Savings behavior (growth rate, emergency fund coverage)
  - Credit utilization (by card, minimum payments, overdue status)
  - Income stability (pay frequency, cash flow buffer)

**Persona Profiles**
- `GET /api/profile/{user_id}` - Persona assignment with audit trail
  - 30-day and 180-day time windows
  - Complete decision trace showing match logic

**Recommendations**
- `GET /api/recommendations/{user_id}` - Personalized financial education
  - Educational content with transparent rationales
  - Partner offers with eligibility checks
  - Data citations for every recommendation

**Consent Management** (Requires Admin Role)
- `POST /api/consent` - Record user opt-in/opt-out
- `GET /api/consent/{user_id}` - Check consent status

**Operator Endpoints** (Requires Authentication)
- `GET /api/operator/users/search` - Search users by ID or name
- `GET /api/operator/signals/{user_id}` - Signal dashboard data
- `GET /api/operator/signals/{user_id}/export` - CSV/JSON export
- `GET /api/operator/personas/{user_id}` - Persona review interface
- `GET /api/operator/review/queue` - Recommendation review queue
- `GET /api/operator/audit` - Audit logs and compliance reporting

---

### Operator Dashboard (Port 3000) - React Frontend

**Purpose:** Human oversight interface for reviewing AI decisions, verifying signal detection, and ensuring recommendation quality.

#### Key Features:

**1. User Search Interface**
- Search users by ID or name
- Autocomplete suggestions (debounced)
- Quick lookup for any user in the system

**2. Time Window Toggle**
- **30-day view** - Short-term behavioral patterns
- **180-day view** - Long-term behavioral trends
- **Side-by-side comparison** - See both windows simultaneously
- Percentage change calculations with directional indicators

**3. Subscription Metrics Display**
- Recurring merchants count (e.g., "5 subscriptions detected")
- Monthly recurring spend (formatted as currency: "$127.50")
- Subscription share (percentage of total spend: "18.2%")
- Visual indicators for concerning values (>30% share)
- Tooltips explaining each metric

**4. Savings Metrics Display**
- Net inflow to savings accounts (monthly)
- Growth rate (percentage change over time)
- Emergency fund coverage (months of expenses saved)
- Color-coded status:
  - 🟢 Green: Healthy (≥3 months)
  - 🟡 Yellow: Concerning (1-3 months)
  - 🔴 Red: Critical (<1 month)
- Target comparison (goal: 3-6 months emergency fund)

**5. Credit Metrics Display**
- Credit utilization by card (balance ÷ limit)
- Color-coded thresholds:
  - <30%: Green (healthy)
  - 30-70%: Yellow (moderate risk)
  - >70%: Red (high risk)
- Interest charges badge (yes/no)
- Minimum payment only flag
- Overdue status alert
- Per-card utilization breakdown

**6. Income Metrics Display**
- Payroll deposits count
- Median pay gap (days between paychecks)
- Payment frequency interpretation:
  - 14 days = "Bi-weekly pay"
  - 30 days = "Monthly pay"
  - >45 days = "Irregular income"
- Cash flow buffer (months of expenses in checking)
- Income stability indicators

**7. Side-by-Side Comparison View**
- Split-pane layout comparing 30-day vs 180-day signals
- Percentage change calculations
- Arrows showing increase/decrease trends
- Highlights key differences between time windows
- Summary of major behavioral changes

**8. Raw Data View**
- Expandable accordion showing full JSON structure
- All signal values with full precision (no rounding)
- Signal calculation timestamps with timezone
- Data version and source information

**9. Export Functionality**
- **CSV export** with headers: `user_id`, `time_window`, `metric_name`, `metric_value`, `computed_at`
- **JSON export** for programmatic access
- Browser download trigger
- Supports compliance and analysis use cases

**10. Visual Design**
- Clean, trustworthy financial services aesthetic
- TailwindCSS styling with calming blues/greens
- Responsive layout (desktop and tablet optimized)
- Loading states with spinners
- Error handling with clear messages
- Empty states with helpful instructions

---

## How the Dashboards Work Together

1. **Backend (Port 8000)** generates synthetic data, detects behavioral signals, assigns personas, and generates recommendations
2. **Frontend (Port 3000)** calls the backend API to retrieve signal data and displays it in a human-friendly interface
3. **Vite proxy configuration** automatically routes API requests from frontend → backend
4. **Authentication** is enforced via JWT tokens (RBAC system with viewer/reviewer/admin roles)

---

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

# Start API server
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
