"""
Operator Metrics API

Provides evaluation metrics endpoints for the operator dashboard.
Integrates all 5 evaluation modules (coverage, explainability, performance,
auditability, fairness) into the FastAPI operator interface.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json
import glob

router = APIRouter(
    prefix="/api/operator/metrics",
    tags=["Operator Metrics"],
    responses={404: {"description": "Not found"}},
)


class EvaluationMetricsLoader:
    """Loads evaluation metrics from JSON files for the operator dashboard."""

    def __init__(self, eval_dir: str = "docs/eval"):
        self.eval_dir = Path(eval_dir)

    def get_latest_metrics(self) -> Dict[str, Any]:
        """Load the latest metrics from all evaluation modules."""
        metrics = {
            'coverage': self._load_latest('coverage_metrics'),
            'explainability': self._load_latest('explainability_metrics'),
            'performance': self._load_latest('performance_metrics'),
            'auditability': self._load_latest('auditability_metrics'),
            'fairness': self._load_latest('fairness_metrics'),
            'timestamp': datetime.now().isoformat()
        }

        # Calculate overall score
        metrics['overall'] = self._calculate_overall_score(metrics)

        return metrics

    def _load_latest(self, metric_type: str) -> Optional[Dict]:
        """Load the latest JSON file for a specific metric type."""
        pattern = str(self.eval_dir / f"{metric_type}_*.json")
        files = glob.glob(pattern)

        if not files:
            return None

        # Get most recent file
        latest_file = max(files, key=lambda f: Path(f).stat().st_mtime)

        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)
                data['_file_path'] = latest_file
                data['_file_timestamp'] = datetime.fromtimestamp(
                    Path(latest_file).stat().st_mtime
                ).isoformat()
                return data
        except Exception as e:
            return {'error': str(e)}

    def _calculate_overall_score(self, metrics: Dict) -> Dict:
        """Calculate weighted overall score from all metrics."""
        score = 0
        weight_total = 0
        components = {}

        # Coverage (20%)
        if metrics.get('coverage') and not metrics['coverage'].get('error'):
            coverage_score = (
                metrics['coverage'].get('persona_assignment_rate', 0) * 0.5 +
                metrics['coverage'].get('behavioral_signal_rate', 0) * 0.5
            ) * 100
            score += coverage_score * 0.20
            weight_total += 0.20
            components['coverage'] = coverage_score

        # Explainability (20%)
        if metrics.get('explainability') and not metrics['explainability'].get('error'):
            expl = metrics['explainability']
            explainability_score = (
                expl.get('rationale_presence_rate', 0) * 0.5 +
                (expl.get('rationale_quality_score', 0) / 5.0) * 0.3 +
                expl.get('decision_trace_completeness', 0) * 0.2
            ) * 100
            score += explainability_score * 0.20
            weight_total += 0.20
            components['explainability'] = explainability_score

        # Performance (20%)
        if metrics.get('performance') and not metrics['performance'].get('error'):
            perf = metrics['performance']
            # Invert latency (lower is better)
            avg_latency = perf.get('average_latency_per_user', 0)
            latency_score = max(0, (1 - (avg_latency / 5.0))) * 100  # 5s target
            score += latency_score * 0.20
            weight_total += 0.20
            components['performance'] = latency_score

        # Auditability (25% - highest weight due to compliance importance)
        if metrics.get('auditability') and not metrics['auditability'].get('error'):
            audit_score = metrics['auditability'].get('overall_compliance_score', 0)
            score += audit_score * 0.25
            weight_total += 0.25
            components['auditability'] = audit_score

        # Fairness (15%)
        if metrics.get('fairness') and not metrics['fairness'].get('error'):
            fair = metrics['fairness']
            assessment = fair.get('overall_fairness_assessment', 'N/A')
            fairness_score = {
                'PASS': 100,
                'CONCERN': 60,
                'FAIL': 30,
                'N/A': 50
            }.get(assessment, 50)
            score += fairness_score * 0.15
            weight_total += 0.15
            components['fairness'] = fairness_score

        # Normalize if weights don't add up to 1.0
        if weight_total > 0:
            score = score / weight_total

        # Determine grade and status
        grade = 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D' if score >= 60 else 'F'
        status = 'PASS' if score >= 70 else 'WARNING' if score >= 50 else 'FAIL'

        return {
            'score': round(score, 1),
            'grade': grade,
            'status': status,
            'components': components,
            'weights': {
                'coverage': 0.20,
                'explainability': 0.20,
                'performance': 0.20,
                'auditability': 0.25,
                'fairness': 0.15
            }
        }

    def get_metrics_history(self, metric_type: str, limit: int = 10) -> List[Dict]:
        """Get historical metrics for trend analysis."""
        pattern = str(self.eval_dir / f"{metric_type}_*.json")
        files = glob.glob(pattern)

        if not files:
            return []

        # Sort by modification time, most recent first
        files.sort(key=lambda f: Path(f).stat().st_mtime, reverse=True)
        files = files[:limit]

        history = []
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data['file_timestamp'] = datetime.fromtimestamp(
                        Path(file_path).stat().st_mtime
                    ).isoformat()
                    history.append(data)
            except Exception:
                continue

        return history


# Initialize metrics loader
metrics_loader = EvaluationMetricsLoader()


@router.get("/latest")
async def get_latest_metrics():
    """
    Get the latest evaluation metrics from all modules.

    Returns:
        - coverage: Persona assignment and signal detection metrics
        - explainability: Rationale quality and decision trace metrics
        - performance: Latency, throughput, and resource utilization
        - auditability: Compliance and audit trail metrics
        - fairness: Demographic parity and bias detection
        - overall: Weighted score, grade, and status
    """
    try:
        metrics = metrics_loader.get_latest_metrics()
        return JSONResponse(content=metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading metrics: {str(e)}")


@router.get("/history/{metric_type}")
async def get_metrics_history(metric_type: str, limit: int = 10):
    """
    Get historical metrics for trend analysis.

    Args:
        metric_type: One of: coverage, explainability, performance, auditability, fairness
        limit: Number of historical records to return (default: 10)

    Returns:
        List of historical metrics in reverse chronological order
    """
    valid_types = ['coverage', 'explainability', 'performance', 'auditability', 'fairness']
    if metric_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric_type. Must be one of: {', '.join(valid_types)}"
        )

    try:
        history = metrics_loader.get_metrics_history(metric_type, limit)
        return JSONResponse(content={'metric_type': metric_type, 'history': history, 'count': len(history)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading history: {str(e)}")


@router.get("/summary")
async def get_metrics_summary():
    """
    Get a simplified metrics summary for dashboard widgets.

    Returns key metrics only for quick dashboard display.
    """
    try:
        metrics = metrics_loader.get_latest_metrics()

        summary = {
            'overall_score': metrics['overall']['score'],
            'overall_grade': metrics['overall']['grade'],
            'overall_status': metrics['overall']['status'],
            'coverage_rate': None,
            'explainability_score': None,
            'performance_latency': None,
            'compliance_score': None,
            'fairness_status': None,
            'timestamp': metrics['timestamp']
        }

        # Extract key values
        if metrics.get('coverage'):
            summary['coverage_rate'] = metrics['coverage'].get('persona_assignment_rate', 0) * 100

        if metrics.get('explainability'):
            summary['explainability_score'] = metrics['explainability'].get('rationale_quality_score', 0)

        if metrics.get('performance'):
            summary['performance_latency'] = metrics['performance'].get('average_latency_per_user', 0)

        if metrics.get('auditability'):
            summary['compliance_score'] = metrics['auditability'].get('overall_compliance_score', 0)

        if metrics.get('fairness'):
            summary['fairness_status'] = metrics['fairness'].get('overall_fairness_assessment', 'N/A')

        return JSONResponse(content=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading summary: {str(e)}")


@router.get("/components")
async def get_component_scores():
    """
    Get individual component scores for comparison chart.

    Returns the weighted score for each evaluation dimension.
    """
    try:
        metrics = metrics_loader.get_latest_metrics()
        overall = metrics.get('overall', {})

        return JSONResponse(content={
            'components': overall.get('components', {}),
            'weights': overall.get('weights', {}),
            'overall_score': overall.get('score', 0),
            'timestamp': metrics['timestamp']
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading components: {str(e)}")
