"""
Test script to assign personas to sample users for UI testing.
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
    """Assign personas to sample users."""
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        return

    print("Assigning personas to sample users...")
    print()

    # Initialize assigner
    assigner = PersonaAssigner(str(DB_PATH))

    # Get first 5 users
    engine = create_engine(f'sqlite:///{DB_PATH}')
    Session = sessionmaker(bind=engine)
    session = Session()

    users = session.query(User).limit(5).all()

    # Reference date
    reference_date = date(2025, 11, 5)

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

        except Exception as e:
            print(f"  ERROR: {e}")

        print()

    session.close()

    print("Done! Test the UI at: http://127.0.0.1:8000")
    print(f"Try these user IDs: {', '.join([u.user_id for u in users])}")

if __name__ == "__main__":
    main()
