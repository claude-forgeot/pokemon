# Pokemon Battle

A Pokemon battle game built with Python and Pygame. Features all 151 Gen 1 Pokemon with authentic sprites, custom backgrounds, move-based combat, XP/evolution system, team battles, and save/load functionality.

## Quick Start

```bash
# Linux / Mac
./run.sh

# Windows
run.bat
```

The script creates a virtual environment, installs dependencies, and launches the game.

**Manual setup** (if the script doesn't work):
```bash
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate.bat     # Windows
pip install -r requirements.txt
python3 main.py
```

## How to Play

1. **Team Battle** -- Select 6 Pokemon from the roster (92 available, locked ones shown in grey). Battle a random opponent team.
2. **Combat** -- Choose from 4 moves per Pokemon. Type effectiveness applies (fire > grass > water > fire). When a Pokemon faints, pick your next one.
3. **XP & Evolution** -- Win battles to earn XP. Level up to evolve your Pokemon. Evolved forms get unlocked.
4. **Save/Load** -- Game saves automatically after each battle. Load previous saves from the menu.
5. **Pokedex** -- Track all Pokemon you have encountered.
6. **Unlock Legendaries** -- Mewtwo unlocks after 10 evolutions. Mew unlocks when the Pokedex is complete (151 entries).

## Features

- **151 Gen 1 Pokemon** with authentic sprites, stats, types, and moves
- **Custom backgrounds** for all screens (main menu, pokedex lab, battle arena, team selection)
- **Move-based combat** with type effectiveness (18 types)
- **XP system** with level-up and evolution mechanics
- **Team battles** (6v6) with manual switch on KO
- **Opponent scaling** (matches player team level)
- **Save/load system** with multiple slots
- **Pokedex tracking** for all encountered Pokemon
- **Combat animations** (shake, flash, HP bar interpolation)
- **Locked Pokemon system** (evolve to unlock, legendary conditions)

## Project Structure

```
pokemonv1/
  main.py               -- Entry point (Pygame loop + state machine)
  models/               -- Domain classes (1 file = 1 class)
    __init__.py
    game.py             -- Game class (orchestrator, save/load, unlocks)
    game_state.py       -- GameState enum
    pokemon.py          -- Pokemon class (stats, XP, evolution, moves, scaling)
    combat.py           -- Combat class (damage, types, moves, XP)
    move.py             -- Move class (name, type, power, accuracy)
    pokedex.py          -- Pokedex class (persistence + anti-duplicate)
    type_chart.py       -- TypeChart class (18 types)
    animation_manager.py -- AnimationManager (combat animations)
  gui/
    base_screen.py       -- BaseScreen parent class
    constants.py         -- Constants (colors, dimensions)
    menu_screen.py       -- Main menu
    selection_screen.py  -- Pokemon selection (1v1)
    team_select_screen.py -- Team selection (6 Pokemon)
    combat_screen.py     -- Combat screen (moves, switch, forced switch)
    result_screen.py     -- Battle results + XP
    pokedex_screen.py    -- Pokedex viewer
    add_pokemon_screen.py -- Add Pokemon
  utils/
    file_handler.py      -- FileHandler (JSON I/O)
  data/
    pokemon.json         -- 151 Gen 1 Pokemon (stats, types, sprites, moves)
    type_chart.json      -- 18x18 type effectiveness table
    pokedex.json         -- Encountered Pokemon (runtime)
  saves/                 -- Save files (JSON)
  assets/
    sprites/             -- 151 authentic Pokemon sprites (PNG)
    backgrounds/         -- Custom backgrounds (main_menu, pokedex_lab, battle_arena, team_arena)
  docs/                  -- Architecture diagrams (D2/SVG), implementation plans
```

## Documentation

The project includes comprehensive architecture documentation:

- **Class Diagram** ([D2](docs/class_diagram.d2) | [SVG](docs/class_diagram.svg)) - Complete class structure
- **Architecture Overview** ([D2](docs/architecture.d2) | [SVG](docs/architecture.svg)) - System architecture
- **State Machine** ([D2](docs/state_machine.d2) | [SVG](docs/state_machine.svg)) - Game state transitions
- **Combat Sequence** ([D2](docs/combat_sequence.d2) | [SVG](docs/combat_sequence.svg)) - Battle flow
- **XP Flow** ([D2](docs/xp_flow.d2) | [SVG](docs/xp_flow.svg)) - Experience and evolution

![Class Diagram](docs/class_diagram.svg)

## Combat Mechanics

- **Turn order**: Player attacks first, then opponent
- **Moves**: Each Pokemon has up to 4 moves with type, power, and accuracy
- **Damage formula** (with move): `((2 * level / 5 + 2) * power * attack / defense) / 50 + 2) * type_multiplier`
- **Type effectiveness**: Official Pokemon 18-type chart (fire > grass > water > fire, etc.)
- **Dual type defense**: Multipliers combine (fire vs grass/ice = 4.0x)
- **Immunity**: 0x multiplier = 0 damage ("No effect!")
- **AI**: Opponent picks a random move each turn
- **XP reward**: 20 + 2 * opponent_level per victory

## Visuals

The game features custom high-quality backgrounds for each screen:
- **Main Menu** - Welcoming entrance screen
- **Pokedex Lab** - Scientific research environment
- **Battle Arena** - Epic battle setting
- **Team Arena** - Team selection stadium

All 151 Gen 1 Pokemon have authentic pixel-art sprites.

## Technologies

- Python 3.10+
- Pygame-CE 2.5+

## Development

### Requirements
- Python 3.10 or higher
- pip (Python package manager)

### Running the game
Use the provided scripts (`run.sh` for Unix/Mac, `run.bat` for Windows) or follow the manual setup in Quick Start.

### Project Documentation
Implementation plans and design documents are available in `docs/plans/`.
