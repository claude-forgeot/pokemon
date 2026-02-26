# Audit Dead Code & Bugs -- Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix 12 bugs and remove 5 dead code items identified in the pokemonv1 audit.

**Architecture:** Model-layer changes (Game, Combat) are TDD with pytest. GUI changes (CombatScreen, MenuScreen) are implemented with manual runtime verification. Changes are ordered: dead code first (simplest), then model fixes, then GUI/integration.

**Tech Stack:** Python 3, Pygame, pytest (new)

**Design doc:** `docs/plans/2026-02-26-audit-dead-code-bugs-design.md`

---

### Task 1: Setup pytest infrastructure

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_smoke.py`

**Step 1: Create test infrastructure**

```bash
mkdir -p tests
touch tests/__init__.py
```

Create `tests/conftest.py`:
```python
"""Shared test fixtures for pokemonv1 tests."""

import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

Create `tests/test_smoke.py`:
```python
"""Smoke test to verify test infrastructure works."""

from models.pokemon import Pokemon
from models.move import Move
from models.combat import Combat


def test_pokemon_creation():
    p = Pokemon("Pikachu", 35, 5, 55, 40, ["electric"])
    assert p.name == "Pikachu"
    assert p.hp == 35
    assert p.is_alive()
```

**Step 2: Run smoke test**

Run: `cd /home/jawkah/Documents/Partage-Projets-SyncThing/Etudes/[ACTIF]Projet_Actuel/pokemonv1 && python3 -m pytest tests/test_smoke.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/
git commit -m "test: setup pytest infrastructure with smoke test"
```

---

### Task 2: Dead code removal -- models (D2, D3, D4)

**Files:**
- Modify: `models/pokemon.py:210-217` (remove `__str__`)
- Modify: `models/move.py:63-65` (remove `__str__`)
- Modify: `models/combat.py:36-54,56-86,88-166` (make `move` required)
- Create: `tests/test_combat_move_required.py`

**Step 1: Write test for move-required API**

Create `tests/test_combat_move_required.py`:
```python
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
```

**Step 2: Run test (should pass -- move works today)**

Run: `python3 -m pytest tests/test_combat_move_required.py -v`
Expected: PASS (the current API accepts move, we're just removing the None path)

**Step 3: Remove `Pokemon.__str__()` (D2)**

In `models/pokemon.py`, delete lines 210-217:
```python
    def __str__(self):
        """Return a readable string representation.

        POO: __str__ is a MAGIC METHOD (or dunder method). Python calls it
        automatically when you do print(pokemon) or str(pokemon).
        """
        types_str = "/".join(self.types)
        return f"{self.name} (Lv.{self.level}) [{types_str}] HP:{self.hp}/{self.max_hp} XP:{self.xp}/{self.xp_to_next_level}"
```

**Step 4: Remove `Move.__str__()` (D3)**

In `models/move.py`, delete lines 63-65:
```python
    def __str__(self):
        """Return a readable string representation."""
        return f"{self.name} ({self.move_type}) PWR:{self.power} ACC:{self.accuracy}"
```

**Step 5: Make `move` required in Combat (D4)**

In `models/combat.py`:

`get_type_multiplier()` -- change signature and remove None branch:
```python
    def get_type_multiplier(self, attacker, defender, move):
        """Get the type effectiveness multiplier for an attack.

        Uses the move's type for lookup.

        Args:
            attacker: The attacking Pokemon.
            defender: The defending Pokemon.
            move: Move instance.

        Returns:
            float: Combined type multiplier.
        """
        return self.type_chart.get_combined_multiplier(move.move_type, defender.types)
```

`calculate_damage()` -- change signature and remove else branch:
```python
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
            int: Damage amount (>= 1).
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
```

`attack()` -- change signature and remove else branch for miss:
```python
    def attack(self, attacker, defender, move):
        """Execute one attack from attacker to defender.

        Uses the move's accuracy for hit check and the move's type/power
        for damage.

        Args:
            attacker: The attacking Pokemon.
            defender: The defending Pokemon.
            move: Move instance.

        Returns:
            dict: Result with keys hit, damage, multiplier, effective, ko,
                  message, move_name.
        """
        move_name = move.name

        # Check for miss
        miss = random.randint(1, 100) > move.accuracy

        if miss:
            message = f"{attacker.name}'s {move_name} missed!"
            return {
                "hit": False,
                "damage": 0,
                "multiplier": 1.0,
                "effective": "normal",
                "ko": False,
                "message": message,
                "move_name": move_name,
            }

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

        return {
            "hit": True,
            "damage": damage,
            "multiplier": multiplier,
            "effective": effective,
            "ko": not defender.is_alive(),
            "message": message,
            "move_name": move_name,
        }
```

**Step 6: Run tests**

Run: `python3 -m pytest tests/ -v`
Expected: ALL PASS

**Step 7: Commit**

```bash
git add models/pokemon.py models/move.py models/combat.py tests/test_combat_move_required.py
git commit -m "refactor: remove dead code D2 D3 D4 -- __str__ methods and move=None branches"
```

---

### Task 3: Dead code removal -- GUI (D1, D5)

**Files:**
- Modify: `gui/add_pokemon_screen.py:60,215` (D1: remove success_message)
- Modify: `gui/combat_screen.py:184-188` (D5: remove dead else branch)

**Step 1: Remove `success_message` (D1)**

In `gui/add_pokemon_screen.py`:
- Line 60: delete `self.success_message = ""`
- Line 215: change comment from `# Error / success messages` to `# Error message`

**Step 2: Remove dead "no moves" branch (D5)**

In `gui/combat_screen.py`, lines 183-188, replace:
```python
                if self.attack_button.collidepoint(event.pos):
                    if self.player.moves:
                        self.show_moves = True
                        self._build_move_buttons()
                    else:
                        self._do_player_attack()
```
with:
```python
                if self.attack_button.collidepoint(event.pos):
                    self.show_moves = True
                    self._build_move_buttons()
```

**Step 3: Run existing tests**

Run: `python3 -m pytest tests/ -v`
Expected: ALL PASS (no model changes)

**Step 4: Commit**

```bash
git add gui/add_pokemon_screen.py gui/combat_screen.py
git commit -m "refactor: remove dead code D1 D5 -- success_message and no-moves branch"
```

---

### Task 4: Game model fixes with TDD (B4, B10, B11, B12)

**Files:**
- Modify: `models/game.py` (multiple methods)
- Create: `tests/test_game.py`

**Step 1: Write failing tests**

Create `tests/test_game.py`:
```python
"""Tests for Game model fixes (B4, B10, B11, B12)."""

import os
import json
import tempfile
import shutil

from models.game import Game
from models.pokemon import Pokemon


class TestNewGameReset:
    """B4: new_game() should reset from source, not runtime."""

    def test_new_game_resets_to_source(self, tmp_path, monkeypatch):
        """After modifying runtime, new_game loads original source."""
        # Setup: create source and runtime files
        source = [{"name": "Bulbasaur", "hp": 45, "level": 5,
                    "attack": 49, "defense": 49, "types": ["grass"]}]
        runtime = [{"name": "Bulbasaur", "hp": 45, "level": 20,
                     "attack": 100, "defense": 80, "types": ["grass"]},
                    {"name": "CustomMon", "hp": 50, "level": 5,
                     "attack": 50, "defense": 50, "types": ["normal"]}]

        source_path = str(tmp_path / "pokemon.json")
        runtime_path = str(tmp_path / "pokemon_state.json")
        type_chart_path = "data/type_chart.json"

        with open(source_path, "w") as f:
            json.dump(source, f)
        with open(runtime_path, "w") as f:
            json.dump(runtime, f)

        monkeypatch.setattr(Game, "POKEMON_SOURCE_PATH", source_path)
        monkeypatch.setattr(Game, "POKEMON_RUNTIME_PATH", runtime_path)

        game = Game()
        assert len(game.pokemon_list) == 2  # loaded runtime (2 pokemon)

        game.new_game()
        assert len(game.pokemon_list) == 1  # reset to source (1 pokemon)
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
        assert len(game.get_available_pokemon()) == 1  # no duplicate added

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

        # Verify file format
        with open(runtime_path) as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert "pokemon_list" in data
        assert data["evolution_count"] == 7

        # Reload and verify
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
        # Should return None (nothing to unlock)
        result = game._check_legendary_unlocks()
        assert result is None
```

**Step 2: Run tests (expect failures)**

Run: `python3 -m pytest tests/test_game.py -v`
Expected: FAIL on TestNewGameReset, TestAddPokemonDuplicate, TestEvolutionCountPersistence

**Step 3: Implement B12 -- persist evolution_count**

In `models/game.py`, modify `_save_pokemon()`:
```python
    def _save_pokemon(self):
        """Persist the current Pokemon list and evolution count to runtime state."""
        data = {
            "pokemon_list": [p.to_dict() for p in self.pokemon_list],
            "evolution_count": self.evolution_count,
        }
        FileHandler.save_json(self.POKEMON_RUNTIME_PATH, data)
```

Modify `_load_pokemon()` for backward compat:
```python
    def _load_pokemon(self):
        """Load available Pokemon from runtime state, falling back to source."""
        if FileHandler.file_exists(self.POKEMON_RUNTIME_PATH):
            data = FileHandler.load_json(self.POKEMON_RUNTIME_PATH)
        elif FileHandler.file_exists(self.POKEMON_SOURCE_PATH):
            data = FileHandler.load_json(self.POKEMON_SOURCE_PATH)
        else:
            self.pokemon_list = []
            return
        # Handle both formats: list (legacy) and dict (new)
        if isinstance(data, list):
            self.pokemon_list = [Pokemon.from_dict(p) for p in data]
        else:
            self.pokemon_list = [Pokemon.from_dict(p) for p in data["pokemon_list"]]
            self.evolution_count = data.get("evolution_count", 0)
```

**Step 4: Implement B4 -- new_game() resets from source**

In `models/game.py`, modify `new_game()`:
```python
    def new_game(self):
        """Reset the game state for a fresh start."""
        self.pokedex.reset()
        self.evolution_count = 0
        if FileHandler.file_exists(self.POKEMON_SOURCE_PATH):
            data = FileHandler.load_json(self.POKEMON_SOURCE_PATH)
            self.pokemon_list = [Pokemon.from_dict(p) for p in data]
        else:
            self.pokemon_list = []
        self._save_pokemon()
```

**Step 5: Implement B10 -- duplicate check in add_pokemon()**

In `models/game.py`, modify `add_pokemon()`:
```python
    def add_pokemon(self, pokemon_data):
        """Add a new Pokemon to the available list and persist it.

        Args:
            pokemon_data: Dictionary with Pokemon attributes.

        Returns:
            bool: True if added, False if a Pokemon with this name exists.
        """
        name = pokemon_data.get("name", "").lower()
        for p in self.pokemon_list:
            if p.name.lower() == name:
                return False
        new_pokemon = Pokemon.from_dict(pokemon_data)
        self.pokemon_list.append(new_pokemon)
        self._save_pokemon()
        return True
```

**Step 6: Implement B11 -- early return in legendary check**

In `models/game.py`, modify `_check_legendary_unlocks()`:
```python
    def _check_legendary_unlocks(self):
        """Check if Mewtwo or Mew should be unlocked.

        - Mewtwo: unlocked after 10 evolutions
        - Mew: unlocked when Pokedex is complete (151 entries)

        Returns:
            str or None: Unlock message, or None.
        """
        # Early return if both already unlocked
        mewtwo_locked = False
        mew_locked = False
        for p in self.pokemon_list:
            if p.name.lower() == "mewtwo" and p.locked:
                mewtwo_locked = True
            if p.name.lower() == "mew" and p.locked:
                mew_locked = True
        if not mewtwo_locked and not mew_locked:
            return None

        messages = []

        # Mewtwo: 10 evolutions
        if self.evolution_count >= 10 and mewtwo_locked:
            for p in self.pokemon_list:
                if p.name.lower() == "mewtwo" and p.locked:
                    p.locked = False
                    messages.append("Mewtwo has been unlocked!")

        # Mew: Pokedex complete
        if self.pokedex.get_count() >= 151 and mew_locked:
            for p in self.pokemon_list:
                if p.name.lower() == "mew" and p.locked:
                    p.locked = False
                    messages.append("Mew has been unlocked!")

        if messages:
            self._save_pokemon()
            return " ".join(messages)
        return None
```

**Step 7: Run tests**

Run: `python3 -m pytest tests/test_game.py -v`
Expected: ALL PASS

**Step 8: Commit**

```bash
git add models/game.py tests/test_game.py
git commit -m "fix: B4 B10 B11 B12 -- new_game reset, duplicate check, evolution_count persistence, legendary optimization"
```

---

### Task 5: Game.sync_from_combat() with TDD (B2, B3)

**Files:**
- Modify: `models/game.py` (add `sync_from_combat`)
- Create: `tests/test_sync_from_combat.py`

**Step 1: Write failing test**

Create `tests/test_sync_from_combat.py`:
```python
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

    # Simulate combat copy that gained XP
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
```

**Step 2: Run test (expect FAIL)**

Run: `python3 -m pytest tests/test_sync_from_combat.py -v`
Expected: FAIL -- `AttributeError: 'Game' object has no attribute 'sync_from_combat'`

**Step 3: Implement sync_from_combat()**

In `models/game.py`, add method after `unlock_pokemon()`:
```python
    def sync_from_combat(self, player_team, original_indices):
        """Synchronize combat copies back to the original roster.

        After combat, the copies may have gained XP, levels, evolved, etc.
        This method copies those changes back to the originals and persists.

        Args:
            player_team: List of Pokemon copies used during combat.
            original_indices: List of indices into self.pokemon_list,
                matching each copy to its original.
        """
        for team_idx, orig_idx in enumerate(original_indices):
            copy = player_team[team_idx]
            original = self.pokemon_list[orig_idx]
            original.xp = copy.xp
            original.level = copy.level
            original.xp_to_next_level = copy.xp_to_next_level
            original.max_hp = copy.max_hp
            original.hp = copy.max_hp  # Full heal after combat
            original.attack = copy.attack
            original.defense = copy.defense
            original.name = copy.name
            original.sprite_path = copy.sprite_path
            original.evolution_level = copy.evolution_level
            original.evolution_target = copy.evolution_target
            original.moves = copy.moves
        self._save_pokemon()
```

**Step 4: Run tests**

Run: `python3 -m pytest tests/test_sync_from_combat.py -v`
Expected: ALL PASS

**Step 5: Run all tests**

Run: `python3 -m pytest tests/ -v`
Expected: ALL PASS

**Step 6: Commit**

```bash
git add models/game.py tests/test_sync_from_combat.py
git commit -m "feat: B2 B3 -- Game.sync_from_combat() to persist XP and evolutions"
```

---

### Task 6: CombatScreen fixes (B1, B5, B6, B8)

**Files:**
- Modify: `gui/combat_screen.py`

These changes are GUI-layer and require Pygame. No unit tests -- verified by runtime.

**Step 1: Fix B1 -- add return after non-final KO**

In `gui/combat_screen.py`, method `_do_player_attack()`, after the else block
at line 278, add `return`:
```python
        if result["ko"]:
            self.player_ko_count += 1
            if self._all_fainted(self.opponent_team):
                self.winner = self.player.name
                self._finish_battle()
                self._add_log("You win the battle!")
                return
            else:
                self._next_alive_opponent()
                self._add_log("Your turn!")
                self.phase = "player_turn"
                return
```

Note: the `return` after `_next_alive_opponent()` gives the player their turn
back instead of falling through to opponent attack scheduling.

**Step 2: Add player_ko_count and player_original_indices to __init__**

In `gui/combat_screen.py`, `__init__()`, add new parameter and attributes:
```python
    def __init__(self, game, player_team, opponent_team, player_original_indices=None):
```
And in the body, after `self.xp_message = ""`:
```python
        self.player_ko_count = 0
        self.player_original_indices = player_original_indices or []
```

**Step 3: Fix B6 -- cumulative XP in _finish_battle()**

Rewrite `_finish_battle()`:
```python
    def _finish_battle(self):
        """Mark battle as finished, award cumulative XP for all KOs."""
        self.phase = "finished"

        # B5: forfeit case -- both alive, no XP
        if self.player.is_alive() and self.opponent.is_alive():
            self.xp_message = "You forfeited - no XP gained."
            return

        # B6: award XP for each KO (cumulative)
        winner_name = self.combat.get_winner()
        if winner_name is None:
            self.xp_message = ""
            return

        # Determine winner Pokemon
        if not self.opponent_pokemon_is_loser():
            # Opponent won
            self.xp_message = ""
            return

        # Player won -- award XP for all KOs
        total_xp = 0
        for opp in self.opponent_team:
            if not opp.is_alive():
                total_xp += Combat.BASE_XP_REWARD + opp.level * 2

        if total_xp > 0:
            old_name = self.player.name
            old_level = self.player.level
            self.player.gain_xp(total_xp)

            self.xp_message = f"{self.player.name} gained {total_xp} XP!"
            if self.player.level > old_level:
                self.xp_message += f" Reached level {self.player.level}!"

            # Track evolution
            if self.player.name != old_name:
                unlock_msg = self.game.record_evolution()
                self.game.unlock_pokemon(self.player.name)
                if unlock_msg:
                    self._add_log(unlock_msg)
        else:
            self.xp_message = ""
```

Wait -- the method needs a simpler way to check "did the player win?" since
`combat.get_winner()` only checks the CURRENT pair. Use `self.winner` instead:

```python
    def _finish_battle(self):
        """Mark battle as finished, award cumulative XP for all KOs."""
        self.phase = "finished"

        # B5: forfeit -- both alive, winner already set by forfeit handler
        if self.player.is_alive() and self.opponent.is_alive():
            self.xp_message = "You forfeited - no XP gained."
            return

        # Only award XP if the player won
        if self.winner != self.player.name:
            self.xp_message = ""
            return

        # B6: cumulative XP for all KO'd opponents
        total_xp = 0
        for opp in self.opponent_team:
            if not opp.is_alive():
                total_xp += Combat.BASE_XP_REWARD + opp.level * 2

        if total_xp > 0:
            old_name = self.player.name
            old_level = self.player.level
            self.player.gain_xp(total_xp)

            self.xp_message = f"{self.player.name} gained {total_xp} XP!"
            if self.player.level > old_level:
                self.xp_message += f" Reached level {self.player.level}!"

            # Track evolution (B3)
            if self.player.name != old_name:
                unlock_msg = self.game.record_evolution()
                self.game.unlock_pokemon(self.player.name)
                if unlock_msg:
                    self._add_log(unlock_msg)
        else:
            self.xp_message = ""
```

**Step 4: Fix B8 -- register player Pokemon in Pokedex**

In `gui/combat_screen.py`, method `handle_events()`, at the RESULT transition
(line 140-143), add player_team registration:
```python
                if self.phase == "finished":
                    for p in self.player_team:
                        self.combat.register_to_pokedex(p, self.game.pokedex)
                    for p in self.opponent_team:
                        self.combat.register_to_pokedex(p, self.game.pokedex)
                    return GameState.RESULT
```

**Step 5: Commit**

```bash
git add gui/combat_screen.py
git commit -m "fix: B1 B5 B6 B8 -- combat flow, forfeit XP, cumulative XP, pokedex registration"
```

---

### Task 7: main.py integration (B2, B3, B7)

**Files:**
- Modify: `main.py`

**Step 1: Pass player_original_indices to CombatScreen**

In `main.py`, modify the COMBAT state transition. For team battle:
```python
                if hasattr(current_screen, "selected_indices") and current_screen.selected_indices:
                    player_indices = list(current_screen.selected_indices)
                    for idx in current_screen.selected_indices:
                        p = Pokemon.from_dict(all_pokemon[idx].to_dict())
                        player_team.append(p)
                    # ... opponent team building stays the same ...
```

For solo battle:
```python
                elif hasattr(current_screen, "selected_index") and current_screen.selected_index is not None:
                    player_indices = [current_screen.selected_index]
                    p = all_pokemon[current_screen.selected_index]
                    player_team = [Pokemon.from_dict(p.to_dict())]
```

Pass indices to CombatScreen:
```python
                if player_team and opponent_team:
                    current_screen = CombatScreen(
                        game, player_team, opponent_team, player_indices
                    )
```

**Step 2: Fix B7 -- remove double copy for opponent**

In `main.py`, solo battle path (around line 93), change:
```python
                    opp = Pokemon.from_dict(game.get_random_opponent().to_dict())
```
to:
```python
                    opp = game.get_random_opponent()
```

**Step 3: Call sync_from_combat in RESULT transition**

In `main.py`, RESULT state transition, before `game.save_game()`:
```python
            elif next_state == GameState.RESULT:
                xp_message = ""
                if hasattr(current_screen, "winner"):
                    winner_name = current_screen.winner
                    combat = current_screen.combat
                    loser_name = combat.get_loser()
                    xp_message = getattr(current_screen, "xp_message", "")
                # B2/B3: sync combat copies back to originals
                if hasattr(current_screen, "player_original_indices") and current_screen.player_original_indices:
                    game.sync_from_combat(
                        current_screen.player_team,
                        current_screen.player_original_indices,
                    )
                game.save_game()
```

**Step 4: Run all tests**

Run: `python3 -m pytest tests/ -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add main.py
git commit -m "fix: B2 B3 B7 -- sync XP post-combat, remove double copy"
```

---

### Task 8: UX fixes (B9, B10-GUI)

**Files:**
- Modify: `gui/menu_screen.py` (B9: hide team battle button)
- Modify: `gui/add_pokemon_screen.py` (B10: handle add_pokemon return value)

**Step 1: Hide Team Battle button when < 3 Pokemon (B9)**

In `gui/menu_screen.py`, method `draw()`, wrap the team_battle button drawing
in a condition. Replace the button drawing loop (lines 89-94):
```python
        for key, rect in self.buttons.items():
            if key == "team_battle" and len(self.game.get_available_pokemon()) < 3:
                continue
            color = Constants.BLUE if self.hover_button == key else Constants.DARK_GRAY
            pygame.draw.rect(surface, color, rect, border_radius=Constants.BUTTON_RADIUS)
            label = self.font_button.render(labels[key], True, Constants.WHITE)
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)
```

**Step 2: Handle duplicate check in AddPokemonScreen (B10)**

In `gui/add_pokemon_screen.py`, method `_try_save()`, after validation passes,
update the call to `self.game.add_pokemon()`:
```python
        if not self.game.add_pokemon(pokemon_data):
            self.error_message = "A Pokemon with this name already exists"
            return None
        return GameState.MENU
```

This replaces the current lines 165-166:
```python
        self.game.add_pokemon(pokemon_data)
        return GameState.MENU
```

**Step 3: Run all tests**

Run: `python3 -m pytest tests/ -v`
Expected: ALL PASS

**Step 4: Commit**

```bash
git add gui/menu_screen.py gui/add_pokemon_screen.py
git commit -m "fix: B9 B10 -- hide team battle button, duplicate pokemon check in UI"
```

---

### Task 9: Runtime verification

**Step 1: Launch the game**

Run: `cd /home/jawkah/Documents/Partage-Projets-SyncThing/Etudes/[ACTIF]Projet_Actuel/pokemonv1 && python3 main.py`

**Step 2: Verify checklist**

- [ ] New Game resets to original 151 Pokemon (B4)
- [ ] Add Pokemon rejects duplicate names (B10)
- [ ] Team Battle button hidden if < 3 Pokemon (B9)
- [ ] Solo combat: player attacks, opponent doesn't attack after KO (B1)
- [ ] After winning combat: XP message shows total (not "No winner yet!") (B5, B6)
- [ ] After combat: return to menu, Pokemon has gained XP/levels (B2)
- [ ] Forfeit shows "You forfeited - no XP gained." (B5)
- [ ] Pokedex registers player Pokemon too (B8)

**Step 3: Final commit (if any adjustments needed)**

```bash
git add -A
git commit -m "fix: runtime adjustments from verification"
```
