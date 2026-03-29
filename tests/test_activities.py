import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Test that GET /activities returns all activities with correct structure.
        """
        # Arrange: No setup needed, activities already loaded from fixture

        # Act: Fetch all activities
        response = client.get("/activities")

        # Assert: Verify response and data structure
        assert response.status_code == 200
        activities_data = response.json()
        assert isinstance(activities_data, dict)
        
        # Assert: Verify required activities exist with correct fields
        required_activities = [
            "Chess Club", "Programming Class", "Gym Class", 
            "Basketball", "Tennis Club", "Painting Studio", 
            "Music Band", "Debate Club", "Science Olympiad"
        ]
        
        for activity_name in required_activities:
            assert activity_name in activities_data
            activity = activities_data[activity_name]
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)

    def test_get_activities_returns_correct_participants(self, client, reset_activities):
        """
        Test that participants are correctly returned for each activity.
        """
        # Arrange: No additional setup needed

        # Act: Fetch all activities
        response = client.get("/activities")

        # Assert: Verify specific activity has expected participants
        activities_data = response.json()
        chess_club = activities_data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client, reset_activities):
        """
        Test that a student can successfully sign up for an activity.
        """
        # Arrange: Define test data
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act: Sign up for the activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Verify response and message
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Assert: Verify signup was recorded
        verify_response = client.get("/activities")
        activities_data = verify_response.json()
        assert email in activities_data[activity_name]["participants"]

    def test_signup_activity_not_found(self, client, reset_activities):
        """
        Test that signing up for a non-existent activity returns 404.
        """
        # Arrange: Define test data with non-existent activity
        activity_name = "Non-Existent Activity"
        email = "student@mergington.edu"

        # Act: Attempt to sign up
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Verify 404 error
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_already_signed_up(self, client, reset_activities):
        """
        Test that attempting to sign up twice returns 400.
        """
        # Arrange: Use a student who is already signed up
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act: Attempt to sign up again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Verify 400 error
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    @pytest.mark.parametrize("activity_name,email", [
        ("Programming Class", "newstudent1@mergington.edu"),
        ("Basketball", "newstudent2@mergington.edu"),
        ("Tennis Club", "newstudent3@mergington.edu"),
    ])
    def test_signup_multiple_activities(self, client, reset_activities, activity_name, email):
        """
        Test that signup works for multiple different activities.
        """
        # Arrange: Test data provided by parametrize decorator

        # Act: Sign up for the activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Verify successful signup
        assert response.status_code == 200
        
        # Assert: Verify participant was added
        verify_response = client.get("/activities")
        activities_data = verify_response.json()
        assert email in activities_data[activity_name]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_remove_participant_successful(self, client, reset_activities):
        """
        Test that a participant can be successfully removed from an activity.
        """
        # Arrange: Select a participant who exists
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Arrange: Verify participant is initially present
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        assert email in initial_data[activity_name]["participants"]

        # Act: Remove the participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert: Verify successful deletion
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Assert: Verify participant was actually removed
        verify_response = client.get("/activities")
        verify_data = verify_response.json()
        assert email not in verify_data[activity_name]["participants"]

    def test_remove_participant_activity_not_found(self, client, reset_activities):
        """
        Test that removing from a non-existent activity returns 404.
        """
        # Arrange: Define test data
        activity_name = "Non-Existent Activity"
        email = "student@mergington.edu"

        # Act: Attempt to remove participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert: Verify 404 error
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_remove_participant_not_found(self, client, reset_activities):
        """
        Test that removing a non-participant returns 404.
        """
        # Arrange: Define test data
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"

        # Act: Attempt to remove non-existent participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert: Verify 404 error
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    @pytest.mark.parametrize("activity_name,email", [
        ("Programming Class", "emma@mergington.edu"),
        ("Music Band", "lucas@mergington.edu"),
        ("Debate Club", "noah@mergington.edu"),
    ])
    def test_remove_multiple_participants(self, client, reset_activities, activity_name, email):
        """
        Test that removal works for multiple different participants.
        """
        # Arrange: Test data provided by parametrize decorator

        # Act: Remove the participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert: Verify successful deletion
        assert response.status_code == 200
        
        # Assert: Verify participant was removed
        verify_response = client.get("/activities")
        verify_data = verify_response.json()
        assert email not in verify_data[activity_name]["participants"]


class TestIntegrationScenarios:
    """Integration tests combining multiple operations."""

    def test_signup_then_remove_workflow(self, client, reset_activities):
        """
        Test the complete workflow of signing up and then removing a participant.
        """
        # Arrange: Define test data
        activity_name = "Tennis Club"
        email = "workflow@mergington.edu"

        # Act: Sign up for activity
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Verify signup succeeded
        assert signup_response.status_code == 200
        
        # Arrange: Verify signup was recorded
        get_response = client.get("/activities")
        activities_data = get_response.json()
        assert email in activities_data[activity_name]["participants"]

        # Act: Remove the participant
        remove_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert: Verify removal succeeded
        assert remove_response.status_code == 200
        
        # Assert: Verify removal was recorded
        final_response = client.get("/activities")
        final_data = final_response.json()
        assert email not in final_data[activity_name]["participants"]

    def test_multiple_signups_same_activity(self, client, reset_activities):
        """
        Test that multiple different students can sign up for the same activity.
        """
        # Arrange: Define test data
        activity_name = "Science Olympiad"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]

        # Act: Sign up multiple students
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            # Assert: Each signup succeeds
            assert response.status_code == 200

        # Assert: Verify all students are signed up
        get_response = client.get("/activities")
        activities_data = get_response.json()
        for email in emails:
            assert email in activities_data[activity_name]["participants"]
