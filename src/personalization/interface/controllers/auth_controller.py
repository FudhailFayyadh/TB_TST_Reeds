"""Authentication Controller - Login and Token Management"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Dict

from ...infrastructure.auth.jwt_handler import (
    create_access_token,
    verify_password,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ...infrastructure.auth.models import Token, LoginRequest, UserCreate
from ...infrastructure.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory user storage (for demo purposes - Milestone 5)
# In production, use a proper database
fake_users_db: Dict[str, dict] = {
    "demo_user": {
        "username": "demo_user",
        "hashed_password": get_password_hash("demo123"),
        "user_id": "user_001"
    }
}


@router.post("/register", response_model=Dict[str, str], status_code=201)
async def register(user: UserCreate):
    """
    Register a new user.
    
    - **username**: Unique username (min 3 characters)
    - **password**: Password (min 6 characters)
    
    Returns:
    - User registration confirmation with user_id
    """
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Generate user_id
    user_id = f"user_{len(fake_users_db) + 1:03d}"
    
    # Store user
    fake_users_db[user.username] = {
        "username": user.username,
        "hashed_password": get_password_hash(user.password),
        "user_id": user_id
    }
    
    return {
        "message": "User registered successfully",
        "username": user.username,
        "user_id": user_id
    }


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible login endpoint.
    
    Returns a JWT access token for authentication.
    
    - **username**: Username
    - **password**: Password
    
    Returns:
    - **access_token**: JWT token (valid for 30 minutes)
    - **token_type**: Bearer
    
    Demo credentials:
    - username: demo_user
    - password: demo123
    """
    # Authenticate user
    user = fake_users_db.get(form_data.username)
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["user_id"]},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=Dict[str, str])
async def get_current_user_info(current_user_id: str = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header.
    
    Returns:
    - **user_id**: Current user's ID
    - **authenticated**: Authentication status
    """
    return {
        "user_id": current_user_id,
        "authenticated": "true",
        "message": "Token is valid"
    }


@router.post("/token", response_model=Token)
async def login_json(login_request: LoginRequest):
    """
    Alternative login endpoint accepting JSON body.
    
    - **username**: Username
    - **password**: Password
    
    Returns JWT access token.
    """
    # Authenticate user
    user = fake_users_db.get(login_request.username)
    
    if not user or not verify_password(login_request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["user_id"]},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")
