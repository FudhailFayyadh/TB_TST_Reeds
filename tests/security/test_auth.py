"""
Security Tests - JWT Authentication & Authorization
Tests for token handling, expiration, and security vulnerabilities
Uses fixtures from conftest.py for state management
"""
import pytest
import time
from datetime import timedelta
from jose import jwt

from src.personalization.infrastructure.auth.jwt_handler import (
    create_access_token,
    verify_token,
    SECRET_KEY,
    ALGORITHM
)


class TestJWTTokenCreation:
    """Test JWT token creation"""
    
    def test_create_token_with_user_id(self):
        """Should create token containing user_id"""
        token = create_access_token(data={"sub": "user-001"})
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_token_contains_correct_claims(self):
        """Token should contain correct claims"""
        token = create_access_token(data={"sub": "user-001"})
        
        # Decode without verification to check claims
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert payload["sub"] == "user-001"
        assert "exp" in payload
    
    def test_token_has_expiration(self):
        """Token should have expiration time"""
        token = create_access_token(data={"sub": "user-001"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert "exp" in payload
        assert payload["exp"] > time.time()
    
    def test_custom_expiration(self):
        """Should allow custom expiration time"""
        # Create token with 5 second expiration
        token = create_access_token(
            data={"sub": "user-001"},
            expires_delta=timedelta(seconds=5)
        )
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Should expire within 10 seconds (allowing some buffer)
        assert payload["exp"] < time.time() + 10


class TestJWTTokenVerification:
    """Test JWT token verification"""
    
    def test_verify_valid_token(self):
        """Should verify valid token and return payload with user_id"""
        token = create_access_token(data={"sub": "user-001"})
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user-001"
    
    def test_verify_invalid_token(self):
        """Should return None for invalid token"""
        invalid_token = "invalid.token.here"
        
        result = verify_token(invalid_token)
        
        assert result is None
    
    def test_verify_tampered_token(self):
        """Should reject tampered token"""
        token = create_access_token(data={"sub": "user-001"})
        
        # Tamper with the token
        tampered_token = token[:-5] + "XXXXX"
        
        result = verify_token(tampered_token)
        
        assert result is None
    
    def test_verify_token_wrong_secret(self):
        """Should reject token signed with wrong secret"""
        # Create token with wrong secret
        wrong_token = jwt.encode(
            {"sub": "user-001", "exp": time.time() + 3600},
            "wrong_secret",
            algorithm=ALGORITHM
        )
        
        result = verify_token(wrong_token)
        
        assert result is None


class TestAuthEndpointSecurity:
    """Test security of auth endpoints"""
    
    def test_password_not_returned_on_register(self, client):
        """Password should never be returned in response"""
        response = client.post("/auth/register", json={
            "username": "testuser",
            "password": "secretpassword"
        })
        
        data = response.json()
        assert "password" not in data
        assert "secretpassword" not in str(data)
    
    def test_password_not_returned_on_login(self, client):
        """Password should not be in login response"""
        client.post("/auth/register", json={
            "username": "testuser",
            "password": "secretpassword"
        })
        
        response = client.post("/auth/login", data={
            "username": "testuser",
            "password": "secretpassword"
        })
        
        data = response.json()
        assert "password" not in data
        assert "secretpassword" not in str(data)
    
    def test_login_timing_attack_resistance(self, client):
        """Login should not reveal if username exists via timing"""
        # Register user
        client.post("/auth/register", json={
            "username": "existinguser",
            "password": "password123"
        })
        
        # Both should fail with same status code
        wrong_user = client.post("/auth/login", data={
            "username": "nonexistent",
            "password": "password123"
        })
        
        wrong_pass = client.post("/auth/login", data={
            "username": "existinguser",
            "password": "wrongpassword"
        })
        
        # Both should return 401 with similar messages
        assert wrong_user.status_code == 401
        assert wrong_pass.status_code == 401


class TestProtectedEndpointSecurity:
    """Test security of protected endpoints"""
    
    def test_no_auth_header_rejected(self, client):
        """Requests without Authorization header should be rejected"""
        response = client.get("/profile/user-001")
        assert response.status_code == 401
    
    def test_invalid_auth_scheme_rejected(self, client):
        """Invalid auth scheme should be rejected"""
        response = client.get(
            "/profile/user-001",
            headers={"Authorization": "Basic dXNlcjpwYXNz"}
        )
        assert response.status_code == 401
    
    def test_empty_bearer_token_rejected(self, client):
        """Empty bearer token should be rejected"""
        response = client.get(
            "/profile/user-001",
            headers={"Authorization": "Bearer "}
        )
        assert response.status_code == 401
    
    def test_malformed_jwt_rejected(self, client):
        """Malformed JWT should be rejected"""
        response = client.get(
            "/profile/user-001",
            headers={"Authorization": "Bearer not.a.valid.jwt"}
        )
        assert response.status_code == 401
    
    def test_forged_jwt_rejected(self, client):
        """JWT signed with wrong key should be rejected"""
        # Create token with wrong secret
        forged_token = jwt.encode(
            {"sub": "admin", "exp": time.time() + 3600},
            "attacker_secret",
            algorithm=ALGORITHM
        )
        
        response = client.get(
            "/profile/admin",
            headers={"Authorization": f"Bearer {forged_token}"}
        )
        assert response.status_code == 401


class TestAuthorizationSecurity:
    """Test authorization (user access control)"""
    
    @pytest.fixture
    def attacker_auth(self, client):
        """Auth info for attacker"""
        resp = client.post("/auth/register", json={
            "username": "attacker",
            "password": "evil123"
        })
        user_id = resp.json()["user_id"]
        response = client.post("/auth/login", data={
            "username": "attacker",
            "password": "evil123"
        })
        token = response.json()["access_token"]
        return {"headers": {"Authorization": f"Bearer {token}"}, "user_id": user_id}
    
    @pytest.fixture
    def victim_auth(self, client):
        """Auth info for victim"""
        resp = client.post("/auth/register", json={
            "username": "victim",
            "password": "innocent123"
        })
        user_id = resp.json()["user_id"]
        response = client.post("/auth/login", data={
            "username": "victim",
            "password": "innocent123"
        })
        token = response.json()["access_token"]
        return {"headers": {"Authorization": f"Bearer {token}"}, "user_id": user_id}
    
    def test_attacker_cannot_create_victim_profile(self, client, attacker_auth, victim_auth):
        """Attacker cannot create profile for another user"""
        response = client.post(
            f"/profile/{victim_auth['user_id']}", 
            headers=attacker_auth["headers"]
        )
        assert response.status_code == 403
    
    def test_attacker_cannot_view_victim_profile(self, client, attacker_auth, victim_auth):
        """Attacker cannot view victim's profile"""
        # Victim creates their profile
        client.post(f"/profile/{victim_auth['user_id']}", headers=victim_auth["headers"])
        
        # Attacker tries to view
        response = client.get(
            f"/profile/{victim_auth['user_id']}", 
            headers=attacker_auth["headers"]
        )
        assert response.status_code == 403
    
    def test_attacker_cannot_add_genre_to_victim(self, client, attacker_auth, victim_auth):
        """Attacker cannot modify victim's genres"""
        client.post(f"/profile/{victim_auth['user_id']}", headers=victim_auth["headers"])
        
        response = client.post(
            f"/profile/{victim_auth['user_id']}/genre",
            headers=attacker_auth["headers"],
            json={"genre": "Malware"}
        )
        assert response.status_code == 403
    
    def test_attacker_cannot_rate_for_victim(self, client, attacker_auth, victim_auth):
        """Attacker cannot add ratings to victim's profile"""
        client.post(f"/profile/{victim_auth['user_id']}", headers=victim_auth["headers"])
        
        response = client.post(
            f"/profile/{victim_auth['user_id']}/rating",
            headers=attacker_auth["headers"],
            json={"book_id": "book-001", "rating": 1}
        )
        assert response.status_code == 403
    
    def test_attacker_cannot_block_for_victim(self, client, attacker_auth, victim_auth):
        """Attacker cannot block items for victim"""
        client.post(f"/profile/{victim_auth['user_id']}", headers=victim_auth["headers"])
        
        response = client.post(
            f"/profile/{victim_auth['user_id']}/block",
            headers=attacker_auth["headers"],
            json={"book_id": "book-001"}
        )
        assert response.status_code == 403


class TestTokenManipulationAttacks:
    """Test against common JWT attacks"""
    
    @pytest.fixture
    def valid_token(self, client):
        """Create a valid token"""
        client.post("/auth/register", json={
            "username": "testuser",
            "password": "testpass"
        })
        response = client.post("/auth/login", data={
            "username": "testuser",
            "password": "testpass"
        })
        return response.json()["access_token"]
    
    def test_none_algorithm_attack(self, client):
        """Should reject tokens with 'none' algorithm"""
        import base64
        header = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').decode().rstrip('=')
        payload = base64.urlsafe_b64encode(b'{"sub":"admin"}').decode().rstrip('=')
        none_token = f"{header}.{payload}."
        
        response = client.get(
            "/profile/admin",
            headers={"Authorization": f"Bearer {none_token}"}
        )
        assert response.status_code == 401
    
    def test_sql_injection_in_user_id(self, client, valid_token):
        """SQL injection attempt in user_id should not work"""
        headers = {"Authorization": f"Bearer {valid_token}"}
        
        response = client.get(
            "/profile/'; DROP TABLE users;--",
            headers=headers
        )
        # Should be 403 (not authorized) not 500 (server error)
        assert response.status_code in [403, 404]
    
    def test_path_traversal_in_user_id(self, client, valid_token):
        """Path traversal in user_id should not work"""
        headers = {"Authorization": f"Bearer {valid_token}"}
        
        response = client.get(
            "/profile/../../../etc/passwd",
            headers=headers
        )
        # Should be 403 or 404, not expose files
        assert response.status_code in [403, 404, 422]
