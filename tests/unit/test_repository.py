"""
Unit Tests for Repository
Tests for in_memory_profil_repository.py and repository interface
"""

import pytest

from src.personalization.infrastructure.in_memory.in_memory_profil_repository import (
    InMemoryProfilMinatBacaRepository,
)
from src.personalization.domain.aggregates import ProfilMinatBaca
from src.personalization.domain.value_objects import GenreFavorit, Rating


class TestInMemoryProfilRepository:
    """Tests for InMemoryProfilMinatBacaRepository"""

    @pytest.fixture
    def repository(self):
        """Create a fresh repository for each test"""
        repo = InMemoryProfilMinatBacaRepository()
        yield repo
        repo.clear()

    @pytest.fixture
    def sample_profile(self):
        """Create a sample profile for testing"""
        return ProfilMinatBaca(user_id="user-001")

    # === Save Tests ===

    def test_save_new_profile(self, repository, sample_profile):
        """Should save a new profile"""
        repository.save(sample_profile)

        retrieved = repository.find_by_user_id("user-001")
        assert retrieved is not None
        assert str(retrieved.user_id) == "user-001"

    def test_save_updates_existing_profile(self, repository):
        """Should update an existing profile"""
        profile = ProfilMinatBaca(user_id="user-001")
        repository.save(profile)

        # Modify and save again
        profile.add_genre_favorit(GenreFavorit("Fiction"))
        repository.save(profile)

        retrieved = repository.find_by_user_id("user-001")
        assert len(retrieved.preferensi_eksplisit.genre_favorit) == 1

    def test_save_multiple_profiles(self, repository):
        """Should save multiple distinct profiles"""
        profile1 = ProfilMinatBaca(user_id="user-001")
        profile2 = ProfilMinatBaca(user_id="user-002")
        profile3 = ProfilMinatBaca(user_id="user-003")

        repository.save(profile1)
        repository.save(profile2)
        repository.save(profile3)

        assert repository.find_by_user_id("user-001") is not None
        assert repository.find_by_user_id("user-002") is not None
        assert repository.find_by_user_id("user-003") is not None

    # === Find By User ID Tests ===

    def test_find_by_user_id_exists(self, repository, sample_profile):
        """Should find profile that exists"""
        repository.save(sample_profile)

        result = repository.find_by_user_id("user-001")

        assert result is not None
        assert str(result.user_id) == "user-001"

    def test_find_by_user_id_not_exists(self, repository):
        """Should return None for non-existent profile"""
        result = repository.find_by_user_id("nonexistent-user")

        assert result is None

    def test_find_by_user_id_empty_repository(self, repository):
        """Should return None when repository is empty"""
        result = repository.find_by_user_id("any-user")

        assert result is None

    def test_find_returns_correct_profile(self, repository):
        """Should return the correct profile when multiple exist"""
        profile1 = ProfilMinatBaca(user_id="user-001")
        profile1.add_genre_favorit(GenreFavorit("Fiction"))

        profile2 = ProfilMinatBaca(user_id="user-002")
        profile2.add_genre_favorit(GenreFavorit("Science"))

        repository.save(profile1)
        repository.save(profile2)

        result = repository.find_by_user_id("user-002")

        assert str(result.user_id) == "user-002"
        assert result.preferensi_eksplisit.has_genre("Science")

    # === Delete Tests ===

    def test_delete_existing_profile(self, repository, sample_profile):
        """Should delete an existing profile"""
        repository.save(sample_profile)
        assert repository.find_by_user_id("user-001") is not None

        repository.delete("user-001")

        assert repository.find_by_user_id("user-001") is None

    def test_delete_nonexistent_profile(self, repository):
        """Should not raise error when deleting non-existent profile"""
        # Should not raise any exception
        repository.delete("nonexistent-user")

    def test_delete_one_of_many(self, repository):
        """Should only delete the specified profile"""
        profile1 = ProfilMinatBaca(user_id="user-001")
        profile2 = ProfilMinatBaca(user_id="user-002")

        repository.save(profile1)
        repository.save(profile2)

        repository.delete("user-001")

        assert repository.find_by_user_id("user-001") is None
        assert repository.find_by_user_id("user-002") is not None

    # === Clear Tests ===

    def test_clear_removes_all_profiles(self, repository):
        """Should remove all profiles"""
        profile1 = ProfilMinatBaca(user_id="user-001")
        profile2 = ProfilMinatBaca(user_id="user-002")

        repository.save(profile1)
        repository.save(profile2)

        repository.clear()

        assert repository.find_by_user_id("user-001") is None
        assert repository.find_by_user_id("user-002") is None

    def test_clear_empty_repository(self, repository):
        """Should not raise error when clearing empty repository"""
        repository.clear()  # Should not raise

    # === Integration Tests ===

    def test_save_find_modify_save(self, repository):
        """Should handle save-find-modify-save workflow"""
        # Create and save
        profile = ProfilMinatBaca(user_id="user-001")
        repository.save(profile)

        # Find and modify
        found = repository.find_by_user_id("user-001")
        found.add_genre_favorit(GenreFavorit("Fiction"))
        found.add_rating("book-001", Rating(5))

        # Save modified
        repository.save(found)

        # Verify changes persisted
        final = repository.find_by_user_id("user-001")
        assert len(final.preferensi_eksplisit.genre_favorit) == 1
        assert len(final.riwayat_baca) == 1

    def test_profile_with_all_features(self, repository):
        """Should correctly store profile with all features"""
        profile = ProfilMinatBaca(user_id="user-001")
        profile.add_genre_favorit(GenreFavorit("Fiction"))
        profile.add_genre_favorit(GenreFavorit("Science"))
        profile.add_rating("book-001", Rating(5))
        profile.add_rating("book-002", Rating(3))
        profile.block_item("book-003")

        repository.save(profile)

        retrieved = repository.find_by_user_id("user-001")

        assert len(retrieved.preferensi_eksplisit.genre_favorit) == 2
        assert len(retrieved.riwayat_baca) == 2
        assert retrieved.daftar_blokir.contains("book-003")
