import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    initial_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(initial_activities)

client = TestClient(app)

def test_get_activities():
    # Arrange: TestClient is instantiated
    # Act: GET /activities
    response = client.get("/activities")
    # Assert: status 200 and each activity has expected keys
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)

def test_signup_success():
    # Arrange: TestClient is instantiated
    # Act: POST /activities/Chess Club/signup?email=test@example.com
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    # Assert: status 200 and response acknowledges signup
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@example.com" in data["message"]
    assert "Chess Club" in data["message"]

def test_signup_duplicate():
    # Arrange: sign up once
    client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")
    # Act: POST same again
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")
    # Assert: status 400 with 'already signed up' detail
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_delete_participant_success():
    # Arrange: sign up participant
    client.post("/activities/Chess%20Club/signup?email=delete@example.com")
    # Act: DELETE /activities/Chess Club/participants?email=delete@example.com
    response = client.delete("/activities/Chess%20Club/participants?email=delete@example.com")
    # Assert: status 200 and participant removed from activity
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "delete@example.com" in data["message"]
    # Check that participant is removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "delete@example.com" not in activities_data["Chess Club"]["participants"]

def test_delete_participant_not_found():
    # Arrange: no participant
    # Act: DELETE with email
    response = client.delete("/activities/Chess%20Club/participants?email=notfound@example.com")
    # Assert: status 404
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data