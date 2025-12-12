"""
API Integration Tests - Testing Endpoints via TestClient
Tests authentication, authorization, and full API workflows
Uses fixtures from conftest.py for state management
"""

import pytest


class TestAuthEndpoints:
    """Test authentication endpoints"""

    def test_register_new_user(self, client):
        """Should register a new user successfully"""
        response = client.post(
            "/auth/register", json={"username": "testuser", "password": "testpass123"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"

    def test_register_duplicate_user(self, client):
        """Should reject duplicate username"""
        # Register first user
        client.post(
            "/auth/register", json={"username": "testuser", "password": "testpass123"}
        )

        # Try to register same username
        response = client.post(
            "/auth/register", json={"username": "testuser", "password": "different"}
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_login_success(self, client):
        """Should login successfully with correct credentials"""
        # Register
        client.post(
            "/auth/register", json={"username": "testuser", "password": "testpass123"}
        )

        # Login
        response = client.post(
            "/auth/login", data={"username": "testuser", "password": "testpass123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client):
        """Should reject invalid credentials"""
        # Register
        client.post(
            "/auth/register", json={"username": "testuser", "password": "testpass123"}
        )

        # Login with wrong password
        response = client.post(
            "/auth/login", data={"username": "testuser", "password": "wrongpassword"}
        )

        assert response.status_code == 401

    def test_get_me_endpoint(self, client, auth_headers):
        """Should return current user info"""
        response = client.get("/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert data["authenticated"] == "true"

    def test_get_me_without_auth(self, client):
        """Should reject /me without auth"""
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_login_json_endpoint(self, client):
        """Should login with JSON body at /auth/token"""
        # Register first
        client.post(
            "/auth/register", json={"username": "jsonuser", "password": "jsonpass123"}
        )

        # Login with JSON
        response = client.post(
            "/auth/token", json={"username": "jsonuser", "password": "jsonpass123"}
        )

        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_json_invalid_credentials(self, client):
        """Should reject invalid credentials at /auth/token"""
        response = client.post(
            "/auth/token", json={"username": "nonexistent", "password": "wrongpass"}
        )

        assert response.status_code == 401


class TestProfileEndpointsAuth:
    """Test profile endpoints authentication"""

    def test_create_profile_without_auth(self, client):
        """Should reject requests without authentication"""
        response = client.post("/profile/user-001")
        assert response.status_code == 401

    def test_create_profile_with_auth(
        self, client, auth_headers, demo_user_credentials
    ):
        """Should create profile with valid auth"""
        user_id = demo_user_credentials["user_id"]
        response = client.post(f"/profile/{user_id}", headers=auth_headers)
        assert response.status_code == 201

    def test_get_profile_without_auth(
        self, client, auth_headers, demo_user_credentials
    ):
        """Should reject get profile without auth"""
        user_id = demo_user_credentials["user_id"]
        # First create profile
        client.post(f"/profile/{user_id}", headers=auth_headers)

        # Try to get without auth
        response = client.get(f"/profile/{user_id}")
        assert response.status_code == 401


class TestProfileEndpointsAuthorization:
    """Test profile endpoints authorization (user can only access own profile)"""

    @pytest.fixture
    def user1_headers(self, client):
        """Auth headers for user 1"""
        client.post("/auth/register", json={"username": "user1", "password": "pass123"})
        response = client.post(
            "/auth/login", data={"username": "user1", "password": "pass123"}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    def user2_auth(self, client):
        """Auth headers and user_id for user 2"""
        resp = client.post(
            "/auth/register", json={"username": "user2", "password": "pass456"}
        )
        user_id = resp.json()["user_id"]
        response = client.post(
            "/auth/login", data={"username": "user2", "password": "pass456"}
        )
        token = response.json()["access_token"]
        return {"headers": {"Authorization": f"Bearer {token}"}, "user_id": user_id}

    def test_user_cannot_create_other_profile(self, client, user1_headers, user2_auth):
        """User 1 cannot create profile for user 2"""
        response = client.post(
            f"/profile/{user2_auth['user_id']}", headers=user1_headers
        )
        assert response.status_code == 403
        assert "only create your own" in response.json()["detail"]

    def test_user_cannot_view_other_profile(self, client, user1_headers, user2_auth):
        """User 1 cannot view user 2's profile"""
        # Create user 2's profile
        client.post(f"/profile/{user2_auth['user_id']}", headers=user2_auth["headers"])

        # User 1 tries to view
        response = client.get(
            f"/profile/{user2_auth['user_id']}", headers=user1_headers
        )
        assert response.status_code == 403

    def test_user_cannot_modify_other_profile(self, client, user1_headers, user2_auth):
        """User 1 cannot modify user 2's profile"""
        # Create user 2's profile
        client.post(f"/profile/{user2_auth['user_id']}", headers=user2_auth["headers"])

        # User 1 tries to add genre
        response = client.post(
            f"/profile/{user2_auth['user_id']}/genre",
            headers=user1_headers,
            json={"genre": "Fantasy"},
        )
        assert response.status_code == 403


class TestProfileEndpointsCRUD:
    """Test profile CRUD operations"""

    @pytest.fixture
    def test_user(self, client):
        """Register test user and return auth info"""
        resp = client.post(
            "/auth/register", json={"username": "testuser", "password": "testpass123"}
        )
        user_id = resp.json()["user_id"]

        response = client.post(
            "/auth/login", data={"username": "testuser", "password": "testpass123"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create profile
        client.post(f"/profile/{user_id}", headers=headers)
        return {"user_id": user_id, "headers": headers}

    def test_add_genre(self, client, test_user):
        """Should add genre to profile"""
        response = client.post(
            f"/profile/{test_user['user_id']}/genre",
            headers=test_user["headers"],
            json={"genre": "Fantasy"},
        )

        assert response.status_code == 200
        assert "Fantasy" in response.json()["genre_favorit"]

    def test_add_max_5_genres(self, client, test_user):
        """Should enforce max 5 genres invariant via API"""
        user_id = test_user["user_id"]
        headers = test_user["headers"]

        genres = ["Fantasy", "Sci-Fi", "Romance", "Mystery", "Horror"]
        for genre in genres:
            client.post(
                f"/profile/{user_id}/genre", headers=headers, json={"genre": genre}
            )

        # Try 6th genre
        response = client.post(
            f"/profile/{user_id}/genre", headers=headers, json={"genre": "Drama"}
        )

        assert response.status_code == 400
        assert "Cannot add" in response.json()["detail"]

    def test_add_rating(self, client, test_user):
        """Should add rating to book"""
        response = client.post(
            f"/profile/{test_user['user_id']}/rating",
            headers=test_user["headers"],
            json={"book_id": "book-001", "rating": 5},
        )

        assert response.status_code == 200
        assert response.json()["rating"] == "5"

    def test_add_invalid_rating(self, client, test_user):
        """Should reject invalid rating (not 1-5)"""
        response = client.post(
            f"/profile/{test_user['user_id']}/rating",
            headers=test_user["headers"],
            json={"book_id": "book-001", "rating": 10},
        )

        # 422 for Pydantic validation error, 400 for domain validation
        assert response.status_code in [400, 422]

    def test_block_item(self, client, test_user):
        """Should block item successfully"""
        response = client.post(
            f"/profile/{test_user['user_id']}/block",
            headers=test_user["headers"],
            json={"book_id": "bad-book"},
        )

        assert response.status_code == 200
        assert "bad-book" in response.json()["blocked_items"]

    def test_cannot_block_rated_book(self, client, test_user):
        """INVARIANT: Cannot block active books (books with ratings)"""
        user_id = test_user["user_id"]
        headers = test_user["headers"]

        # Rate the book first
        client.post(
            f"/profile/{user_id}/rating",
            headers=headers,
            json={"book_id": "book-001", "rating": 4},
        )

        # Try to block it
        response = client.post(
            f"/profile/{user_id}/block", headers=headers, json={"book_id": "book-001"}
        )

        assert response.status_code == 400
        assert "Cannot block active book" in response.json()["detail"]

    def test_get_profile(self, client, test_user):
        """Should get profile with all data"""
        user_id = test_user["user_id"]
        headers = test_user["headers"]

        # Populate profile
        client.post(
            f"/profile/{user_id}/genre", headers=headers, json={"genre": "Fantasy"}
        )
        client.post(
            f"/profile/{user_id}/rating",
            headers=headers,
            json={"book_id": "book-001", "rating": 5},
        )
        client.post(
            f"/profile/{user_id}/block", headers=headers, json={"book_id": "bad-book"}
        )

        # Get profile
        response = client.get(f"/profile/{user_id}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert "Fantasy" in data["genre_favorit"]
        assert "bad-book" in data["blocked_items"]
        assert len(data["riwayat_baca"]) == 1

    def test_get_snapshot(self, client, test_user):
        """Should get profile snapshot with statistics"""
        user_id = test_user["user_id"]
        headers = test_user["headers"]

        # Populate profile
        client.post(
            f"/profile/{user_id}/genre", headers=headers, json={"genre": "Fantasy"}
        )
        client.post(
            f"/profile/{user_id}/rating",
            headers=headers,
            json={"book_id": "book-001", "rating": 5},
        )
        client.post(
            f"/profile/{user_id}/rating",
            headers=headers,
            json={"book_id": "book-002", "rating": 3},
        )

        # Get snapshot
        response = client.get(f"/profile/{user_id}/snapshot", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert "Fantasy" in data["genre_favorit"]
        assert data["jumlah_buku_dibaca"] == 2
        assert data["rata_rata_rating"] == 4.0

    def test_get_snapshot_not_found(self, client, auth_headers, demo_user_credentials):
        """Should return 404 for nonexistent profile snapshot"""
        user_id = demo_user_credentials["user_id"]
        response = client.get(f"/profile/{user_id}/snapshot", headers=auth_headers)
        assert response.status_code == 404

    def test_get_snapshot_unauthorized(self, client, test_user):
        """User cannot view other user's snapshot"""
        # Register another user
        resp = client.post(
            "/auth/register", json={"username": "otheruser", "password": "otherpass123"}
        )
        other_user_id = resp.json()["user_id"]

        # Try to view other user's snapshot
        response = client.get(
            f"/profile/{other_user_id}/snapshot", headers=test_user["headers"]
        )
        assert response.status_code == 403


class TestProfileWorkflow:
    """End-to-end workflow tests"""

    def test_complete_user_workflow(self, client):
        """Test complete user journey"""
        # 1. Register
        register_resp = client.post(
            "/auth/register", json={"username": "newuser", "password": "securepass"}
        )
        assert register_resp.status_code == 201
        user_id = register_resp.json()["user_id"]

        # 2. Login
        login_resp = client.post(
            "/auth/login", data={"username": "newuser", "password": "securepass"}
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create profile
        create_resp = client.post(f"/profile/{user_id}", headers=headers)
        assert create_resp.status_code == 201

        # 4. Add preferences
        client.post(
            f"/profile/{user_id}/genre", headers=headers, json={"genre": "Fantasy"}
        )
        client.post(
            f"/profile/{user_id}/genre", headers=headers, json={"genre": "Sci-Fi"}
        )

        # 5. Rate books
        client.post(
            f"/profile/{user_id}/rating",
            headers=headers,
            json={"book_id": "book-001", "rating": 5},
        )
        client.post(
            f"/profile/{user_id}/rating",
            headers=headers,
            json={"book_id": "book-002", "rating": 3},
        )

        # 6. Block unwanted
        client.post(
            f"/profile/{user_id}/block", headers=headers, json={"book_id": "bad-book"}
        )

        # 7. Get final profile
        profile_resp = client.get(f"/profile/{user_id}", headers=headers)
        assert profile_resp.status_code == 200

        profile = profile_resp.json()
        assert len(profile["genre_favorit"]) == 2
        assert len(profile["riwayat_baca"]) == 2
        assert len(profile["blocked_items"]) == 1
