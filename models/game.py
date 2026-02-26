"""Game module -- top-level game state manager."""

import os
import random

from models.pokemon import Pokemon
from models.pokedex import Pokedex
from models.type_chart import TypeChart
from utils.file_handler import FileHandler


class Game:
    """Top-level game state manager."""

    POKEMON_SOURCE_PATH = "data/pokemon.json"
    SAVE_PATH = "saves/save.json"
    TYPE_CHART_PATH = "data/type_chart.json"
    POKEDEX_PATH = "data/pokedex.json"

    def __init__(self):
        """Initialize the game: load type chart, then restore save or load source."""
        self.file_handler = FileHandler()
        self.type_chart = TypeChart()
        self.type_chart.load_from_file(self.TYPE_CHART_PATH)
        self.pokedex = Pokedex()
        self.pokemon_list = []
        self.evolution_count = 0
        if self.file_handler.file_exists(self.SAVE_PATH):
            self.load_game()
        else:
            self._load_from_source()

    def _load_from_source(self):
        """Load Pokemon from the immutable source file (data/pokemon.json)."""
        if self.file_handler.file_exists(self.POKEMON_SOURCE_PATH):
            data = self.file_handler.load_json(self.POKEMON_SOURCE_PATH)
            self.pokemon_list = []
            for p in data:
                self.pokemon_list.append(Pokemon(data=p))
        else:
            self.pokemon_list = []

    def new_game(self):
        """Reset the game state for a fresh start."""
        self.pokedex.reset()
        self.evolution_count = 0
        self._load_from_source()
        self.save_game()

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
        opponent = Pokemon(data=source.to_dict())
        return opponent

    def add_pokemon(self, pokemon_data):
        """Add a new Pokemon to the available list.

        Args:
            pokemon_data: Dictionary with Pokemon attributes.

        Returns:
            bool: True if added, False if a Pokemon with this name exists.
        """
        name = pokemon_data.get("name", "").lower()
        for p in self.pokemon_list:
            if p.name.lower() == name:
                return False
        new_pokemon = Pokemon(data=pokemon_data)
        self.pokemon_list.append(new_pokemon)
        return True

    def get_available_pokemon(self):
        """Return the list of unlocked (available) Pokemon.

        Returns:
            list[Pokemon]: Pokemon that are not locked.
        """
        available = []
        for p in self.pokemon_list:
            if not p.locked:
                available.append(p)
        return available

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
                return

    def sync_from_combat(self, player_team, original_indices):
        """Synchronize combat copies back to the original roster.

        After combat, the copies may have gained XP, levels, evolved, etc.
        This method copies those changes back to the originals.

        Args:
            player_team: List of Pokemon copies used during combat.
            original_indices: List of indices into self.pokemon_list,
                matching each copy to its original.
        """
        for team_idx, orig_idx in enumerate(original_indices):
            copy = player_team[team_idx]
            original = self.pokemon_list[orig_idx]
            original.xp = copy.xp
            original.level = copy.level
            original.xp_to_next_level = copy.xp_to_next_level
            original.max_hp = copy.max_hp
            original.hp = copy.max_hp  # Full heal after combat
            original.attack = copy.attack
            original.defense = copy.defense
            original.name = copy.name
            original.sprite_path = copy.sprite_path
            original.evolution_level = copy.evolution_level
            original.evolution_target = copy.evolution_target
            original.moves = copy.moves

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
            return " ".join(messages)
        return None

    def has_save(self):
        """Check if a save file exists.

        Returns:
            bool: True if saves/save.json exists.
        """
        return self.file_handler.file_exists(self.SAVE_PATH)

    def save_game(self):
        """Save current game state to saves/save.json."""
        save_dir = os.path.dirname(self.SAVE_PATH)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        pokemon_dicts = []
        for p in self.pokemon_list:
            pokemon_dicts.append(p.to_dict())
        save_data = {
            "pokemon_list": pokemon_dicts,
            "evolution_count": self.evolution_count,
            "pokedex": self.pokedex.get_all_entries(),
        }
        self.file_handler.save_json(self.SAVE_PATH, save_data)
        self.save_pokedex()

    def save_pokedex(self):
        """Write the pokedex to data/pokedex.json."""
        self.file_handler.save_json(self.POKEDEX_PATH, self.pokedex.get_all_entries())

    def load_game(self):
        """Load game state from saves/save.json."""
        data = self.file_handler.load_json(self.SAVE_PATH)
        try:
            new_list = []
            for p in data["pokemon_list"]:
                new_list.append(Pokemon(data=p))
            new_pokedex_entries = data["pokedex"]
            new_evolution_count = data.get("evolution_count", 0)
        except (KeyError, TypeError) as e:
            raise ValueError(f"Invalid save file: {e}")
        self.pokemon_list = new_list
        self.evolution_count = new_evolution_count
        self.pokedex.reset()
        for entry in new_pokedex_entries:
            self.pokedex.add_raw_entry(entry)
        self.save_pokedex()
