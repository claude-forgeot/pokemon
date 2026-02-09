"""Combat module -- manages a battle between two Pokemon."""

import random


class Combat:
    """Manages a battle between two Pokemon.

    POO: This class demonstrates COMPOSITION -- it contains Pokemon objects
    and a TypeChart object as attributes, rather than inheriting from them.
    Composition means "has-a" (a Combat HAS two Pokemon), while inheritance
    means "is-a" (a CombatScreen IS-A BaseScreen).

    The 5 methods required by the assignment are:
        1. get_type_multiplier(attacker, defender)
        2. calculate_damage(attacker, defender)
        3. attack(attacker, defender)
        4. get_winner()
        5. get_loser()
    Plus: register_to_pokedex(pokemon, pokedex)
    """

    MISS_CHANCE = 0.1  # 10% chance to miss

    def __init__(self, player_pokemon, opponent_pokemon, type_chart):
        """Create a new Combat instance.

        Args:
            player_pokemon: The player's Pokemon object.
            opponent_pokemon: The opponent's Pokemon object.
            type_chart: A TypeChart instance for effectiveness lookup.
        """
        self.player_pokemon = player_pokemon
        self.opponent_pokemon = opponent_pokemon
        self.type_chart = type_chart
        self.turn_log = []

    def get_type_multiplier(self, attacker, defender):
        """Get the type effectiveness multiplier for an attack.

        Uses the attacker's primary type (index 0) against all of the
        defender's types, combined together.

        Args:
            attacker: The attacking Pokemon.
            defender: The defending Pokemon.

        Returns:
            float: Combined type multiplier.
        """
        attack_type = attacker.types[0]
        return self.type_chart.get_combined_multiplier(attack_type, defender.types)

    def calculate_damage(self, attacker, defender):
        """Calculate damage dealt by attacker to defender.

        Formula: max(1, (attack * type_multiplier) - defense)
        Exception: if type_multiplier is 0 (immunity), damage is 0.

        Args:
            attacker: The attacking Pokemon.
            defender: The defending Pokemon.

        Returns:
            int: Damage amount (>= 0).
        """
        multiplier = self.get_type_multiplier(attacker, defender)
        if multiplier == 0.0:
            return 0
        raw_damage = int(attacker.attack * multiplier) - defender.defense
        return max(1, raw_damage)

    def attack(self, attacker, defender):
        """Execute one attack from attacker to defender.

        Handles miss chance (10%), damage calculation, and HP reduction.

        Args:
            attacker: The attacking Pokemon.
            defender: The defending Pokemon.

        Returns:
            dict: Result with keys:
                - hit (bool): Whether the attack landed.
                - damage (int): Damage dealt (0 if missed).
                - multiplier (float): Type effectiveness multiplier.
                - effective (str): "super", "not_very", "immune", or "normal".
                - ko (bool): Whether the defender fainted.
                - message (str): Human-readable description of the attack.
        """
        # Check for miss
        if random.random() < self.MISS_CHANCE:
            message = f"{attacker.name}'s attack missed!"
            result = {
                "hit": False,
                "damage": 0,
                "multiplier": 1.0,
                "effective": "normal",
                "ko": False,
                "message": message,
            }
            self.turn_log.append(result)
            return result

        multiplier = self.get_type_multiplier(attacker, defender)
        damage = self.calculate_damage(attacker, defender)
        defender.take_damage(damage)

        # Determine effectiveness label
        if multiplier == 0.0:
            effective = "immune"
        elif multiplier >= 2.0:
            effective = "super"
        elif multiplier < 1.0:
            effective = "not_very"
        else:
            effective = "normal"

        # Build message
        message = f"{attacker.name} attacks {defender.name} for {damage} damage!"
        if effective == "immune":
            message = f"{attacker.name} attacks {defender.name}... It had no effect!"
        elif effective == "super":
            message += " It's super effective!"
        elif effective == "not_very":
            message += " It's not very effective..."

        if not defender.is_alive():
            message += f" {defender.name} fainted!"

        result = {
            "hit": True,
            "damage": damage,
            "multiplier": multiplier,
            "effective": effective,
            "ko": not defender.is_alive(),
            "message": message,
        }
        self.turn_log.append(result)
        return result

    def get_winner(self):
        """Return the name of the winning Pokemon, or None if battle continues.

        Returns:
            str or None: Winner's name, or None if both are still alive.
        """
        if not self.opponent_pokemon.is_alive():
            return self.player_pokemon.name
        if not self.player_pokemon.is_alive():
            return self.opponent_pokemon.name
        return None

    def get_loser(self):
        """Return the name of the losing Pokemon, or None if battle continues.

        Returns:
            str or None: Loser's name, or None if both are still alive.
        """
        if not self.opponent_pokemon.is_alive():
            return self.opponent_pokemon.name
        if not self.player_pokemon.is_alive():
            return self.player_pokemon.name
        return None

    def register_to_pokedex(self, pokemon, pokedex):
        """Register a Pokemon in the Pokedex after an encounter.

        Args:
            pokemon: The Pokemon to register.
            pokedex: The Pokedex instance to add the entry to.

        Returns:
            bool: True if the Pokemon was newly added, False if already known.
        """
        return pokedex.add_entry(pokemon)
