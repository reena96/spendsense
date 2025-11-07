"""
Evaluation Metrics Dashboard Server

A Flask-based web dashboard for visualizing SpendSense evaluation metrics.
Provides real-time visualization of coverage, explainability, performance,
auditability, and fairness metrics.

Usage:
    python -m spendsense.evaluation.dashboard_server

    Then open http://localhost:5000 in your browser
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
from pathlib import Path
from datetime import datetime
import glob
from typing import Dict, List, Optional, Any

app = Flask(__name__,
            template_folder='../../templates',
            static_folder='../../static')
CORS(app)


class EvaluationDashboard:
    """Dashboard data provider for evaluation metrics."""

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
                return json.load(f)
        except Exception as e:
            return {'error': str(e)}

    def _calculate_overall_score(self, metrics: Dict) -> Dict:
        """Calculate weighted overall score from all metrics."""
        score = 0
        weight_total = 0
        components = {}

        # Coverage (20%)
        if metrics.get('coverage'):
            coverage_score = (
                metrics['coverage'].get('persona_assignment_rate', 0) * 0.5 +
                metrics['coverage'].get('behavioral_signal_rate', 0) * 0.5
            ) * 100
            score += coverage_score * 0.20
            weight_total += 0.20
            components['coverage'] = coverage_score

        # Explainability (20%)
        if metrics.get('explainability'):
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
        if metrics.get('performance'):
            perf = metrics['performance']
            # Invert latency (lower is better)
            avg_latency = perf.get('average_latency_per_user', 0)
            latency_score = max(0, (1 - (avg_latency / 5.0))) * 100  # 5s target
            score += latency_score * 0.20
            weight_total += 0.20
            components['performance'] = latency_score

        # Auditability (25% - highest weight due to compliance importance)
        if metrics.get('auditability'):
            audit_score = metrics['auditability'].get('overall_compliance_score', 0)
            score += audit_score * 0.25
            weight_total += 0.25
            components['auditability'] = audit_score

        # Fairness (15%)
        if metrics.get('fairness'):
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
            'components': components
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


# Initialize dashboard
dashboard = EvaluationDashboard()


@app.route('/')
def index():
    """Render the dashboard homepage."""
    return render_template('dashboard.html')


@app.route('/api/metrics')
def get_metrics():
    """API endpoint to get latest metrics."""
    return jsonify(dashboard.get_latest_metrics())


@app.route('/api/metrics/history/<metric_type>')
def get_metrics_history(metric_type):
    """API endpoint to get metrics history for trending."""
    limit = request.args.get('limit', 10, type=int)
    return jsonify(dashboard.get_metrics_history(metric_type, limit))


@app.route('/api/refresh')
def refresh_metrics():
    """Force refresh of metrics (trigger re-evaluation)."""
    # This could trigger re-running evaluation scripts
    return jsonify({'status': 'refresh_triggered', 'timestamp': datetime.now().isoformat()})


def run_dashboard(host: str = '0.0.0.0', port: int = 5000, debug: bool = True):
    """Run the Flask dashboard server."""
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║  SpendSense Evaluation Metrics Dashboard                 ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  Dashboard running at: http://localhost:{port}            ║
    ║                                                           ║
    ║  Visualizing metrics from: docs/eval/                    ║
    ║                                                           ║
    ║  Press Ctrl+C to stop the server                         ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_dashboard()
