"""DaftarBlokir Value Object"""
from dataclasses import dataclass
from typing import Set


@dataclass(frozen=True)
class DaftarBlokir:
    """Value Object representing a list of blocked book IDs"""
    book_ids: frozenset
    
    def __post_init__(self):
        if not isinstance(self.book_ids, (frozenset, set)):
            raise ValueError("book_ids must be a set or frozenset")
        # Convert to frozenset for immutability
        if isinstance(self.book_ids, set):
            object.__setattr__(self, 'book_ids', frozenset(self.book_ids))
    
    @staticmethod
    def empty() -> 'DaftarBlokir':
        """Create an empty block list"""
        return DaftarBlokir(frozenset())
    
    def contains(self, book_id: str) -> bool:
        """Check if a book is blocked"""
        return book_id in self.book_ids
    
    def add(self, book_id: str) -> 'DaftarBlokir':
        """Return a new DaftarBlokir with the book_id added"""
        new_ids = self.book_ids | {book_id}
        return DaftarBlokir(new_ids)
    
    def remove(self, book_id: str) -> 'DaftarBlokir':
        """Return a new DaftarBlokir with the book_id removed"""
        new_ids = self.book_ids - {book_id}
        return DaftarBlokir(new_ids)
    
    def __len__(self) -> int:
        return len(self.book_ids)
