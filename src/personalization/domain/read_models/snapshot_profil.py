"""SnapshotProfil Read Model"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class SnapshotProfil:
    """
    Read Model: Snapshot of user profile for query purposes.
    Optimized for read operations, denormalized data.
    """

    user_id: str
    genre_favorit: List[str]
    jumlah_buku_dibaca: int
    rata_rata_rating: float
    blocked_items: List[str]
    riwayat_baca: List[Dict]

    @staticmethod
    def from_aggregate(profil) -> "SnapshotProfil":
        """Create a snapshot from ProfilMinatBaca aggregate"""
        riwayat_list = profil.get_riwayat_baca_list()

        # Calculate statistics
        ratings = [r["rating"] for r in riwayat_list if r["rating"] is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0

        return SnapshotProfil(
            user_id=str(profil.user_id),
            genre_favorit=profil.get_genre_favorit(),
            jumlah_buku_dibaca=len(riwayat_list),
            rata_rata_rating=round(avg_rating, 2),
            blocked_items=profil.get_blocked_items(),
            riwayat_baca=riwayat_list,
        )
