import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def activities(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Practice chess",
            "schedule": "Fridays",
            "max_participants": 10,
            "participants": ["student@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return test_activities


@pytest.fixture
def client():
    return TestClient(app_module.app, follow_redirects=False)


def test_root_redirects_to_frontend(client):
    # Arrange

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_current_activities(client, activities):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_adds_participant(client, activities):
    # Arrange
    new_email = "new-student@example.com"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {new_email} for Chess Club"
    }
    assert new_email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client, activities):
    # Arrange
    existing_email = "student@example.com"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert activities["Chess Club"]["participants"] == [existing_email]


def test_signup_rejects_unknown_activity(client, activities):
    # Arrange
    unknown_activity = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{unknown_activity}/signup",
        params={"email": "new-student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
    assert activities["Chess Club"]["participants"] == ["student@example.com"]


def test_unregister_removes_participant(client, activities):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_rejects_missing_participant(client, activities):
    # Arrange
    missing_email = "missing@example.com"

    # Act
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert activities["Chess Club"]["participants"] == ["student@example.com"]


def test_unregister_rejects_unknown_activity(client, activities):
    # Arrange
    unknown_activity = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{unknown_activity}/signup",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
    assert activities["Chess Club"]["participants"] == ["student@example.com"]