"""
Database configuration and paths.

Centralized database path configuration for all modules.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Default database path (can be overridden via environment variable)
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "spendsense.db"

# Get database path from environment or use default
DB_PATH = Path(os.environ.get("SPENDSENSE_DB_PATH", str(DEFAULT_DB_PATH)))

# Create database engine and session factory
_engine = None
_SessionLocal = None


def get_db_path() -> Path:
    """
    Get the database file path.

    Returns:
        Path to the SQLite database file

    Example:
        >>> from spendsense.config.database import get_db_path
        >>> db_path = get_db_path()
    """
    return DB_PATH


def get_db_session() -> Session:
    """
    Get a new database session.

    Returns:
        SQLAlchemy Session instance

    Example:
        >>> from spendsense.config.database import get_db_session
        >>> session = get_db_session()
        >>> # Use session for queries
        >>> session.close()
    """
    global _engine, _SessionLocal

    if _engine is None:
        _engine = create_engine(f"sqlite:///{DB_PATH}")
        _SessionLocal = sessionmaker(bind=_engine)

    return _SessionLocal()
