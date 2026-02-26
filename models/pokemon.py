"""Pokemon module -- represents a Pokemon creature with stats and types."""

from models.move import Move


class Pokemon:
    """A Pokemon creature with stats and types.

    Example:
        pikachu = Pokemon("Pikachu", 35, 5, 55, 40, ["electric"])
        pikachu.take_damage(10)   # pikachu.hp becomes 25
        pikachu.is_alive()        # returns True
    """

    def __init__(self, name="", hp=20, level=5, attack=10, defense=10,
                 types=None, sprite_path="", data=None):
        """Create a new Pokemon instance.

        Args:
            name: Display name (e.g. "Charizard").
            hp: Hit points (health).
            level: Current level.
            attack: Attack stat.
            defense: Defense stat.
            types: List of type strings (e.g. ["fire", "flying"]).
            sprite_path: Path to the sprite image file.
            data: Optional dict to build from (overrides other args).
        """
        if data is not None:
            name = data.get("name", "Unknown")
            hp = data.get("hp", 20)
            level = data.get("level", 5)
            attack = data.get("attack", 10)
            defense = data.get("defense", 10)
            types = data.get("types", ["normal"])
            sprite_path = data.get("sprite_path", "")

        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.level = level
        self.attack = attack
        self.defense = defense
        self.types = types if types is not None else ["normal"]
        self.sprite_path = sprite_path

        # XP and evolution system
        self.xp = 0
        self.xp_to_next_level = 10 + level * 5
        self.evolution_level = None
        self.evolution_target = None

        # Moves (list of Move objects)
        self.moves = []

        # Locked Pokemon are not available for selection at game start
        self.locked = False

        # If built from data, restore extra fields
        if data is not None:
            self.xp = data.get("xp", 0)
            self.xp_to_next_level = data.get("xp_to_next_level", 10 + self.level * 5)
            self.evolution_level = data.get("evolution_level", None)
            self.evolution_target = data.get("evolution_target", None)
            raw_moves = data.get("moves", [])
            if raw_moves:
                moves = []
                for m in raw_moves:
                    moves.append(Move(data=m))
                self.moves = moves
            if not self.moves:
                self.moves = self.get_default_moves()
            self.locked = data.get("locked", False)

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
        """Increase level and stats. Called automatically by gain_xp()."""
        self.level += 1
        self.max_hp += 5
        self.attack += 3
        self.defense += 2
        self.hp = self.max_hp
        self.xp_to_next_level = 10 + self.level * 5
        self._try_evolve()

    def _try_evolve(self):
        """Evolve this Pokemon if level requirement is met.

        Updates name and sprite path. Stats are kept as-is (accumulated
        from level ups).
        """
        if self.evolution_level is None or self.evolution_target is None:
            return
        if self.level < self.evolution_level:
            return

        self.name = self.evolution_target
        # Derive sprite path from the new name
        self.sprite_path = f"assets/sprites/{self.name.lower()}.png"
        self.evolution_level = None
        self.evolution_target = None

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
        moves_list = []
        for m in self.moves:
            moves_list.append(m.to_dict())
        # Saves max_hp as "hp" -- Pokemon are fully healed on load (by design)
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
            "moves": moves_list,
            "locked": self.locked,
        }
