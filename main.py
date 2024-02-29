from fastapi import FastAPI, HTTPException, Depends, status, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import User as DBUser, Player as DBPlayer, League as DBLeague, Team as DBTeam, Game as DBGame
from schemas import User, Player, LeagueCreate, TeamCreate
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from database import get_db, create_db_and_tables
from auth import authenticate_user, gen_access_token, get_token, get_user_auth, hash_password, get_current_admin_user
from gen_players import generate_players as gen_players
from gameplay import check_all_positions_filled, get_missing_starters, get_team_lineup, handle_team_performance
from helpers import *
from typing import List
import logging

# ----------------------------------------------------------------------

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=app_lifespan)

@app.post("/register")
def register_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    existing_user = db.query(DBUser).filter(DBUser.username == form_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = hash_password(form_data.password)
    new_user = DBUser(username=form_data.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return new_user

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = gen_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/current_user", response_model=User)
def read_current_user(db: Session = Depends(get_db), token: str = Depends(get_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")
    
    current_user = get_user_auth(db, token)
    return current_user

@app.get("/toggle_admin_status")
def toggle_admin_status(username: str, db: Session = Depends(get_db), token: str = Depends(get_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")
    get_current_admin_user(db, token)

    user_to_toggle = db.query(DBUser).filter(DBUser.username == username).first()
    if not user_to_toggle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Toggle the admin status
    if user_to_toggle.role == "admin":
        user_to_toggle.role = "manager"
    else:
        user_to_toggle.role = "admin"

    db.commit()
    return {"message": f"Admin status for {username} changed to {user_to_toggle.role}"}

@app.post("/league/create", response_model=LeagueCreate)
def create_league(name: str = Form(...), db: Session = Depends(get_db), token: str = Depends(get_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")
    get_current_admin_user(db, token)

    new_league = DBLeague(name=name)
    db.add(new_league)
    db.commit()
    db.refresh(new_league)
    return new_league

# ----------------------------------------------------------------------
# Players

@app.get("/generate_players/{total_players}", response_model=List[Player])
def generate_players(total_players: int, db: Session = Depends(get_db), token: str = Depends(get_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")
    get_current_admin_user(db, token)

    players = gen_players(total_players, db)
    return players

@app.get("/players", response_model=List[Player])
def get_all_players(db: Session = Depends(get_db)):
    players = db.query(DBPlayer).all()
    return players

@app.get("/players/position/{position}", response_model=List[Player])
def get_players_by_position(position: str, db: Session = Depends(get_db)):
    players = db.query(DBPlayer).filter(DBPlayer.primary_position == position).all()
    return players

@app.post("/team/{team_id}/player/{player_id}")
def update_player_team(
    team_id: int,
    player_id: int,
    action: str = Form(...),  # "add" or "move" or "remove"
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")
    get_current_admin_user(db, token)

    check_team = action in ["move", "remove"]
    team, player = get_team_and_player(db, team_id, player_id, check_team=check_team)

    if action == "add":
        if player.team_id is not None:
            raise HTTPException(status_code=400, detail="Player is already on a team")
        player.team_id = team_id
        message = f"Player {player_id} added to team {team_id}"

    elif action == "move":
        if player.team_id is None:
            raise HTTPException(status_code=400, detail="Player is not on a team")
        player.team_id = team_id
        message = f"Player {player_id} moved to team {team_id}"

    elif action == "remove":
        if player.team_id != team_id:
            raise HTTPException(status_code=400, detail="Player is not in the specified team")
        player.team_id = None
        message = f"Player {player_id} removed from team {team_id}"

    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    db.commit()
    return {"message": message}

# ----------------------------------------------------------------------
# Teams

@app.post("/team/create", response_model=TeamCreate)
def create_team_for_current_user(
    name: str = Form(...),
    league_id: int = Form(...),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")
    current_user = get_user_auth(db, token)

    new_team = DBTeam(name=name, owner_id=current_user.id, league_id=league_id)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team

@app.get("/teams/{league_id}", response_model=List[TeamCreate])
def get_teams(league_id, db: Session = Depends(get_db), token: str = Depends(get_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")
    get_current_admin_user(db, token)

    teams = db.query(DBTeam).filter(DBTeam.league_id == league_id).all()
    return teams

@app.get("/my_teams", response_model=TeamCreate)
def get_my_teams(db: Session = Depends(get_db), token: str = Depends(get_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")
    current_user = get_user_auth(db, token)

    teams = db.query(DBTeam).filter(DBTeam.owner_id == current_user.id).all()
    return teams

@app.get("/team/{team_id}/players", response_model=List[Player])
def get_team_players(team_id: int, db: Session = Depends(get_db), token: str = Depends(get_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")

    team = db.query(DBTeam).filter(DBTeam.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    players = db.query(DBPlayer).filter(DBPlayer.team_id == team_id).all()
    return players

# def assign_auto_teams
# get or create id 1 of league.
# get or create id 1 and 2 of teams.
# call check_all_positions_filled to check if all positions are filled.
# if not filled, call gen_players to create 14 players.
# then call get_missing_starters to get the missing starters.
# for each key in missing starters, assign the players to the team.

class TeamLineup(BaseModel):
    Seeker: List[Player]
    Keeper: List[Player]
    Beater: List[Player]
    Chaser: List[Player]

class AutoTeamsResponse(BaseModel):
    team_1: TeamLineup
    team_2: TeamLineup

@app.get("/assign_auto_teams", response_model=AutoTeamsResponse)
def assign_auto_teams(
    league_id: int = 1,
    team_id_1: int = 1,
    team_id_2: int = 2,
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")
    get_current_admin_user(db, token)

    league = db.query(DBLeague).filter(DBLeague.id == league_id).first()
    if not league:
        league = DBLeague(name="test")
        db.add(league)
        db.commit()

    team_1 = db.query(DBTeam).filter(DBTeam.id == team_id_1).first()
    if not team_1:
        team_1 = DBTeam(name="team1", owner_id=1, league_id=league_id)
        db.add(team_1)
        db.commit()
    
    team_2 = db.query(DBTeam).filter(DBTeam.id == team_id_2).first()
    if not team_2:
        team_2 = DBTeam(name="team2", owner_id=1, league_id=league_id)
        db.add(team_2)
        db.commit()

    def assign_players_to_team(db: Session, team_id: int, missing_starters: dict):
        current_depths = {position: db.query(DBPlayer).filter(DBPlayer.team_id == team_id, DBPlayer.current_position == position).count() + 1 for position in missing_starters.keys()}
        for position, count in missing_starters.items():
            players = gen_players(count, db)  # Generate players for each missing position
            for _ in range(count):
                player = players.pop()
                player.team_id = team_id
                player.current_position = position  # Assign the correct position
                player.depth = current_depths[position]  # Set the depth
                current_depths[position] += 1  # Increment the depth counter
        db.commit()

    if not check_all_positions_filled(db, team_id_1):
        missing_starters = get_missing_starters(db, team_id_1)
        assign_players_to_team(db, team_id_1, missing_starters)

    if not check_all_positions_filled(db, team_id_2):
        missing_starters = get_missing_starters(db, team_id_2)
        assign_players_to_team(db, team_id_2, missing_starters)

    return {
        "team_1": get_team_lineup(db, team_id_1, "starters"),
        "team_2": get_team_lineup(db, team_id_2, "starters")
    }

@app.get("/test_team_performance")
def test_team_performance(db: Session = Depends(get_db), token: str = Depends(get_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")

    new_game = DBGame(season_id=1, home_team_id=1, away_team_id=2, status="scheduled")
    db.add(new_game)
    db.commit()

    result = handle_team_performance(db, new_game.id)
    return result