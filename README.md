# Pokemon Battle

A Pokemon battle game built with Python and Pygame. Includes type effectiveness, a Pokedex system, and custom Pokemon creation.

## Setup

```bash
# Create virtual environment
py -m venv .venv

# Activate (Windows / Git Bash)
source .venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Populate Pokemon data from PokeAPI
py scripts/populate_pokemon.py

# Run the game
py main.py

# Run tests
py -m pytest tests/ -v
```

## How to Play

1. **Start Battle** -- Select a Pokemon from your roster, then battle a random opponent. Click "Attack!" to deal damage. Type effectiveness applies (fire > grass > water > fire).
2. **Add Pokemon** -- Create a custom Pokemon by entering a name, stats, and selecting up to 2 types.
3. **Pokedex** -- View all Pokemon you have encountered in battles. Duplicates are automatically prevented.

## Project Structure

```
pokemonv1/
  main.py               -- Entry point (Pygame loop + state machine)
  game_state.py          -- GameState enum
  pokemon.py             -- Pokemon class
  combat.py              -- Combat class (5 required methods)
  pokedex.py             -- Pokedex class (persistence + anti-duplicate)
  type_chart.py          -- TypeChart class (18 types)
  game.py                -- Game class (orchestrator)
  gui/
    constants.py         -- Constants class (colors, dimensions)
    base_screen.py       -- BaseScreen abstract class
    menu_screen.py       -- MenuScreen
    selection_screen.py  -- SelectionScreen
    combat_screen.py     -- CombatScreen
    result_screen.py     -- ResultScreen
    pokedex_screen.py    -- PokedexScreen
    add_pokemon_screen.py -- AddPokemonScreen
  utils/
    file_handler.py      -- FileHandler (JSON I/O)
    api_client.py        -- ApiClient (PokeAPI)
  data/
    pokemon.json         -- Available Pokemon (generated)
    pokedex.json         -- Encountered Pokemon (runtime)
    type_chart.json      -- 18x18 type effectiveness table
    default_pokemon.json -- Fallback if PokeAPI unavailable
  scripts/
    populate_pokemon.py  -- Fetch data from PokeAPI
  tests/                 -- Unit tests (pytest)
```

## Class Diagram

```mermaid
classDiagram
    class GameState {
        <<enum>>
        MENU
        SELECTION
        COMBAT
        RESULT
        POKEDEX
        ADD_POKEMON
        QUIT
    }

    class Pokemon {
        +name: str
        +hp: int
        +max_hp: int
        +level: int
        +attack: int
        +defense: int
        +types: list
        +sprite_path: str
        +take_damage(amount)
        +is_alive() bool
        +heal()
        +to_dict() dict
        +from_dict(data) Pokemon
    }

    class Combat {
        +player_pokemon: Pokemon
        +opponent_pokemon: Pokemon
        +type_chart: TypeChart
        +turn_log: list
        +get_type_multiplier(atk, def) float
        +calculate_damage(atk, def) int
        +attack(atk, def) dict
        +get_winner() str
        +get_loser() str
        +register_to_pokedex(pokemon, pokedex) bool
    }

    class Pokedex {
        -_entries: list
        +file_path: str
        +add_entry(pokemon) bool
        +get_all_entries() list
        +get_count() int
        +save()
        +load()
        +reset()
    }

    class TypeChart {
        +TYPES: list
        +chart: dict
        +get_multiplier(atk_type, def_type) float
        +get_combined_multiplier(atk_type, def_types) float
        +load_from_api(api_client)
        +load_from_file(path)
        +save_to_file(path)
    }

    class Game {
        +type_chart: TypeChart
        +pokedex: Pokedex
        +pokemon_list: list
        +new_game()
        +get_random_opponent() Pokemon
        +add_pokemon(data)
        +get_available_pokemon() list
    }

    class BaseScreen {
        <<abstract>>
        +game: Game
        +handle_events(events)*
        +update()*
        +draw(surface)*
    }

    class MenuScreen { }
    class SelectionScreen { }
    class CombatScreen { }
    class ResultScreen { }
    class PokedexScreen { }
    class AddPokemonScreen { }

    class FileHandler {
        +load_json(path)$ dict
        +save_json(path, data)$
        +file_exists(path)$ bool
        +create_backup(path)$ str
    }

    class ApiClient {
        +BASE_URL: str
        +cache_dir: str
        +fetch_pokemon(name_or_id) dict
        +fetch_type_data(type_name) dict
        +download_sprite(url, path) str
        +fetch_pokemon_list(limit) list
    }

    class Constants {
        +SCREEN_WIDTH: int
        +SCREEN_HEIGHT: int
        +FPS: int
        +TYPE_COLORS: dict
    }

    Game *-- TypeChart
    Game *-- Pokedex
    Game o-- Pokemon
    Combat o-- Pokemon
    Combat o-- TypeChart
    Pokedex ..> FileHandler
    BaseScreen <|-- MenuScreen
    BaseScreen <|-- SelectionScreen
    BaseScreen <|-- CombatScreen
    BaseScreen <|-- ResultScreen
    BaseScreen <|-- PokedexScreen
    BaseScreen <|-- AddPokemonScreen
    CombatScreen o-- Combat
```

## Combat Mechanics

- **Turn order**: Player attacks first, then opponent
- **Type effectiveness**: Official Pokemon 18-type chart (fire > grass > water > fire, etc.)
- **Dual type defense**: Multipliers combine (fire vs grass/ice = 4.0x)
- **Damage formula**: `max(1, attack * type_multiplier - defense)`
- **Miss rate**: 10% fixed chance
- **Immunity**: 0x multiplier = 0 damage ("It had no effect!")

## Technologies

- Python 3.10+
- Pygame 2.5+
- PokeAPI (initial data population)
- pytest (testing)
