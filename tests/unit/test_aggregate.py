"""
Unit Tests for ProfilMinatBaca Aggregate and RiwayatBaca Entity
Tests all domain invariants:
1. Maximum 5 favorite genres
2. Rating must be between 1-5
3. RiwayatBaca unique per (userId, bookId)
4. Cannot block active books (books with ratings)
"""

import pytest
from datetime import datetime
from src.personalization.domain.aggregates.profil_minat_baca import ProfilMinatBaca
from src.personalization.domain.entities.riwayat_baca import RiwayatBaca
from src.personalization.domain.value_objects.user_id import UserId
from src.personalization.domain.value_objects.rating import Rating
from src.personalization.domain.value_objects.genre_favorit import GenreFavorit


# ========================
# RiwayatBaca Entity Tests
# ========================


class TestRiwayatBaca:
    """Test RiwayatBaca entity"""

    def test_create_riwayat_baca_without_rating(self):
        """Should create reading history entry without initial rating"""
        riwayat = RiwayatBaca(book_id="book-001")
        assert riwayat.book_id == "book-001"
        assert riwayat.rating is None
        assert isinstance(riwayat.tanggal_baca, datetime)

    def test_create_riwayat_baca_with_rating(self):
        """Should create reading history entry with initial rating"""
        rating = Rating(nilai=4)
        riwayat = RiwayatBaca(book_id="book-002", rating=rating)
        assert riwayat.book_id == "book-002"
        assert riwayat.rating.nilai == 4

    def test_empty_book_id_raises_error(self):
        """Should raise error for empty book_id"""
        with pytest.raises(ValueError, match="book_id cannot be empty"):
            RiwayatBaca(book_id="")

    def test_whitespace_book_id_raises_error(self):
        """Should raise error for whitespace-only book_id"""
        with pytest.raises(ValueError, match="book_id cannot be empty"):
            RiwayatBaca(book_id="   ")

    def test_update_rating(self):
        """Should update rating on existing entry"""
        riwayat = RiwayatBaca(book_id="book-001")
        new_rating = Rating(nilai=5)
        riwayat.update_rating(new_rating)
        assert riwayat.rating.nilai == 5

    def test_equality_same_book_id(self):
        """Two RiwayatBaca with same book_id should be equal"""
        riwayat1 = RiwayatBaca(book_id="book-001")
        riwayat2 = RiwayatBaca(book_id="book-001", rating=Rating(nilai=3))
        assert riwayat1 == riwayat2

    def test_inequality_different_book_id(self):
        """Two RiwayatBaca with different book_id should not be equal"""
        riwayat1 = RiwayatBaca(book_id="book-001")
        riwayat2 = RiwayatBaca(book_id="book-002")
        assert riwayat1 != riwayat2

    def test_hashable(self):
        """RiwayatBaca should be hashable for use in sets/dicts"""
        riwayat = RiwayatBaca(book_id="book-001")
        assert hash(riwayat) == hash("book-001")


# ================================
# ProfilMinatBaca Aggregate Tests
# ================================


class TestProfilMinatBacaCreation:
    """Test ProfilMinatBaca creation"""

    def test_create_profil_with_user_id(self):
        """Should create profile with user ID"""
        profil = ProfilMinatBaca(user_id=UserId(value="user-001"))
        assert str(profil.user_id) == "user-001"

    def test_create_profil_with_default_values(self):
        """Should create profile with empty default values"""
        profil = ProfilMinatBaca(user_id=UserId(value="user-001"))
        assert len(profil.preferensi_eksplisit) == 0
        assert len(profil.daftar_blokir) == 0
        assert len(profil.riwayat_baca) == 0
        assert len(profil.domain_events) == 0


class TestProfilMinatBacaGenreFavorit:
    """Test genre favorit management in aggregate"""

    @pytest.fixture
    def profil(self):
        """Create fresh profile for each test"""
        return ProfilMinatBaca(user_id=UserId(value="user-001"))

    def test_add_genre_favorit(self, profil):
        """Should add genre to favorites"""
        profil.add_genre_favorit(GenreFavorit(nama="Fantasy"))
        assert "Fantasy" in profil.get_genre_favorit()

    def test_add_multiple_genres(self, profil):
        """Should add multiple genres up to 5"""
        genres = ["Fantasy", "Sci-Fi", "Romance", "Mystery", "Horror"]
        for genre in genres:
            profil.add_genre_favorit(GenreFavorit(nama=genre))

        assert len(profil.get_genre_favorit()) == 5
        for genre in genres:
            assert genre in profil.get_genre_favorit()

    def test_max_5_genres_invariant(self, profil):
        """INVARIANT: Should NOT allow more than 5 favorite genres"""
        for i in range(5):
            profil.add_genre_favorit(GenreFavorit(nama=f"Genre{i}"))

        # 6th genre should fail
        with pytest.raises(ValueError, match="Cannot add genre"):
            profil.add_genre_favorit(GenreFavorit(nama="Genre6"))

    def test_remove_genre_favorit(self, profil):
        """Should remove genre from favorites"""
        profil.add_genre_favorit(GenreFavorit(nama="Fantasy"))
        profil.add_genre_favorit(GenreFavorit(nama="Horror"))

        profil.remove_genre_favorit("Fantasy")

        assert "Fantasy" not in profil.get_genre_favorit()
        assert "Horror" in profil.get_genre_favorit()

    def test_add_genre_raises_domain_event(self, profil):
        """Should raise GenreFavoritDiubah event when adding genre"""
        profil.add_genre_favorit(GenreFavorit(nama="Fantasy"))

        events = profil.clear_events()
        assert len(events) == 1
        assert events[0].genre == "Fantasy"
        assert events[0].action == "added"

    def test_remove_genre_raises_domain_event(self, profil):
        """Should raise GenreFavoritDiubah event when removing genre"""
        profil.add_genre_favorit(GenreFavorit(nama="Fantasy"))
        profil.clear_events()  # Clear add event

        profil.remove_genre_favorit("Fantasy")

        events = profil.clear_events()
        assert len(events) == 1
        assert events[0].genre == "Fantasy"
        assert events[0].action == "removed"


class TestProfilMinatBacaRating:
    """Test rating management in aggregate"""

    @pytest.fixture
    def profil(self):
        """Create fresh profile for each test"""
        return ProfilMinatBaca(user_id=UserId(value="user-001"))

    def test_add_rating_creates_riwayat_baca(self, profil):
        """Should create reading history when adding rating"""
        profil.add_rating("book-001", Rating(nilai=4))

        riwayat_list = profil.get_riwayat_baca_list()
        assert len(riwayat_list) == 1
        assert riwayat_list[0]["book_id"] == "book-001"
        assert riwayat_list[0]["rating"] == 4

    def test_update_existing_rating(self, profil):
        """INVARIANT: RiwayatBaca unique per (userId, bookId) - updates existing"""
        profil.add_rating("book-001", Rating(nilai=3))
        profil.add_rating("book-001", Rating(nilai=5))  # Update

        riwayat_list = profil.get_riwayat_baca_list()
        assert len(riwayat_list) == 1  # Still only one entry
        assert riwayat_list[0]["rating"] == 5  # Updated rating

    def test_empty_book_id_raises_error(self, profil):
        """Should raise error for empty book_id"""
        with pytest.raises(ValueError, match="book_id cannot be empty"):
            profil.add_rating("", Rating(nilai=3))

    def test_cannot_rate_blocked_book(self, profil):
        """Should NOT allow rating a blocked book"""
        profil.block_item("bad-book")

        with pytest.raises(ValueError, match="Cannot rate blocked book"):
            profil.add_rating("bad-book", Rating(nilai=3))

    def test_add_rating_raises_domain_event(self, profil):
        """Should raise RatingDiberikan event"""
        profil.add_rating("book-001", Rating(nilai=4))

        events = profil.clear_events()
        assert len(events) == 1
        assert events[0].book_id == "book-001"
        assert events[0].rating == 4


class TestProfilMinatBacaBlockList:
    """Test block list management - KEY INVARIANT"""

    @pytest.fixture
    def profil(self):
        """Create fresh profile for each test"""
        return ProfilMinatBaca(user_id=UserId(value="user-001"))

    def test_block_item(self, profil):
        """Should add book to block list"""
        profil.block_item("bad-book")

        assert "bad-book" in profil.get_blocked_items()

    def test_cannot_block_active_book_invariant(self, profil):
        """INVARIANT: Cannot block active books (books with ratings)"""
        profil.add_rating("book-001", Rating(nilai=4))  # Active book

        with pytest.raises(ValueError, match="Cannot block active book"):
            profil.block_item("book-001")

    def test_can_block_book_without_rating(self, profil):
        """Should allow blocking book that has no rating"""
        profil.block_item("never-rated-book")
        assert "never-rated-book" in profil.get_blocked_items()

    def test_unblock_item(self, profil):
        """Should remove book from block list"""
        profil.block_item("bad-book")
        profil.unblock_item("bad-book")

        assert "bad-book" not in profil.get_blocked_items()

    def test_empty_book_id_raises_error(self, profil):
        """Should raise error for empty book_id"""
        with pytest.raises(ValueError, match="book_id cannot be empty"):
            profil.block_item("")

    def test_block_raises_domain_event(self, profil):
        """Should raise ItemDiblokir event"""
        profil.block_item("bad-book")

        events = profil.clear_events()
        assert len(events) == 1
        assert events[0].book_id == "bad-book"


class TestProfilMinatBacaDomainEvents:
    """Test domain events handling"""

    @pytest.fixture
    def profil(self):
        """Create fresh profile for each test"""
        return ProfilMinatBaca(user_id=UserId(value="user-001"))

    def test_clear_events_returns_and_clears(self, profil):
        """Should return events and clear list"""
        profil.add_genre_favorit(GenreFavorit(nama="Fantasy"))
        profil.add_rating("book-001", Rating(nilai=4))

        events = profil.clear_events()
        assert len(events) == 2

        # Should be empty now
        events_after = profil.clear_events()
        assert len(events_after) == 0

    def test_events_have_user_id(self, profil):
        """All events should have correct user_id"""
        profil.add_genre_favorit(GenreFavorit(nama="Fantasy"))

        events = profil.clear_events()
        assert events[0].user_id == "user-001"
