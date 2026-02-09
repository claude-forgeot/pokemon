"""Tests for the Combat class."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch
from pokemon import Pokemon
from combat import Combat
from type_chart import TypeChart
from pokedex import Pokedex


def make_type_chart():
    """Create a TypeChart with known test values."""
    tc = TypeChart()
    tc.chart = {
        "fire": {"fire": 0.5, "water": 0.5, "grass": 2.0, "normal": 1.0, "ghost": 1.0},
        "water": {"fire": 2.0, "water": 0.5, "grass": 0.5, "normal": 1.0, "ghost": 1.0},
        "grass": {"fire": 0.5, "water": 2.0, "grass": 0.5, "normal": 1.0, "ghost": 1.0},
        "normal": {"fire": 1.0, "water": 1.0, "grass": 1.0, "normal": 1.0, "ghost": 0.0},
        "ghost": {"fire": 1.0, "water": 1.0, "grass": 1.0, "normal": 0.0, "ghost": 2.0},
    }
    return tc


def test_get_type_multiplier_super_effective():
    """Fire vs Grass is 2.0x."""
    tc = make_type_chart()
    fire_poke = Pokemon("Charmander", 39, 5, 52, 43, ["fire"])
    grass_poke = Pokemon("Bulbasaur", 45, 5, 49, 49, ["grass"])
    combat = Combat(fire_poke, grass_poke, tc)
    assert combat.get_type_multiplier(fire_poke, grass_poke) == 2.0


def test_get_type_multiplier_not_very_effective():
    """Water vs Grass is 0.5x."""
    tc = make_type_chart()
    water_poke = Pokemon("Squirtle", 44, 5, 48, 65, ["water"])
    grass_poke = Pokemon("Bulbasaur", 45, 5, 49, 49, ["grass"])
    combat = Combat(water_poke, grass_poke, tc)
    assert combat.get_type_multiplier(water_poke, grass_poke) == 0.5


def test_get_type_multiplier_immune():
    """Normal vs Ghost is 0.0x (immunity)."""
    tc = make_type_chart()
    normal_poke = Pokemon("Rattata", 30, 5, 56, 35, ["normal"])
    ghost_poke = Pokemon("Gastly", 30, 5, 35, 30, ["ghost"])
    combat = Combat(normal_poke, ghost_poke, tc)
    assert combat.get_type_multiplier(normal_poke, ghost_poke) == 0.0


def test_calculate_damage_normal():
    """Normal damage: max(1, attack * 1.0 - defense)."""
    tc = make_type_chart()
    attacker = Pokemon("A", 50, 5, 60, 40, ["fire"])
    defender = Pokemon("B", 50, 5, 40, 30, ["normal"])
    combat = Combat(attacker, defender, tc)
    # fire vs normal = 1.0, so damage = max(1, 60*1.0 - 30) = 30
    assert combat.calculate_damage(attacker, defender) == 30


def test_calculate_damage_super_effective():
    """Super effective: fire vs grass = 2.0x."""
    tc = make_type_chart()
    attacker = Pokemon("A", 50, 5, 60, 40, ["fire"])
    defender = Pokemon("B", 50, 5, 40, 30, ["grass"])
    combat = Combat(attacker, defender, tc)
    # damage = max(1, 60*2.0 - 30) = 90
    assert combat.calculate_damage(attacker, defender) == 90


def test_calculate_damage_immune():
    """Immunity: normal vs ghost = 0 damage."""
    tc = make_type_chart()
    attacker = Pokemon("A", 50, 5, 60, 40, ["normal"])
    defender = Pokemon("B", 50, 5, 40, 30, ["ghost"])
    combat = Combat(attacker, defender, tc)
    assert combat.calculate_damage(attacker, defender) == 0


def test_calculate_damage_minimum_one():
    """Damage is at least 1 when multiplier > 0 even if defense > attack."""
    tc = make_type_chart()
    attacker = Pokemon("A", 50, 5, 10, 40, ["fire"])
    defender = Pokemon("B", 50, 5, 40, 200, ["normal"])
    combat = Combat(attacker, defender, tc)
    # fire vs normal = 1.0, damage = max(1, 10*1.0 - 200) = max(1, -190) = 1
    assert combat.calculate_damage(attacker, defender) == 1


@patch("combat.random.random", return_value=0.05)
def test_attack_miss(mock_random):
    """Attack misses when random < MISS_CHANCE."""
    tc = make_type_chart()
    attacker = Pokemon("A", 50, 5, 60, 40, ["fire"])
    defender = Pokemon("B", 50, 5, 40, 30, ["grass"])
    combat = Combat(attacker, defender, tc)
    result = combat.attack(attacker, defender)
    assert result["hit"] is False
    assert result["damage"] == 0
    assert defender.hp == 50  # no damage taken


@patch("combat.random.random", return_value=0.5)
def test_attack_hit(mock_random):
    """Attack hits and deals correct damage."""
    tc = make_type_chart()
    attacker = Pokemon("A", 50, 5, 60, 40, ["fire"])
    defender = Pokemon("B", 50, 5, 40, 30, ["grass"])
    combat = Combat(attacker, defender, tc)
    result = combat.attack(attacker, defender)
    assert result["hit"] is True
    assert result["damage"] == 90  # 60*2.0 - 30
    assert result["effective"] == "super"
    assert defender.hp == 0  # 50 - 90, floored at 0
    assert result["ko"] is True


def test_get_winner_none():
    """No winner when both are alive."""
    tc = make_type_chart()
    p1 = Pokemon("A", 50, 5, 60, 40, ["fire"])
    p2 = Pokemon("B", 50, 5, 40, 30, ["water"])
    combat = Combat(p1, p2, tc)
    assert combat.get_winner() is None


def test_get_winner_player():
    """Player wins when opponent faints."""
    tc = make_type_chart()
    p1 = Pokemon("A", 50, 5, 60, 40, ["fire"])
    p2 = Pokemon("B", 50, 5, 40, 30, ["water"])
    combat = Combat(p1, p2, tc)
    p2.take_damage(50)
    assert combat.get_winner() == "A"
    assert combat.get_loser() == "B"


def test_get_winner_opponent():
    """Opponent wins when player faints."""
    tc = make_type_chart()
    p1 = Pokemon("A", 50, 5, 60, 40, ["fire"])
    p2 = Pokemon("B", 50, 5, 40, 30, ["water"])
    combat = Combat(p1, p2, tc)
    p1.take_damage(50)
    assert combat.get_winner() == "B"
    assert combat.get_loser() == "A"


def test_register_to_pokedex(tmp_path):
    """register_to_pokedex adds Pokemon to pokedex."""
    tc = make_type_chart()
    p1 = Pokemon("A", 50, 5, 60, 40, ["fire"])
    p2 = Pokemon("B", 50, 5, 40, 30, ["water"])
    combat = Combat(p1, p2, tc)
    pokedex = Pokedex(file_path=str(tmp_path / "pokedex.json"))
    assert combat.register_to_pokedex(p2, pokedex) is True
    assert combat.register_to_pokedex(p2, pokedex) is False  # duplicate


def test_turn_log():
    """Turn log accumulates attack results."""
    tc = make_type_chart()
    p1 = Pokemon("A", 100, 5, 60, 40, ["fire"])
    p2 = Pokemon("B", 100, 5, 40, 30, ["water"])
    combat = Combat(p1, p2, tc)
    with patch("combat.random.random", return_value=0.5):
        combat.attack(p1, p2)
        combat.attack(p2, p1)
    assert len(combat.turn_log) == 2
