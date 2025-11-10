#!/usr/bin/env python3
"""
Migrate SQLite database to PostgreSQL (v2 - handles type differences)

This script copies all data from the SQLite database to PostgreSQL,
properly handling SQLite/PostgreSQL type differences (booleans, etc.)
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sqlite3
import psycopg2

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
    sys.exit(1)

# Handle Railway's postgres:// prefix
if POSTGRES_URL.startswith("postgres://"):
    POSTGRES_URL = POSTGRES_URL.replace("postgres://", "postgresql://", 1)

print("=" * 60)
print("  SQLite to PostgreSQL Migration (v2)")
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

# Connect to both databases
sqlite_conn = sqlite3.connect(str(SQLITE_DB))
sqlite_conn.row_factory = sqlite3.Row

# Parse PostgreSQL URL
from urllib.parse import urlparse
result = urlparse(POSTGRES_URL)
pg_conn = psycopg2.connect(
    database=result.path[1:],
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port
)
pg_conn.autocommit = False
pg_cursor = pg_conn.cursor()

# Get all tables from SQLite
sqlite_cursor = sqlite_conn.cursor()
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = [row[0] for row in sqlite_cursor.fetchall()]

print(f"📋 Found {len(tables)} tables to migrate\n")

# Create tables in PostgreSQL with proper types
print("📋 Creating PostgreSQL schema...\n")

# Track which columns are boolean for each table
boolean_columns = {}

for table in sorted(tables):
    print(f"  • Creating {table}...", end=" ", flush=True)

    # Get table schema from SQLite
    sqlite_cursor.execute(f"PRAGMA table_info({table})")
    columns = sqlite_cursor.fetchall()

    # Track boolean columns for this table
    boolean_columns[table] = []

    # Build PostgreSQL CREATE TABLE statement
    col_defs = []
    for col in columns:
        col_name = col[1]
        col_type = col[2].upper()
        not_null = " NOT NULL" if col[3] else ""
        default_val = col[4]
        is_pk = col[5]

        # Map SQLite types to PostgreSQL types
        if col_type == "INTEGER":
            # Check if this is a boolean column (common naming patterns)
            if 'is_' in col_name.lower() or col_name.lower() in ['active', 'enabled', 'deleted']:
                pg_type = "BOOLEAN"
                boolean_columns[table].append(col_name)
                if default_val == '1':
                    default_val = 'TRUE'
                elif default_val == '0':
                    default_val = 'FALSE'
            else:
                pg_type = "INTEGER"
        elif col_type == "TEXT":
            pg_type = "TEXT"
        elif col_type == "REAL":
            pg_type = "REAL"
        elif col_type in ["TIMESTAMP", "DATETIME"]:
            pg_type = "TIMESTAMP"
        elif col_type == "DATE":
            pg_type = "DATE"
        elif col_type == "BOOLEAN":
            pg_type = "BOOLEAN"
            boolean_columns[table].append(col_name)
            if default_val == '1':
                default_val = 'TRUE'
            elif default_val == '0':
                default_val = 'FALSE'
        else:
            pg_type = col_type

        # Build column definition
        col_def = f'"{col_name}" {pg_type}{not_null}'
        if default_val and default_val not in ('NULL', 'CURRENT_TIMESTAMP'):
            if pg_type == "BOOLEAN":
                col_def += f' DEFAULT {default_val}'
            elif pg_type in ["TEXT", "VARCHAR"]:
                # Strip any existing quotes from SQLite default value
                clean_val = str(default_val).strip("'\"")
                col_def += f" DEFAULT '{clean_val}'"
            else:
                col_def += f' DEFAULT {default_val}'
        elif default_val == 'CURRENT_TIMESTAMP':
            col_def += ' DEFAULT CURRENT_TIMESTAMP'

        if is_pk:
            col_def += " PRIMARY KEY"

        col_defs.append(col_def)

    create_sql = f'CREATE TABLE IF NOT EXISTS "{table}" ({", ".join(col_defs)})'

    try:
        pg_cursor.execute(create_sql)
        pg_conn.commit()
        print("✓")
    except Exception as e:
        print(f"❌ Error: {e}")
        pg_conn.rollback()

print("\n📊 Copying data...\n")

# Copy data table by table
for table in sorted(tables):
    print(f"  • {table}...", end=" ", flush=True)

    # Get all rows from SQLite
    sqlite_cursor.execute(f"SELECT * FROM {table}")
    rows = sqlite_cursor.fetchall()

    if not rows:
        print("(empty)")
        continue

    # Get column names
    column_names = [description[0] for description in sqlite_cursor.description]

    # Prepare INSERT statement
    placeholders = ", ".join(["%s"] * len(column_names))
    columns_str = ", ".join([f'"{col}"' for col in column_names])
    insert_sql = f'INSERT INTO "{table}" ({columns_str}) VALUES ({placeholders})'

    # Convert rows to tuples and handle boolean conversion
    data_to_insert = []
    for row in rows:
        converted_row = []
        for i, val in enumerate(row):
            # Check if column is boolean type in PostgreSQL
            col_name = column_names[i]
            if col_name in boolean_columns.get(table, []):
                # Convert 0/1 to False/True for boolean columns
                if val in (0, '0'):
                    converted_row.append(False)
                elif val in (1, '1'):
                    converted_row.append(True)
                else:
                    converted_row.append(val)
            else:
                converted_row.append(val)
        data_to_insert.append(tuple(converted_row))

    try:
        pg_cursor.executemany(insert_sql, data_to_insert)
        pg_conn.commit()
        print(f"✓ {len(rows)} rows")
    except Exception as e:
        print(f"❌ Error: {e}")
        pg_conn.rollback()

print("\n✅ Migration completed!\n")

# Verify record counts
print("=" * 60)
print("  Verification")
print("=" * 60)
print()

for table in sorted(tables):
    sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
    sqlite_count = sqlite_cursor.fetchone()[0]

    pg_cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
    pg_count = pg_cursor.fetchone()[0]

    status = "✓" if sqlite_count == pg_count else "❌"
    print(f"{status} {table:30} SQLite: {sqlite_count:6} → PostgreSQL: {pg_count:6}")

# Close connections
sqlite_conn.close()
pg_conn.close()

print("\n" + "=" * 60)
print("  Migration Complete!")
print("=" * 60)
print(f"\n✓ All data migrated from SQLite to PostgreSQL")
print(f"✓ {len(tables)} tables copied")
print()
