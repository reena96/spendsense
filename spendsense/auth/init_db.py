"""
Initialize authentication database tables and create seed data.

This script creates the auth-related tables and seeds an initial admin operator.
Run this after setting up the main database to enable operator authentication.

Usage:
    python -m spendsense.auth.init_db
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

from spendsense.auth.operator import create_operator, save_operator


def init_auth_tables(db_path: Path) -> None:
    """
    Create authentication tables in the database.

    Args:
        db_path: Path to SQLite database file
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create operators table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operators (
            operator_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('viewer', 'reviewer', 'admin')),
            created_at TIMESTAMP NOT NULL,
            last_login_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)

    # Create index on username
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_operators_username
        ON operators(username)
    """)

    # Create operator_sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operator_sessions (
            session_id TEXT PRIMARY KEY,
            operator_id TEXT NOT NULL,
            token_hash TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (operator_id) REFERENCES operators(operator_id)
        )
    """)

    # Create indexes on operator_sessions
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sessions_operator
        ON operator_sessions(operator_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sessions_expires
        ON operator_sessions(expires_at)
    """)

    # Create auth_audit_log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_audit_log (
            log_id TEXT PRIMARY KEY,
            operator_id TEXT,
            event_type TEXT NOT NULL,
            endpoint TEXT,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP NOT NULL,
            details TEXT
        )
    """)

    # Create indexes on auth_audit_log
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_auth_audit_timestamp
        ON auth_audit_log(timestamp)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_auth_audit_operator
        ON auth_audit_log(operator_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_auth_audit_event
        ON auth_audit_log(event_type)
    """)

    conn.commit()
    conn.close()

    print(f"✅ Authentication tables created in {db_path}")


def seed_admin_operator(db_path: Path) -> None:
    """
    Create initial admin operator if it doesn't exist.

    Args:
        db_path: Path to SQLite database file
    """
    conn = sqlite3.connect(db_path)

    # Check if any operators exist
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM operators")
    count = cursor.fetchone()[0]

    if count > 0:
        print(f"ℹ️  Operators already exist ({count} found). Skipping seed.")
        conn.close()
        return

    # Create admin operator with default credentials
    # IMPORTANT: Change these credentials in production!
    default_username = "admin"
    default_password = "AdminPass123!"  # Meets complexity requirements

    try:
        admin = create_operator(
            username=default_username,
            password=default_password,
            role="admin",
            operator_id="op_admin_default"
        )

        save_operator(conn, admin)

        print(f"""
✅ Default admin operator created:
   Username: {default_username}
   Password: {default_password}

⚠️  IMPORTANT: Change these credentials immediately in production!
   Use POST /api/operator/change-password endpoint after first login.
""")

    except ValueError as e:
        print(f"❌ Failed to create admin operator: {e}")
        conn.close()
        raise

    conn.close()


def main():
    """Main initialization function."""
    # Determine database path from environment or use default
    db_path = os.getenv("DATABASE_PATH", "data/processed/spendsense.db")
    db_path = Path(db_path)

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        print("   Run data ingestion first to create the main database.")
        return

    print(f"🔧 Initializing authentication for database: {db_path}")

    # Create tables
    init_auth_tables(db_path)

    # Seed admin operator
    seed_admin_operator(db_path)

    print("\n✅ Authentication initialization complete!")
    print("   You can now use the operator authentication endpoints.")


if __name__ == "__main__":
    main()
