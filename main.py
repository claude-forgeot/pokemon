"""Main module -- entry point for the Pokemon game.

This file contains ONLY the Pygame main loop and state machine dispatch.
No classes are defined here (as per project rules: 1 file = 1 class).

Usage:
    python3 main.py
"""

import os
import random
import sys

import pygame

from models.game import Game
from models.game_state import GameState
from models.pokemon import Pokemon
from gui.add_pokemon_screen import AddPokemonScreen
from gui.combat_screen import CombatScreen
from gui.constants import Constants
from gui.menu_screen import MenuScreen
from gui.pokedex_screen import PokedexScreen
from gui.result_screen import ResultScreen
from gui.selection_screen import SelectionScreen
from gui.team_select_screen import TeamSelectScreen

def main():
    """Run the Pygame main loop with state machine dispatch."""
    # Set cwd to script directory so relative paths work
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

    # Combat context (set during RESULT transition)
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
                player_team = []
                opponent_team = []
                player_indices = []
                # Indices reference the full list (including locked)
                all_pokemon = game.get_all_pokemon()
                available = game.get_available_pokemon()
                if state == GameState.TEAM_SELECT and current_screen.selected_indices:
                    player_indices = list(current_screen.selected_indices)
                    for idx in current_screen.selected_indices:
                        p = Pokemon(data=all_pokemon[idx].to_dict())
                        player_team.append(p)
                    opp_sources = random.sample(
                        available, min(len(player_team), len(available))
                    )
                    for p in opp_sources:
                        opponent_team.append(Pokemon(data=p.to_dict()))
                    # Scale opponents to match player team average level
                    total_level = 0
                    for p in player_team:
                        total_level += p.level
                    avg_level = total_level // len(player_team)
                    for opp in opponent_team:
                        opp.scale_to_level(avg_level)
                elif state == GameState.SELECTION and current_screen.selected_index is not None:
                    player_indices = [current_screen.selected_index]
                    p = all_pokemon[current_screen.selected_index]
                    player_team = [Pokemon(data=p.to_dict())]
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
                if state == GameState.COMBAT:
                    winner_name = current_screen.winner
                    combat = current_screen.combat
                    loser_name = combat.get_loser()
                    xp_message = current_screen.xp_message
                    # Sync combat copies back to originals
                    if current_screen.player_original_indices:
                        game.sync_from_combat(
                            current_screen.player_team,
                            current_screen.player_original_indices,
                        )
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
