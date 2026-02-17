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
