"""Pokemon module -- represents a Pokemon creature with stats and types."""

from move import Move


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

        # Moves (up to 4 attacks)
        self.moves = []

        # XP and evolution system (by Yasmine)
        self.xp = 0
        self.xp_to_next_level = 10 + level * 5
        self.evolution_level = None
        self.evolution_target = None

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

    def gain_xp(self, amount):
        """Add XP and handle level ups.

        Args:
            amount: XP points to add (positive int).
        """
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level_up()

    def level_up(self):
        """Increase level and stats. Called automatically by gain_xp()."""
        self.level += 1
        self.max_hp += 5
        self.attack += 3
        self.defense += 2
        self.hp = self.max_hp
        self.xp_to_next_level = 10 + self.level * 5
        self.try_evolve()

    def try_evolve(self):
        """Evolve this Pokemon if level requirement is met."""
        if self.evolution_level is None or self.evolution_target is None:
            return
        if self.level >= self.evolution_level:
            old_name = self.name
            self.name = self.evolution_target
            self.evolution_level = None
            self.evolution_target = None
            print(f"{old_name} evolved into {self.name}!")

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
            "moves": [m.to_dict() for m in self.moves],
            "xp": self.xp,
            "xp_to_next_level": self.xp_to_next_level,
            "evolution_level": self.evolution_level,
            "evolution_target": self.evolution_target,
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
        pokemon = cls(
            name=data["name"],
            hp=data["hp"],
            level=data.get("level", 5),
            attack=data["attack"],
            defense=data["defense"],
            types=data["types"],
            sprite_path=data.get("sprite_path", ""),
        )
        # Restore moves if present
        moves_data = data.get("moves", [])
        pokemon.moves = [Move.from_dict(m) for m in moves_data]
        # Restore XP fields if present (backward-compatible with old saves)
        pokemon.xp = data.get("xp", 0)
        pokemon.xp_to_next_level = data.get("xp_to_next_level", 10 + pokemon.level * 5)
        pokemon.evolution_level = data.get("evolution_level", None)
        pokemon.evolution_target = data.get("evolution_target", None)
        return pokemon

    def __str__(self):
        """Return a readable string representation.

        POO: __str__ is a MAGIC METHOD (or dunder method). Python calls it
        automatically when you do print(pokemon) or str(pokemon).
        """
        types_str = "/".join(self.types)
        return f"{self.name} (Lv.{self.level}) [{types_str}] HP:{self.hp}/{self.max_hp} XP:{self.xp}/{self.xp_to_next_level}"
