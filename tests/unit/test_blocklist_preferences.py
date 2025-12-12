"""
Unit Tests for DaftarBlokir and PreferensiEksplisit Value Objects
"""
import pytest
from src.personalization.domain.value_objects.daftar_blokir import DaftarBlokir
from src.personalization.domain.value_objects.preferensi_eksplisit import PreferensiEksplisit
from src.personalization.domain.value_objects.genre_favorit import GenreFavorit


class TestDaftarBlokir:
    """Test DaftarBlokir value object"""
    
    def test_create_empty_blocklist(self):
        """Should create empty blocklist using factory method"""
        blokir = DaftarBlokir.empty()
        assert len(blokir) == 0
        assert not blokir.contains("any_book")
    
    def test_create_with_book_ids(self):
        """Should create blocklist with initial book IDs"""
        blokir = DaftarBlokir(frozenset({"book-001", "book-002"}))
        assert len(blokir) == 2
        assert blokir.contains("book-001")
        assert blokir.contains("book-002")
    
    def test_add_book_to_blocklist(self):
        """Should add book to blocklist (returns new instance)"""
        blokir = DaftarBlokir.empty()
        new_blokir = blokir.add("book-bad-001")
        
        # Original should be unchanged (immutable)
        assert not blokir.contains("book-bad-001")
        assert new_blokir.contains("book-bad-001")
    
    def test_remove_book_from_blocklist(self):
        """Should remove book from blocklist (returns new instance)"""
        blokir = DaftarBlokir(frozenset({"book-001", "book-002"}))
        new_blokir = blokir.remove("book-001")
        
        # Original should be unchanged
        assert blokir.contains("book-001")
        assert not new_blokir.contains("book-001")
        assert new_blokir.contains("book-002")
    
    def test_remove_nonexistent_book(self):
        """Should handle removing nonexistent book gracefully"""
        blokir = DaftarBlokir(frozenset({"book-001"}))
        new_blokir = blokir.remove("book-999")
        assert len(new_blokir) == 1
        assert new_blokir.contains("book-001")
    
    def test_contains_blocked_book(self):
        """Should correctly check if book is blocked"""
        blokir = DaftarBlokir(frozenset({"book-bad"}))
        assert blokir.contains("book-bad") == True
        assert blokir.contains("book-good") == False
    
    def test_blocklist_immutability(self):
        """DaftarBlokir should be immutable"""
        blokir = DaftarBlokir.empty()
        with pytest.raises(AttributeError):
            blokir.book_ids = frozenset({"book-001"})
    
    def test_create_with_set_converts_to_frozenset(self):
        """Should convert set to frozenset"""
        blokir = DaftarBlokir({"book-001", "book-002"})
        assert isinstance(blokir.book_ids, frozenset)
        assert len(blokir) == 2
    
    def test_invalid_book_ids_type(self):
        """Should raise error for invalid book_ids type"""
        with pytest.raises(ValueError, match="book_ids must be a set or frozenset"):
            DaftarBlokir(["book-001", "book-002"])


class TestPreferensiEksplisit:
    """Test PreferensiEksplisit value object - MAX 5 GENRES INVARIANT"""
    
    def test_create_empty_preferences(self):
        """Should create empty preferences"""
        pref = PreferensiEksplisit.empty()
        assert len(pref) == 0
        assert pref.genre_favorit == ()
    
    def test_add_single_genre(self):
        """Should add a single genre"""
        pref = PreferensiEksplisit.empty()
        new_pref = pref.add_genre(GenreFavorit(nama="Fantasy"))
        
        assert len(new_pref) == 1
        assert new_pref.has_genre("Fantasy")
    
    def test_add_multiple_genres_up_to_5(self):
        """Should add up to 5 genres successfully"""
        pref = PreferensiEksplisit.empty()
        genres = ["Fantasy", "Sci-Fi", "Romance", "Mystery", "Horror"]
        
        for genre in genres:
            pref = pref.add_genre(GenreFavorit(nama=genre))
        
        assert len(pref) == 5
        for genre in genres:
            assert pref.has_genre(genre)
    
    def test_max_5_genres_invariant(self):
        """INVARIANT: Should NOT allow more than 5 genres"""
        pref = PreferensiEksplisit.empty()
        
        # Add 5 genres
        for i in range(5):
            pref = pref.add_genre(GenreFavorit(nama=f"Genre{i}"))
        
        # Try to add 6th genre - should fail
        with pytest.raises(ValueError, match="Cannot add more than 5 favorite genres"):
            pref.add_genre(GenreFavorit(nama="Genre6"))
    
    def test_no_duplicate_genres(self):
        """Should not allow duplicate genres"""
        pref = PreferensiEksplisit.empty()
        pref = pref.add_genre(GenreFavorit(nama="Fantasy"))
        
        with pytest.raises(ValueError, match="already exists"):
            pref.add_genre(GenreFavorit(nama="Fantasy"))
    
    def test_remove_genre(self):
        """Should remove genre by name"""
        pref = PreferensiEksplisit.empty()
        pref = pref.add_genre(GenreFavorit(nama="Fantasy"))
        pref = pref.add_genre(GenreFavorit(nama="Horror"))
        
        new_pref = pref.remove_genre("Fantasy")
        
        assert not new_pref.has_genre("Fantasy")
        assert new_pref.has_genre("Horror")
        assert len(new_pref) == 1
    
    def test_remove_nonexistent_genre(self):
        """Should handle removing nonexistent genre gracefully"""
        pref = PreferensiEksplisit.empty()
        pref = pref.add_genre(GenreFavorit(nama="Fantasy"))
        
        new_pref = pref.remove_genre("NonExistent")
        assert len(new_pref) == 1
        assert new_pref.has_genre("Fantasy")
    
    def test_has_genre(self):
        """Should correctly check if genre exists"""
        pref = PreferensiEksplisit.empty()
        pref = pref.add_genre(GenreFavorit(nama="Fantasy"))
        
        assert pref.has_genre("Fantasy") == True
        assert pref.has_genre("Horror") == False
    
    def test_preferences_immutability(self):
        """PreferensiEksplisit should be immutable"""
        pref = PreferensiEksplisit.empty()
        with pytest.raises(AttributeError):
            pref.genre_favorit = (GenreFavorit(nama="Test"),)
    
    def test_create_with_more_than_5_genres_fails(self):
        """Should fail when creating with more than 5 genres directly"""
        genres = tuple(GenreFavorit(nama=f"Genre{i}") for i in range(6))
        with pytest.raises(ValueError, match="Maximum 5 favorite genres"):
            PreferensiEksplisit(genres)
    
    def test_create_with_non_genre_favorit_fails(self):
        """Should fail when creating with non-GenreFavorit items"""
        with pytest.raises(ValueError, match="All items must be GenreFavorit instances"):
            PreferensiEksplisit(("Fantasy", "Horror"))
    
    def test_create_with_list_converts_to_tuple(self):
        """Should convert list to tuple"""
        genres = [GenreFavorit(nama="Fantasy")]
        pref = PreferensiEksplisit(tuple(genres))
        assert isinstance(pref.genre_favorit, tuple)
