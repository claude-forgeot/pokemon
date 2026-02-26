"""Smoke test to verify test infrastructure works."""

from models.pokemon import Pokemon
from models.move import Move
from models.combat import Combat


def test_pokemon_creation():
    p = Pokemon("Pikachu", 35, 5, 55, 40, ["electric"])
    assert p.name == "Pikachu"
    assert p.hp == 35
    assert p.is_alive()
