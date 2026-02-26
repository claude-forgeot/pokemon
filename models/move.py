"""Move module -- represents a Pokemon attack move."""


class Move:
    """A Pokemon attack move with type, power, and accuracy.

    Example:
        thunderbolt = Move("Thunderbolt", "electric", 90, 100)
    """

    def __init__(self, name="", move_type="normal", power=0, accuracy=100, data=None):
        """Create a new Move instance.

        Args:
            name: Display name (e.g. "Thunderbolt").
            move_type: Elemental type (e.g. "electric").
            power: Base power (int, higher = more damage).
            accuracy: Hit chance as percentage (1-100).
            data: Optional dict to build from (overrides other args).
        """
        if data is not None:
            name = data["name"]
            move_type = data["move_type"]
            power = data["power"]
            accuracy = data.get("accuracy", 100)
        if not name or not name.strip():
            raise ValueError("Move name cannot be empty")
        if not (0 <= accuracy <= 100):
            raise ValueError("Accuracy must be between 0 and 100")
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
