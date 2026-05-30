import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities_state():
    app_module.activities = copy.deepcopy(INITIAL_ACTIVITIES)
    yield
    app_module.activities = copy.deepcopy(INITIAL_ACTIVITIES)


def test_root_redirects_to_static_index():
    # Arrange
    client = TestClient(app_module.app)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure():
    # Arrange
    client = TestClient(app_module.app)

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_for_activity_adds_participant():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    new_email = "new.student@mergington.edu"
    before = client.get("/activities").json()[activity_name]["participants"]
    assert new_email not in before

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    after = client.get("/activities").json()[activity_name]["participants"]
    assert new_email in after


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_from_activity_removes_participant():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    before = client.get("/activities").json()[activity_name]["participants"]
    assert existing_email in before

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": existing_email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {existing_email} from {activity_name}"
    }
    after = client.get("/activities").json()[activity_name]["participants"]
    assert existing_email not in after


def test_unregister_from_unknown_activity_returns_404():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_missing_participant_returns_404():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    missing_email = "missing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": missing_email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found in this activity"}
