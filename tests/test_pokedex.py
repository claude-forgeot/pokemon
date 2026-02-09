"""Tests for the Pokedex class."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pokemon import Pokemon
from pokedex import Pokedex


def test_add_entry(tmp_path):
    """Adding a Pokemon creates an entry."""
    pdex = Pokedex(file_path=str(tmp_path / "pokedex.json"))
    p = Pokemon("Pikachu", 35, 5, 55, 40, ["electric"])
    assert pdex.add_entry(p) is True
    assert pdex.get_count() == 1


def test_duplicate_rejected(tmp_path):
    """Adding the same Pokemon twice is rejected."""
    pdex = Pokedex(file_path=str(tmp_path / "pokedex.json"))
    p = Pokemon("Pikachu", 35, 5, 55, 40, ["electric"])
    pdex.add_entry(p)
    assert pdex.add_entry(p) is False
    assert pdex.get_count() == 1


def test_duplicate_case_insensitive(tmp_path):
    """Duplicate check is case-insensitive."""
    pdex = Pokedex(file_path=str(tmp_path / "pokedex.json"))
    p1 = Pokemon("Pikachu", 35, 5, 55, 40, ["electric"])
    p2 = Pokemon("pikachu", 35, 5, 55, 40, ["electric"])
    pdex.add_entry(p1)
    assert pdex.add_entry(p2) is False


def test_get_all_entries(tmp_path):
    """get_all_entries returns a list of dictionaries."""
    pdex = Pokedex(file_path=str(tmp_path / "pokedex.json"))
    p1 = Pokemon("Pikachu", 35, 5, 55, 40, ["electric"])
    p2 = Pokemon("Charizard", 78, 5, 84, 78, ["fire", "flying"])
    pdex.add_entry(p1)
    pdex.add_entry(p2)
    entries = pdex.get_all_entries()
    assert len(entries) == 2
    assert entries[0]["name"] == "Pikachu"
    assert entries[1]["name"] == "Charizard"


def test_persistence(tmp_path):
    """Pokedex persists between instances."""
    path = str(tmp_path / "pokedex.json")
    pdex1 = Pokedex(file_path=path)
    pdex1.add_entry(Pokemon("Pikachu", 35, 5, 55, 40, ["electric"]))
    pdex1.add_entry(Pokemon("Charizard", 78, 5, 84, 78, ["fire", "flying"]))

    # Create a new instance from the same file
    pdex2 = Pokedex(file_path=path)
    assert pdex2.get_count() == 2
    assert pdex2.get_all_entries()[0]["name"] == "Pikachu"


def test_reset(tmp_path):
    """reset clears all entries."""
    pdex = Pokedex(file_path=str(tmp_path / "pokedex.json"))
    pdex.add_entry(Pokemon("Pikachu", 35, 5, 55, 40, ["electric"]))
    assert pdex.get_count() == 1
    pdex.reset()
    assert pdex.get_count() == 0


def test_empty_on_missing_file(tmp_path):
    """Pokedex starts empty if file does not exist."""
    pdex = Pokedex(file_path=str(tmp_path / "nonexistent.json"))
    assert pdex.get_count() == 0


def test_corrupted_file_backup(tmp_path):
    """Corrupted file is backed up and Pokedex resets."""
    path = tmp_path / "pokedex.json"
    path.write_text("{invalid json", encoding="utf-8")
    pdex = Pokedex(file_path=str(path))
    assert pdex.get_count() == 0
    # Backup should exist
    backups = list(tmp_path.glob("*_backup_*"))
    assert len(backups) == 1
