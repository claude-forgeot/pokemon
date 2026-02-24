"""Move module -- represents an attack that a Pokemon can use."""


class Move:
    """A move (attack) that a Pokemon can use in battle.

    Each move has a name, type, power, and accuracy. Pokemon have up to 4 moves.

    Example:
        thunderbolt = Move("Thunderbolt", "electric", 90, 100)
        thunderbolt.power  # 90
    """

    def __init__(self, name, move_type, power, accuracy):
        """Create a new Move.

        Args:
            name: Display name (e.g. "Thunderbolt").
            move_type: Type string (e.g. "electric").
            power: Base power (int). 0 for status moves.
            accuracy: Hit chance in percent (e.g. 100 = always hits).
        """
        self.name = name
        self.move_type = move_type
        self.power = power
        self.accuracy = accuracy

    def to_dict(self):
        """Serialize to dictionary for JSON storage."""
        return {
            "name": self.name,
            "move_type": self.move_type,
            "power": self.power,
            "accuracy": self.accuracy,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Move from a dictionary."""
        return cls(
            name=data["name"],
            move_type=data["move_type"],
            power=data.get("power", 40),
            accuracy=data.get("accuracy", 100),
        )

    def __str__(self):
        return f"{self.name} ({self.move_type}) PWR:{self.power} ACC:{self.accuracy}"
