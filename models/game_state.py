"""Game state module -- named constants for all possible game states."""


class GameState:
    """Named constants for the game state machine.

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
