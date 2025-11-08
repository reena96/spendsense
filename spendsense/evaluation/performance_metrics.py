"""
Performance & Latency Metrics Module

Measures system performance including:
- End-to-end latency per user (target <5 seconds)
- Component-level latency breakdown
- Throughput (users processed per minute)
- Resource utilization (memory, CPU)
- Latency percentiles (p50, p95, p99)
- Performance bottleneck identification
- Scalability projections
"""

import json
import logging
import os
import psutil
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy.orm import Session

from spendsense.ingestion.database_writer import User
from spendsense.features.behavioral_summary import BehavioralSummaryGenerator
from spendsense.personas.assigner import PersonaAssigner
from spendsense.recommendations.engine import RecommendationEngine
from spendsense.recommendations.generated_models import RecommendationRequest
from spendsense.guardrails.consent import ConsentService
from spendsense.guardrails.eligibility import EligibilityChecker
from spendsense.guardrails.tone import ToneValidator

logger = logging.getLogger(__name__)

# Thread-local storage for component timing
_timing_data = threading.local()


@dataclass
class PerformanceMetrics:
    """
    Performance metrics dataclass.

    Attributes:
        total_latency_seconds: Total time to process all users
        component_latencies: Dict mapping component name to average latency (seconds)
        throughput_users_per_minute: Users processed per minute
        resource_utilization: Dict with memory_mb, cpu_percent metrics
        latency_percentiles: Dict with p50, p95, p99 percentiles (seconds)
        bottlenecks: List of dicts with bottleneck details and optimization suggestions
        scalability_projections: Dict mapping user count to estimated time
        timestamp: When metrics were collected
        per_user_latencies: List of individual user latencies for analysis
        run_metadata: Additional metadata about the run
    """
    total_latency_seconds: float
    component_latencies: Dict[str, float]
    throughput_users_per_minute: float
    resource_utilization: Dict[str, Any]
    latency_percentiles: Dict[str, float]
    bottlenecks: List[Dict[str, Any]]
    scalability_projections: Dict[int, float]
    timestamp: datetime
    per_user_latencies: List[float] = field(default_factory=list)
    run_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with JSON-serializable values."""
        data = asdict(self)
        # Convert datetime to ISO format
        data['timestamp'] = self.timestamp.isoformat()
        # Convert numpy types if present
        for key in ['per_user_latencies']:
            if key in data and data[key]:
                data[key] = [float(x) for x in data[key]]
        return data

    def to_json(self, filepath: Optional[str] = None) -> str:
        """
        Serialize to JSON.

        Args:
            filepath: If provided, save to this file path

        Returns:
            JSON string
        """
        json_str = json.dumps(self.to_dict(), indent=2)
        if filepath:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(json_str)
            logger.info(f"Performance metrics saved to {filepath}")
        return json_str


def _get_timing_storage() -> Dict[str, List[float]]:
    """Get thread-local timing storage."""
    if not hasattr(_timing_data, 'timings'):
        _timing_data.timings = {}
    return _timing_data.timings


def _clear_timing_storage():
    """Clear thread-local timing storage."""
    if hasattr(_timing_data, 'timings'):
        _timing_data.timings.clear()


@contextmanager
def measure_component_latency(component_name: str):
    """
    Context manager to measure execution time of a component.

    Usage:
        with measure_component_latency("signal_detection"):
            # ... component code ...
            pass

    Args:
        component_name: Name of the component being measured
    """
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        storage = _get_timing_storage()
        if component_name not in storage:
            storage[component_name] = []
        storage[component_name].append(elapsed)


def calculate_throughput(user_count: int, total_time_seconds: float) -> float:
    """
    Calculate users processed per minute.

    Args:
        user_count: Number of users processed
        total_time_seconds: Total processing time in seconds

    Returns:
        Users processed per minute

    Example:
        >>> throughput = calculate_throughput(100, 300)  # 100 users in 5 minutes
        >>> print(f"{throughput:.2f} users/min")  # 20.00 users/min
    """
    if total_time_seconds <= 0:
        return 0.0
    return (user_count / total_time_seconds) * 60


def track_resource_utilization() -> Dict[str, Any]:
    """
    Track memory, CPU, and disk I/O using psutil.

    Returns:
        Dict with resource utilization metrics:
        - memory_mb: Current process memory usage in MB
        - memory_percent: Memory usage as % of total system memory
        - cpu_percent: CPU usage percentage (1-second interval)
        - cpu_count: Number of CPU cores
        - disk_read_mb: Disk read bytes in MB
        - disk_write_mb: Disk write bytes in MB

    Example:
        >>> resources = track_resource_utilization()
        >>> print(f"Memory: {resources['memory_mb']:.1f} MB")
        >>> print(f"CPU: {resources['cpu_percent']:.1f}%")
        >>> print(f"Disk Read: {resources['disk_read_mb']:.1f} MB")
    """
    process = psutil.Process()
    memory_info = process.memory_info()

    # Try to get disk I/O counters (not available on all platforms)
    try:
        io_counters = process.io_counters()
        disk_read_mb = io_counters.read_bytes / 1024 / 1024
        disk_write_mb = io_counters.write_bytes / 1024 / 1024
    except (AttributeError, NotImplementedError):
        # I/O counters not available on this platform
        disk_read_mb = 0.0
        disk_write_mb = 0.0

    return {
        "memory_mb": memory_info.rss / 1024 / 1024,
        "memory_percent": process.memory_percent(),
        "cpu_percent": process.cpu_percent(interval=0.1),  # Quick sample
        "cpu_count": psutil.cpu_count(),
        "disk_read_mb": disk_read_mb,
        "disk_write_mb": disk_write_mb,
    }


class PerformanceEvaluator:
    """
    Evaluates system performance and generates comprehensive metrics.

    Measures end-to-end latency, component breakdowns, throughput,
    resource utilization, and generates visualizations.
    """

    def __init__(
        self,
        db_session: Session,
        output_dir: str = "docs/eval",
        db_path: str = "data/processed/spendsense.db",
    ):
        """
        Initialize performance evaluator.

        Args:
            db_session: Database session for querying users
            output_dir: Directory for output files (JSON, visualizations)
            db_path: Path to database file for components that need it
        """
        self.db_session = db_session
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.behavioral_generator = BehavioralSummaryGenerator(db_path)
        self.persona_assigner = PersonaAssigner(db_path)
        self.recommendation_engine = RecommendationEngine()
        self.consent_service = ConsentService(db_session)
        self.eligibility_checker = EligibilityChecker()
        self.tone_validator = ToneValidator()

        logger.info("PerformanceEvaluator initialized")

    def measure_end_to_end_latency(
        self,
        user_ids: List[str],
        time_window: str = "30d",
    ) -> Tuple[float, List[float], Dict[str, List[float]]]:
        """
        Measure total time to process recommendations for given users.

        Args:
            user_ids: List of user IDs to process
            time_window: Time window for behavioral signals (e.g., "30d", "90d")

        Returns:
            Tuple of:
            - Total latency in seconds
            - Per-user latencies (list)
            - Component latencies (dict mapping component to list of times)

        Example:
            >>> evaluator = PerformanceEvaluator(session)
            >>> total, per_user, components = evaluator.measure_end_to_end_latency(
            ...     ["user_MASKED_000", "user_MASKED_001"]
            ... )
            >>> print(f"Total: {total:.2f}s, Avg: {np.mean(per_user):.2f}s")
        """
        _clear_timing_storage()
        per_user_latencies = []

        overall_start = time.time()

        for user_id in user_ids:
            user_start = time.time()

            try:
                # Component 1: Signal Detection
                with measure_component_latency("signal_detection"):
                    signals = self.behavioral_generator.generate_summary(
                        user_id=user_id,
                        reference_date=date.today()
                    )

                # Component 2: Persona Assignment
                with measure_component_latency("persona_assignment"):
                    persona_result = self.persona_assigner.assign_persona(
                        user_id=user_id,
                        reference_date=date.today()
                    )
                    persona_id = persona_result.assigned_persona_id

                # Component 3: Recommendation Matching
                with measure_component_latency("recommendation_matching"):
                    request = RecommendationRequest(
                        user_id=user_id,
                        persona_id=persona_id,
                        time_window=time_window,
                        limit=10
                    )
                    response = self.recommendation_engine.generate_recommendations(
                        request=request,
                        behavioral_signals=signals
                    )

                # Component 4: Guardrail Checks
                if response.recommendations:
                    # Consent check
                    with measure_component_latency("guardrail_consent"):
                        for rec in response.recommendations:
                            self.consent_service.check_consent(
                                user_id=user_id,
                                recommendation_type=rec.rec_type
                            )

                    # Eligibility check
                    with measure_component_latency("guardrail_eligibility"):
                        for rec in response.recommendations:
                            self.eligibility_checker.check_eligibility(
                                user_id=user_id,
                                recommendation=rec,
                                signals=signals
                            )

                    # Tone validation
                    with measure_component_latency("guardrail_tone"):
                        for rec in response.recommendations:
                            self.tone_validator.validate_tone(
                                text=rec.content,
                                context={"rec_type": rec.rec_type}
                            )

                user_elapsed = time.time() - user_start
                per_user_latencies.append(user_elapsed)

            except Exception as e:
                logger.error(f"Error processing user {user_id}: {e}")
                # Still record timing for failed users
                user_elapsed = time.time() - user_start
                per_user_latencies.append(user_elapsed)

        total_latency = time.time() - overall_start
        component_latencies = _get_timing_storage()

        return total_latency, per_user_latencies, component_latencies

    def calculate_latency_percentiles(
        self,
        per_user_latencies: List[float]
    ) -> Dict[str, float]:
        """
        Calculate latency percentiles (p50, p95, p99).

        Args:
            per_user_latencies: List of per-user latency measurements

        Returns:
            Dict with p50, p95, p99 percentile values in seconds

        Example:
            >>> percentiles = evaluator.calculate_latency_percentiles([1.2, 1.5, 1.3, 2.1, 1.4])
            >>> print(f"Median: {percentiles['p50']:.2f}s")
        """
        if not per_user_latencies:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

        latencies = np.array(per_user_latencies)
        return {
            "p50": float(np.percentile(latencies, 50)),
            "p95": float(np.percentile(latencies, 95)),
            "p99": float(np.percentile(latencies, 99)),
        }

    def identify_bottlenecks(
        self,
        component_latencies: Dict[str, List[float]],
        threshold_percent: float = 30.0,
    ) -> List[Dict[str, Any]]:
        """
        Identify components consuming >threshold% of total time with optimization recommendations.

        Args:
            component_latencies: Dict mapping component to list of latencies
            threshold_percent: Threshold percentage (default 30%)

        Returns:
            List of dicts with bottleneck details and optimization suggestions.
            Each dict contains:
            - component: Component name
            - percentage: Percentage of total time
            - severity: 'critical' (>50%), 'high' (>40%), 'medium' (>30%)
            - suggestions: List of optimization recommendations

        Example:
            >>> bottlenecks = evaluator.identify_bottlenecks(components)
            >>> for b in bottlenecks:
            ...     print(f"{b['component']}: {b['percentage']:.1f}% - {b['severity']}")
            ...     for suggestion in b['suggestions']:
            ...         print(f"  - {suggestion}")
        """
        # Calculate average latency per component
        avg_latencies = {
            component: np.mean(times)
            for component, times in component_latencies.items()
        }

        # Calculate total average time
        total_avg = sum(avg_latencies.values())

        if total_avg == 0:
            return []

        # Optimization suggestions mapping
        optimization_suggestions = {
            "signal_detection": [
                "Add database indexing on behavioral_signals table (user_id, timestamp)",
                "Consider caching signal detection results for frequently accessed users",
                "Optimize SQL queries with EXPLAIN QUERY PLAN",
                "Implement batch signal detection for multiple users",
            ],
            "persona_assignment": [
                "Cache persona registry to avoid repeated file reads",
                "Implement batch persona assignment for multiple users",
                "Pre-compute persona criteria scores for faster matching",
                "Consider memoization for frequently assigned personas",
            ],
            "recommendation_matching": [
                "Add indexing to content catalog for faster lookups",
                "Cache recommendation templates and content",
                "Pre-filter content catalog by relevance before scoring",
                "Implement parallel recommendation generation for multiple users",
            ],
            "guardrail_consent": [
                "Cache user consent preferences in memory",
                "Batch consent checks across multiple recommendations",
                "Add database index on consent_preferences table",
                "Implement consent check short-circuiting for known preferences",
            ],
            "guardrail_eligibility": [
                "Parallel eligibility checks across recommendations",
                "Cache eligibility rules and criteria",
                "Pre-filter recommendations by basic eligibility before detailed checks",
                "Optimize signal-based eligibility checks with indexes",
            ],
            "guardrail_tone": [
                "Cache tone validation results for repeated content",
                "Implement rule-based tone caching",
                "Batch tone validation across multiple recommendations",
                "Pre-validate content catalog during system initialization",
            ],
            "rationale_generation": [
                "Cache rationale templates and common patterns",
                "Pre-generate rationale components during recommendation matching",
                "Optimize string formatting and concatenation",
                "Consider async rationale generation for non-critical paths",
            ],
        }

        # Find components exceeding threshold
        bottlenecks = []
        for component, avg_time in avg_latencies.items():
            percentage = (avg_time / total_avg) * 100
            if percentage >= threshold_percent:
                # Determine severity
                if percentage >= 50:
                    severity = "critical"
                elif percentage >= 40:
                    severity = "high"
                else:
                    severity = "medium"

                # Get suggestions or provide generic ones
                suggestions = optimization_suggestions.get(component, [
                    f"Profile {component} to identify specific bottlenecks",
                    f"Add caching for {component} results",
                    f"Consider batch processing in {component}",
                    f"Optimize database queries in {component}",
                ])

                bottlenecks.append({
                    "component": component,
                    "percentage": percentage,
                    "severity": severity,
                    "suggestions": suggestions,
                })

        # Sort by percentage descending (most critical first)
        bottlenecks.sort(key=lambda x: x["percentage"], reverse=True)

        return bottlenecks

    def calculate_scalability_projections(
        self,
        avg_latency_per_user: float,
        user_counts: List[int] = [1000, 10000, 100000],
    ) -> Dict[int, float]:
        """
        Project performance at different user scales (assuming linear scaling).

        Args:
            avg_latency_per_user: Average latency per user in seconds
            user_counts: List of user counts to project for

        Returns:
            Dict mapping user count to estimated total time in seconds

        Example:
            >>> projections = evaluator.calculate_scalability_projections(1.5)
            >>> print(f"10K users: {projections[10000]/60:.1f} minutes")
        """
        return {
            count: avg_latency_per_user * count
            for count in user_counts
        }

    def generate_visualizations(
        self,
        metrics: PerformanceMetrics,
        run_id: str,
    ) -> Dict[str, str]:
        """
        Generate performance visualizations.

        Args:
            metrics: PerformanceMetrics object
            run_id: Unique identifier for this run

        Returns:
            Dict mapping chart name to file path

        Generates:
        - Latency distribution histogram
        - Component breakdown pie chart
        """
        chart_paths = {}

        # 1. Latency Distribution Histogram
        if metrics.per_user_latencies:
            plt.figure(figsize=(10, 6))
            plt.hist(metrics.per_user_latencies, bins=20, edgecolor='black', alpha=0.7)
            plt.axvline(
                metrics.latency_percentiles['p50'],
                color='green',
                linestyle='--',
                label=f"p50: {metrics.latency_percentiles['p50']:.2f}s"
            )
            plt.axvline(
                metrics.latency_percentiles['p95'],
                color='orange',
                linestyle='--',
                label=f"p95: {metrics.latency_percentiles['p95']:.2f}s"
            )
            plt.axvline(
                metrics.latency_percentiles['p99'],
                color='red',
                linestyle='--',
                label=f"p99: {metrics.latency_percentiles['p99']:.2f}s"
            )
            plt.axvline(5.0, color='red', linestyle='-', linewidth=2, label='Target: 5s')
            plt.xlabel('Latency (seconds)')
            plt.ylabel('Number of Users')
            plt.title('Per-User Latency Distribution')
            plt.legend()
            plt.grid(True, alpha=0.3)

            hist_path = self.output_dir / f"latency_distribution_{run_id}.png"
            plt.savefig(hist_path, dpi=150, bbox_inches='tight')
            plt.close()
            chart_paths['latency_distribution'] = str(hist_path)
            logger.info(f"Saved latency distribution to {hist_path}")

        # 2. Component Breakdown Pie Chart
        if metrics.component_latencies:
            plt.figure(figsize=(10, 8))
            components = list(metrics.component_latencies.keys())
            latencies = list(metrics.component_latencies.values())

            # Highlight bottlenecks in red (extract component names from bottleneck dicts)
            bottleneck_components = [b['component'] for b in metrics.bottlenecks]
            colors = ['red' if c in bottleneck_components else 'lightblue' for c in components]

            plt.pie(
                latencies,
                labels=components,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors
            )
            plt.title('Component Latency Breakdown\n(Red = Bottleneck >30%)')

            pie_path = self.output_dir / f"component_breakdown_{run_id}.png"
            plt.savefig(pie_path, dpi=150, bbox_inches='tight')
            plt.close()
            chart_paths['component_breakdown'] = str(pie_path)
            logger.info(f"Saved component breakdown to {pie_path}")

        return chart_paths

    def evaluate(
        self,
        user_ids: Optional[List[str]] = None,
        limit: Optional[int] = None,
        time_window: str = "30d",
        run_id: Optional[str] = None,
    ) -> PerformanceMetrics:
        """
        Run complete performance evaluation.

        Args:
            user_ids: Specific user IDs to evaluate (if None, uses all users)
            limit: Limit number of users to evaluate
            time_window: Time window for behavioral signals
            run_id: Unique identifier for this run (auto-generated if None)

        Returns:
            PerformanceMetrics object with complete results

        Example:
            >>> evaluator = PerformanceEvaluator(session)
            >>> metrics = evaluator.evaluate(limit=50)
            >>> print(f"Throughput: {metrics.throughput_users_per_minute:.1f} users/min")
            >>> print(f"Target met: {metrics.latency_percentiles['p95'] < 5.0}")
        """
        if run_id is None:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        # Get user IDs
        if user_ids is None:
            query = self.db_session.query(User.user_id)
            if limit:
                query = query.limit(limit)
            user_ids = [row[0] for row in query.all()]

        user_count = len(user_ids)
        logger.info(f"Starting performance evaluation for {user_count} users")

        # Track resource utilization at start
        start_resources = track_resource_utilization()

        # Measure end-to-end latency
        total_latency, per_user_latencies, component_latencies_raw = \
            self.measure_end_to_end_latency(user_ids, time_window)

        # Track resource utilization at end
        end_resources = track_resource_utilization()

        # Calculate average component latencies
        component_latencies = {
            component: float(np.mean(times))
            for component, times in component_latencies_raw.items()
        }

        # Calculate metrics
        throughput = calculate_throughput(user_count, total_latency)
        percentiles = self.calculate_latency_percentiles(per_user_latencies)
        bottlenecks = self.identify_bottlenecks(component_latencies_raw)

        avg_latency_per_user = np.mean(per_user_latencies) if per_user_latencies else 0.0
        scalability = self.calculate_scalability_projections(avg_latency_per_user)

        # Resource utilization summary
        resource_util = {
            "start_memory_mb": start_resources["memory_mb"],
            "end_memory_mb": end_resources["memory_mb"],
            "peak_memory_mb": end_resources["memory_mb"],  # Approximation
            "avg_cpu_percent": (start_resources["cpu_percent"] + end_resources["cpu_percent"]) / 2,
            "cpu_count": start_resources["cpu_count"],
            "disk_read_mb": end_resources["disk_read_mb"],
            "disk_write_mb": end_resources["disk_write_mb"],
        }

        # Create metrics object
        metrics = PerformanceMetrics(
            total_latency_seconds=total_latency,
            component_latencies=component_latencies,
            throughput_users_per_minute=throughput,
            resource_utilization=resource_util,
            latency_percentiles=percentiles,
            bottlenecks=bottlenecks,
            scalability_projections=scalability,
            timestamp=datetime.now(),
            per_user_latencies=per_user_latencies,
            run_metadata={
                "user_count": user_count,
                "time_window": time_window,
                "run_id": run_id,
                "avg_latency_per_user": avg_latency_per_user,
                "target_met": percentiles["p95"] < 5.0,
            }
        )

        # Generate visualizations
        chart_paths = self.generate_visualizations(metrics, run_id)
        metrics.run_metadata["chart_paths"] = chart_paths

        # Save metrics to JSON
        json_path = self.output_dir / f"performance_metrics_{run_id}.json"
        metrics.to_json(str(json_path))

        logger.info(f"Performance evaluation complete: {user_count} users in {total_latency:.2f}s")
        logger.info(f"Throughput: {throughput:.2f} users/min")
        logger.info(f"p95 latency: {percentiles['p95']:.2f}s (target: <5s)")

        return metrics

    def evaluate_multiple_runs(
        self,
        num_runs: int = 3,
        **eval_kwargs
    ) -> Tuple[List[PerformanceMetrics], Dict[str, Any]]:
        """
        Run performance evaluation multiple times and calculate consistency metrics.

        Args:
            num_runs: Number of evaluation runs
            **eval_kwargs: Additional arguments passed to evaluate()

        Returns:
            Tuple of:
            - List of PerformanceMetrics from each run
            - Consistency metrics dict with mean, std dev, variance

        Example:
            >>> metrics_list, consistency = evaluator.evaluate_multiple_runs(num_runs=3, limit=50)
            >>> print(f"Avg latency: {consistency['total_latency']['mean']:.2f}s")
            >>> print(f"Std dev: {consistency['total_latency']['std']:.2f}s")
        """
        logger.info(f"Running {num_runs} performance evaluation runs")

        all_metrics = []
        for i in range(num_runs):
            logger.info(f"Run {i+1}/{num_runs}")
            metrics = self.evaluate(**eval_kwargs)
            all_metrics.append(metrics)
            time.sleep(1)  # Brief pause between runs

        # Calculate consistency metrics
        total_latencies = [m.total_latency_seconds for m in all_metrics]
        throughputs = [m.throughput_users_per_minute for m in all_metrics]
        p95_latencies = [m.latency_percentiles['p95'] for m in all_metrics]

        consistency = {
            "total_latency": {
                "mean": float(np.mean(total_latencies)),
                "std": float(np.std(total_latencies)),
                "variance": float(np.var(total_latencies)),
                "cv_percent": float((np.std(total_latencies) / np.mean(total_latencies)) * 100) if np.mean(total_latencies) > 0 else 0.0,
            },
            "throughput": {
                "mean": float(np.mean(throughputs)),
                "std": float(np.std(throughputs)),
                "variance": float(np.var(throughputs)),
                "cv_percent": float((np.std(throughputs) / np.mean(throughputs)) * 100) if np.mean(throughputs) > 0 else 0.0,
            },
            "p95_latency": {
                "mean": float(np.mean(p95_latencies)),
                "std": float(np.std(p95_latencies)),
                "variance": float(np.var(p95_latencies)),
                "cv_percent": float((np.std(p95_latencies) / np.mean(p95_latencies)) * 100) if np.mean(p95_latencies) > 0 else 0.0,
            },
            "num_runs": num_runs,
            "consistent": all([
                consistency["total_latency"]["cv_percent"] < 10,
                consistency["throughput"]["cv_percent"] < 10,
                consistency["p95_latency"]["cv_percent"] < 10,
            ]) if num_runs > 1 else True,
        }

        # Save consistency report
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        consistency_path = self.output_dir / f"consistency_report_{run_id}.json"
        with open(consistency_path, 'w') as f:
            json.dump(consistency, f, indent=2)
        logger.info(f"Consistency report saved to {consistency_path}")

        return all_metrics, consistency
