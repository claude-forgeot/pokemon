"""Game module -- top-level game state manager."""

import os
import random

from pokemon import Pokemon
from pokedex import Pokedex
from type_chart import TypeChart
from utils.file_handler import FileHandler


class Game:
    """Top-level game state manager.

    POO: This class AGGREGATES other objects (Pokedex, list of Pokemon,
    TypeChart). Aggregation is a form of composition where the Game
    coordinates between different parts of the program without those parts
    needing to know about each other.
    """

    POKEMON_PATH = "data/pokemon.json"
    DEFAULT_POKEMON_PATH = "data/default_pokemon.json"
    TYPE_CHART_PATH = "data/type_chart.json"

    def __init__(self):
        """Initialize the game: load type chart, pokemon list, and pokedex."""
        self.type_chart = TypeChart()
        self.type_chart.load_from_file(self.TYPE_CHART_PATH)
        self.pokedex = Pokedex()
        self.pokemon_list = []
        self._load_pokemon()

    def _load_pokemon(self):
        """Load available Pokemon from pokemon.json, with fallback.

        If pokemon.json does not exist, tries to run the populate script.
        If that fails, falls back to default_pokemon.json.
        """
        if not FileHandler.file_exists(self.POKEMON_PATH):
            self._try_populate()

        if FileHandler.file_exists(self.POKEMON_PATH):
            data = FileHandler.load_json(self.POKEMON_PATH)
            self.pokemon_list = [Pokemon.from_dict(p) for p in data]
        elif FileHandler.file_exists(self.DEFAULT_POKEMON_PATH):
            data = FileHandler.load_json(self.DEFAULT_POKEMON_PATH)
            self.pokemon_list = [Pokemon.from_dict(p) for p in data]
        else:
            self.pokemon_list = []

    def _try_populate(self):
        """Try to run the populate script to fetch Pokemon from PokeAPI."""
        try:
            from scripts.populate_pokemon import populate
            populate()
        except Exception:
            pass

    def new_game(self):
        """Reset the game state for a fresh start."""
        self.pokedex.reset()

    def get_random_opponent(self):
        """Pick a random Pokemon from the full list as an opponent.

        The opponent is a fresh copy (full HP) so the original list is not
        modified.

        Returns:
            Pokemon: A new Pokemon instance with full HP, or None if list empty.
        """
        if not self.pokemon_list:
            return None
        source = random.choice(self.pokemon_list)
        opponent = Pokemon.from_dict(source.to_dict())
        return opponent

    def add_pokemon(self, pokemon_data):
        """Add a new Pokemon to the available list and persist it.

        Args:
            pokemon_data: Dictionary with Pokemon attributes.
        """
        new_pokemon = Pokemon.from_dict(pokemon_data)
        self.pokemon_list.append(new_pokemon)
        self._save_pokemon()

    def get_available_pokemon(self):
        """Return the list of all available Pokemon.

        Returns:
            list[Pokemon]: Current Pokemon roster.
        """
        return list(self.pokemon_list)

    def _save_pokemon(self):
        """Persist the current Pokemon list to pokemon.json."""
        data = [p.to_dict() for p in self.pokemon_list]
        FileHandler.save_json(self.POKEMON_PATH, data)
    def save_game(self):
        """Save current game state to a JSON file in saves/ folder.

        POO: SERIALIZATION -- converting objects in memory to a format
        (JSON) that can be stored on disk and loaded back later.

        Returns:
            str: The filename of the saved game.
        """
        import os
        from datetime import datetime

        os.makedirs("saves", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"save_{timestamp}.json"
        filepath = os.path.join("saves", filename)

        save_data = {
            "pokedex": self.pokedex.get_all_entries(),
            "pokemon_list": [p.to_dict() for p in self.pokemon_list],
            "save_date": timestamp,
        }

        from utils.file_handler import FileHandler
        FileHandler.save_json(filepath, save_data)
        return filename

    def load_game(self, filepath):
        """Load game state from a save file.

        POO: DESERIALIZATION -- the reverse of save: reading JSON from
        disk and reconstructing Python objects from it.

        Args:
            filepath: Path to the save JSON file.
        """
        from utils.file_handler import FileHandler
        from pokemon import Pokemon

        data = FileHandler.load_json(filepath)
        self.pokemon_list = [Pokemon.from_dict(p) for p in data["pokemon_list"]]
        self.pokedex.reset()
        for entry in data["pokedex"]:
            self.pokedex._entries.append(entry)
        self.pokedex.save()

    def get_save_files(self):
        """Return a list of available save files, newest first.

        Returns:
            list[dict]: Each dict has 'filename', 'filepath', 'date'.
        """
        import os

        save_dir = "saves"
        if not os.path.isdir(save_dir):
            return []

        saves = []
        for f in os.listdir(save_dir):
            if f.startswith("save_") and f.endswith(".json"):
                filepath = os.path.join(save_dir, f)
                date_str = f.replace("save_", "").replace(".json", "")
                saves.append({
                    "filename": f,
                    "filepath": filepath,
                    "date": date_str,
                })
        saves.sort(key=lambda s: s["date"], reverse=True)
        return saves

    def delete_save(self, filepath):
        """Delete a save file.

        Args:
            filepath: Path to the save file to delete.
        """
        import os

        if os.path.isfile(filepath):
            os.remove(filepath)