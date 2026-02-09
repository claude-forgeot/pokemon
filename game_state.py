"""Game state module -- enum defining all possible game states."""

from enum import Enum


class GameState(Enum):
    """Enum defining all possible game states for the state machine.

    POO: An ENUM is a special class that defines a fixed set of named constants.
    Instead of using raw strings like "menu" or "combat" (which can be mistyped),
    we use GameState.MENU and GameState.COMBAT. This is called TYPE SAFETY --
    if you misspell GameState.MENUU, Python raises an error immediately.

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
    QUIT = "quit"
