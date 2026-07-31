from dataclasses import dataclass
from typing import ClassVar

from app.domain.exceptions import EntityValidationError


@dataclass(frozen=True, slots=True)
class TeamName:
    """Value object representing a football team name."""

    _MIN_LENGTH: ClassVar[int] = 2
    _MAX_LENGTH: ClassVar[int] = 100
    value: str

    def __post_init__(self) -> None:
        """Validate the team name after initialization."""
        normalized_value = self.value.strip()

        if not normalized_value:
            raise EntityValidationError("Team name cannot be empty")

        if len(normalized_value) < self._MIN_LENGTH:
            raise EntityValidationError("Team name must be at least 2 characters long")

        if len(normalized_value) > self._MAX_LENGTH:
            raise EntityValidationError("Team name must not exceed 100 characters")

        object.__setattr__(self, "value", normalized_value)

    def __str__(self) -> str:
        """Return the team name as a string."""
        return self.value

    def __repr__(self) -> str:
        """Return a concise representation of the team name."""
        return f"TeamName({self.value!r})"
