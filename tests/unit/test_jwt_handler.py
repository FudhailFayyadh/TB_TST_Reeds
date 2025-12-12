"""
Unit Tests for JWT Handler
Tests for jwt_handler.py - token creation, verification, and password hashing
"""

from datetime import timedelta
import time
from jose import jwt

from src.personalization.infrastructure.auth.jwt_handler import (
    create_access_token,
    verify_token,
    get_password_hash,
    verify_password,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


class TestPasswordHashing:
    """Tests for password hashing functions"""

    def test_get_password_hash_returns_hashed_string(self):
        """Should return a hashed password string"""
        password = "mypassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert isinstance(hashed, str)

    def test_get_password_hash_different_for_same_password(self):
        """Should generate different hashes for same password (due to salt)"""
        password = "mypassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Different hashes due to different salt
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Should verify correct password"""
        password = "mypassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Should reject incorrect password"""
        password = "mypassword123"
        hashed = get_password_hash(password)

        assert verify_password("wrongpassword", hashed) is False

    def test_verify_password_empty_password(self):
        """Should handle empty password verification"""
        hashed = get_password_hash("somepassword")

        assert verify_password("", hashed) is False

    def test_verify_password_special_characters(self):
        """Should handle passwords with special characters"""
        password = "p@$$w0rd!#$%^&*()"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("p@$$w0rd", hashed) is False


class TestCreateAccessToken:
    """Tests for JWT token creation"""

    def test_create_token_with_user_id(self):
        """Should create token with user_id in payload"""
        token = create_access_token(data={"sub": "user-001"})

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_token_payload_contains_sub(self):
        """Token payload should contain the 'sub' claim"""
        token = create_access_token(data={"sub": "user-001"})

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "user-001"

    def test_create_token_has_expiration(self):
        """Token should have expiration claim"""
        token = create_access_token(data={"sub": "user-001"})

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload

    def test_create_token_default_expiration(self):
        """Token should use default expiration when not specified"""
        token = create_access_token(data={"sub": "user-001"})

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Expiration should be around ACCESS_TOKEN_EXPIRE_MINUTES from now
        expected_exp = time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        # Allow 10 second buffer for test execution time
        assert abs(payload["exp"] - expected_exp) < 10

    def test_create_token_custom_expiration(self):
        """Token should use custom expiration when specified"""
        custom_delta = timedelta(minutes=5)
        token = create_access_token(
            data={"sub": "user-001"}, expires_delta=custom_delta
        )

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expected_exp = time.time() + 300  # 5 minutes in seconds
        # Allow 10 second buffer
        assert abs(payload["exp"] - expected_exp) < 10

    def test_create_token_with_additional_claims(self):
        """Token can include additional custom claims"""
        token = create_access_token(
            data={"sub": "user-001", "role": "admin", "name": "Test User"}
        )

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "user-001"
        assert payload["role"] == "admin"
        assert payload["name"] == "Test User"

    def test_create_token_empty_data(self):
        """Should create token even with empty data dict"""
        token = create_access_token(data={})

        assert token is not None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload


class TestVerifyToken:
    """Tests for JWT token verification"""

    def test_verify_valid_token(self):
        """Should successfully verify a valid token"""
        token = create_access_token(data={"sub": "user-001"})

        payload = verify_token(token)

        assert payload is not None
        assert payload["sub"] == "user-001"

    def test_verify_invalid_token_string(self):
        """Should return None for invalid token string"""
        result = verify_token("invalid.token.string")

        assert result is None

    def test_verify_empty_token(self):
        """Should return None for empty token"""
        result = verify_token("")

        assert result is None

    def test_verify_tampered_token(self):
        """Should return None for tampered token"""
        token = create_access_token(data={"sub": "user-001"})
        # Tamper with the token
        tampered = token[:-5] + "XXXXX"

        result = verify_token(tampered)

        assert result is None

    def test_verify_token_wrong_secret(self):
        """Should return None for token signed with wrong secret"""
        # Create token with different secret
        wrong_token = jwt.encode(
            {"sub": "user-001", "exp": time.time() + 3600},
            "wrong-secret-key",
            algorithm=ALGORITHM,
        )

        result = verify_token(wrong_token)

        assert result is None

    def test_verify_expired_token(self):
        """Should return None for expired token"""
        # Create already expired token
        expired_token = create_access_token(
            data={"sub": "user-001"}, expires_delta=timedelta(seconds=-1)
        )

        result = verify_token(expired_token)

        assert result is None

    def test_verify_token_returns_all_claims(self):
        """Should return all claims from token"""
        token = create_access_token(
            data={"sub": "user-001", "custom_claim": "custom_value"}
        )

        payload = verify_token(token)

        assert payload["sub"] == "user-001"
        assert payload["custom_claim"] == "custom_value"
        assert "exp" in payload
