# SpendSense Evaluation Metrics Dashboard

A real-time web dashboard for visualizing SpendSense evaluation metrics across coverage, explainability, performance, auditability, and fairness dimensions.

## Features

- **Real-time Metrics Visualization**: Live updates every 30 seconds
- **Overall Quality Score**: Weighted score across all 5 evaluation dimensions
- **Interactive Charts**:
  - Coverage bar charts
  - Explainability doughnut charts
  - Performance line charts
  - Auditability radar charts
  - Fairness comparison charts
  - Component scores comparison
- **Status Indicators**: Pass/Warning/Fail badges for each metric
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Auto-refresh**: Automatic updates when new evaluation runs complete

## Quick Start

### 1. Generate Evaluation Metrics

First, run the evaluation scripts to generate metrics data:

```bash
# Set PYTHONPATH
export PYTHONPATH=/Users/reena/gauntletai/spendsense

# Run all 5 evaluation modules
venv/bin/python scripts/evaluate_coverage.py --dataset synthetic
venv/bin/python scripts/evaluate_explainability.py --dataset synthetic
venv/bin/python scripts/evaluate_performance.py --dataset synthetic --limit 10
venv/bin/python scripts/evaluate_auditability.py --dataset synthetic
venv/bin/python scripts/evaluate_fairness.py --dataset data/processed/spendsense.db
```

This will create JSON files in `docs/eval/`:
- `coverage_metrics_<timestamp>.json`
- `explainability_metrics_<timestamp>.json`
- `performance_metrics_<timestamp>.json`
- `auditability_metrics_<timestamp>.json`
- `fairness_metrics_<timestamp>.json`

### 2. Launch the Dashboard

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not already installed)
pip install Flask Flask-CORS

# Launch dashboard
python scripts/run_dashboard.py
```

### 3. Open in Browser

Navigate to: **http://localhost:5000**

You should see the evaluation dashboard with live metrics!

## Dashboard Sections

### Overall Score Card
- **Overall Score**: Weighted score (0-100) across all dimensions
- **Grade**: Letter grade A-F based on score
- **Status**: PASS (≥70), WARNING (50-69), FAIL (<50)

### Coverage Metrics
- Persona assignment rate (target: 100%)
- Behavioral signal detection rate (target: 100%)
- Total users evaluated
- Bar chart visualization

### Explainability Metrics
- Rationale presence rate (target: 100%)
- Quality score (1-5 scale, target: ≥3)
- Decision trace completeness (target: 100%)
- Doughnut chart visualization

### Performance Metrics
- Average latency per user (target: <5 seconds)
- Throughput (users/minute)
- Memory usage (MB)
- Line chart with p50/p95/p99 percentiles

### Auditability & Compliance
- Overall compliance score (weighted)
- Consent compliance (**CRITICAL**: must be 100%)
- Eligibility compliance
- Radar chart with all compliance dimensions

### Fairness & Bias
- Overall fairness assessment (PASS/CONCERN/FAIL)
- Demographic parity ratio (target: ≥0.8)
- Bias indicators count
- Comparison chart (when demographic data available)

### Component Scores Comparison
- Bar chart comparing scores across all 5 evaluation dimensions
- Helps identify strengths and weaknesses

## Scoring Methodology

The overall score uses weighted averages:

| Dimension | Weight | Why |
|-----------|--------|-----|
| **Auditability** | 25% | Critical for compliance and regulatory requirements |
| Coverage | 20% | Foundation - need complete data to evaluate |
| Explainability | 20% | Trust and transparency requirements |
| Performance | 20% | User experience and scalability |
| Fairness | 15% | Ethical AI requirements |

**Total: 100%**

### Grade Scale
- **A**: 90-100% - Excellent, production-ready
- **B**: 80-89% - Good, minor improvements needed
- **C**: 70-79% - Acceptable, significant improvements recommended
- **D**: 60-69% - Poor, major issues to address
- **F**: <60% - Failing, not suitable for production

## API Endpoints

The dashboard provides RESTful API endpoints:

### GET /api/metrics
Returns latest metrics from all evaluation modules.

**Response:**
```json
{
  "coverage": { ... },
  "explainability": { ... },
  "performance": { ... },
  "auditability": { ... },
  "fairness": { ... },
  "overall": {
    "score": 85.3,
    "grade": "B",
    "status": "PASS",
    "components": {
      "coverage": 92.1,
      "explainability": 78.5,
      "performance": 88.2,
      "auditability": 95.0,
      "fairness": 50.0
    }
  },
  "timestamp": "2025-11-07T10:30:00Z"
}
```

### GET /api/metrics/history/<metric_type>?limit=10
Returns historical metrics for trend analysis.

**Parameters:**
- `metric_type`: One of `coverage`, `explainability`, `performance`, `auditability`, `fairness`
- `limit`: Number of historical records to return (default: 10)

### GET /api/refresh
Triggers a refresh of metrics (placeholder for future auto-evaluation).

## Configuration

### Port and Host

```bash
# Run on custom port
python scripts/run_dashboard.py --port 8080

# Allow external access (all interfaces)
python scripts/run_dashboard.py --host 0.0.0.0 --port 5000

# Production mode (no debug)
python scripts/run_dashboard.py --no-debug
```

### Evaluation Directory

By default, the dashboard reads metrics from `docs/eval/`. To change this, modify:

```python
# In spendsense/evaluation/dashboard_server.py
dashboard = EvaluationDashboard(eval_dir="path/to/your/eval/dir")
```

## Auto-Refresh

The dashboard automatically refreshes metrics every 30 seconds. You can also manually refresh by clicking the **↻ Refresh** button in the header.

## Troubleshooting

### No Metrics Showing

**Problem**: Dashboard shows "--" for all metrics

**Solution**: Generate evaluation metrics first:
```bash
export PYTHONPATH=/Users/reena/gauntletai/spendsense
venv/bin/python scripts/evaluate_coverage.py
# ... run other evaluation scripts
```

### Port Already in Use

**Problem**: `Address already in use`

**Solution**: Use a different port:
```bash
python scripts/run_dashboard.py --port 8080
```

### Module Not Found Errors

**Problem**: `ModuleNotFoundError: No module named 'spendsense'`

**Solution**: Set PYTHONPATH or install in development mode:
```bash
export PYTHONPATH=/Users/reena/gauntletai/spendsense
# OR
pip install -e .
```

### Missing Flask Dependencies

**Problem**: `ModuleNotFoundError: No module named 'flask'`

**Solution**: Install dependencies:
```bash
pip install Flask Flask-CORS
# OR
pip install -r requirements.txt
```

## Development

### Adding New Metrics

To add new metrics to the dashboard:

1. **Update `dashboard_server.py`**: Add new metric loading in `get_latest_metrics()`
2. **Update `dashboard.html`**: Add new metric card in the metrics grid
3. **Update `dashboard.css`**: Style the new metric card
4. **Update `dashboard.js`**: Add update function and chart for new metric

### Customizing Charts

Charts use Chart.js. To customize:

1. Edit chart configurations in `dashboard.js`
2. See [Chart.js documentation](https://www.chartjs.org/docs/latest/)

## Architecture

```
spendsense/evaluation/
├── dashboard_server.py     # Flask backend API
├── coverage_metrics.py     # Story 7.1
├── explainability_metrics.py  # Story 7.2
├── performance_metrics.py  # Story 7.3
├── auditability_metrics.py # Story 7.4
└── fairness_metrics.py     # Story 7.5

templates/
└── dashboard.html          # Frontend HTML

static/
├── css/
│   └── dashboard.css       # Styles
└── js/
    └── dashboard.js        # Frontend logic + Chart.js

scripts/
└── run_dashboard.py        # Launch script

docs/eval/                  # Metrics data directory
├── coverage_metrics_*.json
├── explainability_metrics_*.json
├── performance_metrics_*.json
├── auditability_metrics_*.json
└── fairness_metrics_*.json
```

## Future Enhancements

- [ ] Export dashboard as PDF report
- [ ] Historical trend charts (metrics over time)
- [ ] Comparison mode (compare two evaluation runs)
- [ ] Alert notifications (email/Slack when scores drop)
- [ ] Custom metric thresholds configuration
- [ ] Integration with CI/CD for automated evaluation
- [ ] Multi-dataset comparison view
- [ ] Drill-down views for detailed analysis

## Support

For issues or questions:
- Check `docs/stories/7-*.md` for evaluation module documentation
- Review evaluation script help: `python scripts/evaluate_<module>.py --help`
- See Epic 7 documentation in `docs/prd/epic-7-evaluation-harness-metrics.md`
