"""
User authentication endpoints for end-user login.

Provides simple authentication for end users to access their personalized dashboards.
"""

import sqlite3
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

# Router for user auth endpoints
router = APIRouter(prefix="/api/user", tags=["user-auth"])

# Simple password for all users (demo purposes)
DEMO_PASSWORD = "spendsense2024"


# ===== Request/Response Models =====

class UserLoginRequest(BaseModel):
    """User login request model."""
    email: str = Field(..., description="User email (name@gmail.com)")
    password: str = Field(..., description="User password")


class UserLoginResponse(BaseModel):
    """User login response model."""
    user_id: str
    name: str
    email: str
    message: str


# ===== Helper Functions =====

def get_db_connection() -> sqlite3.Connection:
    """Get database connection."""
    db_path = Path(__file__).parent.parent.parent / "data" / "processed" / "spendsense.db"
    if not db_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database not found at {db_path}"
        )
    return sqlite3.connect(str(db_path))


# ===== Endpoints =====

@router.post("/login", response_model=UserLoginResponse, status_code=status.HTTP_200_OK)
async def user_login(login_data: UserLoginRequest):
    """
    User login endpoint.

    Authenticates user with email and password. Returns user information.
    All users use the same password for demo purposes.

    Args:
        login_data: Login credentials

    Returns:
        UserLoginResponse with user details

    Raises:
        HTTPException 401: Invalid credentials
        HTTPException 500: Database error
    """
    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Verify password
        if login_data.password != DEMO_PASSWORD:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Extract name from email (before @gmail.com)
        if not login_data.email.endswith("@gmail.com"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email format. Use name@gmail.com"
            )

        # Get name from email
        email_name = login_data.email.replace("@gmail.com", "").strip()

        # Convert email name to match database name format
        # Email: allison.hill@gmail.com -> Name: Allison Hill
        name_parts = email_name.split(".")
        db_name = " ".join([part.capitalize() for part in name_parts])

        # Find user by name
        cursor.execute(
            "SELECT user_id, name FROM users WHERE LOWER(name) = LOWER(?)",
            (db_name,)
        )

        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"No user found for {login_data.email}"
            )

        user_id, name = user

        return UserLoginResponse(
            user_id=user_id,
            name=name,
            email=login_data.email,
            message=f"Welcome back, {name}!"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}"
        )
    finally:
        if db:
            db.close()


@router.get("/list", status_code=status.HTTP_200_OK)
async def list_users():
    """
    List all available users (for demo purposes).

    Returns list of users with their emails for login.
    """
    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("SELECT user_id, name FROM users ORDER BY name LIMIT 20")
        users = cursor.fetchall()

        user_list = []
        for user_id, name in users:
            # Convert name to email format
            # Allison Hill -> allison.hill@gmail.com
            email_name = name.lower().replace(" ", ".")
            email = f"{email_name}@gmail.com"

            user_list.append({
                "user_id": user_id,
                "name": name,
                "email": email
            })

        return {
            "users": user_list,
            "password": DEMO_PASSWORD,
            "message": "Use any email from the list with the provided password to log in"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
    finally:
        if db:
            db.close()
