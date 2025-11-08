"""
Unit tests for performance metrics module.

Tests cover:
- End-to-end latency measurement
- Component latency breakdown
- Throughput calculation
- Resource utilization tracking
- Latency percentile calculation
- Bottleneck identification
- Scalability projections
- Visualization generation
- Multiple run consistency
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock, patch, MagicMock

import numpy as np
import pytest

from spendsense.evaluation.performance_metrics import (
    PerformanceMetrics,
    PerformanceEvaluator,
    measure_component_latency,
    calculate_throughput,
    track_resource_utilization,
    _get_timing_storage,
    _clear_timing_storage,
)


class TestPerformanceMetricsDataclass:
    """Test PerformanceMetrics dataclass."""

    def test_create_metrics_object(self):
        """Test creating PerformanceMetrics object."""
        metrics = PerformanceMetrics(
            total_latency_seconds=10.5,
            component_latencies={"comp1": 5.0, "comp2": 5.5},
            throughput_users_per_minute=6.0,
            resource_utilization={"memory_mb": 100.0, "cpu_percent": 50.0},
            latency_percentiles={"p50": 2.0, "p95": 4.0, "p99": 5.0},
            bottlenecks=["comp2"],
            scalability_projections={1000: 1000.0, 10000: 10000.0},
            timestamp=datetime.now(),
        )

        assert metrics.total_latency_seconds == 10.5
        assert metrics.component_latencies["comp1"] == 5.0
        assert metrics.throughput_users_per_minute == 6.0
        assert "comp2" in metrics.bottlenecks

    def test_to_dict_serialization(self):
        """Test converting metrics to dictionary."""
        timestamp = datetime.now()
        metrics = PerformanceMetrics(
            total_latency_seconds=10.5,
            component_latencies={"comp1": 5.0},
            throughput_users_per_minute=6.0,
            resource_utilization={"memory_mb": 100.0},
            latency_percentiles={"p50": 2.0, "p95": 4.0, "p99": 5.0},
            bottlenecks=["comp1"],
            scalability_projections={1000: 1000.0},
            timestamp=timestamp,
            per_user_latencies=[1.0, 2.0, 3.0],
        )

        data = metrics.to_dict()
        assert data["total_latency_seconds"] == 10.5
        assert data["timestamp"] == timestamp.isoformat()
        assert data["per_user_latencies"] == [1.0, 2.0, 3.0]

    def test_to_json_without_file(self):
        """Test JSON serialization without saving to file."""
        metrics = PerformanceMetrics(
            total_latency_seconds=10.5,
            component_latencies={"comp1": 5.0},
            throughput_users_per_minute=6.0,
            resource_utilization={"memory_mb": 100.0},
            latency_percentiles={"p50": 2.0, "p95": 4.0, "p99": 5.0},
            bottlenecks=[],
            scalability_projections={1000: 1000.0},
            timestamp=datetime.now(),
        )

        json_str = metrics.to_json()
        data = json.loads(json_str)
        assert data["total_latency_seconds"] == 10.5
        assert "timestamp" in data

    def test_to_json_with_file(self, tmp_path):
        """Test JSON serialization with file save."""
        metrics = PerformanceMetrics(
            total_latency_seconds=10.5,
            component_latencies={"comp1": 5.0},
            throughput_users_per_minute=6.0,
            resource_utilization={"memory_mb": 100.0},
            latency_percentiles={"p50": 2.0, "p95": 4.0, "p99": 5.0},
            bottlenecks=[],
            scalability_projections={1000: 1000.0},
            timestamp=datetime.now(),
        )

        filepath = tmp_path / "metrics.json"
        metrics.to_json(str(filepath))

        assert filepath.exists()
        with open(filepath) as f:
            data = json.load(f)
        assert data["total_latency_seconds"] == 10.5


class TestComponentLatencyMeasurement:
    """Test component latency measurement context manager."""

    def test_measure_component_latency_context_manager(self):
        """Test measuring component execution time."""
        _clear_timing_storage()

        with measure_component_latency("test_component"):
            time.sleep(0.1)  # Simulate work

        storage = _get_timing_storage()
        assert "test_component" in storage
        assert len(storage["test_component"]) == 1
        assert storage["test_component"][0] >= 0.1

    def test_measure_multiple_components(self):
        """Test measuring multiple components."""
        _clear_timing_storage()

        with measure_component_latency("comp1"):
            time.sleep(0.05)

        with measure_component_latency("comp2"):
            time.sleep(0.05)

        storage = _get_timing_storage()
        assert "comp1" in storage
        assert "comp2" in storage
        assert len(storage["comp1"]) == 1
        assert len(storage["comp2"]) == 1

    def test_measure_same_component_multiple_times(self):
        """Test measuring same component multiple times (multiple users)."""
        _clear_timing_storage()

        for _ in range(3):
            with measure_component_latency("signal_detection"):
                time.sleep(0.01)

        storage = _get_timing_storage()
        assert len(storage["signal_detection"]) == 3
        assert all(t >= 0.01 for t in storage["signal_detection"])

    def test_measure_component_with_exception(self):
        """Test that timing is recorded even if exception occurs."""
        _clear_timing_storage()

        try:
            with measure_component_latency("error_component"):
                time.sleep(0.05)
                raise ValueError("Test error")
        except ValueError:
            pass

        storage = _get_timing_storage()
        assert "error_component" in storage
        assert len(storage["error_component"]) == 1
        assert storage["error_component"][0] >= 0.05


class TestThroughputCalculation:
    """Test throughput calculation."""

    def test_calculate_throughput_basic(self):
        """Test basic throughput calculation."""
        throughput = calculate_throughput(100, 300)  # 100 users in 5 minutes
        assert throughput == 20.0

    def test_calculate_throughput_high_speed(self):
        """Test throughput with fast processing."""
        throughput = calculate_throughput(100, 60)  # 100 users in 1 minute
        assert throughput == 100.0

    def test_calculate_throughput_slow_processing(self):
        """Test throughput with slow processing."""
        throughput = calculate_throughput(10, 600)  # 10 users in 10 minutes
        assert throughput == 1.0

    def test_calculate_throughput_zero_time(self):
        """Test throughput with zero time (edge case)."""
        throughput = calculate_throughput(100, 0)
        assert throughput == 0.0

    def test_calculate_throughput_negative_time(self):
        """Test throughput with negative time (edge case)."""
        throughput = calculate_throughput(100, -10)
        assert throughput == 0.0

    def test_calculate_throughput_single_user(self):
        """Test throughput with single user."""
        throughput = calculate_throughput(1, 3.5)
        assert throughput == pytest.approx(17.14, rel=0.01)


class TestResourceUtilization:
    """Test resource utilization tracking."""

    @patch('psutil.Process')
    @patch('psutil.cpu_count')
    def test_track_resource_utilization_basic(self, mock_cpu_count, mock_process_class):
        """Test basic resource tracking."""
        # Mock process
        mock_process = Mock()
        mock_memory_info = Mock()
        mock_memory_info.rss = 100 * 1024 * 1024  # 100 MB
        mock_process.memory_info.return_value = mock_memory_info
        mock_process.memory_percent.return_value = 5.0
        mock_process.cpu_percent.return_value = 25.0

        # Mock I/O counters
        mock_io_counters = Mock()
        mock_io_counters.read_bytes = 50 * 1024 * 1024  # 50 MB
        mock_io_counters.write_bytes = 25 * 1024 * 1024  # 25 MB
        mock_process.io_counters.return_value = mock_io_counters

        mock_process_class.return_value = mock_process

        # Mock CPU count
        mock_cpu_count.return_value = 8

        resources = track_resource_utilization()

        assert resources["memory_mb"] == 100.0
        assert resources["memory_percent"] == 5.0
        assert resources["cpu_percent"] == 25.0
        assert resources["cpu_count"] == 8
        assert resources["disk_read_mb"] == 50.0
        assert resources["disk_write_mb"] == 25.0

    @patch('psutil.Process')
    @patch('psutil.cpu_count')
    def test_track_resource_utilization_high_memory(self, mock_cpu_count, mock_process_class):
        """Test tracking with high memory usage."""
        mock_process = Mock()
        mock_memory_info = Mock()
        mock_memory_info.rss = 2048 * 1024 * 1024  # 2 GB
        mock_process.memory_info.return_value = mock_memory_info
        mock_process.memory_percent.return_value = 25.0
        mock_process.cpu_percent.return_value = 50.0

        # Mock I/O counters
        mock_io_counters = Mock()
        mock_io_counters.read_bytes = 100 * 1024 * 1024  # 100 MB
        mock_io_counters.write_bytes = 50 * 1024 * 1024  # 50 MB
        mock_process.io_counters.return_value = mock_io_counters

        mock_process_class.return_value = mock_process
        mock_cpu_count.return_value = 4

        resources = track_resource_utilization()

        assert resources["memory_mb"] == 2048.0
        assert resources["cpu_count"] == 4
        assert resources["disk_read_mb"] == 100.0
        assert resources["disk_write_mb"] == 50.0

    @patch('psutil.Process')
    @patch('psutil.cpu_count')
    def test_track_resource_utilization_no_io_counters(self, mock_cpu_count, mock_process_class):
        """Test tracking when I/O counters are not available."""
        mock_process = Mock()
        mock_memory_info = Mock()
        mock_memory_info.rss = 100 * 1024 * 1024  # 100 MB
        mock_process.memory_info.return_value = mock_memory_info
        mock_process.memory_percent.return_value = 5.0
        mock_process.cpu_percent.return_value = 25.0

        # Simulate I/O counters not available (platform dependent)
        mock_process.io_counters.side_effect = AttributeError("Not available")

        mock_process_class.return_value = mock_process
        mock_cpu_count.return_value = 8

        resources = track_resource_utilization()

        assert resources["memory_mb"] == 100.0
        assert resources["memory_percent"] == 5.0
        assert resources["cpu_percent"] == 25.0
        assert resources["cpu_count"] == 8
        assert resources["disk_read_mb"] == 0.0
        assert resources["disk_write_mb"] == 0.0


class TestPerformanceEvaluator:
    """Test PerformanceEvaluator class."""

    @pytest.mark.skip(reason="Integration test requiring real database - skipping in unit tests")
    def test_evaluator_initialization(self, tmp_path):
        """Test evaluator initialization."""
        mock_session = Mock()
        evaluator = PerformanceEvaluator(
            db_session=mock_session,
            output_dir=str(tmp_path)
        )

        assert evaluator.db_session == mock_session
        assert evaluator.output_dir == tmp_path
        assert evaluator.behavioral_generator is not None
        assert evaluator.persona_assigner is not None
        assert evaluator.recommendation_engine is not None

    def test_calculate_latency_percentiles_basic(self, tmp_path):
        """Test latency percentile calculation."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        latencies = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        percentiles = evaluator.calculate_latency_percentiles(latencies)

        assert percentiles["p50"] == 5.5  # Median
        assert percentiles["p95"] == pytest.approx(9.55, rel=0.001)
        assert percentiles["p99"] == pytest.approx(9.91, rel=0.001)

    def test_calculate_latency_percentiles_with_outliers(self, tmp_path):
        """Test percentiles with outlier values."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        latencies = [1.0] * 95 + [10.0] * 5  # 95% at 1s, 5% at 10s
        percentiles = evaluator.calculate_latency_percentiles(latencies)

        assert percentiles["p50"] == 1.0
        assert percentiles["p95"] > 1.0
        assert percentiles["p99"] > percentiles["p95"]

    def test_calculate_latency_percentiles_empty(self, tmp_path):
        """Test percentiles with empty list."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        percentiles = evaluator.calculate_latency_percentiles([])

        assert percentiles["p50"] == 0.0
        assert percentiles["p95"] == 0.0
        assert percentiles["p99"] == 0.0

    def test_calculate_latency_percentiles_single_value(self, tmp_path):
        """Test percentiles with single value."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        percentiles = evaluator.calculate_latency_percentiles([2.5])

        assert percentiles["p50"] == 2.5
        assert percentiles["p95"] == 2.5
        assert percentiles["p99"] == 2.5

    def test_identify_bottlenecks_single_bottleneck(self, tmp_path):
        """Test bottleneck identification with one clear bottleneck."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        component_latencies = {
            "comp1": [1.0, 1.0, 1.0],
            "comp2": [5.0, 5.0, 5.0],  # 5/6 = 83% > 30%
        }

        bottlenecks = evaluator.identify_bottlenecks(component_latencies)

        assert len(bottlenecks) == 1
        assert bottlenecks[0]["component"] == "comp2"
        assert bottlenecks[0]["percentage"] > 80
        assert bottlenecks[0]["severity"] == "critical"  # >50%
        assert "suggestions" in bottlenecks[0]
        assert isinstance(bottlenecks[0]["suggestions"], list)
        assert len(bottlenecks[0]["suggestions"]) > 0

    def test_identify_bottlenecks_multiple(self, tmp_path):
        """Test bottleneck identification with multiple bottlenecks."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        component_latencies = {
            "comp1": [2.0, 2.0],  # 2/6 = 33% > 30%
            "comp2": [2.0, 2.0],  # 2/6 = 33% > 30%
            "comp3": [1.0, 1.0],  # 1/6 = 17% < 30%
            "comp4": [1.0, 1.0],  # 1/6 = 17% < 30%
        }

        bottlenecks = evaluator.identify_bottlenecks(component_latencies)

        assert len(bottlenecks) == 2
        bottleneck_components = [b["component"] for b in bottlenecks]
        assert "comp1" in bottleneck_components
        assert "comp2" in bottleneck_components
        assert "comp3" not in bottleneck_components
        assert "comp4" not in bottleneck_components
        # Check all have structured format
        for b in bottlenecks:
            assert "component" in b
            assert "percentage" in b
            assert "severity" in b
            assert "suggestions" in b

    def test_identify_bottlenecks_none(self, tmp_path):
        """Test bottleneck identification when all components are balanced."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        component_latencies = {
            "comp1": [1.0, 1.0],
            "comp2": [1.0, 1.0],
            "comp3": [1.0, 1.0],
            "comp4": [1.0, 1.0],
        }

        bottlenecks = evaluator.identify_bottlenecks(component_latencies)

        assert len(bottlenecks) == 0

    def test_identify_bottlenecks_custom_threshold(self, tmp_path):
        """Test bottleneck identification with custom threshold."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        component_latencies = {
            "comp1": [4.0, 4.0],  # 40%
            "comp2": [6.0, 6.0],  # 60%
        }

        # With 30% threshold
        bottlenecks_30 = evaluator.identify_bottlenecks(component_latencies, threshold_percent=30.0)
        assert len(bottlenecks_30) == 2

        # With 50% threshold
        bottlenecks_50 = evaluator.identify_bottlenecks(component_latencies, threshold_percent=50.0)
        assert len(bottlenecks_50) == 1
        assert bottlenecks_50[0]["component"] == "comp2"
        assert bottlenecks_50[0]["severity"] == "critical"  # 60% > 50%

    def test_identify_bottlenecks_severity_levels(self, tmp_path):
        """Test bottleneck severity classification."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        component_latencies = {
            "critical_comp": [6.0],   # 6/11.5 = 52% > 50% = critical
            "high_comp": [4.5],       # 4.5/11.5 = 39% (30-40%) = medium (not high, which is 40-50%)
            "medium_comp": [1.0],     # 1/11.5 = 9% < 30% = not a bottleneck
        }

        bottlenecks = evaluator.identify_bottlenecks(component_latencies, threshold_percent=30.0)

        assert len(bottlenecks) == 2  # Only critical_comp and high_comp exceed 30%
        # Check sorted by percentage descending
        assert bottlenecks[0]["component"] == "critical_comp"
        assert bottlenecks[0]["severity"] == "critical"  # >50%
        assert bottlenecks[1]["component"] == "high_comp"
        assert bottlenecks[1]["severity"] == "medium"  # 39% is 30-40%

    def test_identify_bottlenecks_known_components(self, tmp_path):
        """Test optimization suggestions for known components."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        component_latencies = {
            "signal_detection": [5.0],
            "persona_assignment": [5.0],
        }

        bottlenecks = evaluator.identify_bottlenecks(component_latencies, threshold_percent=30.0)

        assert len(bottlenecks) == 2
        # Check that known components have specific suggestions
        for b in bottlenecks:
            if b["component"] == "signal_detection":
                assert any("database indexing" in s.lower() for s in b["suggestions"])
            elif b["component"] == "persona_assignment":
                assert any("cache" in s.lower() for s in b["suggestions"])

    def test_calculate_scalability_projections_default(self, tmp_path):
        """Test scalability projections with default user counts."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        avg_latency = 2.5  # seconds per user
        projections = evaluator.calculate_scalability_projections(avg_latency)

        assert projections[1000] == 2500.0  # 2.5 * 1000
        assert projections[10000] == 25000.0  # 2.5 * 10000
        assert projections[100000] == 250000.0  # 2.5 * 100000

    def test_calculate_scalability_projections_custom_counts(self, tmp_path):
        """Test scalability projections with custom user counts."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        avg_latency = 1.0
        projections = evaluator.calculate_scalability_projections(
            avg_latency,
            user_counts=[100, 500, 2000]
        )

        assert projections[100] == 100.0
        assert projections[500] == 500.0
        assert projections[2000] == 2000.0

    def test_calculate_scalability_projections_fast_system(self, tmp_path):
        """Test projections for fast system (<1s per user)."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        avg_latency = 0.5
        projections = evaluator.calculate_scalability_projections(avg_latency)

        assert projections[1000] == 500.0  # 8.3 minutes
        assert projections[10000] == 5000.0  # 83 minutes

    def test_calculate_scalability_projections_slow_system(self, tmp_path):
        """Test projections for slow system (>5s per user)."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        avg_latency = 10.0
        projections = evaluator.calculate_scalability_projections(avg_latency)

        assert projections[1000] == 10000.0  # 2.8 hours
        assert projections[10000] == 100000.0  # 27.8 hours


class TestVisualizationGeneration:
    """Test visualization generation."""

    def test_generate_visualizations_creates_files(self, tmp_path):
        """Test that visualization files are created."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        metrics = PerformanceMetrics(
            total_latency_seconds=10.0,
            component_latencies={
                "signal_detection": 3.0,
                "persona_assignment": 2.0,
                "recommendation_matching": 4.0,
                "guardrails": 1.0,
            },
            throughput_users_per_minute=6.0,
            resource_utilization={"memory_mb": 100.0},
            latency_percentiles={"p50": 1.0, "p95": 2.0, "p99": 3.0},
            bottlenecks=[{
                "component": "recommendation_matching",
                "percentage": 40.0,
                "severity": "high",
                "suggestions": ["Test suggestion"]
            }],
            scalability_projections={1000: 1000.0},
            timestamp=datetime.now(),
            per_user_latencies=[0.8, 1.0, 1.2, 1.5, 2.0],
        )

        chart_paths = evaluator.generate_visualizations(metrics, "test_run")

        assert "latency_distribution" in chart_paths
        assert "component_breakdown" in chart_paths

        # Check files exist
        hist_path = Path(chart_paths["latency_distribution"])
        pie_path = Path(chart_paths["component_breakdown"])
        assert hist_path.exists()
        assert pie_path.exists()

    def test_generate_visualizations_with_empty_latencies(self, tmp_path):
        """Test visualization with no per-user latencies."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        metrics = PerformanceMetrics(
            total_latency_seconds=10.0,
            component_latencies={"comp1": 5.0, "comp2": 5.0},
            throughput_users_per_minute=6.0,
            resource_utilization={"memory_mb": 100.0},
            latency_percentiles={"p50": 0.0, "p95": 0.0, "p99": 0.0},
            bottlenecks=[],
            scalability_projections={1000: 1000.0},
            timestamp=datetime.now(),
            per_user_latencies=[],  # Empty
        )

        chart_paths = evaluator.generate_visualizations(metrics, "empty_run")

        # Should only generate component breakdown, not histogram
        assert "component_breakdown" in chart_paths
        # latency_distribution might not be present


class TestEndToEndIntegration:
    """Integration tests for complete evaluation flow."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        session = Mock()
        return session

    @pytest.mark.skip(reason="Integration test requiring real database - skipping in unit tests")
    def test_evaluator_with_mocked_components(self, tmp_path):
        """Test evaluator with fully mocked components."""
        mock_session = Mock()
        evaluator = PerformanceEvaluator(
            db_session=mock_session,
            output_dir=str(tmp_path)
        )

        # Mock all component methods
        evaluator.behavioral_generator.generate_summary = Mock(return_value=Mock())
        evaluator.persona_assigner.assign_persona = Mock(
            return_value=Mock(persona_id="test_persona")
        )
        evaluator.recommendation_engine.generate_recommendations = Mock(
            return_value=Mock(recommendations=[])
        )

        user_ids = ["user_1", "user_2"]
        total, per_user, components = evaluator.measure_end_to_end_latency(user_ids)

        assert total > 0
        assert len(per_user) == 2
        assert all(t > 0 for t in per_user)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_very_fast_processing(self, tmp_path):
        """Test with very fast processing (<1 second total)."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        latencies = [0.001, 0.002, 0.003]
        percentiles = evaluator.calculate_latency_percentiles(latencies)

        assert percentiles["p50"] < 1.0
        assert percentiles["p95"] < 1.0
        assert percentiles["p99"] < 1.0

    def test_very_slow_processing(self, tmp_path):
        """Test with very slow processing (>10 seconds per user)."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        latencies = [15.0, 20.0, 25.0]
        percentiles = evaluator.calculate_latency_percentiles(latencies)

        assert percentiles["p50"] > 10.0
        assert percentiles["p95"] > 20.0

    def test_throughput_with_large_batch(self):
        """Test throughput calculation with large batch."""
        throughput = calculate_throughput(10000, 600)  # 10K users in 10 minutes
        assert throughput == pytest.approx(1000.0, rel=0.001)  # 1000 users/min

    def test_bottleneck_with_zero_total_time(self, tmp_path):
        """Test bottleneck identification when total time is zero."""
        with patch.object(PerformanceEvaluator, '__init__', lambda self, db_session, output_dir: None):
            evaluator = PerformanceEvaluator(None, None)
            evaluator.output_dir = Path(tmp_path)
        component_latencies = {
            "comp1": [0.0],
            "comp2": [0.0],
        }

        bottlenecks = evaluator.identify_bottlenecks(component_latencies)
        assert len(bottlenecks) == 0
