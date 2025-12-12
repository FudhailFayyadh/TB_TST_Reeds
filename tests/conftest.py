"""
Pytest Configuration & Fixtures
Provides test client, auth helpers, and dependency overrides
"""

import pytest
from fastapi.testclient import TestClient
from typing import Generator, Dict

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from src.personalization.infrastructure.auth.jwt_handler import get_password_hash
from src.personalization.interface.controllers.auth_controller import fake_users_db
from src.personalization.interface.controllers import profile_controller


# ============== Fixtures ==============


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """
    Create a fresh TestClient for each test.
    Clears repository and user database before each test.
    """
    # Clear in-memory storage before each test
    if profile_controller._profil_service:
        profile_controller._profil_service.repository._storage.clear()

    # Reset fake users to only demo_user
    fake_users_db.clear()
    fake_users_db["demo_user"] = {
        "username": "demo_user",
        "hashed_password": get_password_hash("demo123"),
        "user_id": "user_001",
    }

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def demo_user_credentials() -> Dict[str, str]:
    """Demo user credentials for testing"""
    return {"username": "demo_user", "password": "demo123", "user_id": "user_001"}


@pytest.fixture
def second_user_credentials() -> Dict[str, str]:
    """Second user credentials for authorization tests"""
    return {"username": "test_user_2", "password": "testpass123"}


@pytest.fixture
def auth_token(client: TestClient, demo_user_credentials: Dict[str, str]) -> str:
    """Get valid JWT token for demo user"""
    response = client.post(
        "/auth/login",
        data={
            "username": demo_user_credentials["username"],
            "password": demo_user_credentials["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token: str) -> Dict[str, str]:
    """Authorization headers with Bearer token"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def second_user_token(
    client: TestClient, second_user_credentials: Dict[str, str]
) -> str:
    """Register and get token for second user"""
    # Register
    reg_response = client.post(
        "/auth/register",
        json={
            "username": second_user_credentials["username"],
            "password": second_user_credentials["password"],
        },
    )
    assert reg_response.status_code == 201

    # Login
    response = client.post(
        "/auth/login",
        data={
            "username": second_user_credentials["username"],
            "password": second_user_credentials["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def second_user_headers(second_user_token: str) -> Dict[str, str]:
    """Authorization headers for second user"""
    return {"Authorization": f"Bearer {second_user_token}"}


@pytest.fixture
def second_user_id(client: TestClient, second_user_credentials: Dict[str, str]) -> str:
    """Get the user_id for second user after registration"""
    reg_response = client.post(
        "/auth/register",
        json={
            "username": second_user_credentials["username"],
            "password": second_user_credentials["password"],
        },
    )
    if reg_response.status_code == 201:
        return reg_response.json()["user_id"]
    # If already registered, get from login
    return "user_002"


@pytest.fixture
def created_profile(
    client: TestClient,
    auth_headers: Dict[str, str],
    demo_user_credentials: Dict[str, str],
) -> str:
    """Create a profile and return user_id"""
    user_id = demo_user_credentials["user_id"]
    response = client.post(f"/profile/{user_id}", headers=auth_headers)
    assert response.status_code in [201, 400]  # 400 if already exists
    return user_id


# ============== Helper Functions ==============


def get_token_for_user(client: TestClient, username: str, password: str) -> str:
    """Helper to get token for any user"""
    response = client.post(
        "/auth/login", data={"username": username, "password": password}
    )
    return response.json().get("access_token", "")
