"""Tests for Combat with move as required parameter (D4)."""

from models.pokemon import Pokemon
from models.move import Move
from models.combat import Combat
from models.type_chart import TypeChart


def _make_combat():
    tc = TypeChart()
    tc.load_from_file("data/type_chart.json")
    p1 = Pokemon("Charmander", 39, 5, 52, 43, ["fire"])
    p2 = Pokemon("Bulbasaur", 45, 5, 49, 49, ["grass", "poison"])
    return Combat(p1, p2, tc), p1, p2


def test_get_type_multiplier_with_move():
    combat, p1, p2 = _make_combat()
    fire_move = Move("Ember", "fire", 40, 100)
    mult = combat.get_type_multiplier(p1, p2, fire_move)
    assert mult == 2.0  # fire vs grass


def test_calculate_damage_with_move():
    combat, p1, p2 = _make_combat()
    fire_move = Move("Ember", "fire", 40, 100)
    damage = combat.calculate_damage(p1, p2, fire_move)
    assert damage >= 1


def test_attack_with_move():
    combat, p1, p2 = _make_combat()
    fire_move = Move("Ember", "fire", 40, 100)
    result = combat.attack(p1, p2, fire_move)
    assert "move_name" in result
    assert result["move_name"] == "Ember"
    assert isinstance(result["hit"], bool)
    assert isinstance(result["ko"], bool)
