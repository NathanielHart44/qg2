from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str

class User(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True

class PlayerBase(BaseModel):
    first_name: str
    last_name: str
    country: str
    age: int
    years_pro: int
    toughness: int
    awareness: int
    teamwork: int
    speed: int
    strength: int
    skill: int
    injury: int
    primary_position: str
    current_position: str
    depth: Optional[int] = None
    team_id: Optional[int] = None
    location_x: Optional[int] = 0
    location_y: Optional[int] = 0
    location_z: Optional[int] = 0
    target_x: Optional[int] = 0
    target_y: Optional[int] = 0
    target_z: Optional[int] = 0

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    id: int

    class Config:
        from_attributes = True

class TeamBase(BaseModel):
    name: str
    owner_id: int
    league_id: int

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    id: int
    players: List[Player] = []

    class Config:
        from_attributes = True

class LeagueBase(BaseModel):
    name: str

class LeagueCreate(LeagueBase):
    pass

class League(LeagueBase):
    id: int
    teams: List[Team] = []

    class Config:
        from_attributes = True

class SeasonBase(BaseModel):
    start_date: datetime
    end_date: datetime
    game_interval: int

class SeasonCreate(SeasonBase):
    pass

class Season(SeasonBase):
    id: int
    league_id: int

    class Config:
        from_attributes = True

class SnitchBase(BaseModel):
    x: int
    y: int
    z: int

class SnitchCreate(SnitchBase):
    pass

class Snitch(SnitchBase):
    id: int
    game_id: int

    class Config:
        from_attributes = True

class BludgerBase(BaseModel):
    x: int
    y: int
    z: int

class BludgerCreate(BludgerBase):
    pass

class Bludger(BludgerBase):
    id: int
    game_id: int

    class Config:
        from_attributes = True

class GameBase(BaseModel):
    start_time: datetime
    status: str

class GameCreate(GameBase):
    pass

class Game(GameBase):
    id: int
    season_id: int
    league_id: int
    home_team_id: int
    away_team_id: int
    snitch: Snitch
    bludger_1: Bludger
    bludger_2: Bludger

    class Config:
        from_attributes = True

class GameIntervalLogBase(BaseModel):
    order: int
    home_score: int
    away_score: int

class GameIntervalLogCreate(GameIntervalLogBase):
    pass

class GameIntervalLog(GameIntervalLogBase):
    id: int
    game_id: int

    class Config:
        from_attributes = True