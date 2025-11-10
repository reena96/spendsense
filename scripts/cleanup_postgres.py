#!/usr/bin/env python3
"""
Cleanup PostgreSQL database - drops all tables and recreates schema

WARNING: This will delete ALL data in the database!
"""

import os
import sys
from urllib.parse import urlparse
import psycopg2

# PostgreSQL database URL from environment
POSTGRES_URL = os.getenv("DATABASE_URL")

if not POSTGRES_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set!")
    sys.exit(1)

# Handle Railway's postgres:// prefix
if POSTGRES_URL.startswith("postgres://"):
    POSTGRES_URL = POSTGRES_URL.replace("postgres://", "postgresql://", 1)

print("=" * 60)
print("  PostgreSQL Database Cleanup")
print("=" * 60)
print(f"\nTarget: {POSTGRES_URL[:50]}...")
print("\n⚠️  WARNING: This will DROP ALL TABLES and DATA!")
print("=" * 60)
print()

# Confirm before proceeding
response = input("Continue? (yes/no): ")
if response.lower() != "yes":
    print("Cleanup cancelled.")
    sys.exit(0)

print("\n🔄 Cleaning database...\n")

# Parse PostgreSQL URL
result = urlparse(POSTGRES_URL)
pg_conn = psycopg2.connect(
    database=result.path[1:],
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port
)
pg_conn.autocommit = True
pg_cursor = pg_conn.cursor()

try:
    # Drop all tables in the public schema
    print("  • Dropping all tables...", end=" ", flush=True)
    pg_cursor.execute("""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
    """)
    print("✓")

    print("\n✅ Database cleaned successfully!\n")
    print("You can now run the migration script again.")

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
finally:
    pg_conn.close()

print("=" * 60)
