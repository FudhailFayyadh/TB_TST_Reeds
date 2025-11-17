"""RatingDiberikan Domain Event"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RatingDiberikan:
    """Domain Event: User has given a rating to a book"""
    user_id: str
    book_id: str
    rating: int
    timestamp: datetime
