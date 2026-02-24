"""Move module -- represents a Pokemon attack move."""


class Move:
    """A Pokemon attack move with type, power, and accuracy.

    POO: Simple data class. Each move has a name, an elemental type,
    a base power (how much damage it does), and an accuracy (hit chance).

    Example:
        thunderbolt = Move("Thunderbolt", "electric", 90, 100)
        print(thunderbolt)  # "Thunderbolt (electric) PWR:90 ACC:100"
    """

    def __init__(self, name, move_type, power, accuracy):
        """Create a new Move instance.

        Args:
            name: Display name (e.g. "Thunderbolt").
            move_type: Elemental type (e.g. "electric").
            power: Base power (int, higher = more damage).
            accuracy: Hit chance as percentage (1-100).
        """
        self.name = name
        self.move_type = move_type
        self.power = power
        self.accuracy = accuracy

    def to_dict(self):
        """Serialize this Move to a dictionary for JSON storage.

        Returns:
            dict: Move data as a plain dictionary.
        """
        return {
            "name": self.name,
            "move_type": self.move_type,
            "power": self.power,
            "accuracy": self.accuracy,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Move instance from a dictionary.

        Args:
            data: Dictionary with move attributes.

        Returns:
            Move: A new Move instance.
        """
        return cls(
            name=data["name"],
            move_type=data["move_type"],
            power=data["power"],
            accuracy=data.get("accuracy", 100),
        )

    def __str__(self):
        """Return a readable string representation."""
        return f"{self.name} ({self.move_type}) PWR:{self.power} ACC:{self.accuracy}"
