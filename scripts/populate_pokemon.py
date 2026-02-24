"""Populate script -- fetches Pokemon data from PokeAPI and creates pokemon.json.

Run this script to initialize the data/pokemon.json file with real Pokemon data
from PokeAPI. If the API is unreachable, falls back to data/default_pokemon.json.

Usage:
    py scripts/populate_pokemon.py
"""

import os
import random
import sys

# Add project root to path so imports work when running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_client import ApiClient
from utils.file_handler import FileHandler

# Number of moves to fetch per Pokemon
MOVES_PER_POKEMON = 4

# Pokemon IDs to fetch (Gen 1 popular picks)
POKEMON_IDS = [
    6,    # Charizard
    9,    # Blastoise
    3,    # Venusaur
    25,   # Pikachu
    94,   # Gengar
    68,   # Machamp
    65,   # Alakazam
    130,  # Gyarados
    149,  # Dragonite
    143,  # Snorlax
    59,   # Arcanine
    131,  # Lapras
    76,   # Golem
    103,  # Exeggutor
    34,   # Nidoking
]


def _fetch_moves(client, raw_moves):
    """Fetch up to 4 damaging moves for a Pokemon from PokeAPI.

    Picks moves that have power > 0 (damaging moves, not status).
    Tries to get a variety of types. Falls back to a default Tackle move.

    Args:
        client: ApiClient instance.
        raw_moves: List of move entries from the Pokemon API response.

    Returns:
        list[dict]: Up to 4 move dicts with name, move_type, power, accuracy.
    """
    # Shuffle to get variety, then try to fetch damaging moves
    candidates = list(raw_moves)
    random.shuffle(candidates)

    moves = []
    for entry in candidates:
        if len(moves) >= MOVES_PER_POKEMON:
            break
        try:
            move_data = client.fetch_move(entry["move"]["name"])
            power = move_data.get("power")
            if power is None or power == 0:
                continue
            accuracy = move_data.get("accuracy") or 100
            move_type = move_data["type"]["name"]
            move_name = move_data["name"].replace("-", " ").title()
            moves.append({
                "name": move_name,
                "move_type": move_type,
                "power": power,
                "accuracy": accuracy,
            })
        except Exception:
            continue

    # Fallback: always have at least one move
    if not moves:
        moves.append({
            "name": "Tackle",
            "move_type": "normal",
            "power": 40,
            "accuracy": 100,
        })

    return moves


def populate():
    """Fetch Pokemon from PokeAPI and save to data/pokemon.json."""
    client = ApiClient()
    pokemon_list = []

    print(f"Fetching {len(POKEMON_IDS)} Pokemon from PokeAPI...")

    for poke_id in POKEMON_IDS:
        try:
            data = client.fetch_pokemon(poke_id)
            name = data["name"].capitalize()
            types = [t["type"]["name"] for t in data["types"]]

            # Extract base stats
            stats = {}
            for stat in data["stats"]:
                stats[stat["stat"]["name"]] = stat["base_stat"]

            # Download sprite
            sprite_url = data["sprites"]["front_default"]
            sprite_path = f"assets/sprites/{data['name']}.png"

            try:
                if sprite_url:
                    client.download_sprite(sprite_url, sprite_path)
            except Exception:
                sprite_path = ""

            # Fetch up to 4 damaging moves
            moves = _fetch_moves(client, data["moves"])

            pokemon_entry = {
                "name": name,
                "hp": stats.get("hp", 50),
                "level": 5,
                "attack": stats.get("attack", 50),
                "defense": stats.get("defense", 50),
                "types": types,
                "sprite_path": sprite_path,
                "moves": moves,
            }
            pokemon_list.append(pokemon_entry)
            move_names = [m["name"] for m in moves]
            print(f"  [OK] {name} ({'/'.join(types)}) moves: {move_names}")

        except Exception as error:
            print(f"  [WARN] Failed to fetch Pokemon ID {poke_id}: {error}")

    if pokemon_list:
        FileHandler.save_json("data/pokemon.json", pokemon_list)
        print(f"\n[OK] Saved {len(pokemon_list)} Pokemon to data/pokemon.json")
    else:
        print("\n[WARN] No Pokemon fetched. Using default_pokemon.json as fallback.")


if __name__ == "__main__":
    populate()
