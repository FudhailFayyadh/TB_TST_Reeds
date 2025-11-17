"""RiwayatBaca Entity"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from ..value_objects.rating import Rating


@dataclass
class RiwayatBaca:
    """Entity representing a reading history entry"""
    book_id: str
    rating: Optional[Rating] = None
    tanggal_baca: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if not self.book_id or not self.book_id.strip():
            raise ValueError("book_id cannot be empty")
    
    def update_rating(self, rating: Rating) -> None:
        """Update the rating for this book"""
        self.rating = rating
    
    def __eq__(self, other) -> bool:
        """Two RiwayatBaca are equal if they have the same book_id"""
        if not isinstance(other, RiwayatBaca):
            return False
        return self.book_id == other.book_id
    
    def __hash__(self) -> int:
        return hash(self.book_id)
