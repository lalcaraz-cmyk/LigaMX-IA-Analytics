from dataclasses import dataclass

from app.domain.entities.base import Entity
from app.domain.value_objects.team_name import TeamName


@dataclass(eq=False, slots=True)
class Team(Entity[int]):
    """Domain entity representing a football club."""

    id: int
    name: TeamName
