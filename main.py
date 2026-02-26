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

from models.game import Game
from models.game_state import GameState
from gui.add_pokemon_screen import AddPokemonScreen
from gui.combat_screen import CombatScreen
from gui.constants import Constants
from gui.menu_screen import MenuScreen
from gui.pokedex_screen import PokedexScreen
from gui.result_screen import ResultScreen
from gui.selection_screen import SelectionScreen
from gui.save_select_screen import SaveSelectScreen
from gui.team_select_screen import TeamSelectScreen

def main():
    """Run the Pygame main loop with state machine dispatch."""
    # BUG-16: Ensure cwd is the script directory so relative paths work
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

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
            if next_state == GameState.MENU:
                current_screen = MenuScreen(game)
            elif next_state == GameState.SELECTION:
                current_screen = SelectionScreen(game)
            elif next_state == GameState.COMBAT:
                from models.pokemon import Pokemon
                player_team = []
                opponent_team = []
                player_indices = []
                # Indices reference the full list (including locked)
                all_pokemon = game.get_all_pokemon()
                available = game.get_available_pokemon()
                if hasattr(current_screen, "selected_indices") and current_screen.selected_indices:
                    player_indices = list(current_screen.selected_indices)
                    for idx in current_screen.selected_indices:
                        p = Pokemon.from_dict(all_pokemon[idx].to_dict())
                        player_team.append(p)
                    import random
                    opp_sources = random.sample(
                        available, min(len(player_team), len(available))
                    )
                    for p in opp_sources:
                        opponent_team.append(Pokemon.from_dict(p.to_dict()))
                    # Scale opponents to match player team average level
                    avg_level = sum(p.level for p in player_team) // len(player_team)
                    for opp in opponent_team:
                        opp.scale_to_level(avg_level)
                elif hasattr(current_screen, "selected_index") and current_screen.selected_index is not None:
                    player_indices = [current_screen.selected_index]
                    p = all_pokemon[current_screen.selected_index]
                    player_team = [Pokemon.from_dict(p.to_dict())]
                    opp = game.get_random_opponent()
                    opp.scale_to_level(player_team[0].level)
                    opponent_team = [opp]
                if player_team and opponent_team:
                    current_screen = CombatScreen(
                        game, player_team, opponent_team, player_indices
                    )
                else:
                    current_screen = MenuScreen(game)
                    next_state = GameState.MENU
            elif next_state == GameState.RESULT:
                # Get winner/loser and XP message from combat screen
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
                current_screen = ResultScreen(
                    game,
                    winner_name or "Unknown",
                    loser_name or "Unknown",
                    xp_message,
                )
            elif next_state == GameState.POKEDEX:
                current_screen = PokedexScreen(game)
            elif next_state == GameState.ADD_POKEMON:
                current_screen = AddPokemonScreen(game)
            elif next_state == GameState.SAVE_SELECT:
                current_screen = SaveSelectScreen(game)
            elif next_state == GameState.TEAM_SELECT:
                current_screen = TeamSelectScreen(game)
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
