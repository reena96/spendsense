"""
SpendSense API - FastAPI backend for testing and development.

This API provides endpoints for all SpendSense features and serves
a web UI for visual testing and exploration.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
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


# API Models
class GenerateProfilesRequest(BaseModel):
    """Request model for profile generation."""
    num_users: int = Field(ge=50, le=100, default=100, description="Number of profiles to generate (50-100)")
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
    version="1.0.0"
)

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
    """
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
    """
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
    """
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
