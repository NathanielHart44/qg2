from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="manager")

class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    teams = relationship("Team", back_populates="league", cascade="all, delete")

class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id", ondelete="CASCADE"))
    league = relationship("League")
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    game_interval = Column(Integer)
    games = relationship("Game", back_populates="season", cascade="all, delete")

class Snitch(Base):
    __tablename__ = "snitches"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"))
    game = relationship("Game", back_populates="snitch")
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)

class Bludger(Base):
    __tablename__ = "bludgers"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"))
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(Integer, ForeignKey("seasons.id", ondelete="CASCADE"))
    season = relationship("Season", back_populates="games")
    home_team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"))
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_games")
    away_team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"))
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_games")
    start_time = Column(DateTime)
    status = Column(String)
    interval_logs = relationship("GameIntervalLog", back_populates="game", cascade="all, delete")
    snitch = relationship("Snitch", uselist=False, back_populates="game", cascade="all, delete")
    bludger_1_id = Column(Integer, ForeignKey("bludgers.id", ondelete="CASCADE"))
    bludger_1 = relationship("Bludger", foreign_keys=[bludger_1_id], backref="game_as_bludger_1")
    bludger_2_id = Column(Integer, ForeignKey("bludgers.id", ondelete="CASCADE"))
    bludger_2 = relationship("Bludger", foreign_keys=[bludger_2_id], backref="game_as_bludger_2")

class GameIntervalLog(Base):
    __tablename__ = "game_interval_logs"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"))
    game = relationship("Game", back_populates="interval_logs")
    order = Column(Integer)
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User")
    league_id = Column(Integer, ForeignKey("leagues.id", ondelete="CASCADE"))
    league = relationship("League", back_populates="teams")
    players = relationship("Player", back_populates="team")
    home_games = relationship("Game", foreign_keys=[Game.home_team_id], back_populates="home_team")
    away_games = relationship("Game", foreign_keys=[Game.away_team_id], back_populates="away_team")

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    country = Column(String)
    age = Column(Integer)
    years_pro = Column(Integer)
    toughness = Column(Integer)
    awareness = Column(Integer)
    teamwork = Column(Integer)
    speed = Column(Integer)
    strength = Column(Integer)
    skill = Column(Integer)
    injury = Column(Integer)
    primary_position = Column(String)
    current_position = Column(String)
    depth = Column(Integer, nullable=True, default=0)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    team = relationship("Team", back_populates="players", foreign_keys=[team_id])
    location_x = Column(Integer, nullable=True, default=0)
    location_y = Column(Integer, nullable=True, default=0)
    location_z = Column(Integer, nullable=True, default=0)
    target_x = Column(Integer, nullable=True, default=0)
    target_y = Column(Integer, nullable=True, default=0)
    target_z = Column(Integer, nullable=True, default=0)