"""Game state module -- enum defining all possible game states."""

from enum import Enum


class GameState(Enum):
    """Enum defining all possible game states for the state machine.

    POO: An ENUM is a special class that defines a fixed set of named constants.
    Instead of using raw strings like "menu" or "combat" (for mistyped),
    we use GameState.MENU & GameState.COMBAT. Is called TYPE SAFETY --
    if misspell GameState.MENUU, Python raises an error immediately.

    Usage:
        state = GameState.MENU
        if state == GameState.COMBAT:
            ...
    """

    MENU = "menu"
    SELECTION = "selection"
    COMBAT = "combat"
    RESULT = "result"
    POKEDEX = "pokedex"
    ADD_POKEMON = "add_pokemon"
    TEAM_SELECT = "team_select"
    SAVE_SELECT = "save_select"
    QUIT = "quit"
