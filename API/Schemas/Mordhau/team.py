from typing import List
from typing import Optional

from API.Schemas import BaseInDB
from API.Schemas import BaseSchema
from API.Schemas.Mordhau.player import PlayerInDB


class BaseTeam(BaseSchema):
    team_name: str


class Team(BaseTeam):
    elo: int
    discord_id: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "team_name": "Example Team",
                "elo": 1500
            }
        }


class CreateTeam(Team):
    ...


class BaseTeamInDB(Team, BaseInDB):
    ...


class TeamInDB(BaseTeamInDB):
    players: List[PlayerInDB]
