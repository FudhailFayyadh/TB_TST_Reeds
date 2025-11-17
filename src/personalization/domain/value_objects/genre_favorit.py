"""GenreFavorit Value Object"""
from dataclasses import dataclass


@dataclass(frozen=True)
class GenreFavorit:
    """Value Object representing a favorite genre"""
    nama: str
    
    def __post_init__(self):
        if not self.nama or not self.nama.strip():
            raise ValueError("Genre name cannot be empty")
        # Normalize genre name
        object.__setattr__(self, 'nama', self.nama.strip().title())
    
    def __str__(self) -> str:
        return self.nama
