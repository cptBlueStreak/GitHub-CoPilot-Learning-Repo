"""
Tests for the Mergington High School API

Uses the AAA (Arrange-Act-Assert) testing pattern:
- Arrange: Set up test data and fixtures
- Act: Call the endpoint being tested
- Assert: Verify the response meets expectations
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for the FastAPI app.
    This allows tests to make HTTP requests to the app without running a server.
    """
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Set up client
        Act: Retrieve all activities
        Assert: Response contains all activities with correct structure
        """
        # Arrange
        expected_activity_count = 9

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_get_activities_returns_activity_details(self, client):
        """
        Arrange: Set up client
        Act: Retrieve all activities
        Assert: Each activity has required fields (description, schedule, max_participants, participants)
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_chess_club_has_participants(self, client):
        """
        Arrange: Set up client
        Act: Retrieve all activities
        Assert: Chess Club has expected participants
        """
        # Arrange
        expected_chess_participants = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        chess_participants = activities["Chess Club"]["participants"]
        assert chess_participants == expected_chess_participants


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self, client):
        """
        Arrange: Set up client with a new email and an activity with available spots
        Act: Sign up the student for the activity
        Assert: Response indicates successful signup (200 status, confirmation message)
        """
        # Arrange
        activity_name = "Chess Club"
        email = "new_student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_activity_not_found(self, client):
        """
        Arrange: Set up client with a non-existent activity name
        Act: Attempt to sign up for non-existent activity
        Assert: Response is 404 with appropriate error message
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_student_already_registered(self, client):
        """
        Arrange: Set up client and select a student already in an activity
        Act: Attempt to sign up the same student for the same activity again
        Assert: Response is 400 with duplicate registration error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_activity_full(self, client):
        """
        Arrange: Set up client and select an activity that is already full
        Act: Attempt to sign up for a full activity
        Assert: Response is 400 with activity full error
        """
        # Arrange
        # First, get activities to find one we can fill up
        get_response = client.get("/activities")
        activities = get_response.json()
        
        # Find an activity with room to fill it up
        activity_name = "Chess Club"
        activity = activities[activity_name]
        
        # Calculate how many more spots are available
        available_spots = activity["max_participants"] - len(activity["participants"])
        
        # Sign up enough students to fill the activity
        for i in range(available_spots):
            test_email = f"fill_student_{i}@mergington.edu"
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": test_email}
            )

        # Now try to sign up one more student when full
        final_student = "overflow_student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": final_student}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "full" in data["detail"].lower()


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""

    def test_remove_participant_success(self, client):
        """
        Arrange: Set up client and select a participant to remove
        Act: Remove the participant from an activity
        Assert: Response indicates successful removal (200 status, confirmation message)
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Known participant

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_remove_participant_activity_not_found(self, client):
        """
        Arrange: Set up client with a non-existent activity
        Act: Attempt to remove a participant from a non-existent activity
        Assert: Response is 404 with appropriate error message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_remove_participant_not_found(self, client):
        """
        Arrange: Set up client with an activity and an email not in that activity
        Act: Attempt to remove a non-participant
        Assert: Response is 404 with participant not found error
        """
        # Arrange
        activity_name = "Debate Team"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_remove_participant_case_insensitive(self, client):
        """
        Arrange: Set up client with a participant email in lowercase
        Act: Remove the participant using uppercase email
        Assert: Participant is removed successfully (case-insensitive matching)
        """
        # Arrange
        activity_name = "Drama Club"
        original_email = "sophia@mergington.edu"
        uppercase_email = "SOPHIA@MERGINGTON.EDU"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": uppercase_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert original_email in data["message"]
