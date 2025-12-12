"""UserId Value Object"""

from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:
    """Value Object representing a user identifier"""

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("UserId cannot be empty")

    def __str__(self) -> str:
        return self.value
