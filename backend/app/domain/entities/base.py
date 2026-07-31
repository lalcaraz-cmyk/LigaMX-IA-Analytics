from dataclasses import dataclass
from typing import Generic, TypeVar


TId = TypeVar("TId")


@dataclass(eq=False)
class Entity(Generic[TId]):
    """Base class for domain entities."""

    id: TId

    def __eq__(self, other: object) -> bool:
        """Return True when two entities share the same concrete type and id."""
        if type(other) is not type(self):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash entities by their concrete type and id."""
        return hash((type(self), self.id))

    def __repr__(self) -> str:
        """Return a concise representation of the entity."""
        return f"{self.__class__.__name__}(id={self.id!r})"
