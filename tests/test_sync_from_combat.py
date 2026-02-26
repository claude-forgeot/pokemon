"""Tests for Game.sync_from_combat (B2, B3)."""

import json

from models.game import Game
from models.pokemon import Pokemon


def _setup_game(tmp_path, monkeypatch):
    source = [
        {"name": "Charmander", "hp": 39, "level": 5,
         "attack": 52, "defense": 43, "types": ["fire"],
         "evolution_level": 16, "evolution_target": "Charmeleon"},
        {"name": "Squirtle", "hp": 44, "level": 5,
         "attack": 48, "defense": 65, "types": ["water"]},
        {"name": "Charmeleon", "hp": 58, "level": 16,
         "attack": 64, "defense": 58, "types": ["fire"], "locked": True},
    ]
    source_path = str(tmp_path / "pokemon.json")
    runtime_path = str(tmp_path / "pokemon_state.json")

    with open(source_path, "w") as f:
        json.dump(source, f)

    monkeypatch.setattr(Game, "POKEMON_SOURCE_PATH", source_path)
    monkeypatch.setattr(Game, "POKEMON_RUNTIME_PATH", runtime_path)

    return Game()


def test_sync_updates_xp_and_level(tmp_path, monkeypatch):
    game = _setup_game(tmp_path, monkeypatch)
    original = game.pokemon_list[0]
    assert original.xp == 0
    assert original.level == 5

    copy = Pokemon.from_dict(original.to_dict())
    copy.gain_xp(100)

    game.sync_from_combat([copy], [0])

    assert game.pokemon_list[0].xp == copy.xp
    assert game.pokemon_list[0].level == copy.level
    assert game.pokemon_list[0].hp == game.pokemon_list[0].max_hp  # full heal


def test_sync_persists_to_disk(tmp_path, monkeypatch):
    game = _setup_game(tmp_path, monkeypatch)
    copy = Pokemon.from_dict(game.pokemon_list[0].to_dict())
    copy.gain_xp(50)

    game.sync_from_combat([copy], [0])

    runtime_path = str(tmp_path / "pokemon_state.json")
    with open(runtime_path) as f:
        data = json.load(f)
    saved = data["pokemon_list"][0]
    assert saved["xp"] == copy.xp
    assert saved["level"] == copy.level


def test_sync_multiple_pokemon(tmp_path, monkeypatch):
    game = _setup_game(tmp_path, monkeypatch)
    copy0 = Pokemon.from_dict(game.pokemon_list[0].to_dict())
    copy1 = Pokemon.from_dict(game.pokemon_list[1].to_dict())
    copy0.gain_xp(30)
    copy1.gain_xp(50)

    game.sync_from_combat([copy0, copy1], [0, 1])

    assert game.pokemon_list[0].xp == copy0.xp
    assert game.pokemon_list[1].xp == copy1.xp
