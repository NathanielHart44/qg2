from fastapi import FastAPI, HTTPException, Depends, status, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import User as DBUser, Player as DBPlayer, League as DBLeague, Team as DBTeam
from schemas import User, Player, LeagueCreate, TeamCreate
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from database import get_db, create_db_and_tables
from auth import authenticate_user, gen_access_token, get_token, get_user_auth, hash_password, get_current_admin_user
from gen_players import generate_players as gen_players
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

@app.get("/generate_players/{total_players}")
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