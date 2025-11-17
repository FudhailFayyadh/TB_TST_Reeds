"""GenreFavoritDiubah Domain Event"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GenreFavoritDiubah:
    """Domain Event: User's favorite genre has been changed"""
    user_id: str
    genre: str
    action: str  # "added" or "removed"
    timestamp: datetime
