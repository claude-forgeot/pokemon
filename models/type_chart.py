"""Type chart module -- 18-type effectiveness lookup table."""

import os

from utils.file_handler import FileHandler


class TypeChart:
    """18-type effectiveness lookup table.

    POO: This class holds a CLASS ATTRIBUTE (TYPES) shared by all instances,
    and an INSTANCE ATTRIBUTE (self.chart) unique to each instance.
    Class attributes are defined directly in the class body; instance
    attributes are assigned in __init__ using self.

    Source: official Pokemon type chart via PokeAPI.
    Fallback: local data/type_chart.json
    """

    TYPES = [
        "normal", "fire", "water", "electric", "grass", "ice",
        "fighting", "poison", "ground", "flying", "psychic",
        "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy",
    ]

    def __init__(self):
        """Initialize an empty type chart. Call load_from_file() to populate."""
        self.chart = {}

    def get_multiplier(self, attack_type, defend_type):
        """Get the damage multiplier for one attack type vs one defense type.

        Args:
            attack_type: The attacking type (e.g. "fire").
            defend_type: The defending type (e.g. "grass").

        Returns:
            float: Multiplier (0.0, 0.5, 1.0, or 2.0).
        """
        attack_type = attack_type.lower()
        defend_type = defend_type.lower()
        if attack_type in self.chart and defend_type in self.chart[attack_type]:
            return self.chart[attack_type][defend_type]
        return 1.0

    def get_combined_multiplier(self, attack_type, defend_types):
        """Get the combined multiplier against a multi-type defender.

        For a dual-type defender, the multipliers are multiplied together.
        Example: fire vs grass/ice = 2.0 * 2.0 = 4.0

        Args:
            attack_type: The attacking type string.
            defend_types: List of the defender's type strings.

        Returns:
            float: Combined multiplier.
        """
        result = 1.0
        for defend_type in defend_types:
            result *= self.get_multiplier(attack_type, defend_type)
        return result

    def load_from_file(self, path="data/type_chart.json"):
        """Load the type chart from a local JSON file.

        Args:
            path: Path to the JSON file.
        """
        if os.path.isfile(path):
            self.chart = FileHandler.load_json(path)

