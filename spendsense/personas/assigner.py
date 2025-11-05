"""
Persona assignment storage and retrieval.

This module handles storing persona assignments to the database with complete
audit trails and retrieving assignments for users.
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spendsense.personas.matcher import PersonaMatcher, PersonaMatch
from spendsense.personas.prioritizer import PersonaPrioritizer, PersonaAssignment
from spendsense.ingestion.database_writer import PersonaAssignmentRecord, Base
from spendsense.features.behavioral_summary import BehavioralSummaryGenerator

logger = logging.getLogger(__name__)


class PersonaAssigner:
    """
    Handles persona assignment workflow and storage.

    Orchestrates the complete persona assignment process:
    1. Generate behavioral summary
    2. Match personas
    3. Prioritize matches
    4. Store assignment with audit trail

    Usage:
        assigner = PersonaAssigner("data/processed/spendsense.db")

        # Assign persona
        assignment = assigner.assign_persona(
            user_id="user_001",
            reference_date=date(2025, 11, 5),
            time_window="30d"
        )

        print(f"Assigned: {assignment.assigned_persona_id}")

        # Retrieve assignment
        retrieved = assigner.get_assignment("user_001", "30d")
    """

    def __init__(self, db_path: str):
        """
        Initialize persona assigner.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)

        # Initialize components
        self.matcher = PersonaMatcher(db_path)
        self.prioritizer = PersonaPrioritizer()
        self.summary_generator = BehavioralSummaryGenerator(db_path)

        # Ensure tables exist
        Base.metadata.create_all(self.engine)

    def assign_persona(
        self,
        user_id: str,
        reference_date: date,
        time_window: str = "30d"
    ) -> PersonaAssignment:
        """
        Complete persona assignment workflow for a user.

        Args:
            user_id: User identifier
            reference_date: Date to use for behavioral analysis
            time_window: "30d" or "180d"

        Returns:
            PersonaAssignment with assigned persona and audit trail

        Raises:
            ValueError: If time_window is invalid
        """
        if time_window not in ("30d", "180d"):
            raise ValueError(f"Invalid time_window: {time_window}. Must be '30d' or '180d'")

        logger.info(f"Starting persona assignment for user {user_id} (window: {time_window})")

        # Step 1: Generate behavioral summary
        logger.debug(f"Generating behavioral summary for {user_id}")
        behavioral_summary = self.summary_generator.generate_summary(user_id, reference_date)

        # Step 2: Match personas
        logger.debug(f"Matching personas for {user_id}")
        matches = self.matcher.match_personas(behavioral_summary, reference_date, time_window)

        # Step 3: Prioritize
        logger.debug(f"Prioritizing personas for {user_id}")
        assignment = self.prioritizer.prioritize_persona(matches)

        # Step 4: Store assignment
        logger.debug(f"Storing assignment for {user_id}")
        assignment_id = self.store_assignment(user_id, time_window, assignment, matches)

        logger.info(
            f"Persona assignment complete for {user_id}: {assignment.assigned_persona_id} "
            f"(assignment_id: {assignment_id})"
        )

        return assignment

    def store_assignment(
        self,
        user_id: str,
        time_window: str,
        assignment: PersonaAssignment,
        matches: List[PersonaMatch]
    ) -> str:
        """
        Store persona assignment to database with audit trail.

        Args:
            user_id: User identifier
            time_window: "30d" or "180d"
            assignment: PersonaAssignment from prioritizer
            matches: List of PersonaMatch objects from matcher

        Returns:
            assignment_id (UUID)
        """
        # Generate unique assignment ID
        assignment_id = str(uuid4())

        # Build match evidence dict: {persona_id: {matched, evidence, matched_conditions}}
        match_evidence = {}
        for match in matches:
            match_evidence[match.persona_id] = {
                "matched": match.matched,
                "evidence": match.evidence,
                "matched_conditions": match.matched_conditions
            }

        # Create database record
        record = PersonaAssignmentRecord(
            assignment_id=assignment_id,
            user_id=user_id,
            time_window=time_window,
            assigned_persona_id=assignment.assigned_persona_id,
            assigned_at=assignment.assigned_at,
            priority=assignment.priority,
            qualifying_personas=assignment.all_qualifying_personas,
            match_evidence=match_evidence,
            prioritization_reason=assignment.prioritization_reason
        )

        # Store to database
        with self.Session() as session:
            session.add(record)
            session.commit()

        logger.debug(f"Stored assignment {assignment_id} for user {user_id}")
        return assignment_id

    def get_assignment(
        self,
        user_id: str,
        time_window: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve latest persona assignment for a user.

        Args:
            user_id: User identifier
            time_window: "30d" or "180d"

        Returns:
            Dictionary with assignment details, or None if not found
        """
        with self.Session() as session:
            record = session.query(PersonaAssignmentRecord).filter(
                PersonaAssignmentRecord.user_id == user_id,
                PersonaAssignmentRecord.time_window == time_window
            ).order_by(
                PersonaAssignmentRecord.assigned_at.desc()
            ).first()

            if record is None:
                return None

            # Convert to dict
            return {
                "assignment_id": record.assignment_id,
                "assigned_persona_id": record.assigned_persona_id,
                "priority": record.priority,
                "assigned_at": record.assigned_at.isoformat(),
                "all_qualifying_personas": record.qualifying_personas,
                "prioritization_reason": record.prioritization_reason,
                "match_evidence": record.match_evidence
            }

    def get_assignments_both_windows(
        self,
        user_id: str
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Retrieve assignments for both time windows.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with keys "30d" and "180d", values are assignment dicts or None
        """
        return {
            "30d": self.get_assignment(user_id, "30d"),
            "180d": self.get_assignment(user_id, "180d")
        }
