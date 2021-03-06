import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import status
from fastapi.exceptions import HTTPException

from pydantic import UUID4

from API.Database.Crud.User.user import check_user
from API.Auth import JWTBearer

from API.Database.Crud.Mordhau.team import get_teams
from API.Database.Crud.Mordhau.team import remove_player_from_team
from API.Database.Crud.Mordhau.team import add_player_to_team
from API.Database.Crud.Mordhau.team import get_team_by_id
from API.Database.Crud.Mordhau.team import get_team_by_discord_id
from API.Database.Crud.Mordhau.team import get_team_by_name
from API.Database.Crud.Mordhau.team import create_team
from API.Database.Crud.Mordhau.team import delete_team
from API.Database.Crud.Mordhau.team import update_name
from API.Database.Crud.Mordhau.team import update_elo

from API.Endpoints import BaseEndpoint

from API.Schemas.Mordhau.team import Team
from API.Schemas.Mordhau.team import TeamInDB
from API.Schemas import BaseSchema

log = logging.getLogger(__name__)


class MordhauTeam(BaseEndpoint):
    tags = ["mordhau-team"]

    route = APIRouter(prefix="/team")

    @staticmethod
    @route.get("/all", tags=tags, response_model=list[TeamInDB])
    async def team():
        teams = await get_teams()
        print(teams)
        return teams

    @staticmethod
    @route.get("/id", tags=tags, response_model=TeamInDB)
    async def _id(id: str) -> [Team]:
        if team := await get_team_by_id(id):
            return team
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with id \"{id}\" not found"
        )

    @staticmethod
    @route.get("/discord-id", tags=tags, response_model=TeamInDB)
    async def get_team_by_discord_id(discord_id: int):
        return await get_team_by_discord_id(discord_id)

    @staticmethod
    @route.get("/name", tags=tags, response_model=TeamInDB)
    async def name(team_name: str):
        if team := await get_team_by_name(team_name):
            return team
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with name \"{team_name}\" not found"
        )

    @staticmethod
    @route.post("/name", tags=tags, response_model=TeamInDB)
    async def update_name(new_name: str,
                          team_id: str = Query(..., min_length=32, max_length=36),
                          auth=Depends(JWTBearer())):
        await check_user(token=auth[0], user_id=auth[-1])
        if team_id and await get_team_by_id(team_id):
            log.info(f"User id \"{auth[-1]}\" updated team_id \"{team_id}\" team name to \"{new_name}\"")
            return await update_name(team_id, new_name)

    @staticmethod
    @route.post("/create", tags=tags)
    async def create(team: Team, auth=Depends(JWTBearer())) -> BaseSchema:
        await check_user(token=auth[0], user_id=auth[-1])
        log.info(f"User id \"{auth[-1]}\" issued a creation of "
                 f"Mordhau Team \"{team.team_name}\"")
        team_id = await create_team(team)
        return BaseSchema(message=f"Team ID: {team_id}", extra=[{"id": team_id}])

    @staticmethod
    @route.post("/delete", tags=tags, response_model=BaseSchema)
    async def delete(team_id: UUID4, auth=Depends(JWTBearer())):
        await check_user(token=auth[0], user_id=auth[-1])
        if team_id and await get_team_by_id(team_id):
            log.info(f"User id \"{auth[-1]}\" issued a delete of Mordhau Team id \"{team_id}\"")
            await delete_team(team_id)
            return BaseSchema(message=f"Team {team_id} deleted", extra=[{"id": team_id}])

    @staticmethod
    @route.post("/update-elo", tags=tags, response_model=TeamInDB)
    async def update_elo(new_elo: int,
                         team_id: UUID4,
                         auth=Depends(JWTBearer())):
        await check_user(token=auth[0], user_id=auth[-1])
        if team_id and await get_team_by_id(team_id):
            log.info(f"User id \"{auth[-1]}\" updated team_id \"{team_id}\" elo to {new_elo}")
            return await update_elo(team_id, new_elo)

    @staticmethod
    @route.post("/add-player-to-team", tags=tags, response_model=TeamInDB)
    async def add_player_to_team(player_id: UUID4,
                                 team_id: UUID4,
                                 auth=Depends(JWTBearer())):
        await check_user(token=auth[0], user_id=auth[-1])
        return await add_player_to_team(player_id, team_id)

    @staticmethod
    @route.post("/remove-player-from-team", tags=tags, response_model=TeamInDB)
    async def remove_player_from_team(player_id: UUID4, team_id: UUID4, auth=Depends(JWTBearer())):
        await check_user(token=auth[0], user_id=auth[-1])
        return await remove_player_from_team(player_id, team_id)
