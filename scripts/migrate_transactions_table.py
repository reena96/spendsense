#!/usr/bin/env python3
"""
Migrate ONLY the transactions table from SQLite to PostgreSQL

Fixes boolean column detection for the transactions table.
"""

import os
import sys
from pathlib import Path
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
    sys.exit(1)

# Handle Railway's postgres:// prefix
if POSTGRES_URL.startswith("postgres://"):
    POSTGRES_URL = POSTGRES_URL.replace("postgres://", "postgresql://", 1)

print("=" * 60)
print("  Transactions Table Migration")
print("=" * 60)
print(f"\nSource: {SQLITE_DB}")
print(f"Target: {POSTGRES_URL[:50]}...")
print("\nThis will drop and recreate the transactions table")
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

# Get transactions table schema from SQLite
sqlite_cursor = sqlite_conn.cursor()
sqlite_cursor.execute("PRAGMA table_info(transactions)")
columns = sqlite_cursor.fetchall()

# Known boolean columns in transactions table
BOOLEAN_COLUMNS = ['pending']  # Add any other boolean columns here

print("📋 Dropping existing transactions table in PostgreSQL...")
try:
    pg_cursor.execute('DROP TABLE IF EXISTS "transactions" CASCADE')
    pg_conn.commit()
    print("✓ Table dropped\n")
except Exception as e:
    print(f"❌ Error: {e}")
    pg_conn.rollback()
    sys.exit(1)

print("📋 Creating transactions table with correct types...")

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
        # Check if this is a known boolean column
        if col_name in BOOLEAN_COLUMNS:
            pg_type = "BOOLEAN"
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
            clean_val = str(default_val).strip("'\"")
            col_def += f" DEFAULT '{clean_val}'"
        else:
            col_def += f' DEFAULT {default_val}'
    elif default_val == 'CURRENT_TIMESTAMP':
        col_def += ' DEFAULT CURRENT_TIMESTAMP'

    if is_pk:
        col_def += " PRIMARY KEY"

    col_defs.append(col_def)

create_sql = f'CREATE TABLE "transactions" ({", ".join(col_defs)})'

try:
    pg_cursor.execute(create_sql)
    pg_conn.commit()
    print("✓ Table created\n")
except Exception as e:
    print(f"❌ Error: {e}")
    pg_conn.rollback()
    sys.exit(1)

print("📊 Copying transactions data...\n")

# Get all transactions from SQLite
sqlite_cursor.execute("SELECT * FROM transactions")
rows = sqlite_cursor.fetchall()

if not rows:
    print("  ⚠️  No transactions found in SQLite")
else:
    # Get column names
    column_names = [description[0] for description in sqlite_cursor.description]

    # Prepare INSERT statement
    placeholders = ", ".join(["%s"] * len(column_names))
    columns_str = ", ".join([f'"{col}"' for col in column_names])
    insert_sql = f'INSERT INTO "transactions" ({columns_str}) VALUES ({placeholders})'

    # Convert rows to tuples and handle boolean conversion
    data_to_insert = []
    for row in rows:
        converted_row = []
        for i, val in enumerate(row):
            col_name = column_names[i]
            # Convert boolean columns
            if col_name in BOOLEAN_COLUMNS:
                if val in (0, '0', None):
                    converted_row.append(False if val is not None else None)
                elif val in (1, '1'):
                    converted_row.append(True)
                else:
                    converted_row.append(bool(val))
            else:
                converted_row.append(val)
        data_to_insert.append(tuple(converted_row))

    # Insert in batches
    batch_size = 1000
    total = len(data_to_insert)

    for i in range(0, total, batch_size):
        batch = data_to_insert[i:i + batch_size]
        try:
            pg_cursor.executemany(insert_sql, batch)
            pg_conn.commit()
            print(f"  ✓ Inserted {min(i + batch_size, total)}/{total} rows", end="\r", flush=True)
        except Exception as e:
            print(f"\n  ❌ Error at row {i}: {e}")
            pg_conn.rollback()
            sys.exit(1)

    print(f"\n  ✓ Successfully inserted all {total} rows")

print("\n✅ Transactions table migration completed!\n")

# Verify record counts
sqlite_cursor.execute("SELECT COUNT(*) FROM transactions")
sqlite_count = sqlite_cursor.fetchone()[0]

pg_cursor.execute('SELECT COUNT(*) FROM "transactions"')
pg_count = pg_cursor.fetchone()[0]

print("=" * 60)
print("  Verification")
print("=" * 60)
status = "✓" if sqlite_count == pg_count else "❌"
print(f"\n{status} transactions: SQLite {sqlite_count} → PostgreSQL {pg_count}")

if sqlite_count == pg_count:
    print("\n✅ Migration successful! All records match.")
else:
    print(f"\n⚠️  Warning: Record count mismatch!")

# Close connections
sqlite_conn.close()
pg_conn.close()

print("\n" + "=" * 60)
