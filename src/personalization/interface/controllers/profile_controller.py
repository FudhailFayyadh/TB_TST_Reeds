"""Profile Controller - REST API endpoints with JWT Authentication"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict

from ...application.services import ProfilService
from ...application.dto import (
    CreateProfileRequest,
    ProfileResponse,
    SnapshotResponse,
    AddGenreRequest,
    AddRatingRequest,
    BlockItemRequest,
)
from ...infrastructure.auth.dependencies import get_current_user


router = APIRouter(prefix="/profile", tags=["Profile"])

# Dependency injection placeholder - will be set in main.py
_profil_service: ProfilService = None


def get_profil_service() -> ProfilService:
    """Dependency injection for ProfilService"""
    if _profil_service is None:
        raise RuntimeError("ProfilService not initialized")
    return _profil_service


def set_profil_service(service: ProfilService):
    """Set the ProfilService instance"""
    global _profil_service
    _profil_service = service


@router.post("/{user_id}", response_model=Dict[str, str], status_code=201)
async def create_profile(
    user_id: str,
    request: CreateProfileRequest = CreateProfileRequest(),
    service: ProfilService = Depends(get_profil_service),
    current_user: str = Depends(get_current_user),
):
    """
    Create a new user profile.

    Requires JWT authentication. Users can only create their own profile.

    - **user_id**: Unique identifier for the user
    """
    # Authorization check: users can only create their own profile
    if current_user != user_id:
        raise HTTPException(
            status_code=403, detail="You can only create your own profile"
        )

    try:
        profil = service.create_profile(user_id)
        return {
            "message": f"Profile created for user {user_id}",
            "user_id": str(profil.user_id),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=ProfileResponse)
async def get_profile(
    user_id: str,
    service: ProfilService = Depends(get_profil_service),
    current_user: str = Depends(get_current_user),
):
    """
    Get user profile by user_id.

    Requires JWT authentication. Users can only view their own profile.

    - **user_id**: User identifier
    """
    # Authorization check
    if current_user != user_id:
        raise HTTPException(
            status_code=403, detail="You can only view your own profile"
        )

    profil = service.get_profile(user_id)
    if not profil:
        raise HTTPException(
            status_code=404, detail=f"Profile for user {user_id} not found"
        )

    return ProfileResponse(
        user_id=str(profil.user_id),
        genre_favorit=profil.get_genre_favorit(),
        blocked_items=profil.get_blocked_items(),
        riwayat_baca=profil.get_riwayat_baca_list(),
    )


@router.post("/{user_id}/genre")
async def add_genre(
    user_id: str,
    request: AddGenreRequest,
    service: ProfilService = Depends(get_profil_service),
    current_user: str = Depends(get_current_user),
):
    """
    Add a favorite genre to user profile.

    Requires JWT authentication. Users can only modify their own profile.

    - **user_id**: User identifier
    - **genre**: Genre name (max 5 genres allowed)
    """
    # Authorization check
    if current_user != user_id:
        raise HTTPException(
            status_code=403, detail="You can only modify your own profile"
        )

    try:
        profil = service.add_genre(user_id, request.genre)
        return {
            "message": f"Genre '{request.genre}' added to user {user_id}",
            "genre_favorit": profil.get_genre_favorit(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{user_id}/rating", response_model=Dict[str, str])
async def add_rating(
    user_id: str,
    request: AddRatingRequest,
    service: ProfilService = Depends(get_profil_service),
    current_user: str = Depends(get_current_user),
):
    """
    Add or update a rating for a book.

    Requires JWT authentication. Users can only add ratings to their own profile.

    - **user_id**: User identifier
    - **book_id**: Book identifier
    - **rating**: Rating value (1-5)
    """
    # Authorization check
    if current_user != user_id:
        raise HTTPException(
            status_code=403, detail="You can only add ratings to your own profile"
        )

    try:
        service.add_rating(user_id, request.book_id, request.rating)
        return {
            "message": f"Rating {request.rating} added for book {request.book_id}",
            "user_id": user_id,
            "book_id": request.book_id,
            "rating": str(request.rating),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{user_id}/block")
async def block_item(
    user_id: str,
    request: BlockItemRequest,
    service: ProfilService = Depends(get_profil_service),
    current_user: str = Depends(get_current_user),
):
    """
    Block a book from recommendations.

    Requires JWT authentication. Users can only block items in their own profile.

    - **user_id**: User identifier
    - **book_id**: Book identifier to block

    Note: Cannot block books that have been rated (active books)
    """
    # Authorization check
    if current_user != user_id:
        raise HTTPException(
            status_code=403, detail="You can only block items in your own profile"
        )

    try:
        profil = service.block_item(user_id, request.book_id)
        return {
            "message": f"Book {request.book_id} blocked for user {user_id}",
            "blocked_items": profil.get_blocked_items(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}/snapshot", response_model=SnapshotResponse)
async def get_snapshot(
    user_id: str,
    service: ProfilService = Depends(get_profil_service),
    current_user: str = Depends(get_current_user),
):
    """
    Get profile snapshot (read model) with aggregated statistics.

    Requires JWT authentication. Users can only view their own snapshot.

    - **user_id**: User identifier

    Returns denormalized data optimized for queries including:
    - Favorite genres
    - Total books read
    - Average rating
    - Blocked items
    - Reading history
    """
    # Authorization check
    if current_user != user_id:
        raise HTTPException(
            status_code=403, detail="You can only view your own profile snapshot"
        )

    snapshot = service.get_snapshot(user_id)
    if not snapshot:
        raise HTTPException(
            status_code=404, detail=f"Profile for user {user_id} not found"
        )

    return snapshot
