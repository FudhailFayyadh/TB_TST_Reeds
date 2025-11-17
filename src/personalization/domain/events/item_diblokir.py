"""ItemDiblokir Domain Event"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ItemDiblokir:
    """Domain Event: User has blocked a book"""
    user_id: str
    book_id: str
    timestamp: datetime
