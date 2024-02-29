from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import User as DBUser, Player as DBPlayer, League as DBLeague, Team as DBTeam, Game as DBGame, GameIntervalLog as DBGIL

# ----------------------------------------------------------------------

def get_team_and_player(db: Session, team_id: int, player_id: int, check_team: bool = True):
    team = None
    if check_team:
        team = db.query(DBTeam).filter(DBTeam.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

    player = db.query(DBPlayer).filter(DBPlayer.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return team, player