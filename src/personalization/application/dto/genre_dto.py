"""Genre DTOs"""
from pydantic import BaseModel, Field


class AddGenreRequest(BaseModel):
    """Request to add a favorite genre"""
    genre: str = Field(..., min_length=1, description="Genre name to add")
