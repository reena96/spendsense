"""
Migration script to add signal_id column to persona_assignments table.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("data/processed/spendsense.db")

def migrate():
    """Add signal_id column to persona_assignments table."""
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='persona_assignments'")
        if not cursor.fetchone():
            print("persona_assignments table doesn't exist yet - no migration needed")
            return

        # Check if signal_id column already exists
        cursor.execute("PRAGMA table_info(persona_assignments)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'signal_id' in columns:
            print("signal_id column already exists - no migration needed")
            return

        # Add signal_id column
        print("Adding signal_id column to persona_assignments table...")
        cursor.execute("ALTER TABLE persona_assignments ADD COLUMN signal_id TEXT")
        conn.commit()
        print("Migration successful!")

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
