"""Profile DTOs"""
from pydantic import BaseModel
from typing import List, Dict


class CreateProfileRequest(BaseModel):
    """Request to create a new profile"""
    pass  # user_id comes from path parameter


class ProfileResponse(BaseModel):
    """Response containing profile information"""
    user_id: str
    genre_favorit: List[str]
    blocked_items: List[str]
    riwayat_baca: List[Dict]


class SnapshotResponse(BaseModel):
    """Response containing profile snapshot"""
    user_id: str
    genre_favorit: List[str]
    jumlah_buku_dibaca: int
    rata_rata_rating: float
    blocked_items: List[str]
    riwayat_baca: List[Dict]
