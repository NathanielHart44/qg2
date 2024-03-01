from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import (
    User as DBUser, Player as DBPlayer,
    League as DBLeague, Team as DBTeam, Game as DBGame,
    GameIntervalLog as DBGIL, Snitch as DBSnitch, Bludger as DBBludger
)
import random

# ----------------------------------------------------------------------

starter_depth_thresholds = {
    "Seeker": 1,
    "Keeper": 1,
    "Beater": 2,
    "Chaser": 3
}

matrix_size = {'x': 13, 'y': 8, 'z': 8}
spacing = 1.0

# ----------------------------------------------------------------------

def get_missing_starters(db: Session, team_id: int) -> dict:
    team = db.query(DBTeam).filter(DBTeam.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    players = db.query(DBPlayer).filter(DBPlayer.team_id == team_id).all()
    team_positions = {"Seeker": 0, "Keeper": 0, "Beater": 0, "Chaser": 0}
    for player in players:
        team_positions[player.current_position] += 1

    missing_starters = {}
    for position in team_positions:
        if team_positions[position] < starter_depth_thresholds[position]:
            missing_starters[position] = starter_depth_thresholds[position] - team_positions[position]

    return missing_starters

def check_all_positions_filled(db: Session, team_id: int) -> bool:
    team = db.query(DBTeam).filter(DBTeam.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    players = db.query(DBPlayer).filter(DBPlayer.team_id == team_id).all()
    team_positions = {"Seeker": 0, "Keeper": 0, "Beater": 0, "Chaser": 0}
    for player in players:
        team_positions[player.current_position] += 1

    for position in team_positions:
        if team_positions[position] < starter_depth_thresholds[position]:
            return False
    return True

def get_team_lineup(db: Session, team_id: int, lineup_type: str) -> dict:
    # Define the maximum depth for starters by position

    players = db.query(DBPlayer).filter(DBPlayer.team_id == team_id).order_by(
        DBPlayer.current_position, DBPlayer.depth).all()

    lineup = {"Seeker": [], "Keeper": [], "Beater": [], "Chaser": []}
    for player in players:
        position = player.current_position
        if lineup_type == "starters" and player.depth <= starter_depth_thresholds[position]:
            lineup[position].append(player)
        elif lineup_type == "bench" and player.depth > starter_depth_thresholds[position]:
            lineup[position].append(player)

    return lineup

def get_beater_performance(team_beaters: list, opponent_beaters: list) -> dict:
    team_beater_performance = 0
    opponent_beater_performance = 0

    for beater in team_beaters:
        skill_mod = random.uniform(0.1, 0.45)
        strength_mod = random.uniform(0.3, 0.65)
        speed_mod = random.uniform(0.1, 0.25)
        team_beater_performance += (beater.strength * strength_mod) + (beater.skill * skill_mod) + (beater.speed * speed_mod)

    for beater in opponent_beaters:
        skill_mod = random.uniform(0.1, 0.45)
        strength_mod = random.uniform(0.3, 0.65)
        speed_mod = random.uniform(0.1, 0.25)
        opponent_beater_performance += (beater.strength * strength_mod) + (beater.skill * skill_mod) + (beater.speed * speed_mod)

    return {"team_beater_performance": team_beater_performance, "opponent_beater_performance": opponent_beater_performance}

# get_chaser_performance
# take in team's chasers, opponent's chasers, both team's beater performance.


# handle_team_performance
# take in a team id. and a game id.
# calculate the performance of the team's various positions, in relation to the opponent.
# return goals scored by the team and snitch catches by the team.

def handle_team_performance(db: Session, game_id: int) -> dict:
    game = db.query(DBGame).filter(DBGame.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Get the home team's lineup
    home_starters = get_team_lineup(db, game.home_team_id, "starters")

    # Get the away team's lineup
    opponent_starters = get_team_lineup(db, game.away_team_id, "starters")

    # Calculate the performance of the team's various positions
    performance = {"Seeker": 0, "Keeper": 0, "Beater": 0, "Chaser": 0}
    for position in performance:
        for player in home_starters[position]:
            performance[position] += player.skill

        for player in opponent_starters[position]:
            performance[position] -= player.skill

    # Calculate the team's goals scored and snitch catches
    goals_scored = 0
    snitch_catches = 0

    # return {"goals_score": goals_scored, "snitch_catches": snitch_catches}
    return performance

# function handle_game_log.
# take in a game id.
# find all the game logs of this game.
# create a new game interval log for the game, with the order being the last order + 1.
# calculate the performance of each team by calling handle_team_performance.
# update teh game's scores.
# check if game should end, and if so, end the game.







def handle_player_movement(db: Session, team_id: int, game_id: int) -> dict:
    team = db.query(DBTeam).filter(DBTeam.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found - player movement")

    game = db.query(DBGame).filter(DBGame.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail=f"Game ({game_id}) not found - player movement")

    # Get the team's starting lineup
    starters = get_team_lineup(db, team_id, "starters")

    # Generate a random number for each player
    player_movements = {}

    player_movements = {}
    for position_name in starter_depth_thresholds:
        for count, player in enumerate(starters[position_name]):
            player_movement = generate_player_position(player)

            player_movements[f"{position_name}_{count + 1}"] = player_movement

    return player_movements

def generate_player_position(player: DBPlayer):
    if not player.target_x and not player.target_y and not player.target_z:
        player.location_x = (random.random() * (matrix_size['x'] - 1) - (matrix_size['x'] - 1) / 2) * spacing
        player.location_y = (random.random() * (matrix_size['y'] - 1) - (matrix_size['y'] - 1) / 2) * spacing
        player.location_z = (random.random() * (matrix_size['z'] - 1) - (matrix_size['z'] - 1) / 2) * spacing
    else:
        player.location_x = player.target_x
        player.location_y = player.target_y
        player.location_z = player.target_z
    player.target_x = (random.random() * (matrix_size['x'] - 1) - (matrix_size['x'] - 1) / 2) * spacing
    player.target_y = (random.random() * (matrix_size['y'] - 1) - (matrix_size['y'] - 1) / 2) * spacing
    player.target_z = (random.random() * (matrix_size['z'] - 1) - (matrix_size['z'] - 1) / 2) * spacing
    position = {
        'x': player.location_x,
        'y': player.location_y,
        'z': player.location_z
    }
    target = {
        'x': player.target_x,
        'y': player.target_y,
        'z': player.target_z
    }

    return {
        'id': player.id,
        'position': position,
        'target': target
    }

def handle_snitch_placement(db: Session, game_id: int) -> dict:
    game = db.query(DBGame).filter(DBGame.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found - snitch placement")

    if not game.snitch:
        snitch = DBSnitch(
            x=(random.random() * (matrix_size['x'] - 1) - (matrix_size['x'] - 1) / 2) * spacing,
            y=(random.random() * (matrix_size['y'] - 1) - (matrix_size['y'] - 1) / 2) * spacing,
            z=(random.random() * (matrix_size['z'] - 1) - (matrix_size['z'] - 1) / 2) * spacing,
            game_id=game_id
        )
        db.add(snitch)
        db.commit()
    else:
        snitch = game.snitch
        snitch.x = (random.random() * (matrix_size['x'] - 1) - (matrix_size['x'] - 1) / 2) * spacing
        snitch.y = (random.random() * (matrix_size['y'] - 1) - (matrix_size['y'] - 1) / 2) * spacing
        snitch.z = (random.random() * (matrix_size['z'] - 1) - (matrix_size['z'] - 1) / 2) * spacing
        db.commit()

def handle_snitch_catch(db: Session, game_id: int) -> bool:
    game = db.query(DBGame).filter(DBGame.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found - snitch catch")
    
    snitch: DBSnitch = game.snitch

    team_1 = db.query(DBTeam).filter(DBTeam.id == game.home_team_id).first()
    team_2 = db.query(DBTeam).filter(DBTeam.id == game.away_team_id).first()
    if not team_1 or not team_2:
        raise HTTPException(status_code=404, detail="Teams not found")
    
    seeker_1 = db.query(DBPlayer).filter(DBPlayer.team_id == team_1.id, DBPlayer.current_position == "Seeker").first()
    seeker_2 = db.query(DBPlayer).filter(DBPlayer.team_id == team_2.id, DBPlayer.current_position == "Seeker").first()

    distance_1 = ((seeker_1.location_x - snitch.x) ** 2 + (seeker_1.location_y - snitch.y) ** 2 + (seeker_1.location_z - snitch.z) ** 2) ** 0.5
    distance_2 = ((seeker_2.location_x - snitch.x) ** 2 + (seeker_2.location_y - snitch.y) ** 2 + (seeker_2.location_z - snitch.z) ** 2) ** 0.5

    if distance_1 < 5 or distance_2 < 5:
        if distance_1 < distance_2:
            return 'HOME'
        elif distance_2 < distance_1:
            return 'AWAY'
        else:
            None
    else:
        return None