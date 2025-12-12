"""
Unit Tests for ProfilService - Application Service Layer
Tests service orchestration and repository integration
"""
import pytest
from unittest.mock import Mock, MagicMock
from src.personalization.application.services.profil_service import ProfilService
from src.personalization.domain.aggregates.profil_minat_baca import ProfilMinatBaca
from src.personalization.domain.value_objects.user_id import UserId
from src.personalization.domain.value_objects.rating import Rating
from src.personalization.domain.value_objects.genre_favorit import GenreFavorit
from src.personalization.infrastructure.in_memory.in_memory_profil_repository import InMemoryProfilMinatBacaRepository


class TestProfilServiceWithMock:
    """Test ProfilService with mocked repository"""
    
    @pytest.fixture
    def mock_repository(self):
        """Create mock repository"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository):
        """Create service with mock repository"""
        return ProfilService(repository=mock_repository)
    
    def test_create_profile_success(self, service, mock_repository):
        """Should create profile when user doesn't exist"""
        mock_repository.find_by_user_id.return_value = None
        
        profil = service.create_profile("user-001")
        
        assert str(profil.user_id) == "user-001"
        mock_repository.save.assert_called_once()
    
    def test_create_profile_already_exists(self, service, mock_repository):
        """Should raise error if profile already exists"""
        existing_profil = ProfilMinatBaca(user_id=UserId(value="user-001"))
        mock_repository.find_by_user_id.return_value = existing_profil
        
        with pytest.raises(ValueError, match="already exists"):
            service.create_profile("user-001")
    
    def test_get_profile_found(self, service, mock_repository):
        """Should return profile if found"""
        expected_profil = ProfilMinatBaca(user_id=UserId(value="user-001"))
        mock_repository.find_by_user_id.return_value = expected_profil
        
        result = service.get_profile("user-001")
        
        assert result == expected_profil
        mock_repository.find_by_user_id.assert_called_with("user-001")
    
    def test_get_profile_not_found(self, service, mock_repository):
        """Should return None if profile not found"""
        mock_repository.find_by_user_id.return_value = None
        
        result = service.get_profile("nonexistent")
        
        assert result is None


class TestProfilServiceAddGenre:
    """Test add_genre service method"""
    
    @pytest.fixture
    def mock_repository(self):
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository):
        return ProfilService(repository=mock_repository)
    
    @pytest.fixture
    def existing_profil(self):
        return ProfilMinatBaca(user_id=UserId(value="user-001"))
    
    def test_add_genre_success(self, service, mock_repository, existing_profil):
        """Should add genre to existing profile"""
        mock_repository.find_by_user_id.return_value = existing_profil
        
        result = service.add_genre("user-001", "Fantasy")
        
        assert "Fantasy" in result.get_genre_favorit()
        mock_repository.save.assert_called_once()
    
    def test_add_genre_profile_not_found(self, service, mock_repository):
        """Should raise error if profile not found"""
        mock_repository.find_by_user_id.return_value = None
        
        with pytest.raises(ValueError, match="not found"):
            service.add_genre("nonexistent", "Fantasy")
    
    def test_add_genre_max_5_invariant(self, service, mock_repository, existing_profil):
        """Should enforce max 5 genres invariant"""
        # Pre-populate with 5 genres
        for i in range(5):
            existing_profil.add_genre_favorit(GenreFavorit(nama=f"Genre{i}"))
        
        mock_repository.find_by_user_id.return_value = existing_profil
        
        with pytest.raises(ValueError):
            service.add_genre("user-001", "Genre6")


class TestProfilServiceAddRating:
    """Test add_rating service method"""
    
    @pytest.fixture
    def mock_repository(self):
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository):
        return ProfilService(repository=mock_repository)
    
    @pytest.fixture
    def existing_profil(self):
        return ProfilMinatBaca(user_id=UserId(value="user-001"))
    
    def test_add_rating_success(self, service, mock_repository, existing_profil):
        """Should add rating to book"""
        mock_repository.find_by_user_id.return_value = existing_profil
        
        result = service.add_rating("user-001", "book-001", 4)
        
        riwayat = result.get_riwayat_baca_list()
        assert len(riwayat) == 1
        assert riwayat[0]["rating"] == 4
        mock_repository.save.assert_called_once()
    
    def test_add_rating_profile_not_found(self, service, mock_repository):
        """Should raise error if profile not found"""
        mock_repository.find_by_user_id.return_value = None
        
        with pytest.raises(ValueError, match="not found"):
            service.add_rating("nonexistent", "book-001", 4)
    
    def test_add_rating_invalid_value(self, service, mock_repository, existing_profil):
        """Should enforce rating 1-5 invariant"""
        mock_repository.find_by_user_id.return_value = existing_profil
        
        with pytest.raises(ValueError):
            service.add_rating("user-001", "book-001", 6)


class TestProfilServiceBlockItem:
    """Test block_item service method"""
    
    @pytest.fixture
    def mock_repository(self):
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository):
        return ProfilService(repository=mock_repository)
    
    @pytest.fixture
    def existing_profil(self):
        return ProfilMinatBaca(user_id=UserId(value="user-001"))
    
    def test_block_item_success(self, service, mock_repository, existing_profil):
        """Should block book successfully"""
        mock_repository.find_by_user_id.return_value = existing_profil
        
        result = service.block_item("user-001", "bad-book")
        
        assert "bad-book" in result.get_blocked_items()
        mock_repository.save.assert_called_once()
    
    def test_block_item_profile_not_found(self, service, mock_repository):
        """Should raise error if profile not found"""
        mock_repository.find_by_user_id.return_value = None
        
        with pytest.raises(ValueError, match="not found"):
            service.block_item("nonexistent", "book-001")
    
    def test_cannot_block_active_book(self, service, mock_repository, existing_profil):
        """Should enforce cannot block active book invariant"""
        # First rate the book (makes it active)
        existing_profil.add_rating("book-001", Rating(nilai=4))
        mock_repository.find_by_user_id.return_value = existing_profil
        
        with pytest.raises(ValueError, match="Cannot block active book"):
            service.block_item("user-001", "book-001")


class TestProfilServiceIntegration:
    """Integration tests with real in-memory repository"""
    
    @pytest.fixture
    def repository(self):
        """Create real in-memory repository"""
        return InMemoryProfilMinatBacaRepository()
    
    @pytest.fixture
    def service(self, repository):
        """Create service with real repository"""
        return ProfilService(repository=repository)
    
    def test_full_workflow(self, service):
        """Test complete profile workflow"""
        # Create profile
        profil = service.create_profile("user-integration")
        assert str(profil.user_id) == "user-integration"
        
        # Add genres
        service.add_genre("user-integration", "Fantasy")
        service.add_genre("user-integration", "Sci-Fi")
        
        # Add rating
        service.add_rating("user-integration", "book-001", 5)
        
        # Block item
        service.block_item("user-integration", "bad-book")
        
        # Get snapshot
        snapshot = service.get_snapshot("user-integration")
        assert snapshot is not None
        assert len(snapshot.genre_favorit) == 2
        assert "bad-book" in snapshot.blocked_items
    
    def test_repository_persistence(self, service, repository):
        """Test that changes persist in repository"""
        service.create_profile("user-persist")
        service.add_genre("user-persist", "Fantasy")
        
        # Retrieve from repository
        profil = repository.find_by_user_id("user-persist")
        assert profil is not None
        assert "Fantasy" in profil.get_genre_favorit()


class TestProfilServiceSnapshot:
    """Test get_snapshot method"""
    
    @pytest.fixture
    def repository(self):
        return InMemoryProfilMinatBacaRepository()
    
    @pytest.fixture
    def service(self, repository):
        return ProfilService(repository=repository)
    
    def test_get_snapshot_returns_read_model(self, service):
        """Should return SnapshotProfil read model"""
        service.create_profile("user-snapshot")
        service.add_genre("user-snapshot", "Fantasy")
        service.add_rating("user-snapshot", "book-001", 4)
        
        snapshot = service.get_snapshot("user-snapshot")
        
        assert snapshot.user_id == "user-snapshot"
        assert "Fantasy" in snapshot.genre_favorit
        assert len(snapshot.riwayat_baca) == 1
    
    def test_get_snapshot_not_found(self, service):
        """Should return None if profile not found"""
        snapshot = service.get_snapshot("nonexistent")
        assert snapshot is None
