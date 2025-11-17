"""PreferensiEksplisit Value Object"""
from dataclasses import dataclass
from typing import List
from .genre_favorit import GenreFavorit


@dataclass(frozen=True)
class PreferensiEksplisit:
    """Value Object representing explicit user preferences"""
    genre_favorit: tuple
    
    def __post_init__(self):
        # Validate that all items are GenreFavorit instances
        if not all(isinstance(g, GenreFavorit) for g in self.genre_favorit):
            raise ValueError("All items must be GenreFavorit instances")
        
        # Ensure tuple for immutability
        if not isinstance(self.genre_favorit, tuple):
            object.__setattr__(self, 'genre_favorit', tuple(self.genre_favorit))
        
        # Enforce maximum 5 genres
        if len(self.genre_favorit) > 5:
            raise ValueError("Maximum 5 favorite genres allowed")
    
    @staticmethod
    def empty() -> 'PreferensiEksplisit':
        """Create empty preferences"""
        return PreferensiEksplisit(tuple())
    
    def add_genre(self, genre: GenreFavorit) -> 'PreferensiEksplisit':
        """Add a genre, enforcing max 5 genres"""
        if len(self.genre_favorit) >= 5:
            raise ValueError("Cannot add more than 5 favorite genres")
        
        # Avoid duplicates
        if any(g.nama == genre.nama for g in self.genre_favorit):
            raise ValueError(f"Genre '{genre.nama}' already exists")
        
        new_genres = self.genre_favorit + (genre,)
        return PreferensiEksplisit(new_genres)
    
    def remove_genre(self, genre_name: str) -> 'PreferensiEksplisit':
        """Remove a genre by name"""
        new_genres = tuple(g for g in self.genre_favorit if g.nama != genre_name)
        return PreferensiEksplisit(new_genres)
    
    def has_genre(self, genre_name: str) -> bool:
        """Check if a genre exists"""
        return any(g.nama == genre_name for g in self.genre_favorit)
    
    def __len__(self) -> int:
        return len(self.genre_favorit)
