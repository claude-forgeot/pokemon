"""Pokedex module -- records encountered Pokemon (in-memory only)."""


class Pokedex:
    """Records encountered Pokemon in memory.

    Persistence is handled externally by Game.save_game().
    """

    def __init__(self):
        """Create an empty Pokedex."""
        self._entries = []

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
        })
        return True

    def get_all_entries(self):
        """Return a copy of all Pokedex entries.

        Returns:
            list[dict]: List of Pokemon data dictionaries.
        """
        return list(self._entries)

    def add_raw_entry(self, entry_dict):
        """Add a raw dictionary entry to the Pokedex (used by save/load).

        Skips duplicates based on name (case-insensitive).

        Args:
            entry_dict: A dictionary with Pokemon data (name, types, hp, etc.).
        """
        name = entry_dict.get("name", "")
        for entry in self._entries:
            if entry.get("name", "").lower() == name.lower():
                return
        self._entries.append(entry_dict)

    def get_count(self):
        """Return the number of registered Pokemon.

        Returns:
            int: Number of entries.
        """
        return len(self._entries)

    def reset(self):
        """Clear all entries."""
        self._entries = []
