"""
Test script to assign personas to users for UI testing.

This script assigns personas to all users in the database for both 30d and 180d windows.
"""

from datetime import date
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spendsense.personas.assigner import PersonaAssigner
from spendsense.ingestion.database_writer import User

# Database path
DB_PATH = Path("data/processed/spendsense.db")

def main():
    """Assign personas to all users."""
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        print("Please run data generation first.")
        return

    print("Starting persona assignments...")
    print(f"Database: {DB_PATH}")
    print()

    # Initialize assigner
    assigner = PersonaAssigner(str(DB_PATH))

    # Get all users
    engine = create_engine(f'sqlite:///{DB_PATH}')
    Session = sessionmaker(bind=engine)
    session = Session()

    users = session.query(User).all()
    print(f"Found {len(users)} users in database")
    print()

    # Reference date for analysis
    reference_date = date(2025, 11, 5)

    # Assign personas for all users
    success_count = 0
    error_count = 0

    for user in users:
        try:
            print(f"Processing {user.user_id}...")

            # Assign for 30d window
            assignment_30d = assigner.assign_persona(
                user_id=user.user_id,
                reference_date=reference_date,
                time_window="30d"
            )
            print(f"  30d: {assignment_30d.assigned_persona_id} (priority {assignment_30d.priority})")

            # Assign for 180d window
            assignment_180d = assigner.assign_persona(
                user_id=user.user_id,
                reference_date=reference_date,
                time_window="180d"
            )
            print(f"  180d: {assignment_180d.assigned_persona_id} (priority {assignment_180d.priority})")

            success_count += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            error_count += 1

        print()

    session.close()

    print("=" * 60)
    print(f"Persona assignment complete!")
    print(f"Success: {success_count} users")
    print(f"Errors: {error_count} users")
    print()
    print("You can now test the UI at: http://127.0.0.1:8000")
    print("Navigate to the 'Persona Assignment' tab and enter a user_id")

if __name__ == "__main__":
    main()
