"""ProfilService - Application Service Layer"""
from typing import Optional

from ...domain.aggregates import ProfilMinatBaca
from ...domain.value_objects import UserId, GenreFavorit, Rating
from ...domain.read_models import SnapshotProfil
from ...infrastructure.repositories.profil_repository import ProfilMinatBacaRepository


class ProfilService:
    """
    Application Service for managing user profiles.
    Orchestrates domain operations without containing business logic.
    """
    
    def __init__(self, repository: ProfilMinatBacaRepository):
        self.repository = repository
    
    def create_profile(self, user_id: str) -> ProfilMinatBaca:
        """Create a new user profile"""
        # Check if profile already exists
        existing = self.repository.find_by_user_id(user_id)
        if existing:
            raise ValueError(f"Profile for user {user_id} already exists")
        
        # Create new aggregate
        user_id_vo = UserId(user_id)
        profil = ProfilMinatBaca(user_id=user_id_vo)
        
        # Save to repository
        self.repository.save(profil)
        return profil
    
    def get_profile(self, user_id: str) -> Optional[ProfilMinatBaca]:
        """Get user profile by user_id"""
        return self.repository.find_by_user_id(user_id)
    
    def add_genre(self, user_id: str, genre: str) -> ProfilMinatBaca:
        """Add a favorite genre to user profile"""
        # Load aggregate
        profil = self.repository.find_by_user_id(user_id)
        if not profil:
            raise ValueError(f"Profile for user {user_id} not found")
        
        # Execute domain logic
        genre_vo = GenreFavorit(genre)
        profil.add_genre_favorit(genre_vo)
        
        # Save aggregate
        self.repository.save(profil)
        return profil
    
    def add_rating(self, user_id: str, book_id: str, rating: int) -> ProfilMinatBaca:
        """Add or update a rating for a book"""
        # Load aggregate
        profil = self.repository.find_by_user_id(user_id)
        if not profil:
            raise ValueError(f"Profile for user {user_id} not found")
        
        # Execute domain logic
        rating_vo = Rating(rating)
        profil.add_rating(book_id, rating_vo)
        
        # Save aggregate
        self.repository.save(profil)
        return profil
    
    def block_item(self, user_id: str, book_id: str) -> ProfilMinatBaca:
        """Block a book from recommendations"""
        # Load aggregate
        profil = self.repository.find_by_user_id(user_id)
        if not profil:
            raise ValueError(f"Profile for user {user_id} not found")
        
        # Execute domain logic
        profil.block_item(book_id)
        
        # Save aggregate
        self.repository.save(profil)
        return profil
    
    def get_snapshot(self, user_id: str) -> Optional[SnapshotProfil]:
        """Get profile snapshot (read model) for query purposes"""
        profil = self.repository.find_by_user_id(user_id)
        if not profil:
            return None
        
        return SnapshotProfil.from_aggregate(profil)
