"""Tests for the TypeChart class."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from type_chart import TypeChart


def make_chart():
    """Create a TypeChart loaded from the local file."""
    tc = TypeChart()
    tc.load_from_file("data/type_chart.json")
    return tc


def test_fire_vs_grass():
    """Fire is super effective against Grass (2.0x)."""
    tc = make_chart()
    assert tc.get_multiplier("fire", "grass") == 2.0


def test_water_vs_fire():
    """Water is super effective against Fire (2.0x)."""
    tc = make_chart()
    assert tc.get_multiplier("water", "fire") == 2.0


def test_grass_vs_water():
    """Grass is super effective against Water (2.0x)."""
    tc = make_chart()
    assert tc.get_multiplier("grass", "water") == 2.0


def test_fire_vs_water():
    """Fire is not very effective against Water (0.5x)."""
    tc = make_chart()
    assert tc.get_multiplier("fire", "water") == 0.5


def test_normal_vs_ghost():
    """Normal cannot hit Ghost (0.0x immunity)."""
    tc = make_chart()
    assert tc.get_multiplier("normal", "ghost") == 0.0


def test_electric_vs_ground():
    """Electric cannot hit Ground (0.0x immunity)."""
    tc = make_chart()
    assert tc.get_multiplier("electric", "ground") == 0.0


def test_neutral_matchup():
    """Normal vs Normal is 1.0x."""
    tc = make_chart()
    assert tc.get_multiplier("normal", "normal") == 1.0


def test_combined_multiplier_dual_type():
    """Fire vs Grass/Ice = 2.0 * 2.0 = 4.0."""
    tc = make_chart()
    result = tc.get_combined_multiplier("fire", ["grass", "ice"])
    assert result == 4.0


def test_combined_multiplier_single_type():
    """Single type returns the simple multiplier."""
    tc = make_chart()
    result = tc.get_combined_multiplier("fire", ["grass"])
    assert result == 2.0


def test_unknown_type_defaults_to_neutral():
    """Unknown types default to 1.0x."""
    tc = make_chart()
    assert tc.get_multiplier("fire", "unknown_type") == 1.0
    assert tc.get_multiplier("unknown_type", "fire") == 1.0


def test_case_insensitive():
    """Type names are case-insensitive."""
    tc = make_chart()
    assert tc.get_multiplier("Fire", "Grass") == 2.0
    assert tc.get_multiplier("WATER", "fire") == 2.0


def test_18_types_defined():
    """TypeChart.TYPES has exactly 18 entries."""
    assert len(TypeChart.TYPES) == 18


def test_save_and_load(tmp_path):
    """TypeChart can be saved and loaded from a file."""
    tc = make_chart()
    save_path = str(tmp_path / "tc.json")
    tc.save_to_file(save_path)

    tc2 = TypeChart()
    tc2.load_from_file(save_path)
    assert tc2.get_multiplier("fire", "grass") == 2.0
