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
    BASE_XP_REWARD = 20  # XP given to the winner

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

    def get_type_multiplier(self, attacker, defender, move=None):
        """Get the type effectiveness multiplier for an attack.

        If a move is provided, uses the move's type. Otherwise uses
        the attacker's primary type (index 0).

        Args:
            attacker: The attacking Pokemon.
            defender: The defending Pokemon.
            move: Optional Move instance.

        Returns:
            float: Combined type multiplier.
        """
        if move is not None:
            attack_type = move.move_type
        else:
            attack_type = attacker.types[0]
        return self.type_chart.get_combined_multiplier(attack_type, defender.types)

    def calculate_damage(self, attacker, defender, move=None):
        """Calculate damage dealt by attacker to defender.

        If a move is provided, uses a formula that includes level and move power:
            base = ((2 * level / 5 + 2) * power * attack / defense) / 50 + 2
            damage = base * type_multiplier
        Otherwise falls back to the simple formula for backward compatibility.

        Args:
            attacker: The attacking Pokemon.
            defender: The defending Pokemon.
            move: Optional Move instance.

        Returns:
            int: Damage amount (>= 0).
        """
        multiplier = self.get_type_multiplier(attacker, defender, move)
        if multiplier == 0.0:
            return 0

        if move is not None:
            # Damage formula inspired by Pokemon games (simplified)
            level = attacker.level
            power = move.power
            base = ((2 * level / 5 + 2) * power * attacker.attack / defender.defense) / 50 + 2
            raw_damage = int(base * multiplier)
        else:
            raw_damage = int(attacker.attack * multiplier) - defender.defense

        return max(1, raw_damage)

    def attack(self, attacker, defender, move=None):
        """Execute one attack from attacker to defender.

        If a move is provided, uses the move's accuracy for hit/miss check
        and the move's type and power for damage. Otherwise uses the default
        miss chance (10%) and simple formula.

        Args:
            attacker: The attacking Pokemon.
            defender: The defending Pokemon.
            move: Optional Move instance.

        Returns:
            dict: Result with keys:
                - hit (bool): Whether the attack landed.
                - damage (int): Damage dealt (0 if missed).
                - multiplier (float): Type effectiveness multiplier.
                - effective (str): "super", "not_very", "immune", or "normal".
                - ko (bool): Whether the defender fainted.
                - message (str): Human-readable description of the attack.
                - move_name (str): Name of the move used (or "Attack").
        """
        move_name = move.name if move else "Attack"

        # Check for miss using move accuracy or default miss chance
        if move is not None:
            miss = random.randint(1, 100) > move.accuracy
        else:
            miss = random.random() < self.MISS_CHANCE

        if miss:
            message = f"{attacker.name}'s {move_name} missed!"
            result = {
                "hit": False,
                "damage": 0,
                "multiplier": 1.0,
                "effective": "normal",
                "ko": False,
                "message": message,
                "move_name": move_name,
            }
            self.turn_log.append(result)
            return result

        multiplier = self.get_type_multiplier(attacker, defender, move)
        damage = self.calculate_damage(attacker, defender, move)
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
        message = f"{attacker.name} used {move_name}! {damage} damage!"
        if effective == "immune":
            message = f"{attacker.name} used {move_name}... It had no effect!"
        elif effective == "super":
            message += " Super effective!"
        elif effective == "not_very":
            message += " Not very effective..."

        if not defender.is_alive():
            message += f" {defender.name} fainted!"

        result = {
            "hit": True,
            "damage": damage,
            "multiplier": multiplier,
            "effective": effective,
            "ko": not defender.is_alive(),
            "message": message,
            "move_name": move_name,
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

    def award_xp_to_winner(self):
        """Give XP to the winning Pokemon after battle ends.

        Returns:
            str: Message describing XP gained and level up if any.
        """
        winner_name = self.get_winner()
        if winner_name is None:
            return "No winner yet!"

        loser_pokemon = (
            self.opponent_pokemon
            if winner_name == self.player_pokemon.name
            else self.player_pokemon
        )
        winner_pokemon = (
            self.player_pokemon
            if winner_name == self.player_pokemon.name
            else self.opponent_pokemon
        )

        xp_reward = self.BASE_XP_REWARD + loser_pokemon.level * 2
        old_level = winner_pokemon.level
        winner_pokemon.gain_xp(xp_reward)

        message = f"{winner_pokemon.name} gained {xp_reward} XP!"
        if winner_pokemon.level > old_level:
            message += f" {winner_pokemon.name} reached level {winner_pokemon.level}!"
        return message

    def register_to_pokedex(self, pokemon, pokedex):
        """Register a Pokemon in the Pokedex after an encounter.

        Args:
            pokemon: The Pokemon to register.
            pokedex: The Pokedex instance to add the entry to.

        Returns:
            bool: True if the Pokemon was newly added, False if already known.
        """
        return pokedex.add_entry(pokemon)
