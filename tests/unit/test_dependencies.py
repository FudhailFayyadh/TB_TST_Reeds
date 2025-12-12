"""
Unit Tests for Auth Dependencies
Tests for dependencies.py - authentication dependency injection
"""

import pytest
from fastapi import HTTPException

from src.personalization.infrastructure.auth.dependencies import get_current_user
from src.personalization.infrastructure.auth.jwt_handler import create_access_token


class TestGetCurrentUser:
    """Tests for get_current_user dependency"""

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        """Should return user_id for valid token"""
        token = create_access_token(data={"sub": "user-001"})

        result = await get_current_user(token)

        assert result == "user-001"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Should raise HTTPException for invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("invalid.token.here")

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_empty_token(self):
        """Should raise HTTPException for empty token"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("")

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self):
        """Should raise HTTPException for expired token"""
        from datetime import timedelta

        expired_token = create_access_token(
            data={"sub": "user-001"}, expires_delta=timedelta(seconds=-1)
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(expired_token)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_token_without_sub(self):
        """Should raise HTTPException when token has no 'sub' claim"""
        from jose import jwt
        from src.personalization.infrastructure.auth.jwt_handler import (
            SECRET_KEY,
            ALGORITHM,
        )
        import time

        # Create token without 'sub' claim
        token = jwt.encode(
            {"exp": time.time() + 3600, "some_other_claim": "value"},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_returns_string(self):
        """Should return user_id as string"""
        token = create_access_token(data={"sub": "user-123"})

        result = await get_current_user(token)

        assert isinstance(result, str)
        assert result == "user-123"

    @pytest.mark.asyncio
    async def test_get_current_user_with_special_characters(self):
        """Should handle user_id with special characters"""
        user_id = "user_001-test@example"
        token = create_access_token(data={"sub": user_id})

        result = await get_current_user(token)

        assert result == user_id

    @pytest.mark.asyncio
    async def test_get_current_user_tampered_token(self):
        """Should raise HTTPException for tampered token"""
        token = create_access_token(data={"sub": "user-001"})
        tampered = token[:-5] + "XXXXX"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(tampered)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_exception_has_www_authenticate_header(self):
        """HTTPException should include WWW-Authenticate header"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("invalid")

        assert exc_info.value.headers is not None
        assert exc_info.value.headers.get("WWW-Authenticate") == "Bearer"
