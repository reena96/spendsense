"""
Example test file to verify pytest configuration.

This test file ensures that the testing framework is properly configured
and provides basic examples of test structure.
"""

import pytest


def test_basic_assertion():
    """Test basic assertion to verify pytest is working."""
    assert 1 + 1 == 2


def test_string_operations():
    """Test string operations."""
    text = "SpendSense"
    assert text.lower() == "spendsense"
    assert len(text) == 10


def test_list_operations():
    """Test list operations."""
    items = [1, 2, 3, 4, 5]
    assert len(items) == 5
    assert sum(items) == 15
    assert max(items) == 5


@pytest.mark.unit
def test_marked_as_unit():
    """Example of a unit test marker."""
    assert True


def test_dictionary_operations():
    """Test dictionary operations."""
    data = {"name": "SpendSense", "version": "0.1.0"}
    assert data["name"] == "SpendSense"
    assert "version" in data
    assert data.get("author") is None


def test_exception_handling():
    """Test exception handling."""
    with pytest.raises(ZeroDivisionError):
        _ = 1 / 0


def test_approximate_values():
    """Test approximate numerical comparisons."""
    assert 0.1 + 0.2 == pytest.approx(0.3)


class TestExampleClass:
    """Example test class to demonstrate class-based testing."""

    def test_class_method_example(self):
        """Example test within a test class."""
        assert "spendsense".capitalize() == "Spendsense"

    def test_another_class_method(self):
        """Another example test within a test class."""
        numbers = list(range(10))
        assert len(numbers) == 10
        assert numbers[0] == 0
        assert numbers[-1] == 9
