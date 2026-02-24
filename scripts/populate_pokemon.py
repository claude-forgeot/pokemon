"""Populate script -- fetches all 151 Gen 1 Pokemon from PokeAPI.

Creates data/pokemon.json with stats, types, sprites, moves, and evolution data.
If the API is unreachable, falls back to data/default_pokemon.json.

Usage:
    python3 scripts/populate_pokemon.py
"""

import os
import sys
import time

# Add project root to path so imports work when running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_client import ApiClient
from utils.file_handler import FileHandler

# All 151 Gen 1 Pokemon
GEN1_COUNT = 151

# Cache for move data (many Pokemon share the same moves)
_move_cache = {}

# Cache for evolution chains (Pokemon in the same family share a chain)
_evolution_chain_cache = {}


def fetch_move_data(client, move_name):
    """Fetch and cache a move's data (name, type, power, accuracy).

    Args:
        client: ApiClient instance.
        move_name: Name of the move.

    Returns:
        dict or None: Move data dict, or None if move has no power.
    """
    if move_name in _move_cache:
        return _move_cache[move_name]

    try:
        data = client.fetch_move(move_name)
        # Skip status moves (no power)
        if data.get("power") is None:
            _move_cache[move_name] = None
            return None

        move_info = {
            "name": data["name"].replace("-", " ").title(),
            "move_type": data["type"]["name"],
            "power": data["power"],
            "accuracy": data.get("accuracy") or 100,
        }
        _move_cache[move_name] = move_info
        return move_info
    except Exception:
        _move_cache[move_name] = None
        return None


def get_level_up_moves(pokemon_data, client, count=4):
    """Pick the best level-up moves for a Pokemon.

    Fetches move details from PokeAPI and picks up to `count` damaging
    moves, preferring moves learned at lower levels.

    Args:
        pokemon_data: Raw PokeAPI Pokemon response.
        client: ApiClient instance.
        count: Number of moves to pick (default 4).

    Returns:
        list[dict]: List of move dicts with name, move_type, power, accuracy.
    """
    # Collect level-up moves from Gen 1 (red-blue) or any version
    level_moves = []
    for move_entry in pokemon_data.get("moves", []):
        move_name = move_entry["move"]["name"]
        for vg in move_entry.get("version_group_details", []):
            if vg["move_learn_method"]["name"] == "level-up":
                level = vg["level_learned_at"]
                level_moves.append((level, move_name))
                break

    # Sort by level (lowest first) so we get early moves
    level_moves.sort(key=lambda x: x[0])

    # Fetch details and keep only damaging moves
    result = []
    for _level, move_name in level_moves:
        if len(result) >= count:
            break
        move_info = fetch_move_data(client, move_name)
        if move_info is not None:
            result.append(move_info)

    # If we don't have enough moves, add Tackle as fallback
    if len(result) == 0:
        tackle = fetch_move_data(client, "tackle")
        if tackle:
            result.append(tackle)

    return result


def parse_evolution_chain(chain_data):
    """Parse an evolution chain into a flat list of evolutions.

    Args:
        chain_data: The 'chain' field from PokeAPI evolution-chain response.

    Returns:
        list[dict]: Each dict has 'from_name', 'to_name', 'min_level'.
            Only includes evolutions triggered by level-up.
    """
    evolutions = []

    def walk(node, parent_name=None):
        current_name = node["species"]["name"]
        if parent_name is not None:
            # Check if this evolution is by level-up
            for detail in node.get("evolution_details", []):
                if detail.get("trigger", {}).get("name") == "level-up":
                    min_level = detail.get("min_level")
                    if min_level is not None:
                        evolutions.append({
                            "from_name": parent_name,
                            "to_name": current_name,
                            "min_level": min_level,
                        })
                    break
        for child in node.get("evolves_to", []):
            walk(child, current_name)

    walk(chain_data)
    return evolutions


def get_evolution_info(client, species_data, all_pokemon_data):
    """Get evolution target info for a Pokemon.

    Args:
        client: ApiClient instance.
        species_data: Raw PokeAPI species response.
        all_pokemon_data: Dict mapping pokemon name -> raw API data (for stats).

    Returns:
        dict: With keys evolution_level, evolution_target, evolution_data
            (target stats/types/sprite), or empty values if no level evolution.
    """
    chain_url = species_data["evolution_chain"]["url"]

    if chain_url not in _evolution_chain_cache:
        try:
            chain_response = client.fetch_evolution_chain(chain_url)
            _evolution_chain_cache[chain_url] = parse_evolution_chain(
                chain_response["chain"]
            )
        except Exception:
            _evolution_chain_cache[chain_url] = []

    evolutions = _evolution_chain_cache[chain_url]
    pokemon_name = species_data["name"]

    # Find evolution FROM this Pokemon
    for evo in evolutions:
        if evo["from_name"] == pokemon_name:
            target_name = evo["to_name"]
            target_data = all_pokemon_data.get(target_name)

            if target_data is None:
                return {
                    "evolution_level": evo["min_level"],
                    "evolution_target": target_name.capitalize(),
                    "evolution_data": None,
                }

            # Extract target stats
            target_stats = {}
            for stat in target_data["stats"]:
                target_stats[stat["stat"]["name"]] = stat["base_stat"]

            return {
                "evolution_level": evo["min_level"],
                "evolution_target": target_name.capitalize(),
                "evolution_data": {
                    "hp": target_stats.get("hp", 50),
                    "attack": target_stats.get("attack", 50),
                    "defense": target_stats.get("defense", 50),
                    "types": [t["type"]["name"] for t in target_data["types"]],
                    "sprite_path": f"assets/sprites/{target_name}.png",
                },
            }

    return {
        "evolution_level": None,
        "evolution_target": None,
        "evolution_data": None,
    }


def determine_locked(pokemon_name, species_data, all_evolutions):
    """Determine if a Pokemon should be locked at game start.

    Locked Pokemon:
    - Stage 2+ of level-based evolution chains
    - Mewtwo (unlocked after 10 evolutions)
    - Mew (unlocked after Pokedex complete)

    Args:
        pokemon_name: Lowercase Pokemon name.
        species_data: Raw PokeAPI species response.
        all_evolutions: Dict mapping chain_url -> list of evolution dicts.

    Returns:
        bool: True if locked.
    """
    if pokemon_name == "mewtwo":
        return True
    if pokemon_name == "mew":
        return True

    # Check if this Pokemon is a target of a level-up evolution
    for chain_url, evolutions in all_evolutions.items():
        for evo in evolutions:
            if evo["to_name"] == pokemon_name:
                return True

    return False


def populate():
    """Fetch all 151 Gen 1 Pokemon from PokeAPI and save to data/pokemon.json."""
    client = ApiClient()

    print(f"Fetching {GEN1_COUNT} Pokemon from PokeAPI...")
    print("This may take a few minutes on first run.\n")

    # Phase 1: Fetch all raw Pokemon data
    all_pokemon_raw = {}
    all_species_raw = {}

    for poke_id in range(1, GEN1_COUNT + 1):
        try:
            data = client.fetch_pokemon(poke_id)
            name = data["name"]
            all_pokemon_raw[name] = data
            print(f"  [{poke_id:3d}/151] {name.capitalize()}")
        except Exception as error:
            print(f"  [{poke_id:3d}/151] [WARN] Failed: {error}")
        # Small delay to be nice to the API
        if poke_id % 20 == 0:
            time.sleep(0.5)

    print(f"\n[OK] Fetched {len(all_pokemon_raw)} Pokemon base data.")

    # Phase 2: Fetch species data (for evolution chains)
    print("\nFetching species and evolution data...")
    for name, data in all_pokemon_raw.items():
        try:
            species = client.fetch_pokemon_species(data["id"])
            all_species_raw[name] = species

            # Pre-fetch evolution chain (caches automatically)
            chain_url = species["evolution_chain"]["url"]
            if chain_url not in _evolution_chain_cache:
                chain_response = client.fetch_evolution_chain(chain_url)
                _evolution_chain_cache[chain_url] = parse_evolution_chain(
                    chain_response["chain"]
                )
        except Exception as error:
            print(f"  [WARN] Species/evol for {name}: {error}")

    print(f"[OK] Fetched {len(all_species_raw)} species, "
          f"{len(_evolution_chain_cache)} evolution chains.")

    # Phase 3: Fetch moves for each Pokemon
    print("\nFetching move data...")
    all_moves = {}
    for name, data in all_pokemon_raw.items():
        moves = get_level_up_moves(data, client, count=4)
        all_moves[name] = moves

    print(f"[OK] {len(_move_cache)} unique moves cached.")

    # Phase 4: Build pokemon.json entries
    print("\nBuilding pokemon entries...")
    pokemon_list = []

    for poke_id in range(1, GEN1_COUNT + 1):
        # Find the Pokemon with this ID
        matching = [
            (name, data) for name, data in all_pokemon_raw.items()
            if data["id"] == poke_id
        ]
        if not matching:
            continue

        name, data = matching[0]
        species = all_species_raw.get(name)

        # Extract base stats
        stats = {}
        for stat in data["stats"]:
            stats[stat["stat"]["name"]] = stat["base_stat"]

        types = [t["type"]["name"] for t in data["types"]]

        # Download sprite
        sprite_url = data["sprites"]["front_default"]
        sprite_path = f"assets/sprites/{name}.png"
        try:
            if sprite_url and not os.path.isfile(sprite_path):
                client.download_sprite(sprite_url, sprite_path)
        except Exception:
            sprite_path = ""

        # Evolution info
        evo_info = {"evolution_level": None, "evolution_target": None,
                    "evolution_data": None}
        if species:
            evo_info = get_evolution_info(client, species, all_pokemon_raw)

            # Download evolution target sprite if needed
            if evo_info.get("evolution_data"):
                target_sprite = evo_info["evolution_data"].get("sprite_path", "")
                target_name = evo_info["evolution_target"].lower()
                target_data = all_pokemon_raw.get(target_name)
                if target_data and target_sprite and not os.path.isfile(target_sprite):
                    target_sprite_url = target_data["sprites"]["front_default"]
                    try:
                        if target_sprite_url:
                            client.download_sprite(target_sprite_url, target_sprite)
                    except Exception:
                        pass

        # Locked status
        locked = False
        if species:
            locked = determine_locked(name, species, _evolution_chain_cache)

        # Moves
        moves = all_moves.get(name, [])

        pokemon_entry = {
            "name": name.capitalize(),
            "hp": stats.get("hp", 50),
            "level": 5,
            "attack": stats.get("attack", 50),
            "defense": stats.get("defense", 50),
            "types": types,
            "sprite_path": sprite_path,
            "moves": moves,
            "locked": locked,
            "evolution_level": evo_info.get("evolution_level"),
            "evolution_target": evo_info.get("evolution_target"),
            "evolution_data": evo_info.get("evolution_data"),
        }
        pokemon_list.append(pokemon_entry)

    if pokemon_list:
        FileHandler.save_json("data/pokemon.json", pokemon_list)
        locked_count = sum(1 for p in pokemon_list if p["locked"])
        available_count = len(pokemon_list) - locked_count
        print(f"\n[OK] Saved {len(pokemon_list)} Pokemon to data/pokemon.json")
        print(f"     {available_count} available at start, {locked_count} locked")
    else:
        print("\n[WARN] No Pokemon fetched. Using default_pokemon.json as fallback.")


if __name__ == "__main__":
    populate()
