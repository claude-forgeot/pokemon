"""Pokedex module -- records encountered Pokemon, persisted to JSON."""

import json
import os

from utils.file_handler import FileHandler


class Pokedex:
    """Records encountered Pokemon, persisted to JSON.

    POO: This class demonstrates ENCAPSULATION -- the internal list of entries
    (self._entries) is managed through public methods (add_entry, get_all_entries),
    not accessed directly from outside. The underscore prefix (_entries) is a
    Python convention meaning "this attribute is private, don't touch it directly."
    This protects data integrity: you can't accidentally add duplicates because
    add_entry() checks for you.
    """

    def __init__(self, file_path="data/pokedex.json"):
        """Create a Pokedex, optionally loading existing data from disk.

        Args:
            file_path: Path to the JSON persistence file.
        """
        self.file_path = file_path
        self._entries = []
        self.load()

    def add_entry(self, pokemon):
        """Add a Pokemon to the Pokedex if not already registered.

        Duplicate detection is based on the Pokemon's name (case-insensitive).

        Args:
            pokemon: A Pokemon instance to register.

        Returns:
            bool: True if newly added, False if already present.
        """
        for entry in self._entries:
            if entry["name"].lower() == pokemon.name.lower():
                return False
        self._entries.append({
            "name": pokemon.name,
            "types": pokemon.types,
            "hp": pokemon.max_hp,
            "attack": pokemon.attack,
            "defense": pokemon.defense,
            "level": pokemon.level,
        })
        self.save()
        return True

    def get_all_entries(self):
        """Return a copy of all Pokedex entries.

        Returns:
            list[dict]: List of Pokemon data dictionaries.
        """
        return list(self._entries)

    def get_count(self):
        """Return the number of registered Pokemon.

        Returns:
            int: Number of entries.
        """
        return len(self._entries)

    def save(self):
        """Persist the current entries to the JSON file."""
        FileHandler.save_json(self.file_path, self._entries)

    def load(self):
        """Load entries from the JSON file if it exists.

        If the file is corrupted, creates a backup and resets to empty.
        If the file does not exist, starts with an empty list.
        """
        if not os.path.isfile(self.file_path):
            self._entries = []
            return
        try:
            data = FileHandler.load_json(self.file_path)
            if isinstance(data, list):
                self._entries = data
            else:
                self._entries = []
        except (json.JSONDecodeError, KeyError):
            FileHandler.create_backup(self.file_path)
            self._entries = []
            self.save()

    def reset(self):
        """Clear all entries and save the empty state."""
        self._entries = []
        self.save()
