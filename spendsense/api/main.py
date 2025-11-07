"""
SpendSense API - FastAPI backend for testing and development.

This API provides endpoints for all SpendSense features and serves
a web UI for visual testing and exploration.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from spendsense.generators import (
    ProfileGenerator,
    generate_synthetic_profiles,
    TransactionGenerator,
    generate_synthetic_transactions,
    LiabilityGenerator,
    generate_synthetic_liabilities,
)
from spendsense.api.operator_auth import router as operator_auth_router
from spendsense.api.operator_signals import router as operator_signals_router
from spendsense.api.operator_personas import router as operator_personas_router
from spendsense.api.operator_review import router as operator_review_router
from spendsense.api.operator_audit import router as operator_audit_router
from spendsense.api.operator_consent import router as operator_consent_router
from spendsense.auth.rbac import require_role
from spendsense.auth.tokens import TokenData


# API Models
class GenerateProfilesRequest(BaseModel):
    """Request model for profile generation."""
    num_users: int = Field(ge=50, le=120, default=120, description="Number of profiles to generate (50-120)")
    seed: int = Field(default=42, description="Random seed for reproducibility")


class GenerateProfilesResponse(BaseModel):
    """Response model for profile generation."""
    success: bool
    num_profiles: int
    validation: dict
    message: str


class ProfileListResponse(BaseModel):
    """Response model for profile listing."""
    total: int
    profiles: list[dict]


class StatsResponse(BaseModel):
    """Response model for statistics."""
    total_profiles: int
    persona_distribution: dict
    income_range: tuple[float, float]
    validation: dict


# Create FastAPI app
app = FastAPI(
    title="SpendSense API",
    description="Backend API for SpendSense synthetic data generation and testing",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True  # Keep authorization between page refreshes
    }
)

# Configure OpenAPI security scheme for Bearer token authentication
# This adds the "Authorize" button to Swagger UI
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Add Bearer token security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token in the format: `<your_token>` (no 'Bearer' prefix needed)"
        }
    }

    # Mark protected endpoints (consent endpoints) as requiring BearerAuth
    # This makes the Authorize button auto-fill the authorization header
    protected_paths = [
        ("/api/consent", "post"),
        ("/api/consent/{user_id}", "get"),
    ]

    for path, method in protected_paths:
        if path in openapi_schema["paths"] and method in openapi_schema["paths"][path]:
            # Add security requirement
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

            # Remove the confusing authorization parameter from the UI
            # The Authorize button handles authentication instead
            if "parameters" in openapi_schema["paths"][path][method]:
                openapi_schema["paths"][path][method]["parameters"] = [
                    p for p in openapi_schema["paths"][path][method]["parameters"]
                    if p.get("name") != "authorization"
                ]

            # Add a note to the endpoint description about authentication
            current_desc = openapi_schema["paths"][path][method].get("description", "")
            if "🔒" not in current_desc:
                auth_note = "\n\n🔒 **Authentication Required:** Use the 'Authorize' button (top right) to provide your JWT token. Once authorized, you can execute this endpoint directly."
                openapi_schema["paths"][path][method]["description"] = current_desc + auth_note

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Path to static files and data
STATIC_DIR = Path(__file__).parent / "static"
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "synthetic"
USERS_DIR = DATA_DIR / "users"
TRANSACTIONS_DIR = DATA_DIR / "transactions"
LIABILITIES_DIR = DATA_DIR / "liabilities"
DEFAULT_PROFILES_FILE = USERS_DIR / "profiles.json"
DEFAULT_TRANSACTIONS_FILE = TRANSACTIONS_DIR / "transactions.json"
DEFAULT_LIABILITIES_FILE = LIABILITIES_DIR / "liabilities.json"


# Ensure directories exist
STATIC_DIR.mkdir(exist_ok=True)
USERS_DIR.mkdir(parents=True, exist_ok=True)
TRANSACTIONS_DIR.mkdir(parents=True, exist_ok=True)
LIABILITIES_DIR.mkdir(parents=True, exist_ok=True)


# Serve static files for UI
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include operator authentication router (Epic 6 - Story 6.1)
app.include_router(operator_auth_router)

# Include operator signals router (Epic 6 - Story 6.2)
app.include_router(operator_signals_router)

# Include operator personas router (Epic 6 - Story 6.3)
app.include_router(operator_personas_router)

# Include operator review router (Epic 6 - Story 6.4)
app.include_router(operator_review_router)

# Include operator audit router (Epic 6 - Story 6.5)
app.include_router(operator_audit_router)

# Include operator consent router (Epic 6 - Story 6.6)
app.include_router(operator_consent_router)


@app.get("/")
async def root():
    """Serve the main UI page."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "SpendSense API", "docs": "/docs", "ui": "UI not yet installed"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "spendsense-api"}


# ===== Profile Generation Endpoints =====

@app.post("/api/generate", response_model=GenerateProfilesResponse)
async def generate_profiles(request: GenerateProfilesRequest):
    """
    Generate synthetic user profiles.

    This endpoint generates profiles with persona-based characteristics
    and saves them to the default profiles file.
    """
    try:
        profiles, validation = generate_synthetic_profiles(
            num_users=request.num_users,
            seed=request.seed,
            output_path=DEFAULT_PROFILES_FILE
        )

        return GenerateProfilesResponse(
            success=True,
            num_profiles=len(profiles),
            validation=validation,
            message=f"Successfully generated {len(profiles)} profiles"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/profiles", response_model=ProfileListResponse)
async def list_profiles(
    limit: int = Query(default=10, ge=1, le=100, description="Number of profiles to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    persona: Optional[str] = Query(default=None, description="Filter by persona type")
):
    """
    List generated profiles with pagination and filtering.

    Returns a paginated list of profiles. Can filter by persona type.
    Reads from database if available, falls back to JSON file.
    """
    # Try database first (preferred)
    if DB_PATH.exists():
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from spendsense.ingestion.database_writer import User, Account

        try:
            engine = create_engine(f'sqlite:///{DB_PATH}')
            Session = sessionmaker(bind=engine)

            with Session() as session:
                # Query users
                query = session.query(User)

                # Filter by persona if specified
                if persona:
                    query = query.filter(User.persona == persona)

                # Get total count
                total = query.count()

                # Apply pagination
                users = query.order_by(User.user_id).offset(offset).limit(limit).all()

                # Build profile list
                profiles = []
                for user in users:
                    # Get user's accounts
                    accounts = session.query(Account).filter(Account.user_id == user.user_id).all()

                    account_list = []
                    for acc in accounts:
                        account_list.append({
                            "type": acc.type,
                            "subtype": acc.subtype,
                            "initial_balance": float(acc.balance_current or 0),
                            "limit": float(acc.balance_limit) if acc.balance_limit else None
                        })

                    profiles.append({
                        "user_id": user.user_id,
                        "name": user.name,
                        "persona": user.persona,
                        "annual_income": float(user.annual_income) if user.annual_income else 0,
                        "characteristics": user.characteristics or {},
                        "accounts": account_list
                    })

                return ProfileListResponse(
                    total=total,
                    profiles=profiles
                )
        except Exception as e:
            # If database read fails, fall through to JSON file
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Database read failed, falling back to JSON: {e}")

    # Fallback to JSON file
    if not DEFAULT_PROFILES_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="No profiles found. Generate profiles first using POST /api/generate"
        )

    with open(DEFAULT_PROFILES_FILE) as f:
        all_profiles = json.load(f)

    # Filter by persona if specified
    if persona:
        all_profiles = [p for p in all_profiles if p["persona"] == persona]

    # Paginate
    total = len(all_profiles)
    profiles = all_profiles[offset:offset + limit]

    return ProfileListResponse(
        total=total,
        profiles=profiles
    )


@app.get("/api/profiles/{user_id}")
async def get_profile(user_id: str):
    """
    Get a specific profile by user ID.

    Returns the full profile details for the specified user.
    Reads from database if available, falls back to JSON file.
    """
    # Try database first (preferred)
    if DB_PATH.exists():
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from spendsense.ingestion.database_writer import User, Account

        try:
            engine = create_engine(f'sqlite:///{DB_PATH}')
            Session = sessionmaker(bind=engine)

            with Session() as session:
                # Query user
                user = session.query(User).filter(User.user_id == user_id).first()

                if not user:
                    raise HTTPException(status_code=404, detail=f"Profile {user_id} not found")

                # Get user's accounts
                accounts = session.query(Account).filter(Account.user_id == user.user_id).all()

                account_list = []
                for acc in accounts:
                    account_list.append({
                        "type": acc.type,
                        "subtype": acc.subtype,
                        "initial_balance": float(acc.balance_current or 0),
                        "limit": float(acc.balance_limit) if acc.balance_limit else None
                    })

                return {
                    "user_id": user.user_id,
                    "name": user.name,
                    "persona": user.persona,
                    "annual_income": float(user.annual_income) if user.annual_income else 0,
                    "characteristics": user.characteristics or {},
                    "accounts": account_list
                }
        except HTTPException:
            raise
        except Exception as e:
            # If database read fails, fall through to JSON file
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Database read failed for user {user_id}, falling back to JSON: {e}")

    # Fallback to JSON file
    if not DEFAULT_PROFILES_FILE.exists():
        raise HTTPException(status_code=404, detail="No profiles found")

    with open(DEFAULT_PROFILES_FILE) as f:
        profiles = json.load(f)

    profile = next((p for p in profiles if p["user_id"] == user_id), None)

    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile {user_id} not found")

    return profile


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get statistics about generated profiles.

    Returns persona distribution, income range, and validation status.
    Reads from database if available, falls back to JSON file.
    """
    # Try database first (preferred)
    if DB_PATH.exists():
        from sqlalchemy import create_engine, func
        from sqlalchemy.orm import sessionmaker
        from spendsense.ingestion.database_writer import User

        try:
            engine = create_engine(f'sqlite:///{DB_PATH}')
            Session = sessionmaker(bind=engine)

            with Session() as session:
                # Get total count
                total = session.query(User).count()

                if total == 0:
                    raise HTTPException(status_code=404, detail="No profiles found")

                # Get persona distribution
                persona_counts = session.query(
                    User.persona,
                    func.count(User.user_id)
                ).group_by(User.persona).all()

                persona_distribution = {persona: count for persona, count in persona_counts}

                # Get income range
                income_stats = session.query(
                    func.min(User.annual_income),
                    func.max(User.annual_income)
                ).first()

                income_range = (float(income_stats[0] or 0), float(income_stats[1] or 0))

                # Validate distribution
                persona_percentages = {
                    persona: (count / total) * 100
                    for persona, count in persona_distribution.items()
                }

                validation_errors = []
                # Note: With 6 personas, expected distribution is ~16.7% each, not 20%
                # We'll use a looser validation for now
                for persona, percentage in persona_percentages.items():
                    if percentage < 5.0 or percentage > 30.0:  # Loose bounds
                        validation_errors.append(
                            f"Persona {persona} has {percentage:.1f}% (unusual distribution)"
                        )

                validation = {
                    "valid": len(validation_errors) == 0,
                    "errors": validation_errors,
                    "persona_percentages": persona_percentages
                }

                return StatsResponse(
                    total_profiles=total,
                    persona_distribution=persona_distribution,
                    income_range=income_range,
                    validation=validation
                )
        except HTTPException:
            raise
        except Exception as e:
            # If database read fails, fall through to JSON file
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Database read failed, falling back to JSON: {e}")

    # Fallback to JSON file
    if not DEFAULT_PROFILES_FILE.exists():
        raise HTTPException(status_code=404, detail="No profiles found")

    with open(DEFAULT_PROFILES_FILE) as f:
        profiles = json.load(f)

    # Calculate statistics
    from collections import Counter

    persona_counts = Counter(p["persona"] for p in profiles)
    persona_distribution = dict(persona_counts)

    incomes = [p["annual_income"] for p in profiles]
    income_range = (min(incomes), max(incomes))

    # Validate distribution
    total = len(profiles)
    persona_percentages = {
        persona: (count / total) * 100
        for persona, count in persona_distribution.items()
    }

    validation_errors = []
    for persona, percentage in persona_percentages.items():
        if not (19.0 <= percentage <= 21.0):
            validation_errors.append(
                f"Persona {persona} has {percentage:.1f}% (expected ~20%)"
            )

    validation = {
        "valid": len(validation_errors) == 0,
        "errors": validation_errors,
        "persona_percentages": persona_percentages
    }

    return StatsResponse(
        total_profiles=total,
        persona_distribution=persona_distribution,
        income_range=income_range,
        validation=validation
    )


@app.get("/api/personas")
async def get_personas():
    """
    Get information about available personas.

    Returns descriptions and characteristics for each persona type.
    """
    from spendsense.personas.definitions import PERSONA_DESCRIPTIONS, PersonaType

    personas = {}
    for persona_type in PersonaType:
        personas[persona_type.value] = {
            "name": persona_type.value.replace("_", " ").title(),
            "description": PERSONA_DESCRIPTIONS[persona_type]
        }

    return personas


# ===== Transaction Endpoints (Story 1.4) =====

class GenerateTransactionsRequest(BaseModel):
    """Request model for transaction generation."""
    seed: int = Field(default=42, description="Random seed for reproducibility")
    days: int = Field(default=180, ge=180, description="Days of transaction history (minimum 180)")


class GenerateTransactionsResponse(BaseModel):
    """Response model for transaction generation."""
    success: bool
    num_users: int
    total_transactions: int
    date_range: tuple[str, str]
    message: str


class TransactionListResponse(BaseModel):
    """Response model for transaction listing."""
    user_id: str
    total: int
    transactions: list[dict]


class TransactionStatsResponse(BaseModel):
    """Response model for transaction statistics."""
    total_users: int
    total_transactions: int
    date_range: tuple[str, str]
    categories: dict
    personas: dict


@app.post("/api/transactions/generate", response_model=GenerateTransactionsResponse)
async def generate_transactions(request: GenerateTransactionsRequest):
    """
    Generate synthetic transactions for all profiles.

    Requires profiles to be generated first. Creates realistic transaction
    history based on persona characteristics.
    """
    if not DEFAULT_PROFILES_FILE.exists():
        raise HTTPException(
            status_code=400,
            detail="No profiles found. Generate profiles first using POST /api/generate"
        )

    try:
        result = generate_synthetic_transactions(
            profiles_path=DEFAULT_PROFILES_FILE,
            output_path=DEFAULT_TRANSACTIONS_FILE,
            seed=request.seed,
            days_of_history=request.days
        )

        # Calculate stats
        total_txns = sum(len(txns) for txns in result.values())
        all_dates = []
        for user_txns in result.values():
            all_dates.extend([t["date"] for t in user_txns])

        date_range = (min(all_dates), max(all_dates)) if all_dates else ("", "")

        return GenerateTransactionsResponse(
            success=True,
            num_users=len(result),
            total_transactions=total_txns,
            date_range=date_range,
            message=f"Successfully generated {total_txns:,} transactions for {len(result)} users"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transactions", response_model=TransactionListResponse)
async def list_transactions(
    user_id: str = Query(..., description="User ID to get transactions for"),
    limit: int = Query(default=50, ge=1, le=500, description="Number of transactions to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    category: Optional[str] = Query(default=None, description="Filter by category")
):
    """
    List transactions for a specific user.

    Returns paginated transaction history with optional category filtering.
    """
    if not DEFAULT_TRANSACTIONS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="No transactions found. Generate transactions first using POST /api/transactions/generate"
        )

    with open(DEFAULT_TRANSACTIONS_FILE) as f:
        all_transactions = json.load(f)

    if user_id not in all_transactions:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    user_txns = all_transactions[user_id]

    # Filter by category if specified
    if category:
        user_txns = [t for t in user_txns if t["personal_finance_category"] == category]

    # Sort by date descending
    user_txns = sorted(user_txns, key=lambda t: t["date"], reverse=True)

    # Paginate
    total = len(user_txns)
    transactions = user_txns[offset:offset + limit]

    return TransactionListResponse(
        user_id=user_id,
        total=total,
        transactions=transactions
    )


@app.get("/api/transactions/stats", response_model=TransactionStatsResponse)
async def get_transaction_stats():
    """
    Get statistics about generated transactions.

    Returns counts, date range, category distribution, and persona breakdown.
    """
    if not DEFAULT_TRANSACTIONS_FILE.exists():
        raise HTTPException(status_code=404, detail="No transactions found")

    if not DEFAULT_PROFILES_FILE.exists():
        raise HTTPException(status_code=404, detail="No profiles found")

    with open(DEFAULT_TRANSACTIONS_FILE) as f:
        transactions = json.load(f)

    with open(DEFAULT_PROFILES_FILE) as f:
        profiles = json.load(f)

    # Calculate stats
    from collections import defaultdict, Counter

    total_txns = sum(len(txns) for txns in transactions.values())

    # Date range
    all_dates = []
    for user_txns in transactions.values():
        all_dates.extend([t["date"] for t in user_txns])
    date_range = (min(all_dates), max(all_dates)) if all_dates else ("", "")

    # Category distribution
    category_counts = Counter()
    for user_txns in transactions.values():
        for txn in user_txns:
            category_counts[txn["personal_finance_category"]] += 1

    # Persona breakdown
    persona_map = {p["user_id"]: p["persona"] for p in profiles}
    persona_stats = defaultdict(lambda: {"users": 0, "transactions": 0, "avg_spending": 0, "avg_income": 0})

    for user_id, user_txns in transactions.items():
        persona = persona_map.get(user_id, "Unknown")
        persona_stats[persona]["users"] += 1
        persona_stats[persona]["transactions"] += len(user_txns)

        income = sum(t["amount"] for t in user_txns if t["amount"] > 0)
        spending = sum(abs(t["amount"]) for t in user_txns if t["amount"] < 0)

        persona_stats[persona]["avg_income"] += income
        persona_stats[persona]["avg_spending"] += spending

    # Calculate averages
    for persona, stats in persona_stats.items():
        if stats["users"] > 0:
            stats["avg_income"] = round(stats["avg_income"] / stats["users"], 2)
            stats["avg_spending"] = round(stats["avg_spending"] / stats["users"], 2)

    return TransactionStatsResponse(
        total_users=len(transactions),
        total_transactions=total_txns,
        date_range=date_range,
        categories=dict(category_counts.most_common(10)),
        personas=dict(persona_stats)
    )


# ===== Liability Endpoints (Story 1.5) =====

class GenerateLiabilitiesRequest(BaseModel):
    """Request model for liability generation."""
    seed: int = Field(default=42, description="Random seed for reproducibility")


class GenerateLiabilitiesResponse(BaseModel):
    """Response model for liability generation."""
    success: bool
    num_users: int
    total_credit_cards: int
    total_student_loans: int
    total_mortgages: int
    message: str


class LiabilityStatsResponse(BaseModel):
    """Response model for liability statistics."""
    total_users: int
    total_credit_cards: int
    total_student_loans: int
    total_mortgages: int
    avg_apr: float
    avg_utilization: float


@app.post("/api/liabilities/generate", response_model=GenerateLiabilitiesResponse)
async def generate_liabilities(request: GenerateLiabilitiesRequest):
    """
    Generate synthetic liabilities for all profiles.

    Requires profiles and transactions to be generated first.
    """
    if not DEFAULT_PROFILES_FILE.exists():
        raise HTTPException(
            status_code=400,
            detail="No profiles found. Generate profiles first using POST /api/generate"
        )

    try:
        result = generate_synthetic_liabilities(
            profiles_path=DEFAULT_PROFILES_FILE,
            transactions_path=DEFAULT_TRANSACTIONS_FILE if DEFAULT_TRANSACTIONS_FILE.exists() else None,
            output_path=DEFAULT_LIABILITIES_FILE,
            seed=request.seed
        )

        # Calculate stats
        total_cc = sum(len(liabs["credit_cards"]) for liabs in result.values())
        total_sl = sum(len(liabs["student_loans"]) for liabs in result.values())
        total_mtg = sum(len(liabs["mortgages"]) for liabs in result.values())

        return GenerateLiabilitiesResponse(
            success=True,
            num_users=len(result),
            total_credit_cards=total_cc,
            total_student_loans=total_sl,
            total_mortgages=total_mtg,
            message=f"Successfully generated liabilities for {len(result)} users"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/liabilities/stats", response_model=LiabilityStatsResponse)
async def get_liability_stats():
    """
    Get statistics about generated liabilities.

    Returns counts and averages for credit cards, loans, and mortgages.
    """
    if not DEFAULT_LIABILITIES_FILE.exists():
        raise HTTPException(status_code=404, detail="No liabilities found")

    with open(DEFAULT_LIABILITIES_FILE) as f:
        liabilities = json.load(f)

    # Calculate stats
    total_cc = sum(len(liabs["credit_cards"]) for liabs in liabilities.values())
    total_sl = sum(len(liabs["student_loans"]) for liabs in liabilities.values())
    total_mtg = sum(len(liabs["mortgages"]) for liabs in liabilities.values())

    # Calculate average APR and utilization from credit cards
    all_aprs = []
    for user_liabs in liabilities.values():
        for cc in user_liabs["credit_cards"]:
            all_aprs.extend(cc["aprs"])

    avg_apr = sum(all_aprs) / len(all_aprs) if all_aprs else 0.0

    return LiabilityStatsResponse(
        total_users=len(liabilities),
        total_credit_cards=total_cc,
        total_student_loans=total_sl,
        total_mortgages=total_mtg,
        avg_apr=round(avg_apr, 4),
        avg_utilization=0.0  # Can be calculated if needed
    )


@app.get("/api/liabilities/user/{user_id}")
async def get_user_liabilities(user_id: str):
    """
    Get liabilities for a specific user.

    Returns credit cards, student loans, and mortgages.
    """
    if not DEFAULT_LIABILITIES_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="No liabilities found. Generate liabilities first using POST /api/liabilities/generate"
        )

    with open(DEFAULT_LIABILITIES_FILE) as f:
        liabilities = json.load(f)

    if user_id not in liabilities:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    return liabilities[user_id]


# ===== Behavioral Signal Endpoints (Epic 2) =====

from datetime import date
from spendsense.features import (
    BehavioralSummaryGenerator,
    SubscriptionDetector,
    SavingsDetector,
    CreditDetector,
    IncomeDetector
)

# Path to database
DB_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "spendsense.db"


@app.get("/api/signals/{user_id}")
async def get_behavioral_summary(
    user_id: str,
    reference_date: Optional[str] = Query(default=None, description="Reference date (YYYY-MM-DD), defaults to today")
):
    """
    Get comprehensive behavioral summary for a user.

    Returns all detected signals: subscriptions, savings, credit, and income
    patterns for both 30-day and 180-day windows.
    """
    if not DB_PATH.exists():
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        # Parse reference date or use today
        if reference_date:
            ref_date = date.fromisoformat(reference_date)
        else:
            ref_date = date.today()

        # Generate behavioral summary
        generator = BehavioralSummaryGenerator(str(DB_PATH))
        summary = generator.generate_summary(
            user_id=user_id,
            reference_date=ref_date
        )

        # Convert to dict for JSON response
        return summary.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@app.get("/api/signals/{user_id}/subscriptions")
async def get_subscription_signals(
    user_id: str,
    window_days: int = Query(default=30, description="Time window in days (30 or 180)"),
    reference_date: Optional[str] = Query(default=None, description="Reference date (YYYY-MM-DD)")
):
    """
    Get subscription pattern detection results for a user.
    """
    if not DB_PATH.exists():
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        ref_date = date.fromisoformat(reference_date) if reference_date else date.today()

        detector = SubscriptionDetector(str(DB_PATH))
        metrics = detector.detect_subscriptions(
            user_id=user_id,
            reference_date=ref_date,
            window_days=window_days
        )

        # Convert to dict
        from dataclasses import asdict
        return asdict(metrics)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/signals/{user_id}/savings")
async def get_savings_signals(
    user_id: str,
    window_days: int = Query(default=30, description="Time window in days (30 or 180)"),
    reference_date: Optional[str] = Query(default=None, description="Reference date (YYYY-MM-DD)")
):
    """
    Get savings behavior detection results for a user.
    """
    if not DB_PATH.exists():
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        ref_date = date.fromisoformat(reference_date) if reference_date else date.today()

        detector = SavingsDetector(str(DB_PATH))
        metrics = detector.detect_savings_patterns(
            user_id=user_id,
            reference_date=ref_date,
            window_days=window_days
        )

        from dataclasses import asdict
        result = asdict(metrics)
        # Convert date to string
        result['reference_date'] = result['reference_date'].isoformat()
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/signals/{user_id}/credit")
async def get_credit_signals(
    user_id: str,
    window_days: int = Query(default=30, description="Time window in days (30 or 180)"),
    reference_date: Optional[str] = Query(default=None, description="Reference date (YYYY-MM-DD)")
):
    """
    Get credit utilization and debt signals for a user.
    """
    if not DB_PATH.exists():
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        ref_date = date.fromisoformat(reference_date) if reference_date else date.today()

        detector = CreditDetector(str(DB_PATH))
        metrics = detector.detect_credit_patterns(
            user_id=user_id,
            reference_date=ref_date,
            window_days=window_days
        )

        from dataclasses import asdict
        result = asdict(metrics)
        # Convert date to string
        result['reference_date'] = result['reference_date'].isoformat()
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/signals/{user_id}/income")
async def get_income_signals(
    user_id: str,
    window_days: int = Query(default=180, description="Time window in days (30 or 180)"),
    reference_date: Optional[str] = Query(default=None, description="Reference date (YYYY-MM-DD)")
):
    """
    Get income stability detection results for a user.
    """
    if not DB_PATH.exists():
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        ref_date = date.fromisoformat(reference_date) if reference_date else date.today()

        detector = IncomeDetector(str(DB_PATH))
        metrics = detector.detect_income_patterns(
            user_id=user_id,
            reference_date=ref_date,
            window_days=window_days
        )

        from dataclasses import asdict
        result = asdict(metrics)
        # Convert dates to strings
        result['reference_date'] = result['reference_date'].isoformat()
        result['payroll_dates'] = [d.isoformat() for d in result['payroll_dates']]
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/profile/{user_id}")
async def get_persona_profile(
    user_id: str,
    time_window: Optional[str] = Query(default=None, description="Time window: '30d', '180d', or None for both")
):
    """
    Get persona assignment profile for a user.

    Returns current persona assignment(s) with complete audit trail including
    all qualifying personas, match evidence, and prioritization reasoning.

    Args:
        user_id: User identifier
        time_window: Optional filter for specific time window

    Returns:
        Persona assignment(s) with audit trail, or 404 if user not found
    """
    if not DB_PATH.exists():
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        from spendsense.personas.assigner import PersonaAssigner

        assigner = PersonaAssigner(str(DB_PATH))

        # Check if user exists
        from spendsense.ingestion.database_writer import User
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        engine = create_engine(f'sqlite:///{DB_PATH}')
        Session = sessionmaker(bind=engine)

        with Session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user is None:
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        # Get assignments
        if time_window and time_window not in ("30d", "180d"):
            raise HTTPException(status_code=400, detail="time_window must be '30d' or '180d'")

        if time_window:
            assignment = assigner.get_assignment(user_id, time_window)
            return {
                "user_id": user_id,
                "assignments": {
                    time_window: assignment
                }
            }
        else:
            # Get both windows
            assignments = assigner.get_assignments_both_windows(user_id)
            return {
                "user_id": user_id,
                "assignments": assignments
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving persona profile: {str(e)}")


@app.get("/api/recommendations")
async def list_recommendations():
    """
    [Future] List generated recommendations.

    This endpoint will be implemented in Epic 4.
    """
    return {
        "message": "Recommendation engine coming in Epic 4",
        "status": "not_implemented"
    }


@app.get("/api/recommendations/{user_id}")
async def get_recommendations(
    user_id: str,
    time_window: str = Query(default="30d", description="Time window (30d or 180d)"),
    generate: bool = Query(default=False, description="Generate new recommendations if true")
):
    """
    Get personalized recommendations for a user (Epic 4 Story 4.5).

    Returns assembled recommendations with education content, partner offers,
    rationales, and mandatory disclaimer.

    Args:
        user_id: User identifier
        time_window: Time window for recommendations (30d or 180d)
        generate: If true, generates new recommendations; if false, returns cached

    Returns:
        Assembled recommendation set with full details

    Raises:
        HTTPException 403: User has not granted consent for data processing
    """
    # ===== CONSENT CHECK (Epic 5 - Story 5.1 AC4) =====
    # Check user consent before any data processing or recommendation generation
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from spendsense.guardrails.consent import ConsentService, ConsentNotGrantedError

    try:
        engine = create_engine(f"sqlite:///{str(DB_PATH)}")
        Session = sessionmaker(bind=engine)
        with Session() as session:
            consent_service = ConsentService(session)
            consent_service.require_consent(user_id)
    except ConsentNotGrantedError as e:
        raise HTTPException(
            status_code=403,
            detail=f"Consent required: {str(e)}"
        )
    except ValueError:
        # User not found - let it proceed, will be caught below
        pass
    # ===== END CONSENT CHECK =====

    from pathlib import Path
    from spendsense.recommendations.content_library import ContentLibrary
    from spendsense.recommendations.partner_offer_library import PartnerOfferLibrary
    from spendsense.recommendations.assembler import RecommendationAssembler
    from spendsense.recommendations.storage import RecommendationStorage

    # Validate time window
    if time_window not in ["30d", "180d"]:
        raise HTTPException(
            status_code=400,
            detail="time_window must be '30d' or '180d'"
        )

    # Initialize storage
    storage = RecommendationStorage(str(DATA_DIR / "recommendations"))

    # If not generating new, try to return cached
    if not generate:
        cached = storage.get_latest_by_user(user_id, time_window)
        if cached:
            return cached

    # Need to generate new recommendations
    if not DB_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="Database not available. Ingest data first."
        )

    try:
        # Get user's persona (from Epic 3)
        from spendsense.personas.assigner import PersonaAssigner
        from datetime import date

        assigner = PersonaAssigner(str(DB_PATH))
        ref_date = date.today()
        persona_result = assigner.assign_persona(user_id, ref_date, time_window)

        if not persona_result:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} not found or no persona assigned"
            )

        # Get behavioral signals
        from spendsense.features.behavioral_summary import BehavioralSummaryGenerator

        summary_generator = BehavioralSummaryGenerator(str(DB_PATH))
        behavioral_summary = summary_generator.generate_summary(user_id, ref_date)

        # Extract signals from behavioral summary based on time window
        # Use the appropriate time window data (30d or 180d)
        credit_data = behavioral_summary.credit_30d if time_window == "30d" else behavioral_summary.credit_180d
        income_data = behavioral_summary.income_30d if time_window == "30d" else behavioral_summary.income_180d
        savings_data = behavioral_summary.savings_30d if time_window == "30d" else behavioral_summary.savings_180d
        subscriptions_data = behavioral_summary.subscriptions_30d if time_window == "30d" else behavioral_summary.subscriptions_180d

        signals = []
        # Derive signals from metrics using correct attribute names
        if credit_data and credit_data.high_utilization_count > 0:
            signals.append("credit_utilization")
        if income_data and income_data.payment_frequency == "irregular":
            signals.append("irregular_income")
        if savings_data and savings_data.emergency_fund_months < 3:
            signals.append("savings_balance")
        if subscriptions_data and subscriptions_data.subscription_count >= 3:
            signals.append("subscription_count")

        # Build user data for eligibility checking
        # Calculate annualized income from window data
        annual_income = 50000  # Default
        if income_data and income_data.total_income > 0:
            # Annualize based on window size
            multiplier = 365 / income_data.window_days
            annual_income = income_data.total_income * multiplier

        user_data = {
            "annual_income": annual_income,
            "credit_score": 700,  # Default - would come from external source
            "existing_accounts": [],
            "credit_utilization": credit_data.aggregate_utilization if credit_data else 0,
            "age": 30,  # Default - would come from profile
            "is_employed": True,  # Default - would come from profile
        }

        # Add personalization data for rationales
        if credit_data:
            user_data["credit_max_utilization_pct"] = credit_data.aggregate_utilization * 100  # Convert to percentage
            user_data["account_name"] = "Credit Card ****0000"  # Placeholder

        if savings_data:
            user_data["savings_balance"] = savings_data.total_savings_balance
            user_data["savings_total_balance"] = savings_data.total_savings_balance  # Alias for templates
            user_data["months_expenses"] = savings_data.emergency_fund_months
            user_data["monthly_expenses"] = savings_data.avg_monthly_expenses
            user_data["monthly_spend"] = savings_data.avg_monthly_expenses  # Alias for templates
            user_data["emergency_fund_goal"] = savings_data.avg_monthly_expenses * 3  # 3-month goal
            user_data["three_month_fund_target"] = savings_data.avg_monthly_expenses * 3
            user_data["target_savings"] = savings_data.avg_monthly_expenses * 6  # 6-month goal
            user_data["category_count"] = 10  # Default estimate for spending categories

            # Calculate interest projections for high-yield savings offers
            user_data["current_interest"] = savings_data.total_savings_balance * 0.005  # Assume 0.5% current rate
            user_data["projected_interest"] = savings_data.total_savings_balance * 0.044  # 4.4% high-yield rate

        if subscriptions_data:
            user_data["subscription_count"] = subscriptions_data.subscription_count
            user_data["subscription_share"] = subscriptions_data.subscription_share * 100  # Convert to percentage
            user_data["monthly_subscription_cost"] = subscriptions_data.monthly_recurring_spend
            user_data["monthly_subscription_total"] = subscriptions_data.monthly_recurring_spend
            user_data["annual_subscription_total"] = subscriptions_data.monthly_recurring_spend * 12
            user_data["potential_savings"] = subscriptions_data.monthly_recurring_spend * 0.3  # Assume 30% savings potential
            user_data["bill_count"] = subscriptions_data.subscription_count  # Alias for templates

        if income_data:
            user_data["has_irregular_income"] = income_data.payment_frequency == "irregular"

        # Initialize libraries and assembler
        config_dir = Path(__file__).parent.parent / "config"
        content_library = ContentLibrary(str(config_dir / "recommendations.yaml"))
        partner_library = PartnerOfferLibrary(str(config_dir / "partner_offers.yaml"))
        assembler = RecommendationAssembler(content_library, partner_library)

        # Assemble recommendations
        rec_set = assembler.assemble_recommendations(
            user_id=user_id,
            persona_id=persona_result.assigned_persona_id,
            signals=signals,
            user_data=user_data,
            time_window=time_window,
        )

        # Save to storage
        storage.save_recommendation_set(rec_set)

        # Return as dict
        return rec_set.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ===== Consent Management Endpoints (Epic 5 - Story 5.1) =====

class ConsentRequest(BaseModel):
    """Request model for consent recording."""
    user_id: str = Field(default="user_MASKED_000", description="User ID to update consent for")
    consent_status: str = Field(default="opted_in", description="Consent status: 'opted_in' or 'opted_out'")
    consent_version: str = Field(default="1.0", description="Consent version")


class ConsentResponse(BaseModel):
    """Response model for consent operations."""
    user_id: str
    consent_status: str
    consent_timestamp: str
    consent_version: str
    message: str


@app.post("/api/consent", response_model=ConsentResponse, status_code=201)
async def record_consent(
    consent_request: ConsentRequest,
    current_operator: TokenData = Depends(require_role("admin"))
):
    """
    Record user consent change (Epic 5 - Story 5.1 AC8, Epic 6 - Story 6.1 AC4).

    Operators can record when users opt-in or opt-out of data processing.
    All consent changes are logged in audit trail.
    **Requires admin role.**

    Args:
        consent_request: Consent request with user_id, consent_status, consent_version
        current_operator: Operator info from JWT token (injected by FastAPI Depends)

    Returns:
        ConsentResponse with updated consent status

    Raises:
        HTTPException 401: Unauthorized (missing or invalid token)
        HTTPException 403: Forbidden (insufficient permissions)
        HTTPException 400: Invalid consent status
        HTTPException 404: User not found
        HTTPException 500: Database error
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from spendsense.guardrails.consent import ConsentService, ConsentStatus, ConsentNotGrantedError

    # Validate consent status
    if consent_request.consent_status not in ['opted_in', 'opted_out']:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid consent_status: {consent_request.consent_status}. Must be 'opted_in' or 'opted_out'"
        )

    try:
        engine = create_engine(f"sqlite:///{str(DB_PATH)}")
        Session = sessionmaker(bind=engine)
        with Session() as session:
            consent_service = ConsentService(session)

            # Record consent
            consent_status_enum = ConsentStatus(consent_request.consent_status)
            result = consent_service.record_consent(
                user_id=consent_request.user_id,
                consent_status=consent_status_enum,
                consent_version=consent_request.consent_version
            )

            return ConsentResponse(
                user_id=result.user_id,
                consent_status=result.consent_status.value,
                consent_timestamp=result.consent_timestamp.isoformat() if result.consent_timestamp else "",
                consent_version=result.consent_version,
                message=f"Consent recorded: {result.consent_status.value}"
            )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error recording consent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/consent/{user_id}", response_model=ConsentResponse)
async def get_consent(
    user_id: str,
    current_operator: TokenData = Depends(require_role("reviewer"))
):
    """
    Get user consent status (Epic 5 - Story 5.1 AC9, Epic 6 - Story 6.1 AC4).

    Operators can check consent status for any user to verify
    data processing permissions.
    **Requires reviewer or admin role.**

    Args:
        user_id: User identifier
        current_operator: Operator info from JWT token (injected by FastAPI Depends)

    Returns:
        ConsentResponse with current consent status

    Raises:
        HTTPException 401: Unauthorized (missing or invalid token)
        HTTPException 403: Forbidden (insufficient permissions)
        HTTPException 404: User not found
        HTTPException 500: Database error
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from spendsense.guardrails.consent import ConsentService

    try:
        engine = create_engine(f"sqlite:///{str(DB_PATH)}")
        Session = sessionmaker(bind=engine)
        with Session() as session:
            consent_service = ConsentService(session)

            # Check consent
            result = consent_service.check_consent(user_id)

            return ConsentResponse(
                user_id=result.user_id,
                consent_status=result.consent_status.value,
                consent_timestamp=result.consent_timestamp.isoformat() if result.consent_timestamp else "",
                consent_version=result.consent_version,
                message=f"Current consent status: {result.consent_status.value}"
            )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error retrieving consent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
