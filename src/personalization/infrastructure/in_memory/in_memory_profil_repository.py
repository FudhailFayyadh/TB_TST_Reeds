"""InMemoryProfilMinatBacaRepository - In-Memory Implementation"""

from typing import Dict, Optional
from ...domain.aggregates import ProfilMinatBaca
from ..repositories.profil_repository import ProfilMinatBacaRepository


class InMemoryProfilMinatBacaRepository(ProfilMinatBacaRepository):
    """In-memory implementation of ProfilMinatBacaRepository for testing/development"""

    def __init__(self):
        self._storage: Dict[str, ProfilMinatBaca] = {}

    def save(self, profil: ProfilMinatBaca) -> None:
        """Save or update a profile in memory"""
        user_id = str(profil.user_id)
        self._storage[user_id] = profil

    def find_by_user_id(self, user_id: str) -> Optional[ProfilMinatBaca]:
        """Find a profile by user_id"""
        return self._storage.get(user_id)

    def delete(self, user_id: str) -> None:
        """Delete a profile from memory"""
        if user_id in self._storage:
            del self._storage[user_id]

    def clear(self) -> None:
        """Clear all data (useful for testing)"""
        self._storage.clear()
