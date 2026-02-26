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
    def get_type_multiplier(self, attacker, defender, move):
        """Get the type effectiveness multiplier for an attack.

        Args:
            attacker: The attacking Pokemon.
            defender: The defending Pokemon.
            move: Move instance.

        Returns:
            float: Combined type multiplier.
        """
        return self.type_chart.get_combined_multiplier(move.move_type, defender.types)

    def calculate_damage(self, attacker, defender, move, multiplier=None):
        """Calculate damage dealt by attacker to defender.

        Uses a Pokemon-like formula:
            base = ((2 * level / 5 + 2) * power * attack / defense) / 50 + 2
            damage = int(base * type_multiplier)

        Args:
            attacker: The attacking Pokemon.
            defender: The defending Pokemon.
            move: Move instance.
            multiplier: Pre-computed type multiplier (avoids redundant lookup).

        Returns:
            int: Damage amount (>= 0).
        """
        if multiplier is None:
            multiplier = self.get_type_multiplier(attacker, defender, move)
        if multiplier == 0.0:
            return 0

        level = attacker.level
        power = move.power
        base = ((2 * level / 5 + 2) * power * attacker.attack / defender.defense) / 50 + 2
        raw_damage = int(base * multiplier)

        return max(1, raw_damage)

    def attack(self, attacker, defender, move):
        """Execute one attack from attacker to defender.

        Uses the move's accuracy for hit check and the move's type/power for damage.

        Args:
            attacker: The attacking Pokemon.
            defender: The defending Pokemon.
            move: Move instance.

        Returns:
            dict: Result with keys:
                - hit (bool): Whether the attack landed.
                - damage (int): Damage dealt (0 if missed).
                - multiplier (float): Type effectiveness multiplier.
                - effective (str): "super", "not_very", "immune", or "normal".
                - ko (bool): Whether the defender fainted.
                - message (str): Human-readable description of the attack.
                - move_name (str): Name of the move used.
        """
        move_name = move.name

        # Check for miss
        miss = random.randint(1, 100) > move.accuracy

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
            return result

        multiplier = self.get_type_multiplier(attacker, defender, move)
        damage = self.calculate_damage(attacker, defender, move, multiplier=multiplier)
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
            message = f"{attacker.name} used {move_name}... No effect!"
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

        NOTE: This method is part of the 5 required methods for the assignment.
        CombatScreen._finish_battle() uses cumulative XP calculation instead,
        but this method is kept for API completeness.

        Returns:
            str: Message describing XP gained and level up if any.
        """
        winner_name = self.get_winner()
        if winner_name is None:
            return "No winner yet!"

        if not self.opponent_pokemon.is_alive():
            winner_pokemon = self.player_pokemon
            loser_pokemon = self.opponent_pokemon
        else:
            winner_pokemon = self.opponent_pokemon
            loser_pokemon = self.player_pokemon

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
