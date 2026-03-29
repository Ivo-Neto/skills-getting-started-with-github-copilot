import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture that provides a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture that resets the activities dict to its original state after each test.
    This ensures test isolation when tests modify the in-memory activities data.
    """
    # Arrange: Save the original state before the test
    original_activities = deepcopy(activities)
    
    yield  # Test runs here
    
    # Cleanup: Restore the original state after the test
    activities.clear()
    activities.update(original_activities)
