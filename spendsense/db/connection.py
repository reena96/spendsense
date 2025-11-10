"""
Database connection utilities

Provides a centralized way to get database connections,
supporting both SQLite (dev) and PostgreSQL (production).
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_database_url() -> str:
    """
    Get database URL from environment or default to SQLite.

    Returns:
        Database URL string for SQLAlchemy
    """
    # Check for DATABASE_URL environment variable (Railway, production)
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Railway uses postgres:// but SQLAlchemy needs postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url

    # Default to SQLite for local development
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "data" / "processed" / "spendsense.db"
    return f"sqlite:///{str(db_path)}"


def get_db_session():
    """
    Create and return a database session.

    Returns:
        SQLAlchemy Session object
    """
    database_url = get_database_url()
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session()


def get_engine():
    """
    Create and return a database engine.

    Returns:
        SQLAlchemy Engine object
    """
    database_url = get_database_url()
    return create_engine(database_url)
