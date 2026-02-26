"""Pokemon module -- represents a Pokemon creature with stats and types."""

from models.move import Move


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

        # XP and evolution system (by Yasmine, extended)
        self.xp = 0
        self.xp_to_next_level = 10 + level * 5
        self.evolution_level = None
        self.evolution_target = None

        # Moves (list of Move objects)
        self.moves = []

        # Locked Pokemon are not available for selection at game start
        self.locked = False

    def get_default_moves(self):
        """Generate fallback moves if this Pokemon has none.

        Creates Tackle (normal) + a move matching the Pokemon's primary type.

        Returns:
            list[Move]: Default move list.
        """
        defaults = [Move("Tackle", "normal", 40, 100)]
        if self.types and self.types[0] != "normal":
            type_move_name = f"{self.types[0].capitalize()} Attack"
            defaults.append(Move(type_move_name, self.types[0], 50, 100))
        return defaults

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

    def gain_xp(self, amount):
        """Add XP and handle level ups.

        Args:
            amount: XP points to add (positive int).
        """
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self._level_up()

    def _level_up(self):
        """Increase level and stats. Called automatically by gain_xp().

        Returns:
            str or None: Evolution message if the Pokemon evolved, None otherwise.
        """
        self.level += 1
        self.max_hp += 5
        self.attack += 3
        self.defense += 2
        self.hp = self.max_hp
        self.xp_to_next_level = 10 + self.level * 5
        return self._try_evolve()

    def _try_evolve(self):
        """Evolve this Pokemon if level requirement is met.

        Updates name and sprite path. Stats are kept as-is (accumulated
        from level ups).

        Returns:
            str or None: Evolution message if evolved, None otherwise.
        """
        if self.evolution_level is None or self.evolution_target is None:
            return None
        if self.level < self.evolution_level:
            return None

        old_name = self.name
        self.name = self.evolution_target
        # Derive sprite path from the new name
        self.sprite_path = f"assets/sprites/{self.name.lower()}.png"
        self.evolution_level = None
        self.evolution_target = None
        return f"{old_name} evolved into {self.name}!"

    def scale_to_level(self, target_level):
        """Scale this Pokemon's stats to match a target level.

        Adjusts HP, attack, and defense proportionally based on the level
        difference from the Pokemon's current level.

        Args:
            target_level: Desired level.
        """
        if self.level == target_level:
            return
        diff = target_level - self.level
        self.level = target_level
        self.max_hp = max(1, self.max_hp + diff * 5)
        self.attack = max(1, self.attack + diff * 3)
        self.defense = max(1, self.defense + diff * 2)
        self.hp = self.max_hp
        self.xp_to_next_level = 10 + self.level * 5

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
            "xp": self.xp,
            "xp_to_next_level": self.xp_to_next_level,
            "evolution_level": self.evolution_level,
            "evolution_target": self.evolution_target,
            "moves": [m.to_dict() if isinstance(m, Move) else m for m in self.moves],
            "locked": self.locked,
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
            name=data.get("name", "Unknown"),
            hp=data.get("hp", 20),
            level=data.get("level", 5),
            attack=data.get("attack", 10),
            defense=data.get("defense", 10),
            types=data.get("types", ["normal"]),
            sprite_path=data.get("sprite_path", ""),
        )
        # Restore XP fields if present (backward-compatible with old saves)
        pokemon.xp = data.get("xp", 0)
        pokemon.xp_to_next_level = data.get("xp_to_next_level", 10 + pokemon.level * 5)
        pokemon.evolution_level = data.get("evolution_level", None)
        pokemon.evolution_target = data.get("evolution_target", None)
        raw_moves = data.get("moves", [])
        pokemon.moves = [Move.from_dict(m) for m in raw_moves] if raw_moves else []
        # Generate default moves if none (backward compat with old saves)
        if not pokemon.moves:
            pokemon.moves = pokemon.get_default_moves()
        pokemon.locked = data.get("locked", False)
        return pokemon

