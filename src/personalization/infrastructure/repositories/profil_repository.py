"""ProfilMinatBacaRepository - Repository Interface"""

from abc import ABC, abstractmethod
from typing import Optional
from ...domain.aggregates import ProfilMinatBaca


class ProfilMinatBacaRepository(ABC):
    """Repository interface for ProfilMinatBaca aggregate"""

    @abstractmethod
    def save(self, profil: ProfilMinatBaca) -> None:
        """Save or update a profile"""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> Optional[ProfilMinatBaca]:
        """Find a profile by user_id"""
        pass

    @abstractmethod
    def delete(self, user_id: str) -> None:
        """Delete a profile"""
        pass
