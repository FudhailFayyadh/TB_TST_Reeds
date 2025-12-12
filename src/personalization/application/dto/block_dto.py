"""Block DTOs"""

from pydantic import BaseModel, Field


class BlockItemRequest(BaseModel):
    """Request to block a book"""

    book_id: str = Field(..., min_length=1, description="Book ID to block")
