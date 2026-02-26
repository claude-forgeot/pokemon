"""Tests for Game model fixes (B4, B10, B11, B12)."""

import json

from models.game import Game
from models.pokemon import Pokemon


class TestNewGameReset:
    """B4: new_game() should reset from source, not runtime."""

    def test_new_game_resets_to_source(self, tmp_path, monkeypatch):
        source = [{"name": "Bulbasaur", "hp": 45, "level": 5,
                    "attack": 49, "defense": 49, "types": ["grass"]}]
        runtime = [{"name": "Bulbasaur", "hp": 45, "level": 20,
                     "attack": 100, "defense": 80, "types": ["grass"]},
                    {"name": "CustomMon", "hp": 50, "level": 5,
                     "attack": 50, "defense": 50, "types": ["normal"]}]

        source_path = str(tmp_path / "pokemon.json")
        runtime_path = str(tmp_path / "pokemon_state.json")

        with open(source_path, "w") as f:
            json.dump(source, f)
        with open(runtime_path, "w") as f:
            json.dump(runtime, f)

        monkeypatch.setattr(Game, "POKEMON_SOURCE_PATH", source_path)
        monkeypatch.setattr(Game, "POKEMON_RUNTIME_PATH", runtime_path)

        game = Game()
        assert len(game.pokemon_list) == 2

        game.new_game()
        assert len(game.pokemon_list) == 1
        assert game.pokemon_list[0].name == "Bulbasaur"
        assert game.pokemon_list[0].level == 5


class TestAddPokemonDuplicate:
    """B10: add_pokemon should reject duplicates."""

    def test_add_duplicate_returns_false(self, tmp_path, monkeypatch):
        source = [{"name": "Pikachu", "hp": 35, "level": 5,
                    "attack": 55, "defense": 40, "types": ["electric"]}]
        source_path = str(tmp_path / "pokemon.json")
        runtime_path = str(tmp_path / "pokemon_state.json")

        with open(source_path, "w") as f:
            json.dump(source, f)

        monkeypatch.setattr(Game, "POKEMON_SOURCE_PATH", source_path)
        monkeypatch.setattr(Game, "POKEMON_RUNTIME_PATH", runtime_path)

        game = Game()
        result = game.add_pokemon({"name": "Pikachu", "hp": 35, "level": 5,
                                    "attack": 55, "defense": 40,
                                    "types": ["electric"]})
        assert result is False
        assert len(game.get_available_pokemon()) == 1

    def test_add_unique_returns_true(self, tmp_path, monkeypatch):
        source = [{"name": "Pikachu", "hp": 35, "level": 5,
                    "attack": 55, "defense": 40, "types": ["electric"]}]
        source_path = str(tmp_path / "pokemon.json")
        runtime_path = str(tmp_path / "pokemon_state.json")

        with open(source_path, "w") as f:
            json.dump(source, f)

        monkeypatch.setattr(Game, "POKEMON_SOURCE_PATH", source_path)
        monkeypatch.setattr(Game, "POKEMON_RUNTIME_PATH", runtime_path)

        game = Game()
        result = game.add_pokemon({"name": "Charmander", "hp": 39, "level": 5,
                                    "attack": 52, "defense": 43,
                                    "types": ["fire"]})
        assert result is True
        assert len(game.get_available_pokemon()) == 2


class TestEvolutionCountPersistence:
    """B12: evolution_count should be persisted in pokemon_state.json."""

    def test_evolution_count_saved_and_loaded(self, tmp_path, monkeypatch):
        source = [{"name": "Charmander", "hp": 39, "level": 5,
                    "attack": 52, "defense": 43, "types": ["fire"]}]
        source_path = str(tmp_path / "pokemon.json")
        runtime_path = str(tmp_path / "pokemon_state.json")

        with open(source_path, "w") as f:
            json.dump(source, f)

        monkeypatch.setattr(Game, "POKEMON_SOURCE_PATH", source_path)
        monkeypatch.setattr(Game, "POKEMON_RUNTIME_PATH", runtime_path)

        game = Game()
        game.evolution_count = 7
        game._save_pokemon()

        with open(runtime_path) as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert "pokemon_list" in data
        assert data["evolution_count"] == 7

        game2 = Game()
        assert game2.evolution_count == 7


class TestLegendaryUnlockOptimization:
    """B11: _check_legendary_unlocks should early-return if already unlocked."""

    def test_already_unlocked_skips_scan(self, tmp_path, monkeypatch):
        source = [
            {"name": "Mewtwo", "hp": 106, "level": 70, "attack": 110,
             "defense": 90, "types": ["psychic"], "locked": False},
            {"name": "Mew", "hp": 100, "level": 100, "attack": 100,
             "defense": 100, "types": ["psychic"], "locked": False},
        ]
        source_path = str(tmp_path / "pokemon.json")
        runtime_path = str(tmp_path / "pokemon_state.json")

        with open(source_path, "w") as f:
            json.dump(source, f)

        monkeypatch.setattr(Game, "POKEMON_SOURCE_PATH", source_path)
        monkeypatch.setattr(Game, "POKEMON_RUNTIME_PATH", runtime_path)

        game = Game()
        game.evolution_count = 50
        result = game._check_legendary_unlocks()
        assert result is None
