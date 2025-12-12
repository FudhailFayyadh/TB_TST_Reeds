"""Rating DTOs"""

from pydantic import BaseModel, Field


class AddRatingRequest(BaseModel):
    """Request to add a rating"""

    book_id: str = Field(..., min_length=1, description="Book ID to rate")
    rating: int = Field(..., ge=1, le=5, description="Rating value (1-5)")
