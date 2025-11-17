"""ProfilMinatBaca Aggregate Root"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

from ..value_objects import UserId, GenreFavorit, Rating, DaftarBlokir, PreferensiEksplisit
from ..entities import RiwayatBaca
from ..events import RatingDiberikan, GenreFavoritDiubah, ItemDiblokir


@dataclass
class ProfilMinatBaca:
    """
    Aggregate Root: ProfilMinatBaca
    Manages user reading preferences, reading history, and blocked items.
    
    Invariants:
    - Maximum 5 favorite genres
    - Rating must be between 1-5
    - RiwayatBaca unique per (userId, bookId)
    - Block list cannot contain active books (books currently being read)
    """
    user_id: UserId
    preferensi_eksplisit: PreferensiEksplisit = field(default_factory=PreferensiEksplisit.empty)
    daftar_blokir: DaftarBlokir = field(default_factory=DaftarBlokir.empty)
    riwayat_baca: Dict[str, RiwayatBaca] = field(default_factory=dict)
    domain_events: List = field(default_factory=list, init=False)
    
    def add_genre_favorit(self, genre: GenreFavorit) -> None:
        """
        Add a favorite genre to user preferences.
        Enforces invariant: Maximum 5 favorite genres
        """
        try:
            self.preferensi_eksplisit = self.preferensi_eksplisit.add_genre(genre)
            # Raise domain event
            self.domain_events.append(
                GenreFavoritDiubah(
                    user_id=str(self.user_id),
                    genre=genre.nama,
                    action="added",
                    timestamp=datetime.utcnow()
                )
            )
        except ValueError as e:
            raise ValueError(f"Cannot add genre: {e}")
    
    def remove_genre_favorit(self, genre_name: str) -> None:
        """Remove a favorite genre from user preferences"""
        self.preferensi_eksplisit = self.preferensi_eksplisit.remove_genre(genre_name)
        # Raise domain event
        self.domain_events.append(
            GenreFavoritDiubah(
                user_id=str(self.user_id),
                genre=genre_name,
                action="removed",
                timestamp=datetime.utcnow()
            )
        )
    
    def add_rating(self, book_id: str, rating: Rating) -> None:
        """
        Add or update a rating for a book.
        Enforces invariant: Rating must be between 1-5 (enforced by Rating value object)
        Enforces invariant: RiwayatBaca unique per (userId, bookId)
        """
        if not book_id or not book_id.strip():
            raise ValueError("book_id cannot be empty")
        
        # Check if book is blocked
        if self.daftar_blokir.contains(book_id):
            raise ValueError(f"Cannot rate blocked book: {book_id}")
        
        # Get or create RiwayatBaca entry
        if book_id in self.riwayat_baca:
            self.riwayat_baca[book_id].update_rating(rating)
        else:
            riwayat = RiwayatBaca(book_id=book_id, rating=rating)
            self.riwayat_baca[book_id] = riwayat
        
        # Raise domain event
        self.domain_events.append(
            RatingDiberikan(
                user_id=str(self.user_id),
                book_id=book_id,
                rating=rating.nilai,
                timestamp=datetime.utcnow()
            )
        )
    
    def block_item(self, book_id: str) -> None:
        """
        Block a book from recommendations.
        Enforces invariant: Block list cannot contain active books (books with ratings)
        """
        if not book_id or not book_id.strip():
            raise ValueError("book_id cannot be empty")
        
        # Check if book has been rated (considered "active")
        if book_id in self.riwayat_baca and self.riwayat_baca[book_id].rating is not None:
            raise ValueError(f"Cannot block active book: {book_id}. Remove rating first.")
        
        self.daftar_blokir = self.daftar_blokir.add(book_id)
        
        # Raise domain event
        self.domain_events.append(
            ItemDiblokir(
                user_id=str(self.user_id),
                book_id=book_id,
                timestamp=datetime.utcnow()
            )
        )
    
    def unblock_item(self, book_id: str) -> None:
        """Unblock a book"""
        self.daftar_blokir = self.daftar_blokir.remove(book_id)
    
    def get_genre_favorit(self) -> List[str]:
        """Get list of favorite genre names"""
        return [g.nama for g in self.preferensi_eksplisit.genre_favorit]
    
    def get_riwayat_baca_list(self) -> List[Dict]:
        """Get reading history as a list"""
        return [
            {
                "book_id": r.book_id,
                "rating": r.rating.nilai if r.rating else None,
                "tanggal_baca": r.tanggal_baca.isoformat()
            }
            for r in self.riwayat_baca.values()
        ]
    
    def get_blocked_items(self) -> List[str]:
        """Get list of blocked book IDs"""
        return list(self.daftar_blokir.book_ids)
    
    def clear_events(self) -> List:
        """Clear and return domain events"""
        events = self.domain_events.copy()
        self.domain_events.clear()
        return events
