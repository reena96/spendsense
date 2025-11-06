"""
Tests for recommendation content library.

Tests cover:
- Model validation
- YAML loading
- Content access methods
- Error handling
- Edge cases
"""

import pytest
import tempfile
from pathlib import Path
from pydantic import ValidationError

from spendsense.recommendations.models import (
    Recommendation,
    RecommendationCategory,
    RecommendationType,
    DifficultyLevel,
    TimeCommitment,
    EstimatedImpact,
)
from spendsense.recommendations.content_library import ContentLibrary


# === Model Validation Tests ===


def test_valid_recommendation_model():
    """Test creating a valid recommendation."""
    rec = Recommendation(
        id="test-recommendation",
        type=RecommendationType.ARTICLE,
        category=RecommendationCategory.ACTION,
        title="Test Action Item",
        description="This is a test recommendation with a detailed description.",
        personas=["test_persona"],
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
    )

    assert rec.id == "test-recommendation"
    assert rec.category == RecommendationCategory.ACTION
    assert rec.priority == 1
    assert rec.is_high_priority is True
    assert rec.is_quick_win is True
    assert rec.impact_score == 3


def test_recommendation_missing_required_field():
    """Test that missing required fields raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Recommendation(
            # Missing 'id'
            type=RecommendationType.ARTICLE,
            category=RecommendationCategory.ACTION,
            title="Test Title",
            description="Test description",
            personas=["test_persona"],
            priority=1,
            difficulty=DifficultyLevel.BEGINNER,
            time_commitment=TimeCommitment.ONE_TIME,
            estimated_impact=EstimatedImpact.HIGH,
        )

    assert "id" in str(exc_info.value)


def test_recommendation_invalid_enum_value():
    """Test that invalid enum values raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Recommendation(
            id="test-rec",
            type=RecommendationType.ARTICLE,
            category="invalid_category",  # Invalid enum
            title="Test Title",
            description="Test description",
            personas=["test_persona"],
            priority=1,
            difficulty=DifficultyLevel.BEGINNER,
            time_commitment=TimeCommitment.ONE_TIME,
            estimated_impact=EstimatedImpact.HIGH,
        )

    assert "category" in str(exc_info.value).lower()


def test_recommendation_priority_validation():
    """Test priority must be between 1-10."""
    # Priority too low
    with pytest.raises(ValidationError):
        Recommendation(
            id="test-rec",
            type=RecommendationType.ARTICLE,
            category=RecommendationCategory.ACTION,
            title="Test Title",
            description="Test description",
            personas=["test_persona"],
            priority=0,  # Invalid: must be >= 1
            difficulty=DifficultyLevel.BEGINNER,
            time_commitment=TimeCommitment.ONE_TIME,
            estimated_impact=EstimatedImpact.HIGH,
        )

    # Priority too high
    with pytest.raises(ValidationError):
        Recommendation(
            id="test-rec",
            type=RecommendationType.ARTICLE,
            category=RecommendationCategory.ACTION,
            title="Test Title",
            description="Test description",
            personas=["test_persona"],
            priority=11,  # Invalid: must be <= 10
            difficulty=DifficultyLevel.BEGINNER,
            time_commitment=TimeCommitment.ONE_TIME,
            estimated_impact=EstimatedImpact.HIGH,
        )


def test_recommendation_id_format_validation():
    """Test ID format validation (kebab-case)."""
    # Valid kebab-case
    rec = Recommendation(
        id="valid-kebab-case-123",
        type=RecommendationType.ARTICLE,
        category=RecommendationCategory.ACTION,
        title="Test Title",
        description="Test description",
        personas=["test_persona"],
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
    )
    assert rec.id == "valid-kebab-case-123"

    # Invalid: uppercase
    with pytest.raises(ValidationError) as exc_info:
        Recommendation(
            id="Invalid-ID",
            type=RecommendationType.ARTICLE,
            category=RecommendationCategory.ACTION,
            title="Test Title",
            description="Test description",
            personas=["test_persona"],
            priority=1,
            difficulty=DifficultyLevel.BEGINNER,
            time_commitment=TimeCommitment.ONE_TIME,
            estimated_impact=EstimatedImpact.HIGH,
        )
    assert "kebab-case" in str(exc_info.value).lower()

    # Invalid: starts with hyphen
    with pytest.raises(ValidationError):
        Recommendation(
            id="-invalid-id",
            type=RecommendationType.ARTICLE,
            category=RecommendationCategory.ACTION,
            title="Test Title",
            description="Test description",
            personas=["test_persona"],
            priority=1,
            difficulty=DifficultyLevel.BEGINNER,
            time_commitment=TimeCommitment.ONE_TIME,
            estimated_impact=EstimatedImpact.HIGH,
        )


def test_recommendation_title_validation():
    """Test title length validation."""
    # Title too short (less than min_length characters)
    with pytest.raises(ValidationError) as exc_info:
        Recommendation(
            id="test-rec",
            type=RecommendationType.ARTICLE,
            category=RecommendationCategory.ACTION,
            title="Test",  # Only 4 characters, min is 5
            description="Test description that is long enough",
            personas=["test_persona"],
            priority=1,
            difficulty=DifficultyLevel.BEGINNER,
            time_commitment=TimeCommitment.ONE_TIME,
            estimated_impact=EstimatedImpact.HIGH,
        )
    assert "at least 5 characters" in str(exc_info.value).lower()

    # Title with 1 word (but meets min_length)
    with pytest.raises(ValidationError) as exc_info:
        Recommendation(
            id="test-rec",
            type=RecommendationType.ARTICLE,
            category=RecommendationCategory.ACTION,
            title="Testing",  # 1 word, but long enough for min_length
            description="Test description that is long enough",
            personas=["test_persona"],
            priority=1,
            difficulty=DifficultyLevel.BEGINNER,
            time_commitment=TimeCommitment.ONE_TIME,
            estimated_impact=EstimatedImpact.HIGH,
        )
    assert "at least 2 words" in str(exc_info.value).lower()

    # Title too long (>15 words)
    long_title = " ".join(["word"] * 20)
    with pytest.raises(ValidationError) as exc_info:
        Recommendation(
            id="test-rec",
            type=RecommendationType.ARTICLE,
            category=RecommendationCategory.ACTION,
            title=long_title,
            description="Test description",
            personas=["test_persona"],
            priority=1,
            difficulty=DifficultyLevel.BEGINNER,
            time_commitment=TimeCommitment.ONE_TIME,
            estimated_impact=EstimatedImpact.HIGH,
        )
    assert "at most 15 words" in str(exc_info.value).lower()


def test_recommendation_helper_properties():
    """Test helper properties for recommendations."""
    # High priority recommendation
    high_priority_rec = Recommendation(
        id="test-high",
        type=RecommendationType.ARTICLE,
        category=RecommendationCategory.ACTION,
        title="High Priority Action",
        description="Test description",
        personas=["test_persona"],
        priority=2,
        difficulty=DifficultyLevel.INTERMEDIATE,
        time_commitment=TimeCommitment.ONGOING,
        estimated_impact=EstimatedImpact.HIGH,
    )
    assert high_priority_rec.is_high_priority is True
    assert high_priority_rec.is_quick_win is False
    assert high_priority_rec.impact_score == 3

    # Low priority, quick win recommendation
    quick_win_rec = Recommendation(
        id="test-quick",
        type=RecommendationType.ARTICLE,
        category=RecommendationCategory.TIP,
        title="Quick Win Tip",
        description="Test description",
        personas=["test_persona"],
        priority=8,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.MEDIUM,
    )
    assert quick_win_rec.is_high_priority is False
    assert quick_win_rec.is_quick_win is True
    assert quick_win_rec.impact_score == 2


def test_recommendation_to_dict():
    """Test converting recommendation to dictionary."""
    rec = Recommendation(
        id="test-rec",
        type=RecommendationType.ARTICLE,
        category=RecommendationCategory.EDUCATION,
        title="Test Education Item",
        description="Test description",
        personas=["test_persona"],
        priority=3,
        difficulty=DifficultyLevel.INTERMEDIATE,
        time_commitment=TimeCommitment.WEEKLY,
        estimated_impact=EstimatedImpact.MEDIUM,
        content_url="/content/test",
    )

    rec_dict = rec.to_dict()
    assert rec_dict["id"] == "test-rec"
    assert rec_dict["category"] == "education"
    assert rec_dict["priority"] == 3
    assert rec_dict["content_url"] == "/content/test"


# === YAML Loading Tests ===


def test_load_valid_yaml_file():
    """Test loading valid YAML file."""
    yaml_content = """
educational_content:
  - id: "test-rec-1"
    type: "article"
    category: "action"
    title: "Test Action One"
    description: "This is the first test recommendation"
    personas: ["test_persona"]
    priority: 1
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "high"
  - id: "test-rec-2"
    type: "article"
    category: "education"
    title: "Test Education Two"
    description: "This is the second test recommendation"
    personas: ["test_persona"]
    priority: 2
    difficulty: "intermediate"
    time_commitment: "ongoing"
    estimated_impact: "medium"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name

    try:
        library = ContentLibrary(temp_path)
        assert len(library.get_all_personas()) == 1
        assert "test_persona" in library.get_all_personas()
        assert library.get_recommendation_count("test_persona") == 2
    finally:
        Path(temp_path).unlink()


def test_load_missing_file():
    """Test that missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError) as exc_info:
        ContentLibrary("/nonexistent/path/recommendations.yaml")

    assert "not found" in str(exc_info.value).lower()


def test_load_invalid_yaml_syntax():
    """Test that invalid YAML syntax raises ValueError."""
    yaml_content = """
educational_content:
  - id: "test-rec"
    type: "article"
    category: "action"
    title: "Test Title"
    personas: ["test_persona"]
    invalid_yaml: [unclosed bracket
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name

    try:
        with pytest.raises(ValueError) as exc_info:
            ContentLibrary(temp_path)
        assert "invalid yaml" in str(exc_info.value).lower()
    finally:
        Path(temp_path).unlink()


def test_load_invalid_recommendation_structure():
    """Test that invalid recommendation structure raises ValueError."""
    yaml_content = """
educational_content:
  - id: "test-rec"
    type: "article"
    category: "action"
    personas: ["test_persona"]
    # Missing required fields: title, description, etc.
    priority: 1
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name

    try:
        with pytest.raises(ValueError) as exc_info:
            ContentLibrary(temp_path)
        assert "invalid recommendation" in str(exc_info.value).lower()
    finally:
        Path(temp_path).unlink()


def test_load_all_personas_present():
    """Test that loading actual config has all 6 personas."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "recommendations.yaml"

    if not config_path.exists():
        pytest.skip("Recommendations YAML file not found")

    library = ContentLibrary(str(config_path))

    expected_personas = {
        "high_utilization",
        "irregular_income",
        "low_savings",
        "subscription_heavy",
        "cash_flow_optimizer",
        "young_professional",
    }

    actual_personas = set(library.get_all_personas())
    assert expected_personas == actual_personas


# === Content Access Tests ===


def test_get_recommendations_by_persona():
    """Test retrieving recommendations by persona ID."""
    yaml_content = """
educational_content:
  - id: "emergency-fund"
    type: "article"
    category: "action"
    title: "Build Emergency Fund"
    description: "Start with $1,000 emergency fund"
    personas: ["low_savings"]
    priority: 1
    difficulty: "beginner"
    time_commitment: "ongoing"
    estimated_impact: "high"
  - id: "automate-savings"
    type: "article"
    category: "action"
    title: "Automate Savings"
    description: "Set up automatic transfers"
    personas: ["low_savings"]
    priority: 2
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "high"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name

    try:
        library = ContentLibrary(temp_path)
        recs = library.get_by_persona("low_savings")

        assert len(recs) == 2
        assert recs[0].id == "emergency-fund"
        assert recs[1].id == "automate-savings"
    finally:
        Path(temp_path).unlink()


def test_get_recommendations_sorted_by_priority():
    """Test recommendations are sorted by priority (1=highest)."""
    yaml_content = """
educational_content:
  - id: "rec-low-priority"
    type: "article"
    category: "tip"
    title: "Low Priority Tip"
    description: "This should come last"
    personas: ["test_persona"]
    priority: 5
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "low"
  - id: "rec-high-priority"
    type: "article"
    category: "action"
    title: "High Priority Action"
    description: "This should come first"
    personas: ["test_persona"]
    priority: 1
    difficulty: "intermediate"
    time_commitment: "ongoing"
    estimated_impact: "high"
  - id: "rec-mid-priority"
    type: "article"
    category: "education"
    title: "Mid Priority Education"
    description: "This should come in the middle"
    personas: ["test_persona"]
    priority: 3
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "medium"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name

    try:
        library = ContentLibrary(temp_path)
        recs = library.get_by_persona("test_persona")

        assert len(recs) == 3
        assert recs[0].priority == 1
        assert recs[1].priority == 3
        assert recs[2].priority == 5
    finally:
        Path(temp_path).unlink()


def test_get_recommendation_by_id():
    """Test retrieving specific recommendation by ID."""
    yaml_content = """
educational_content:
  - id: "target-rec"
    type: "article"
    category: "action"
    title: "Target Recommendation"
    description: "This is the recommendation we're looking for"
    personas: ["test_persona"]
    priority: 1
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "high"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name

    try:
        library = ContentLibrary(temp_path)
        rec = library.get_by_id("target-rec")

        assert rec is not None
        assert rec.id == "target-rec"
        assert rec.title == "Target Recommendation"
    finally:
        Path(temp_path).unlink()


def test_get_unknown_persona():
    """Test that unknown persona returns empty list."""
    yaml_content = """
educational_content:
  - id: "test-rec"
    type: "article"
    category: "action"
    title: "Test Recommendation"
    description: "Test description"
    personas: ["test_persona"]
    priority: 1
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "high"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name

    try:
        library = ContentLibrary(temp_path)
        recs = library.get_by_persona("nonexistent_persona")

        assert recs == []
    finally:
        Path(temp_path).unlink()


def test_get_unknown_recommendation_id():
    """Test that unknown recommendation ID returns None."""
    yaml_content = """
educational_content:
  - id: "test-rec"
    type: "article"
    category: "action"
    title: "Test Recommendation"
    description: "Test description"
    personas: ["test_persona"]
    priority: 1
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "high"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name

    try:
        library = ContentLibrary(temp_path)
        rec = library.get_by_id("nonexistent-rec")

        assert rec is None
    finally:
        Path(temp_path).unlink()


# === Additional Access Methods Tests ===


def test_get_by_category():
    """Test filtering recommendations by category."""
    yaml_content = """
educational_content:
  - id: "action-1"
    type: "article"
    category: "action"
    title: "Action One"
    description: "First action"
    personas: ["test_persona"]
    priority: 1
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "high"
  - id: "education-1"
    type: "article"
    category: "education"
    title: "Education One"
    description: "First education"
    personas: ["test_persona"]
    priority: 2
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "medium"
  - id: "action-2"
    type: "article"
    category: "action"
    title: "Action Two"
    description: "Second action"
    personas: ["test_persona"]
    priority: 3
    difficulty: "intermediate"
    time_commitment: "ongoing"
    estimated_impact: "high"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name

    try:
        library = ContentLibrary(temp_path)
        actions = library.get_by_category("test_persona", "action")

        assert len(actions) == 2
        assert all(r.category == RecommendationCategory.ACTION for r in actions)
        assert actions[0].id == "action-1"
        assert actions[1].id == "action-2"
    finally:
        Path(temp_path).unlink()


def test_get_high_priority():
    """Test getting top N priority recommendations."""
    yaml_content = """
educational_content:
  - id: "rec-1"
    type: "article"
    category: "action"
    title: "Priority One"
    description: "Highest priority"
    personas: ["test_persona"]
    priority: 1
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "high"
  - id: "rec-2"
    type: "article"
    category: "action"
    title: "Priority Two"
    description: "Second priority"
    personas: ["test_persona"]
    priority: 2
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "high"
  - id: "rec-3"
    type: "article"
    category: "action"
    title: "Priority Three"
    description: "Third priority"
    personas: ["test_persona"]
    priority: 3
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "medium"
  - id: "rec-4"
    type: "article"
    category: "tip"
    title: "Priority Four"
    description: "Fourth priority"
    personas: ["test_persona"]
    priority: 4
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "low"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name

    try:
        library = ContentLibrary(temp_path)
        top_2 = library.get_high_priority("test_persona", limit=2)

        assert len(top_2) == 2
        assert top_2[0].priority == 1
        assert top_2[1].priority == 2
    finally:
        Path(temp_path).unlink()


def test_get_quick_wins():
    """Test getting quick win recommendations."""
    yaml_content = """
educational_content:
  - id: "quick-1"
    type: "article"
    category: "tip"
    title: "Quick Win One"
    description: "One-time quick action"
    personas: ["test_persona"]
    priority: 1
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "high"
  - id: "not-quick"
    type: "article"
    category: "action"
    title: "Not a Quick Win"
    description: "Ongoing advanced action"
    personas: ["test_persona"]
    priority: 2
    difficulty: "advanced"
    time_commitment: "ongoing"
    estimated_impact: "high"
  - id: "quick-2"
    type: "article"
    category: "action"
    title: "Quick Win Two"
    description: "Beginner-friendly action"
    personas: ["test_persona"]
    priority: 3
    difficulty: "beginner"
    time_commitment: "weekly"
    estimated_impact: "medium"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name

    try:
        library = ContentLibrary(temp_path)
        quick_wins = library.get_quick_wins("test_persona")

        assert len(quick_wins) == 2
        assert all(r.is_quick_win for r in quick_wins)
        assert quick_wins[0].id == "quick-1"
        assert quick_wins[1].id == "quick-2"
    finally:
        Path(temp_path).unlink()


def test_get_recommendation_count():
    """Test counting recommendations."""
    yaml_content = """
educational_content:
  - id: "rec-a1"
    type: "article"
    category: "action"
    title: "Persona A Rec 1"
    description: "First rec for A"
    personas: ["persona_a"]
    priority: 1
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "high"
  - id: "rec-a2"
    type: "article"
    category: "tip"
    title: "Persona A Rec 2"
    description: "Second rec for A"
    personas: ["persona_a"]
    priority: 2
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "medium"
  - id: "rec-b1"
    type: "article"
    category: "education"
    title: "Persona B Rec 1"
    description: "First rec for B"
    personas: ["persona_b"]
    priority: 1
    difficulty: "intermediate"
    time_commitment: "ongoing"
    estimated_impact: "high"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name

    try:
        library = ContentLibrary(temp_path)

        # Total count
        assert library.get_recommendation_count() == 3

        # Count for persona_a
        assert library.get_recommendation_count("persona_a") == 2

        # Count for persona_b
        assert library.get_recommendation_count("persona_b") == 1

        # Count for unknown persona
        assert library.get_recommendation_count("unknown") == 0
    finally:
        Path(temp_path).unlink()


# === Edge Cases Tests ===


def test_empty_persona_recommendations():
    """Test persona with empty recommendations list."""
    yaml_content = """
educational_content:
  - id: "rec-1"
    type: "article"
    category: "action"
    title: "Normal Recommendation"
    description: "This persona has recommendations"
    personas: ["normal_persona"]
    priority: 1
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "high"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name

    try:
        library = ContentLibrary(temp_path)

        empty_recs = library.get_by_persona("empty_persona")
        assert empty_recs == []

        normal_recs = library.get_by_persona("normal_persona")
        assert len(normal_recs) == 1
    finally:
        Path(temp_path).unlink()


def test_duplicate_recommendation_ids_warning(caplog):
    """Test that duplicate recommendation IDs log warning and keep first."""
    yaml_content = """
educational_content:
  - id: "duplicate-id"
    type: "article"
    category: "action"
    title: "First Instance"
    description: "This should be kept"
    personas: ["persona_a"]
    priority: 1
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "high"
  - id: "duplicate-id"
    type: "article"
    category: "education"
    title: "Second Instance"
    description: "This should log warning"
    personas: ["persona_b"]
    priority: 1
    difficulty: "intermediate"
    time_commitment: "ongoing"
    estimated_impact: "medium"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name

    try:
        with caplog.at_level("WARNING"):
            library = ContentLibrary(temp_path)

        # Check warning was logged
        assert "duplicate-id" in caplog.text.lower()

        # Check first instance was kept
        rec = library.get_by_id("duplicate-id")
        assert rec.title == "First Instance"
    finally:
        Path(temp_path).unlink()
