"""
Unit Tests for Domain Value Objects
Tests invariants: rating 1-5, genre non-empty, etc.
"""
import pytest
from src.personalization.domain.value_objects.rating import Rating
from src.personalization.domain.value_objects.genre_favorit import GenreFavorit
from src.personalization.domain.value_objects.user_id import UserId


class TestRating:
    """Test Rating value object invariants"""
    
    def test_valid_rating_1(self):
        """Rating 1 should be valid"""
        rating = Rating(nilai=1)
        assert rating.nilai == 1
    
    def test_valid_rating_5(self):
        """Rating 5 should be valid"""
        rating = Rating(nilai=5)
        assert rating.nilai == 5
    
    def test_valid_rating_3(self):
        """Rating 3 should be valid"""
        rating = Rating(nilai=3)
        assert rating.nilai == 3
    
    def test_valid_rating_all_values(self):
        """All ratings from 1 to 5 should be valid"""
        for i in range(1, 6):
            rating = Rating(nilai=i)
            assert rating.nilai == i
    
    def test_invalid_rating_0(self):
        """Rating 0 should be invalid"""
        with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
            Rating(nilai=0)
    
    def test_invalid_rating_6(self):
        """Rating 6 should be invalid"""
        with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
            Rating(nilai=6)
    
    def test_invalid_rating_negative(self):
        """Negative rating should be invalid"""
        with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
            Rating(nilai=-1)
    
    def test_invalid_rating_large_number(self):
        """Very large rating should be invalid"""
        with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
            Rating(nilai=100)
    
    def test_rating_int_conversion(self):
        """Rating should be convertible to int"""
        rating = Rating(nilai=4)
        assert int(rating) == 4
    
    def test_rating_equality(self):
        """Two ratings with same value should be equal"""
        r1 = Rating(nilai=4)
        r2 = Rating(nilai=4)
        assert r1 == r2
    
    def test_rating_inequality(self):
        """Two ratings with different values should not be equal"""
        r1 = Rating(nilai=3)
        r2 = Rating(nilai=4)
        assert r1 != r2
    
    def test_rating_immutability(self):
        """Rating should be immutable (frozen dataclass)"""
        rating = Rating(nilai=3)
        with pytest.raises(AttributeError):
            rating.nilai = 5
    
    def test_rating_string_conversion(self):
        """Rating should be convertible to string (uses dataclass default repr)"""
        rating = Rating(nilai=4)
        # Dataclass uses default repr format
        assert "4" in str(rating)
        assert "Rating" in str(rating)


class TestGenreFavorit:
    """Test GenreFavorit value object"""
    
    def test_create_genre_favorit(self):
        """Should create genre favorit with valid genre"""
        genre = GenreFavorit(nama="Fantasy")
        assert genre.nama == "Fantasy"
    
    def test_genre_normalization_title_case(self):
        """Genre name should be normalized to title case"""
        genre = GenreFavorit(nama="science fiction")
        assert genre.nama == "Science Fiction"
    
    def test_genre_normalization_strip_whitespace(self):
        """Genre name should strip leading/trailing whitespace"""
        genre = GenreFavorit(nama="  Mystery  ")
        assert genre.nama == "Mystery"
    
    def test_empty_genre_raises_error(self):
        """Empty genre name should raise ValueError"""
        with pytest.raises(ValueError, match="Genre name cannot be empty"):
            GenreFavorit(nama="")
    
    def test_whitespace_only_genre_raises_error(self):
        """Whitespace-only genre name should raise ValueError"""
        with pytest.raises(ValueError, match="Genre name cannot be empty"):
            GenreFavorit(nama="   ")
    
    def test_genre_string_conversion(self):
        """Genre should be convertible to string"""
        genre = GenreFavorit(nama="Horror")
        assert str(genre) == "Horror"
    
    def test_genre_equality(self):
        """Two genres with same name should be equal"""
        g1 = GenreFavorit(nama="Romance")
        g2 = GenreFavorit(nama="romance")  # Should normalize to same
        assert g1 == g2
    
    def test_genre_immutability(self):
        """Genre should be immutable (frozen dataclass)"""
        genre = GenreFavorit(nama="Comedy")
        with pytest.raises(AttributeError):
            genre.nama = "Drama"


class TestUserId:
    """Test UserId value object"""
    
    def test_create_user_id(self):
        """Should create valid user id"""
        user_id = UserId(value="user_001")
        assert user_id.value == "user_001"
    
    def test_user_id_string_conversion(self):
        """UserId should be convertible to string"""
        user_id = UserId(value="user_001")
        assert str(user_id) == "user_001"
    
    def test_user_id_equality(self):
        """Two UserIds with same value should be equal"""
        u1 = UserId(value="user_001")
        u2 = UserId(value="user_001")
        assert u1 == u2
    
    def test_user_id_inequality(self):
        """Two UserIds with different values should not be equal"""
        u1 = UserId(value="user_001")
        u2 = UserId(value="user_002")
        assert u1 != u2
    
    def test_user_id_immutability(self):
        """UserId should be immutable"""
        user_id = UserId(value="user_001")
        with pytest.raises(AttributeError):
            user_id.value = "user_002"
    
    def test_empty_user_id_raises_error(self):
        """Empty user_id should raise ValueError"""
        with pytest.raises(ValueError, match="cannot be empty"):
            UserId(value="")
    
    def test_whitespace_user_id_raises_error(self):
        """Whitespace-only user_id should raise ValueError"""
        with pytest.raises(ValueError, match="cannot be empty"):
            UserId(value="   ")
