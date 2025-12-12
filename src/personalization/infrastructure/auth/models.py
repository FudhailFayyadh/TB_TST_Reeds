"""Authentication Models and Schemas"""

from typing import Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data extracted from JWT"""

    user_id: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request model"""

    username: str = Field(..., min_length=3, description="Username for authentication")
    password: str = Field(..., min_length=6, description="Password for authentication")


class UserCreate(BaseModel):
    """User creation model"""

    username: str = Field(..., min_length=3, description="Username")
    password: str = Field(..., min_length=6, description="Password")


class UserResponse(BaseModel):
    """User response model (without password)"""

    username: str
    user_id: str
