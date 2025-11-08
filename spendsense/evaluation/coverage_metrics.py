"""
Coverage metrics calculation for persona assignment and behavioral signal detection.

This module calculates user coverage metrics showing:
- Percentage of users with assigned personas (target: 100%)
- Percentage of users with ≥3 detected behavioral signals (target: 100%)
- Distribution of users across 6 persona types
- Completion rates by time window (30-day vs 180-day)
- Missing data analysis with failure reasons
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from spendsense.ingestion.database_writer import User, PersonaAssignmentRecord, Base
from spendsense.personas.registry import load_persona_registry

logger = logging.getLogger(__name__)


@dataclass
class CoverageMetrics:
    """
    Coverage metrics for persona assignment and behavioral signal detection.

    Attributes:
        timestamp: When metrics were calculated (ISO 8601)
        dataset: Dataset identifier (e.g., "synthetic_50_users", "real_production")

        persona_assignment_rate: Percentage of users with assigned persona (0.0-1.0)
        behavioral_signal_rate: Percentage of users with ≥3 detected signals (0.0-1.0)

        persona_distribution: Count of users per persona type

        window_completion_30d: Percentage of users with 30-day data completeness
        window_completion_180d: Percentage of users with 180-day data completeness

        missing_data_users: List of users missing personas/signals with reasons

        total_users: Total number of users evaluated
        users_with_personas: Count of users with assigned personas
        users_with_3plus_signals: Count of users with ≥3 behavioral signals
    """
    timestamp: str
    dataset: str

    persona_assignment_rate: float
    behavioral_signal_rate: float

    persona_distribution: Dict[str, int]

    window_completion_30d: float
    window_completion_180d: float

    missing_data_users: List[Dict[str, Any]]

    total_users: int
    users_with_personas: int
    users_with_3plus_signals: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


def calculate_persona_coverage(db_path: str, time_window: str = "30d") -> Dict[str, Any]:
    """
    Calculate persona assignment coverage metrics.

    Args:
        db_path: Path to SQLite database
        time_window: Time window for analysis ("30d" or "180d")

    Returns:
        Dictionary with:
            - assignment_rate: Percentage of users with assigned persona
            - total_users: Total user count
            - users_with_personas: Count with assigned personas
            - users_without_personas: List of user_ids without personas

    Raises:
        ValueError: If time_window is invalid
    """
    if time_window not in ("30d", "180d"):
        raise ValueError(f"Invalid time_window: {time_window}. Must be '30d' or '180d'")

    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Query all users
        total_users = session.query(User).count()

        if total_users == 0:
            logger.warning("No users found in database")
            return {
                'assignment_rate': 0.0,
                'total_users': 0,
                'users_with_personas': 0,
                'users_without_personas': []
            }

        # Query users with persona assignments for this time window
        assigned_users = session.query(PersonaAssignmentRecord.user_id).filter(
            PersonaAssignmentRecord.time_window == time_window,
            PersonaAssignmentRecord.assigned_persona_id != 'unclassified'
        ).distinct().all()

        users_with_personas = len(assigned_users)
        assigned_user_ids = {row[0] for row in assigned_users}

        # Find users without personas
        all_user_ids = {row[0] for row in session.query(User.user_id).all()}
        users_without_personas = list(all_user_ids - assigned_user_ids)

        assignment_rate = users_with_personas / total_users if total_users > 0 else 0.0

        logger.info(
            f"Persona coverage ({time_window}): {users_with_personas}/{total_users} "
            f"({assignment_rate:.1%})"
        )

        return {
            'assignment_rate': assignment_rate,
            'total_users': total_users,
            'users_with_personas': users_with_personas,
            'users_without_personas': users_without_personas
        }

    finally:
        session.close()


def calculate_persona_distribution(db_path: str, time_window: str = "30d") -> Dict[str, int]:
    """
    Calculate distribution of users across persona types.

    Args:
        db_path: Path to SQLite database
        time_window: Time window for analysis ("30d" or "180d")

    Returns:
        Dictionary mapping persona IDs to user counts

    Raises:
        ValueError: If time_window is invalid
    """
    if time_window not in ("30d", "180d"):
        raise ValueError(f"Invalid time_window: {time_window}. Must be '30d' or '180d'")

    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Load expected personas from registry
        registry = load_persona_registry()
        expected_personas = registry.get_persona_ids()
        distribution = {persona: 0 for persona in expected_personas}

        # Query persona assignments
        results = session.query(
            PersonaAssignmentRecord.assigned_persona_id,
            func.count(PersonaAssignmentRecord.user_id.distinct())
        ).filter(
            PersonaAssignmentRecord.time_window == time_window,
            PersonaAssignmentRecord.assigned_persona_id != 'unclassified'
        ).group_by(
            PersonaAssignmentRecord.assigned_persona_id
        ).all()

        # Update distribution with actual counts
        for persona_id, count in results:
            if persona_id in distribution:
                distribution[persona_id] = count
            else:
                # Track unexpected personas
                logger.warning(f"Unexpected persona ID found: {persona_id}")
                distribution[persona_id] = count

        logger.info(f"Persona distribution ({time_window}): {distribution}")

        return distribution

    finally:
        session.close()


def calculate_signal_coverage(
    db_path: str,
    time_window: str = "30d",
    min_signals: int = 3
) -> Dict[str, Any]:
    """
    Calculate behavioral signal coverage metrics.

    Args:
        db_path: Path to SQLite database
        time_window: Time window for analysis ("30d" or "180d")
        min_signals: Minimum signal count threshold (default: 3)

    Returns:
        Dictionary with:
            - signal_coverage_rate: Percentage of users with ≥min_signals
            - total_users: Total user count
            - users_with_min_signals: Count meeting threshold
            - users_below_threshold: List of user_ids below threshold with signal counts

    Raises:
        ValueError: If time_window is invalid
    """
    if time_window not in ("30d", "180d"):
        raise ValueError(f"Invalid time_window: {time_window}. Must be '30d' or '180d'")

    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Query all users
        all_users = session.query(User.user_id).all()
        total_users = len(all_users)

        if total_users == 0:
            logger.warning("No users found in database")
            return {
                'signal_coverage_rate': 0.0,
                'total_users': 0,
                'users_with_min_signals': 0,
                'users_below_threshold': []
            }

        # Count signals per user by examining qualifying_personas in assignments
        # qualifying_personas is a JSON array of persona IDs that matched
        # We'll count distinct qualifying personas as a proxy for signal count
        # since each persona qualification requires specific behavioral signals

        users_meeting_threshold = []
        users_below_threshold = []

        for (user_id,) in all_users:
            # Get the most recent persona assignment for this user and time window
            assignment = session.query(PersonaAssignmentRecord).filter(
                PersonaAssignmentRecord.user_id == user_id,
                PersonaAssignmentRecord.time_window == time_window
            ).order_by(PersonaAssignmentRecord.assigned_at.desc()).first()

            if assignment and assignment.qualifying_personas:
                # Count qualifying personas as signal strength indicator
                # Each qualifying persona implies detection of specific behavioral signals
                signal_count = len(assignment.qualifying_personas)

                if signal_count >= min_signals:
                    users_meeting_threshold.append(user_id)
                else:
                    users_below_threshold.append({
                        'user_id': user_id,
                        'signal_count': signal_count,
                        'qualifying_personas': assignment.qualifying_personas
                    })
            else:
                # No assignment or no qualifying personas
                users_below_threshold.append({
                    'user_id': user_id,
                    'signal_count': 0,
                    'qualifying_personas': []
                })

        users_with_min_signals = len(users_meeting_threshold)
        signal_coverage_rate = users_with_min_signals / total_users if total_users > 0 else 0.0

        logger.info(
            f"Signal coverage ({time_window}, ≥{min_signals} signals): "
            f"{users_with_min_signals}/{total_users} ({signal_coverage_rate:.1%})"
        )

        return {
            'signal_coverage_rate': signal_coverage_rate,
            'total_users': total_users,
            'users_with_min_signals': users_with_min_signals,
            'users_below_threshold': users_below_threshold
        }

    finally:
        session.close()


def analyze_missing_data(
    db_path: str,
    time_window: str = "30d"
) -> List[Dict[str, Any]]:
    """
    Analyze users with missing personas or insufficient signals.

    Identifies reasons for missing data:
    - insufficient_transaction_history: User has less than required transaction data
    - no_qualifying_signals: User has data but no behavioral signals meet thresholds
    - no_persona_assignment: User has qualifying personas but none assigned
    - processing_error: Assignment failed or is incomplete

    Args:
        db_path: Path to SQLite database
        time_window: Time window for analysis ("30d" or "180d")

    Returns:
        List of dictionaries with user_id, issue_type, and details

    Raises:
        ValueError: If time_window is invalid
    """
    if time_window not in ("30d", "180d"):
        raise ValueError(f"Invalid time_window: {time_window}. Must be '30d' or '180d'")

    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        missing_data_report = []

        # Get all users
        all_users = session.query(User.user_id).all()

        for (user_id,) in all_users:
            # Check for persona assignment
            assignment = session.query(PersonaAssignmentRecord).filter(
                PersonaAssignmentRecord.user_id == user_id,
                PersonaAssignmentRecord.time_window == time_window
            ).order_by(PersonaAssignmentRecord.assigned_at.desc()).first()

            if not assignment:
                # No assignment record at all
                missing_data_report.append({
                    'user_id': user_id,
                    'issue_type': 'processing_error',
                    'severity': 'high',
                    'details': f'No persona assignment record found for {time_window} window',
                    'qualifying_personas': [],
                    'signal_count': 0
                })
                continue

            # Check if assigned persona is "unclassified"
            if assignment.assigned_persona_id == 'unclassified':
                if not assignment.qualifying_personas or len(assignment.qualifying_personas) == 0:
                    # No qualifying personas means no signals detected
                    missing_data_report.append({
                        'user_id': user_id,
                        'issue_type': 'no_qualifying_signals',
                        'severity': 'medium',
                        'details': 'User has transaction data but no behavioral signals meet persona thresholds',
                        'qualifying_personas': [],
                        'signal_count': 0
                    })
                else:
                    # Has qualifying personas but still unclassified (shouldn't happen with prioritizer)
                    missing_data_report.append({
                        'user_id': user_id,
                        'issue_type': 'no_persona_assignment',
                        'severity': 'high',
                        'details': f'User has {len(assignment.qualifying_personas)} qualifying personas but none assigned',
                        'qualifying_personas': assignment.qualifying_personas,
                        'signal_count': len(assignment.qualifying_personas)
                    })

            # Check for insufficient signals even if persona assigned
            elif len(assignment.qualifying_personas) < 3:
                missing_data_report.append({
                    'user_id': user_id,
                    'issue_type': 'insufficient_behavioral_signals',
                    'severity': 'low',
                    'details': f'User has persona but only {len(assignment.qualifying_personas)} qualifying signals (target: ≥3)',
                    'qualifying_personas': assignment.qualifying_personas,
                    'signal_count': len(assignment.qualifying_personas),
                    'assigned_persona': assignment.assigned_persona_id
                })

        # Sort by severity: high > medium > low
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        missing_data_report.sort(key=lambda x: severity_order.get(x['severity'], 3))

        logger.info(
            f"Missing data analysis ({time_window}): "
            f"{len(missing_data_report)} users with issues"
        )

        return missing_data_report

    finally:
        session.close()


def calculate_coverage_metrics(
    db_path: str,
    dataset: str = "synthetic_dataset",
    time_window_30d: bool = True,
    time_window_180d: bool = True
) -> CoverageMetrics:
    """
    Calculate comprehensive coverage metrics for persona assignment and signals.

    Args:
        db_path: Path to SQLite database
        dataset: Dataset identifier for tracking (e.g., "synthetic_50_users")
        time_window_30d: Include 30-day window metrics
        time_window_180d: Include 180-day window metrics

    Returns:
        CoverageMetrics object with all calculated metrics

    Raises:
        ValueError: If neither time window is enabled
    """
    if not time_window_30d and not time_window_180d:
        raise ValueError("At least one time window must be enabled")

    logger.info(f"Calculating coverage metrics for dataset: {dataset}")

    # Use 30d as primary window for overall metrics, fallback to 180d
    primary_window = "30d" if time_window_30d else "180d"

    # Calculate persona coverage
    persona_cov = calculate_persona_coverage(db_path, primary_window)

    # Calculate persona distribution
    persona_dist = calculate_persona_distribution(db_path, primary_window)

    # Calculate signal coverage
    signal_cov = calculate_signal_coverage(db_path, primary_window, min_signals=3)

    # Calculate window completion rates
    window_30d_rate = 0.0
    window_180d_rate = 0.0

    if time_window_30d:
        cov_30d = calculate_persona_coverage(db_path, "30d")
        window_30d_rate = cov_30d['assignment_rate']

    if time_window_180d:
        cov_180d = calculate_persona_coverage(db_path, "180d")
        window_180d_rate = cov_180d['assignment_rate']

    # Analyze missing data
    missing_data = analyze_missing_data(db_path, primary_window)

    # Build CoverageMetrics object
    metrics = CoverageMetrics(
        timestamp=datetime.utcnow().isoformat(),
        dataset=dataset,
        persona_assignment_rate=persona_cov['assignment_rate'],
        behavioral_signal_rate=signal_cov['signal_coverage_rate'],
        persona_distribution=persona_dist,
        window_completion_30d=window_30d_rate,
        window_completion_180d=window_180d_rate,
        missing_data_users=missing_data,
        total_users=persona_cov['total_users'],
        users_with_personas=persona_cov['users_with_personas'],
        users_with_3plus_signals=signal_cov['users_with_min_signals']
    )

    logger.info(
        f"Coverage metrics calculated: "
        f"Persona={metrics.persona_assignment_rate:.1%}, "
        f"Signals={metrics.behavioral_signal_rate:.1%}"
    )

    return metrics


def save_coverage_metrics(metrics: CoverageMetrics, output_dir: Path) -> Path:
    """
    Save coverage metrics to JSON file with timestamp.

    Args:
        metrics: CoverageMetrics object to save
        output_dir: Directory to save metrics file

    Returns:
        Path to saved JSON file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp (use current time with microseconds for uniqueness)
    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"coverage_metrics_{timestamp_str}.json"
    output_path = output_dir / filename

    # Save to JSON
    with open(output_path, 'w') as f:
        json.dump(metrics.to_dict(), f, indent=2)

    # Also save as "latest" for easy reference
    latest_path = output_dir / "coverage_metrics_latest.json"
    with open(latest_path, 'w') as f:
        json.dump(metrics.to_dict(), f, indent=2)

    logger.info(f"Coverage metrics saved to {output_path}")

    return output_path


def load_previous_metrics(output_dir: Path, count: int = 10) -> List[CoverageMetrics]:
    """
    Load previous coverage metrics from JSON files for trend analysis.

    Args:
        output_dir: Directory containing metrics files
        count: Maximum number of previous metrics to load

    Returns:
        List of CoverageMetrics objects, sorted by timestamp (oldest first)
    """
    output_dir = Path(output_dir)

    if not output_dir.exists():
        logger.warning(f"Metrics directory does not exist: {output_dir}")
        return []

    # Find all coverage metrics JSON files (excluding "latest")
    # Pattern: coverage_metrics_YYYYMMDD_HHMMSS.json
    metric_files = sorted(
        [f for f in output_dir.glob("coverage_metrics_[0-9]*.json")
         if "latest" not in f.name],
        reverse=True  # Most recent first
    )[:count]

    metrics_list = []

    for file_path in reversed(metric_files):  # Reverse to get oldest first
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Reconstruct CoverageMetrics from dict
                metrics = CoverageMetrics(**data)
                metrics_list.append(metrics)
        except Exception as e:
            logger.warning(f"Failed to load metrics from {file_path}: {e}")
            continue

    logger.info(f"Loaded {len(metrics_list)} previous metric files")

    return metrics_list


def calculate_coverage_trends(
    current_metrics: CoverageMetrics,
    previous_metrics: List[CoverageMetrics]
) -> Dict[str, Any]:
    """
    Calculate coverage trends by comparing current with previous metrics.

    Args:
        current_metrics: Most recent CoverageMetrics
        previous_metrics: List of previous CoverageMetrics for comparison

    Returns:
        Dictionary with trend analysis:
            - persona_assignment_trend: Change in assignment rate
            - signal_coverage_trend: Change in signal coverage rate
            - persona_distribution_changes: Changes in persona counts
            - improvement_summary: Human-readable summary
    """
    if not previous_metrics:
        return {
            'persona_assignment_trend': None,
            'signal_coverage_trend': None,
            'persona_distribution_changes': {},
            'improvement_summary': 'No previous metrics available for comparison'
        }

    # Compare with most recent previous metrics
    prev = previous_metrics[-1]

    # Calculate deltas
    persona_delta = current_metrics.persona_assignment_rate - prev.persona_assignment_rate
    signal_delta = current_metrics.behavioral_signal_rate - prev.behavioral_signal_rate

    # Calculate persona distribution changes
    dist_changes = {}
    for persona in current_metrics.persona_distribution.keys():
        current_count = current_metrics.persona_distribution.get(persona, 0)
        prev_count = prev.persona_distribution.get(persona, 0)
        change = current_count - prev_count
        if change != 0:
            dist_changes[persona] = change

    # Generate summary
    summary_parts = []

    if abs(persona_delta) >= 0.01:  # 1% threshold
        direction = "improved" if persona_delta > 0 else "decreased"
        summary_parts.append(
            f"Persona assignment {direction} by {abs(persona_delta):.1%} "
            f"({prev.persona_assignment_rate:.1%} → {current_metrics.persona_assignment_rate:.1%})"
        )
    else:
        summary_parts.append(f"Persona assignment stable at {current_metrics.persona_assignment_rate:.1%}")

    if abs(signal_delta) >= 0.01:  # 1% threshold
        direction = "improved" if signal_delta > 0 else "decreased"
        summary_parts.append(
            f"Signal coverage {direction} by {abs(signal_delta):.1%} "
            f"({prev.behavioral_signal_rate:.1%} → {current_metrics.behavioral_signal_rate:.1%})"
        )
    else:
        summary_parts.append(f"Signal coverage stable at {current_metrics.behavioral_signal_rate:.1%}")

    improvement_summary = ". ".join(summary_parts)

    return {
        'persona_assignment_trend': persona_delta,
        'signal_coverage_trend': signal_delta,
        'persona_distribution_changes': dist_changes,
        'improvement_summary': improvement_summary,
        'comparison_timestamp': prev.timestamp
    }
