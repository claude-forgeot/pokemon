"""Game module -- top-level game state manager."""

import os
import random

from models.pokemon import Pokemon
from models.pokedex import Pokedex
from models.type_chart import TypeChart
from utils.file_handler import FileHandler


class Game:
    """Top-level game state manager.

    POO: This class AGGREGATES other objects (Pokedex, list of Pokemon,
    TypeChart). Aggregation is a form of composition where the Game
    coordinates between different parts of the program without those parts
    needing to know about each other.
    """

    POKEMON_SOURCE_PATH = "data/pokemon.json"
    POKEMON_RUNTIME_PATH = "data/pokemon_state.json"
    TYPE_CHART_PATH = "data/type_chart.json"

    def __init__(self):
        """Initialize the game: load type chart, pokemon list, and pokedex."""
        self.type_chart = TypeChart()
        self.type_chart.load_from_file(self.TYPE_CHART_PATH)
        self.pokedex = Pokedex()
        self.pokemon_list = []
        self.evolution_count = 0
        self._load_pokemon()

    def _load_pokemon(self):
        """Load available Pokemon from runtime state, falling back to source."""
        if FileHandler.file_exists(self.POKEMON_RUNTIME_PATH):
            data = FileHandler.load_json(self.POKEMON_RUNTIME_PATH)
        elif FileHandler.file_exists(self.POKEMON_SOURCE_PATH):
            data = FileHandler.load_json(self.POKEMON_SOURCE_PATH)
        else:
            self.pokemon_list = []
            return
        # Handle both formats: list (legacy) and dict (new)
        if isinstance(data, list):
            self.pokemon_list = [Pokemon.from_dict(p) for p in data]
        else:
            self.pokemon_list = [Pokemon.from_dict(p) for p in data["pokemon_list"]]
            self.evolution_count = data.get("evolution_count", 0)

    def new_game(self):
        """Reset the game state for a fresh start."""
        self.pokedex.reset()
        self.evolution_count = 0
        if FileHandler.file_exists(self.POKEMON_SOURCE_PATH):
            data = FileHandler.load_json(self.POKEMON_SOURCE_PATH)
            self.pokemon_list = [Pokemon.from_dict(p) for p in data]
        else:
            self.pokemon_list = []
        self._save_pokemon()

    def get_random_opponent(self):
        """Pick a random Pokemon from the full list as an opponent.

        The opponent is a fresh copy (full HP) so the original list is not
        modified.

        Returns:
            Pokemon: A new Pokemon instance with full HP, or None if list empty.
        """
        available = self.get_available_pokemon()
        if not available:
            return None
        source = random.choice(available)
        opponent = Pokemon.from_dict(source.to_dict())
        return opponent

    def add_pokemon(self, pokemon_data):
        """Add a new Pokemon to the available list and persist it.

        Args:
            pokemon_data: Dictionary with Pokemon attributes.

        Returns:
            bool: True if added, False if a Pokemon with this name exists.
        """
        name = pokemon_data.get("name", "").lower()
        for p in self.pokemon_list:
            if p.name.lower() == name:
                return False
        new_pokemon = Pokemon.from_dict(pokemon_data)
        self.pokemon_list.append(new_pokemon)
        self._save_pokemon()
        return True

    def get_available_pokemon(self):
        """Return the list of unlocked (available) Pokemon.

        Returns:
            list[Pokemon]: Pokemon that are not locked.
        """
        return [p for p in self.pokemon_list if not p.locked]

    def get_all_pokemon(self):
        """Return the full list including locked Pokemon (for display).

        Returns:
            list[Pokemon]: All Pokemon in the roster.
        """
        return list(self.pokemon_list)

    def unlock_pokemon(self, name):
        """Unlock a Pokemon by name (e.g. after evolution).

        Args:
            name: Name of the Pokemon to unlock.
        """
        for p in self.pokemon_list:
            if p.name.lower() == name.lower() and p.locked:
                p.locked = False
                self._save_pokemon()
                return

    def record_evolution(self):
        """Record that an evolution happened. Checks legendary unlocks.

        Returns:
            str or None: Unlock message if a legendary was unlocked.
        """
        self.evolution_count += 1
        return self._check_legendary_unlocks()

    def _check_legendary_unlocks(self):
        """Check if Mewtwo or Mew should be unlocked.

        - Mewtwo: unlocked after 10 evolutions
        - Mew: unlocked when Pokedex is complete (151 entries)

        Returns:
            str or None: Unlock message, or None.
        """
        # Early return if both already unlocked
        mewtwo_locked = False
        mew_locked = False
        for p in self.pokemon_list:
            if p.name.lower() == "mewtwo" and p.locked:
                mewtwo_locked = True
            if p.name.lower() == "mew" and p.locked:
                mew_locked = True
        if not mewtwo_locked and not mew_locked:
            return None

        messages = []

        if self.evolution_count >= 10 and mewtwo_locked:
            for p in self.pokemon_list:
                if p.name.lower() == "mewtwo" and p.locked:
                    p.locked = False
                    messages.append("Mewtwo has been unlocked!")

        if self.pokedex.get_count() >= 151 and mew_locked:
            for p in self.pokemon_list:
                if p.name.lower() == "mew" and p.locked:
                    p.locked = False
                    messages.append("Mew has been unlocked!")

        if messages:
            self._save_pokemon()
            return " ".join(messages)
        return None

    def _save_pokemon(self):
        """Persist the current Pokemon list and evolution count to runtime state."""
        data = {
            "pokemon_list": [p.to_dict() for p in self.pokemon_list],
            "evolution_count": self.evolution_count,
        }
        FileHandler.save_json(self.POKEMON_RUNTIME_PATH, data)

    def save_game(self):
        """Save current game state to a JSON file in saves/ folder.

        POO: SERIALIZATION -- converting objects in memory to a format
        (JSON) that can be stored on disk and loaded back later.
        """
        from datetime import datetime

        os.makedirs("saves", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"save_{timestamp}.json"
        filepath = os.path.join("saves", filename)

        save_data = {
            "pokedex": self.pokedex.get_all_entries(),
            "pokemon_list": [p.to_dict() for p in self.pokemon_list],
            "evolution_count": self.evolution_count,
        }

        FileHandler.save_json(filepath, save_data)

    def load_game(self, filepath):
        """Load game state from a save file.

        POO: DESERIALIZATION -- the reverse of save: reading JSON from
        disk and reconstructing Python objects from it.

        Args:
            filepath: Path to the save JSON file.
        """
        data = FileHandler.load_json(filepath)
        try:
            new_list = [Pokemon.from_dict(p) for p in data["pokemon_list"]]
            new_pokedex_entries = data["pokedex"]
            new_evolution_count = data.get("evolution_count", 0)
        except (KeyError, TypeError) as e:
            raise ValueError(f"Invalid save file: {e}")
        self.pokemon_list = new_list
        self.evolution_count = new_evolution_count
        self.pokedex.reset()
        for entry in new_pokedex_entries:
            self.pokedex.add_raw_entry(entry)
        self.pokedex.save()
        self._save_pokemon()

    def get_save_files(self):
        """Return a list of available save files, newest first.

        Returns:
            list[dict]: Each dict has 'filename', 'filepath', 'date'.
        """
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
        if os.path.isfile(filepath):
            os.remove(filepath)