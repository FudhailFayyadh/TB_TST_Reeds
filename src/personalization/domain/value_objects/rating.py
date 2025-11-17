"""Rating Value Object"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Rating:
    """Value Object representing a book rating (1-5)"""
    nilai: int
    
    def __post_init__(self):
        if not isinstance(self.nilai, int):
            raise ValueError("Rating must be an integer")
        if not 1 <= self.nilai <= 5:
            raise ValueError("Rating must be between 1 and 5")
    
    def __int__(self) -> int:
        return self.nilai
