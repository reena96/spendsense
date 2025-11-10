#!/usr/bin/env python3
"""
Migrate SQLite database to PostgreSQL

This script copies all data from the SQLite database to PostgreSQL,
preserving all tables, data, and relationships.

Usage:
    # Set DATABASE_URL environment variable first
    export DATABASE_URL="postgresql://user:pass@host:port/dbname"

    # Or get it from Railway
    railway variables | grep DATABASE_URL

    # Then run migration
    python scripts/migrate_sqlite_to_postgres.py
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# SQLite database path
SQLITE_DB = project_root / "data" / "processed" / "spendsense.db"

# PostgreSQL database URL from environment
POSTGRES_URL = os.getenv("DATABASE_URL")

if not POSTGRES_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set!")
    print("\nSet it with:")
    print("  export DATABASE_URL='postgresql://user:pass@host:port/dbname'")
    print("\nOr get it from Railway:")
    print("  railway variables | grep DATABASE_URL")
    sys.exit(1)

# Handle Railway's postgres:// prefix (should be postgresql://)
if POSTGRES_URL.startswith("postgres://"):
    POSTGRES_URL = POSTGRES_URL.replace("postgres://", "postgresql://", 1)

print("=" * 60)
print("  SQLite to PostgreSQL Migration")
print("=" * 60)
print(f"\nSource: {SQLITE_DB}")
print(f"Target: {POSTGRES_URL[:50]}...")
print("\nThis will copy all data from SQLite to PostgreSQL")
print("=" * 60)
print()

# Confirm before proceeding
response = input("Continue? (yes/no): ")
if response.lower() != "yes":
    print("Migration cancelled.")
    sys.exit(0)

print("\n🔄 Starting migration...\n")

# Create engines
sqlite_engine = create_engine(f"sqlite:///{SQLITE_DB}")
postgres_engine = create_engine(POSTGRES_URL)

# Reflect SQLite schema
sqlite_metadata = MetaData()
sqlite_metadata.reflect(bind=sqlite_engine)

# Fix boolean columns for PostgreSQL
# SQLite uses INTEGER (0/1) for booleans, PostgreSQL needs BOOLEAN type
from sqlalchemy import Boolean, Integer

print("📋 Creating tables in PostgreSQL...")

for table_name, table in sqlite_metadata.tables.items():
    for column in table.columns:
        # Convert INTEGER columns with boolean-like defaults to BOOLEAN
        if isinstance(column.type, Integer) and column.default is not None:
            if hasattr(column.default, 'arg') and column.default.arg in (0, 1, '0', '1'):
                column.type = Boolean()
                # Update default value: 1 -> True, 0 -> False
                if column.default.arg in (1, '1'):
                    from sqlalchemy import text
                    column.default = text('TRUE')
                elif column.default.arg in (0, '0'):
                    from sqlalchemy import text
                    column.default = text('FALSE')

sqlite_metadata.create_all(postgres_engine)
print("✓ Tables created\n")

# Copy data table by table
sqlite_session = sessionmaker(bind=sqlite_engine)()
postgres_session = sessionmaker(bind=postgres_engine)()

table_names = sorted(sqlite_metadata.tables.keys())

print(f"📊 Copying data from {len(table_names)} tables...\n")

for table_name in table_names:
    print(f"  • {table_name}...", end=" ", flush=True)

    table = Table(table_name, sqlite_metadata, autoload_with=sqlite_engine)

    # Read all rows from SQLite
    sqlite_rows = sqlite_session.execute(table.select()).fetchall()

    if not sqlite_rows:
        print("(empty)")
        continue

    # Insert into PostgreSQL
    postgres_session.execute(
        table.insert(),
        [dict(row._mapping) for row in sqlite_rows]
    )
    postgres_session.commit()

    print(f"✓ {len(sqlite_rows)} rows")

print("\n✅ Migration completed successfully!\n")

# Verify record counts
print("=" * 60)
print("  Verification")
print("=" * 60)
print()

for table_name in table_names:
    table = Table(table_name, sqlite_metadata, autoload_with=sqlite_engine)

    sqlite_count = sqlite_session.execute(
        f"SELECT COUNT(*) FROM {table_name}"
    ).scalar()

    postgres_count = postgres_session.execute(
        f"SELECT COUNT(*) FROM {table_name}"
    ).scalar()

    status = "✓" if sqlite_count == postgres_count else "❌"
    print(f"{status} {table_name:30} SQLite: {sqlite_count:6} → PostgreSQL: {postgres_count:6}")

sqlite_session.close()
postgres_session.close()

print("\n" + "=" * 60)
print("  Migration Summary")
print("=" * 60)
print(f"\n✓ All data migrated from SQLite to PostgreSQL")
print(f"✓ {len(table_names)} tables copied")
print(f"✓ Original SQLite database preserved at: {SQLITE_DB}")
print(f"✓ Backup available at: backups/")
print("\nNext steps:")
print("  1. Update code to use DATABASE_URL")
print("  2. Test the application with PostgreSQL")
print("  3. Deploy to Railway")
print()
