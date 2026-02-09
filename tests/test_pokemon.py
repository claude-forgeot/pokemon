"""Tests for the Pokemon class."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pokemon import Pokemon


def test_creation():
    """Pokemon is created with correct attributes."""
    p = Pokemon("Pikachu", 35, 5, 55, 40, ["electric"])
    assert p.name == "Pikachu"
    assert p.hp == 35
    assert p.max_hp == 35
    assert p.level == 5
    assert p.attack == 55
    assert p.defense == 40
    assert p.types == ["electric"]


def test_take_damage():
    """take_damage reduces HP correctly, floored at 0."""
    p = Pokemon("Pikachu", 35, 5, 55, 40, ["electric"])
    p.take_damage(10)
    assert p.hp == 25
    p.take_damage(100)
    assert p.hp == 0


def test_is_alive():
    """is_alive returns True when HP > 0, False at 0."""
    p = Pokemon("Pikachu", 35, 5, 55, 40, ["electric"])
    assert p.is_alive() is True
    p.take_damage(35)
    assert p.is_alive() is False


def test_heal():
    """heal restores HP to max_hp."""
    p = Pokemon("Pikachu", 35, 5, 55, 40, ["electric"])
    p.take_damage(20)
    assert p.hp == 15
    p.heal()
    assert p.hp == 35


def test_to_dict():
    """to_dict produces a serializable dictionary."""
    p = Pokemon("Charizard", 78, 5, 84, 78, ["fire", "flying"], "sprites/charizard.png")
    d = p.to_dict()
    assert d["name"] == "Charizard"
    assert d["hp"] == 78
    assert d["types"] == ["fire", "flying"]
    assert d["sprite_path"] == "sprites/charizard.png"


def test_from_dict():
    """from_dict creates a Pokemon from a dictionary."""
    data = {
        "name": "Blastoise",
        "hp": 79,
        "level": 5,
        "attack": 83,
        "defense": 100,
        "types": ["water"],
    }
    p = Pokemon.from_dict(data)
    assert p.name == "Blastoise"
    assert p.hp == 79
    assert p.max_hp == 79
    assert p.types == ["water"]


def test_from_dict_default_level():
    """from_dict uses default level 5 if not provided."""
    data = {"name": "Test", "hp": 50, "attack": 50, "defense": 50, "types": ["normal"]}
    p = Pokemon.from_dict(data)
    assert p.level == 5


def test_str():
    """__str__ returns a readable string."""
    p = Pokemon("Pikachu", 35, 5, 55, 40, ["electric"])
    result = str(p)
    assert "Pikachu" in result
    assert "electric" in result
    assert "35/35" in result


def test_roundtrip_serialization():
    """to_dict -> from_dict preserves all data."""
    original = Pokemon("Gengar", 60, 10, 65, 60, ["ghost", "poison"], "sprite.png")
    data = original.to_dict()
    restored = Pokemon.from_dict(data)
    assert restored.name == original.name
    assert restored.max_hp == original.max_hp
    assert restored.attack == original.attack
    assert restored.defense == original.defense
    assert restored.types == original.types
