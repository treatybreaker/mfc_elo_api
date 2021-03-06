import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi import Query

from fastapi.exceptions import HTTPException

from pydantic import UUID4

from API.Auth import JWTBearer

from API.Database.Crud.Mordhau.Game.match import get_match_by_id
from API.Database.Crud.Mordhau.Game.match import get_matches_by_team_ids
from API.Database.Crud.Mordhau.Game.match import get_matches_by_team_id
from API.Database.Crud.Mordhau.Game.match import get_matches
from API.Database.Crud.Mordhau.Game.match import create_match
from API.Database.Crud.Mordhau.Game.match import calculate_elo
from API.Database.Crud.User.user import check_user

from API.Schemas import BaseSchema
from API.Schemas.Mordhau.Game.match import Match
from API.Schemas.Mordhau.Game.match import MatchInDB

from API.Endpoints import BaseEndpoint

log = logging.getLogger(__name__)


class Match(BaseEndpoint):
    tags = ["mordhau-match"]

    route = APIRouter(prefix="/match")

    @staticmethod
    @route.get("/id", tags=tags, response_model=MatchInDB)
    async def _id(id: UUID4):
        if match := await get_match_by_id(id):
            return match
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with id {id} not found"
        )

    @staticmethod
    @route.get("/get-matches-by-teams", tags=tags, response_model=list[MatchInDB])
    async def get_matches_by_team_ids(team1_id, team2_id):
        return get_matches_by_team_ids(team1_id, team2_id)

    @staticmethod
    @route.get("/get-matches-by-team-id", tags=tags, response_model=list[MatchInDB])
    async def get_matches_by_team_id(team_id):
        return get_matches_by_team_id(team_id)

    @staticmethod
    @route.get("/all", tags=tags, response_model=list[MatchInDB])
    async def get_all_matches(start_time: Optional[datetime] = Query(None, title="ISO 8601 Timestamp", Optional=True),
                              end_time: Optional[datetime] = Query(None, title="ISO 8601 Timestamp", Optional=True)):
        if start_time and not end_time or end_time and not start_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Both a start and end time MUST be supplied if a date is given!")
        matches = await get_matches(start_time, end_time)
        return matches

    @staticmethod
    @route.post("/create-match", tags=tags, response_model=BaseSchema)
    async def create_match(match: Match, auth=Depends(JWTBearer())):
        await check_user(token=auth[0], user_id=auth[-1])
        match_id = await create_match(match)
        log.info(f"User \"{auth[-1]}\" created a match \"{match_id}\"")
        return BaseSchema(
            message=f"Created match with id: {match_id}",
            extra=[
                {
                    "match_id": match_id
                }
            ]
        )

    @staticmethod
    @route.post("/calculate-match-elo", tags=tags, response_model=BaseSchema)
    async def calculate_match_elo(match_id: UUID4, auth=Depends(JWTBearer())):
        await check_user(token=auth[0], user_id=auth[-1])
        calculated_elo = await calculate_elo(match_id)
        return BaseSchema(message="Updated elo.", extra=[{"New ELO": calculated_elo}])
