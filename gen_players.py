import json
import random
from models import Player as DBPlayer
from sqlalchemy.orm import Session

# ----------------------------------------------------------------------

def load_position_data():
    with open('data/positions.json') as f:
        return json.load(f)

def random_name(file_path):
    with open(file_path) as f:
        names = f.readlines()
    return random.choice(names).strip()

def generate_player_attributes(position, attribute_ranges):
    attributes = {}
    for attribute in ["speed", "strength", "skill", "toughness", "awareness", "teamwork"]:
        default_range = (0, 100)
        range_values = attribute_ranges.get(attribute, default_range)
        attributes[attribute] = random.randint(*range_values)
    return attributes

def generate_players(total_players: int, db: Session):
    position_data = load_position_data()
    players = []

    for _ in range(total_players):
        position = random.choice(list(position_data.keys()))
        attributes = generate_player_attributes(position, position_data[position])
        player_age = random.randint(17, 55)
        new_player = DBPlayer(
            first_name=random_name('data/first_names.txt'),
            last_name=random_name('data/last_names.txt'),
            country=random_name('data/countries.txt'),
            age=player_age,
            years_pro=random.randint(0, player_age - 17),
            toughness=attributes["toughness"],
            awareness=attributes["awareness"],
            teamwork=attributes["teamwork"],
            speed=attributes["speed"],
            strength=attributes["strength"],
            skill=attributes["skill"],
            injury=random.randint(0, 100),
            primary_position=position,
            current_position=position,
        )
        db.add(new_player)
        players.append(new_player)

    db.commit()
    return players
