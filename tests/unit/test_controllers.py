"""
Unit Tests for Controllers
Tests for auth_controller.py and profile_controller.py using TestClient
These are technically integration tests but placed in unit for coverage
"""
import pytest
from fastapi.testclient import TestClient

from main import app, repository
from src.personalization.interface.controllers.auth_controller import fake_users_db
from src.personalization.infrastructure.in_memory.in_memory_profil_repository import (
    InMemoryProfilMinatBacaRepository
)


class TestAuthControllerUnit:
    """Unit-level tests for auth controller endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Clear fake_users_db before each test"""
        fake_users_db.clear()
        # Add back demo user
        from src.personalization.infrastructure.auth.jwt_handler import get_password_hash
        fake_users_db["demo_user"] = {
            "username": "demo_user",
            "hashed_password": get_password_hash("demo123"),
            "user_id": "user_001"
        }
        yield
        fake_users_db.clear()
    
    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)
    
    # === Registration Tests ===
    
    def test_register_new_user(self, client):
        """Should register a new user successfully"""
        response = client.post("/auth/register", json={
            "username": "newuser",
            "password": "password123"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert "user_id" in data
        assert data["message"] == "User registered successfully"
    
    def test_register_duplicate_username(self, client):
        """Should reject duplicate username"""
        # First registration
        client.post("/auth/register", json={
            "username": "testuser",
            "password": "password123"
        })
        
        # Duplicate registration
        response = client.post("/auth/register", json={
            "username": "testuser",
            "password": "different123"
        })
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    # === Login Tests (Form Data) ===
    
    def test_login_success_form(self, client):
        """Should login with correct credentials (form data)"""
        response = client.post("/auth/login", data={
            "username": "demo_user",
            "password": "demo123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client):
        """Should reject wrong password"""
        response = client.post("/auth/login", data={
            "username": "demo_user",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client):
        """Should reject nonexistent user"""
        response = client.post("/auth/login", data={
            "username": "nonexistent",
            "password": "password123"
        })
        
        assert response.status_code == 401
    
    # === Login Tests (JSON) ===
    
    def test_login_json_success(self, client):
        """Should login with JSON body"""
        response = client.post("/auth/token", json={
            "username": "demo_user",
            "password": "demo123"
        })
        
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_json_invalid_credentials(self, client):
        """Should reject invalid JSON credentials"""
        response = client.post("/auth/token", json={
            "username": "demo_user",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
    
    # === Get Current User Tests ===
    
    def test_get_me_with_valid_token(self, client):
        """Should get current user info with valid token"""
        # Login first
        login_resp = client.post("/auth/login", data={
            "username": "demo_user",
            "password": "demo123"
        })
        token = login_resp.json()["access_token"]
        
        # Get user info
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user_001"
        assert data["authenticated"] == "true"
    
    def test_get_me_without_token(self, client):
        """Should reject request without token"""
        response = client.get("/auth/me")
        
        assert response.status_code == 401
    
    def test_get_me_with_invalid_token(self, client):
        """Should reject invalid token"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401


class TestProfileControllerUnit:
    """Unit-level tests for profile controller endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Clear data before each test"""
        fake_users_db.clear()
        # Clear repository data using the clear() method
        repository.clear()
        
        from src.personalization.infrastructure.auth.jwt_handler import get_password_hash
        fake_users_db["testuser"] = {
            "username": "testuser",
            "hashed_password": get_password_hash("password123"),
            "user_id": "user_001"
        }
        yield
        # Cleanup after test
        repository.clear()
    
    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self, client):
        """Get auth headers for testuser"""
        login_resp = client.post("/auth/login", data={
            "username": "testuser",
            "password": "password123"
        })
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    # === Create Profile Tests ===
    
    def test_create_profile_success(self, client, auth_headers):
        """Should create profile for authenticated user"""
        response = client.post(
            "/profile/user_001",
            headers=auth_headers
        )
        
        assert response.status_code == 201
        assert response.json()["user_id"] == "user_001"
    
    def test_create_profile_unauthorized(self, client, auth_headers):
        """Should reject creating other user's profile"""
        response = client.post(
            "/profile/different_user",
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    def test_create_profile_no_auth(self, client):
        """Should reject without authentication"""
        response = client.post("/profile/user_001")
        
        assert response.status_code == 401
    
    # === Get Profile Tests ===
    
    def test_get_profile_success(self, client, auth_headers):
        """Should get own profile"""
        # Create first
        client.post("/profile/user_001", headers=auth_headers)
        
        response = client.get(
            "/profile/user_001",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["user_id"] == "user_001"
    
    def test_get_profile_not_found(self, client, auth_headers):
        """Should return 404 for nonexistent profile"""
        response = client.get(
            "/profile/user_001",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_get_profile_unauthorized(self, client, auth_headers):
        """Should reject getting other user's profile"""
        response = client.get(
            "/profile/other_user",
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    # === Add Genre Tests ===
    
    def test_add_genre_success(self, client, auth_headers):
        """Should add genre to profile"""
        client.post("/profile/user_001", headers=auth_headers)
        
        response = client.post(
            "/profile/user_001/genre",
            headers=auth_headers,
            json={"genre": "Fiction"}
        )
        
        assert response.status_code == 200
    
    def test_add_genre_profile_not_found(self, client, auth_headers):
        """Should return 400 for nonexistent profile (ValueError from service)"""
        response = client.post(
            "/profile/user_001/genre",
            headers=auth_headers,
            json={"genre": "Fiction"}
        )
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]
    
    def test_add_genre_max_5(self, client, auth_headers):
        """Should reject more than 5 genres"""
        client.post("/profile/user_001", headers=auth_headers)
        
        # Add 5 genres
        for i in range(5):
            client.post(
                "/profile/user_001/genre",
                headers=auth_headers,
                json={"genre": f"Genre{i}"}
            )
        
        # Try to add 6th
        response = client.post(
            "/profile/user_001/genre",
            headers=auth_headers,
            json={"genre": "Genre6"}
        )
        
        assert response.status_code == 400
    
    # === Add Rating Tests ===
    
    def test_add_rating_success(self, client, auth_headers):
        """Should add rating to profile"""
        client.post("/profile/user_001", headers=auth_headers)
        
        response = client.post(
            "/profile/user_001/rating",
            headers=auth_headers,
            json={"book_id": "book-001", "rating": 5}
        )
        
        assert response.status_code == 200
    
    def test_add_rating_invalid_value(self, client, auth_headers):
        """Should reject invalid rating value (Pydantic validation)"""
        client.post("/profile/user_001", headers=auth_headers)
        
        response = client.post(
            "/profile/user_001/rating",
            headers=auth_headers,
            json={"book_id": "book-001", "rating": 10}
        )
        
        # Pydantic validation returns 422 for invalid values
        assert response.status_code == 422
    
    def test_add_rating_profile_not_found(self, client, auth_headers):
        """Should return 400 for nonexistent profile (ValueError from service)"""
        response = client.post(
            "/profile/user_001/rating",
            headers=auth_headers,
            json={"book_id": "book-001", "rating": 5}
        )
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]
    
    # === Block Item Tests ===
    
    def test_block_item_success(self, client, auth_headers):
        """Should block item in profile"""
        # Create profile first
        client.post("/profile/user_001", headers=auth_headers)
        
        response = client.post(
            "/profile/user_001/block",
            headers=auth_headers,
            json={"book_id": "book-002"}  # Use different book that hasn't been rated
        )
        
        assert response.status_code == 200
        assert "book-002" in response.json()["blocked_items"]
    
    def test_block_item_cannot_block_rated(self, client, auth_headers):
        """Should not allow blocking a rated book"""
        client.post("/profile/user_001", headers=auth_headers)
        
        # Rate book first
        client.post(
            "/profile/user_001/rating",
            headers=auth_headers,
            json={"book_id": "book-001", "rating": 5}
        )
        
        # Try to block
        response = client.post(
            "/profile/user_001/block",
            headers=auth_headers,
            json={"book_id": "book-001"}
        )
        
        assert response.status_code == 400
    
    # === Get Snapshot Tests ===
    
    def test_get_snapshot_success(self, client, auth_headers):
        """Should get profile snapshot"""
        client.post("/profile/user_001", headers=auth_headers)
        
        response = client.get(
            "/profile/user_001/snapshot",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user_001"
    
    def test_get_snapshot_not_found(self, client, auth_headers):
        """Should return 404 for nonexistent profile snapshot"""
        # Don't create profile - test not found case
        response = client.get(
            "/profile/user_001/snapshot",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_get_snapshot_unauthorized(self, client, auth_headers):
        """Should reject getting other user's snapshot"""
        response = client.get(
            "/profile/other_user/snapshot",
            headers=auth_headers
        )
        
        assert response.status_code == 403
