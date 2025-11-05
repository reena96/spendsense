"""
Tests for recommendation storage.

Tests the persistence and retrieval of assembled recommendations.
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime

import pytest

from spendsense.recommendations.storage import RecommendationStorage
from spendsense.recommendations.assembler import (
    AssembledRecommendationSet,
    AssembledRecommendationItem,
    MANDATORY_DISCLAIMER,
)


@pytest.fixture
def temp_storage_dir():
    """Create temporary storage directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def storage(temp_storage_dir):
    """Create storage instance with temporary directory."""
    return RecommendationStorage(temp_storage_dir)


@pytest.fixture
def sample_recommendation_set():
    """Create sample recommendation set for testing."""
    recommendations = [
        AssembledRecommendationItem(
            item_type="education",
            item_id="test_rec_1",
            content={"title": "Test Recommendation 1", "description": "Test description"},
            rationale="This is a test rationale",
            persona_match_reason="Matches your profile",
            signal_citations=["credit_utilization: 68%"],
        ),
        AssembledRecommendationItem(
            item_type="partner_offer",
            item_id="test_offer_1",
            content={"title": "Test Offer 1", "provider": "Test Provider"},
            rationale="This is a test offer rationale",
            persona_match_reason="Good fit for your needs",
            signal_citations=["savings_balance: $500"],
        ),
    ]

    return AssembledRecommendationSet(
        user_id="test_user_123",
        persona_id="test_persona",
        time_window="30d",
        recommendations=recommendations,
        disclaimer=MANDATORY_DISCLAIMER,
        metadata={
            "total_recommendations": 2,
            "education_count": 1,
            "partner_offer_count": 1,
            "generation_time_ms": 125.5,
        },
    )


# Storage Initialization Tests


def test_storage_initialization(temp_storage_dir):
    """Test storage can be initialized."""
    storage = RecommendationStorage(temp_storage_dir)

    assert storage is not None
    assert storage.storage_path.exists()
    assert storage.storage_path.is_dir()


def test_storage_creates_directory_if_not_exists():
    """Test storage creates directory if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "new_storage_dir"
        assert not storage_path.exists()

        storage = RecommendationStorage(str(storage_path))

        assert storage_path.exists()
        assert storage_path.is_dir()


# Save Tests (AC5)


def test_save_recommendation_set(storage, sample_recommendation_set):
    """Test saving recommendation set to storage (PRD AC5)."""
    file_path = storage.save_recommendation_set(sample_recommendation_set)

    assert file_path is not None
    assert Path(file_path).exists()
    assert Path(file_path).is_file()


def test_save_creates_user_directory(storage, sample_recommendation_set):
    """Test saving creates user-specific directory."""
    storage.save_recommendation_set(sample_recommendation_set)

    user_dir = storage.storage_path / sample_recommendation_set.user_id
    assert user_dir.exists()
    assert user_dir.is_dir()


def test_save_creates_timestamped_file(storage, sample_recommendation_set):
    """Test saved file has timestamp in filename."""
    file_path = storage.save_recommendation_set(sample_recommendation_set)

    filename = Path(file_path).name
    assert "recommendations_30d_" in filename
    assert filename.endswith(".json")


def test_save_creates_latest_file(storage, sample_recommendation_set):
    """Test saving also creates 'latest' file for easy retrieval."""
    storage.save_recommendation_set(sample_recommendation_set)

    user_dir = storage.storage_path / sample_recommendation_set.user_id
    latest_file = user_dir / "latest_30d.json"

    assert latest_file.exists()


def test_saved_file_contains_correct_data(storage, sample_recommendation_set):
    """Test saved file contains correct JSON data."""
    file_path = storage.save_recommendation_set(sample_recommendation_set)

    with open(file_path, "r") as f:
        data = json.load(f)

    assert data["user_id"] == sample_recommendation_set.user_id
    assert data["persona_id"] == sample_recommendation_set.persona_id
    assert data["time_window"] == sample_recommendation_set.time_window
    assert len(data["recommendations"]) == 2
    assert data["disclaimer"] == MANDATORY_DISCLAIMER


def test_save_handles_multiple_time_windows(storage, sample_recommendation_set):
    """Test saving handles both 30d and 180d time windows."""
    # Save 30d
    storage.save_recommendation_set(sample_recommendation_set)

    # Save 180d
    rec_set_180d = sample_recommendation_set
    rec_set_180d.time_window = "180d"
    storage.save_recommendation_set(rec_set_180d)

    user_dir = storage.storage_path / sample_recommendation_set.user_id

    assert (user_dir / "latest_30d.json").exists()
    assert (user_dir / "latest_180d.json").exists()


# Retrieve Tests (AC6)


def test_get_latest_by_user(storage, sample_recommendation_set):
    """Test retrieving latest recommendation set by user (PRD AC6)."""
    storage.save_recommendation_set(sample_recommendation_set)

    retrieved = storage.get_latest_by_user(
        sample_recommendation_set.user_id,
        "30d"
    )

    assert retrieved is not None
    assert retrieved["user_id"] == sample_recommendation_set.user_id
    assert retrieved["time_window"] == "30d"


def test_get_latest_returns_none_if_not_exists(storage):
    """Test get_latest returns None if no recommendations exist."""
    retrieved = storage.get_latest_by_user("nonexistent_user", "30d")

    assert retrieved is None


def test_get_latest_returns_correct_time_window(storage, sample_recommendation_set):
    """Test get_latest returns correct time window."""
    # Save 30d
    storage.save_recommendation_set(sample_recommendation_set)

    # Save 180d
    rec_set_180d = AssembledRecommendationSet(
        user_id=sample_recommendation_set.user_id,
        persona_id=sample_recommendation_set.persona_id,
        time_window="180d",
        recommendations=sample_recommendation_set.recommendations,
        disclaimer=MANDATORY_DISCLAIMER,
        metadata=sample_recommendation_set.metadata,
    )
    storage.save_recommendation_set(rec_set_180d)

    # Retrieve 30d
    retrieved_30d = storage.get_latest_by_user(sample_recommendation_set.user_id, "30d")
    assert retrieved_30d["time_window"] == "30d"

    # Retrieve 180d
    retrieved_180d = storage.get_latest_by_user(sample_recommendation_set.user_id, "180d")
    assert retrieved_180d["time_window"] == "180d"


def test_get_all_by_user(storage, sample_recommendation_set):
    """Test retrieving all recommendation sets for a user (PRD AC6)."""
    import time
    # Save multiple sets with different timestamps
    for i in range(3):
        # Create new set with new timestamp
        rec_set = AssembledRecommendationSet(
            user_id=sample_recommendation_set.user_id,
            persona_id=sample_recommendation_set.persona_id,
            time_window=sample_recommendation_set.time_window,
            recommendations=sample_recommendation_set.recommendations,
            disclaimer=sample_recommendation_set.disclaimer,
            metadata=sample_recommendation_set.metadata,
            generated_at=datetime.utcnow(),  # New timestamp each time
        )
        storage.save_recommendation_set(rec_set)
        time.sleep(0.01)  # Small delay to ensure different timestamps

    all_recs = storage.get_all_by_user(sample_recommendation_set.user_id)

    assert len(all_recs) >= 3
    assert all(rec["user_id"] == sample_recommendation_set.user_id for rec in all_recs)


def test_get_all_by_user_filters_by_time_window(storage, sample_recommendation_set):
    """Test get_all filters by time window."""
    import time
    # Save 30d sets with different timestamps
    for i in range(2):
        rec_set = AssembledRecommendationSet(
            user_id=sample_recommendation_set.user_id,
            persona_id=sample_recommendation_set.persona_id,
            time_window=sample_recommendation_set.time_window,
            recommendations=sample_recommendation_set.recommendations,
            disclaimer=sample_recommendation_set.disclaimer,
            metadata=sample_recommendation_set.metadata,
            generated_at=datetime.utcnow(),
        )
        storage.save_recommendation_set(rec_set)
        time.sleep(0.01)

    # Save 180d sets with different timestamps
    for i in range(3):
        rec_set_180d = AssembledRecommendationSet(
            user_id=sample_recommendation_set.user_id,
            persona_id=sample_recommendation_set.persona_id,
            time_window="180d",
            recommendations=sample_recommendation_set.recommendations,
            disclaimer=MANDATORY_DISCLAIMER,
            metadata=sample_recommendation_set.metadata,
            generated_at=datetime.utcnow(),
        )
        storage.save_recommendation_set(rec_set_180d)
        time.sleep(0.01)

    # Get only 30d
    recs_30d = storage.get_all_by_user(sample_recommendation_set.user_id, time_window="30d")
    assert len(recs_30d) >= 2
    assert all(rec["time_window"] == "30d" for rec in recs_30d)

    # Get only 180d
    recs_180d = storage.get_all_by_user(sample_recommendation_set.user_id, time_window="180d")
    assert len(recs_180d) >= 3
    assert all(rec["time_window"] == "180d" for rec in recs_180d)


def test_get_all_returns_empty_list_if_not_exists(storage):
    """Test get_all returns empty list if no recommendations exist."""
    all_recs = storage.get_all_by_user("nonexistent_user")

    assert all_recs == []


def test_get_all_returns_sorted_by_timestamp(storage, sample_recommendation_set):
    """Test get_all returns recommendations sorted by timestamp (newest first)."""
    import time

    # Save multiple sets with different timestamps
    for i in range(3):
        rec_set = AssembledRecommendationSet(
            user_id=sample_recommendation_set.user_id,
            persona_id=sample_recommendation_set.persona_id,
            time_window=sample_recommendation_set.time_window,
            recommendations=sample_recommendation_set.recommendations,
            disclaimer=sample_recommendation_set.disclaimer,
            metadata=sample_recommendation_set.metadata,
            generated_at=datetime.utcnow(),
        )
        storage.save_recommendation_set(rec_set)
        time.sleep(0.01)  # Small delay to ensure different timestamps

    all_recs = storage.get_all_by_user(sample_recommendation_set.user_id)

    # Should be sorted newest first
    assert len(all_recs) >= 3

    # Check timestamps are in descending order
    timestamps = [rec["generated_at"] for rec in all_recs]
    sorted_timestamps = sorted(timestamps, reverse=True)
    assert timestamps == sorted_timestamps


# Cleanup Tests


def test_delete_old_recommendations(storage, sample_recommendation_set):
    """Test deleting old recommendation files."""
    import time
    # Save multiple sets with different timestamps
    for i in range(10):
        rec_set = AssembledRecommendationSet(
            user_id=sample_recommendation_set.user_id,
            persona_id=sample_recommendation_set.persona_id,
            time_window=sample_recommendation_set.time_window,
            recommendations=sample_recommendation_set.recommendations,
            disclaimer=sample_recommendation_set.disclaimer,
            metadata=sample_recommendation_set.metadata,
            generated_at=datetime.utcnow(),
        )
        storage.save_recommendation_set(rec_set)
        time.sleep(0.01)

    # Delete old ones, keeping only 3
    deleted_count = storage.delete_old_recommendations(
        sample_recommendation_set.user_id,
        keep_count=3
    )

    assert deleted_count > 0

    # Verify only 3 remain
    all_recs = storage.get_all_by_user(sample_recommendation_set.user_id, time_window="30d")
    assert len(all_recs) == 3


def test_delete_returns_zero_if_user_not_exists(storage):
    """Test delete returns 0 if user doesn't exist."""
    deleted_count = storage.delete_old_recommendations("nonexistent_user")

    assert deleted_count == 0


def test_delete_preserves_latest_files(storage, sample_recommendation_set):
    """Test delete preserves 'latest' files."""
    # Save multiple sets
    for i in range(5):
        storage.save_recommendation_set(sample_recommendation_set)

    # Delete old ones
    storage.delete_old_recommendations(sample_recommendation_set.user_id, keep_count=2)

    # Latest file should still exist
    user_dir = storage.storage_path / sample_recommendation_set.user_id
    latest_file = user_dir / "latest_30d.json"

    assert latest_file.exists()


# Statistics Tests


def test_get_storage_stats(storage, sample_recommendation_set):
    """Test getting storage statistics."""
    # Save some data
    storage.save_recommendation_set(sample_recommendation_set)

    # Create another user
    rec_set_2 = AssembledRecommendationSet(
        user_id="test_user_456",
        persona_id="test_persona",
        time_window="30d",
        recommendations=sample_recommendation_set.recommendations,
        disclaimer=MANDATORY_DISCLAIMER,
        metadata=sample_recommendation_set.metadata,
    )
    storage.save_recommendation_set(rec_set_2)

    stats = storage.get_storage_stats()

    assert stats["total_users"] == 2
    assert stats["total_recommendation_files"] >= 2
    assert stats["total_size_mb"] > 0
    assert "storage_path" in stats


def test_get_storage_stats_empty(storage):
    """Test getting stats on empty storage."""
    stats = storage.get_storage_stats()

    assert stats["total_users"] == 0
    assert stats["total_recommendation_files"] == 0
    assert stats["total_size_mb"] == 0


# Edge Cases


def test_save_overwrites_latest_file(storage, sample_recommendation_set):
    """Test saving overwrites the latest file."""
    # Save first time
    storage.save_recommendation_set(sample_recommendation_set)

    user_dir = storage.storage_path / sample_recommendation_set.user_id
    latest_file = user_dir / "latest_30d.json"

    # Read first content
    with open(latest_file, "r") as f:
        first_content = json.load(f)

    # Modify and save again
    sample_recommendation_set.metadata["test_field"] = "modified"
    storage.save_recommendation_set(sample_recommendation_set)

    # Read second content
    with open(latest_file, "r") as f:
        second_content = json.load(f)

    # Should be different (overwritten)
    assert "test_field" in second_content["metadata"]
    assert second_content["metadata"]["test_field"] == "modified"


def test_storage_handles_special_characters_in_user_id(storage):
    """Test storage handles user IDs with special characters."""
    rec_set = AssembledRecommendationSet(
        user_id="user_MASKED_001",  # Underscore in user ID
        persona_id="test_persona",
        time_window="30d",
        recommendations=[],
        disclaimer=MANDATORY_DISCLAIMER,
        metadata={},
    )

    # Should not raise exception
    file_path = storage.save_recommendation_set(rec_set)
    assert file_path is not None

    # Should be retrievable
    retrieved = storage.get_latest_by_user("user_MASKED_001", "30d")
    assert retrieved is not None


def test_storage_handles_corrupted_file(storage, sample_recommendation_set):
    """Test storage handles corrupted JSON file gracefully."""
    storage.save_recommendation_set(sample_recommendation_set)

    # Corrupt a file
    user_dir = storage.storage_path / sample_recommendation_set.user_id
    files = list(user_dir.glob("recommendations_30d_*.json"))
    if files:
        with open(files[0], "w") as f:
            f.write("corrupted json {[")

    # Should still work (skip corrupted file)
    all_recs = storage.get_all_by_user(sample_recommendation_set.user_id)
    # Should return empty or partial list (not crash)
    assert isinstance(all_recs, list)
