"""Main module -- entry point for the Pokemon game.

This file contains ONLY the Pygame main loop and state machine dispatch.
No classes are defined here (as per project rules: 1 file = 1 class).

Usage:
    py main.py
"""

import os
import sys

# Force window position on Windows (fix for invisible window on some configs)
os.environ["SDL_VIDEO_CENTERED"] = "1"

import pygame

from game import Game
from game_state import GameState
from gui.add_pokemon_screen import AddPokemonScreen
from gui.combat_screen import CombatScreen
from gui.constants import Constants
from gui.menu_screen import MenuScreen
from gui.pokedex_screen import PokedexScreen
from gui.result_screen import ResultScreen
from gui.selection_screen import SelectionScreen
from gui.save_select_screen import SaveSelectScreen

def main():
    """Run the Pygame main loop with state machine dispatch."""
    pygame.init()
    screen = pygame.display.set_mode(
        (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT)
    )
    pygame.display.set_caption("Pokemon Battle")
    clock = pygame.time.Clock()

    game = Game()
    state = GameState.MENU
    current_screen = MenuScreen(game)

    # Combat context (set during SELECTION, used by COMBAT and RESULT)
    selected_pokemon = None
    opponent_pokemon = None
    winner_name = None
    loser_name = None

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if not running:
            break

        # Let the current screen process events
        next_state = current_screen.handle_events(events)

        # State transitions
        if next_state is not None and next_state != state:
            match next_state:
                case GameState.MENU:
                    current_screen = MenuScreen(game)
                case GameState.SELECTION:
                    current_screen = SelectionScreen(game)
                case GameState.COMBAT:
                    # Get selected Pokemon from selection screen
                    if hasattr(current_screen, "selected_index") and current_screen.selected_index is not None:
                        pokemon_list = game.get_available_pokemon()
                        selected_pokemon = pokemon_list[current_screen.selected_index]
                        # Create a fresh copy for combat
                        from pokemon import Pokemon
                        selected_pokemon = Pokemon.from_dict(selected_pokemon.to_dict())
                    opponent_pokemon = game.get_random_opponent()
                    if selected_pokemon and opponent_pokemon:
                        current_screen = CombatScreen(
                            game, selected_pokemon, opponent_pokemon
                        )
                    else:
                        current_screen = MenuScreen(game)
                        next_state = GameState.MENU
                case GameState.RESULT:
                    # Get winner/loser from combat screen
                    if hasattr(current_screen, "winner"):
                        winner_name = current_screen.winner
                        combat = current_screen.combat
                        loser_name = combat.get_loser()
                    game.save_game()
                    current_screen = ResultScreen(
                        game,
                        winner_name or "Unknown",
                        loser_name or "Unknown",
                    )
                case GameState.POKEDEX:
                    current_screen = PokedexScreen(game)
                case GameState.ADD_POKEMON:
                    current_screen = AddPokemonScreen(game)
                case GameState.SAVE_SELECT:
                    current_screen = SaveSelectScreen(game)    
                case GameState.QUIT:
                    running = False
            state = next_state

        # Update and draw
        current_screen.update()
        current_screen.draw(screen)
        pygame.display.flip()
        clock.tick(Constants.FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
