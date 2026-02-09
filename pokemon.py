"""Pokemon module -- represents a Pokemon creature with stats and types."""


class Pokemon:
    """A Pokemon creature with stats and types.

    POO: This is a CLASS -- a blueprint (or template) for creating objects.
    Each Pokemon created from this class is an INSTANCE (a concrete object).
    __init__ is the CONSTRUCTOR -- it runs automatically when you write
    Pokemon(...). 'self' refers to the current instance being manipulated.

    ATTRIBUTES are variables attached to an instance (self.name, self.hp, etc.).
    METHODS are functions defined inside a class that operate on an instance.

    Example:
        pikachu = Pokemon("Pikachu", 35, 5, 55, 40, ["electric"])
        pikachu.take_damage(10)   # pikachu.hp becomes 25
        pikachu.is_alive()        # returns True
    """

    def __init__(self, name, hp, level, attack, defense, types, sprite_path=""):
        """Create a new Pokemon instance.

        Args:
            name: Display name (e.g. "Charizard").
            hp: Hit points (health).
            level: Current level.
            attack: Attack stat.
            defense: Defense stat.
            types: List of type strings (e.g. ["fire", "flying"]).
            sprite_path: Path to the sprite image file.
        """
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.level = level
        self.attack = attack
        self.defense = defense
        self.types = types
        self.sprite_path = sprite_path

    def take_damage(self, amount):
        """Reduce HP by the given amount, floored at 0.

        Args:
            amount: Damage to apply (positive int).
        """
        self.hp = max(0, self.hp - amount)

    def is_alive(self):
        """Check if this Pokemon is still standing.

        Returns:
            bool: True if HP > 0, False otherwise.
        """
        return self.hp > 0

    def heal(self):
        """Fully restore HP to max_hp."""
        self.hp = self.max_hp

    def to_dict(self):
        """Serialize this Pokemon to a dictionary for JSON storage.

        Returns:
            dict: All Pokemon data as a plain dictionary.
        """
        return {
            "name": self.name,
            "hp": self.max_hp,
            "level": self.level,
            "attack": self.attack,
            "defense": self.defense,
            "types": self.types,
            "sprite_path": self.sprite_path,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Pokemon instance from a dictionary.

        POO: A @classmethod receives the class itself (cls) instead of an
        instance (self). It's used as an alternative constructor -- a second
        way to create objects, here from saved JSON data.

        Args:
            data: Dictionary with Pokemon attributes.

        Returns:
            Pokemon: A new Pokemon instance.
        """
        return cls(
            name=data["name"],
            hp=data["hp"],
            level=data.get("level", 5),
            attack=data["attack"],
            defense=data["defense"],
            types=data["types"],
            sprite_path=data.get("sprite_path", ""),
        )

    def __str__(self):
        """Return a readable string representation.

        POO: __str__ is a MAGIC METHOD (or dunder method). Python calls it
        automatically when you do print(pokemon) or str(pokemon).
        """
        types_str = "/".join(self.types)
        return f"{self.name} (Lv.{self.level}) [{types_str}] HP:{self.hp}/{self.max_hp}"
