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
from gui.team_select_screen import TeamSelectScreen

def _scale_pokemon_level(pokemon, target_level):
    """Scale a Pokemon's stats to match a target level.

    Adjusts HP, attack, and defense proportionally based on the level
    difference from the Pokemon's base level (5).

    Args:
        pokemon: The Pokemon to scale.
        target_level: Desired level.
    """
    if pokemon.level == target_level:
        return
    base_level = pokemon.level
    diff = target_level - base_level
    pokemon.level = target_level
    pokemon.max_hp += diff * 5
    pokemon.hp = pokemon.max_hp
    pokemon.attack += diff * 3
    pokemon.defense += diff * 2
    pokemon.xp_to_next_level = 10 + pokemon.level * 5


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
                    from pokemon import Pokemon
                    player_team = []
                    opponent_team = []
                    # Indices reference the full list (including locked)
                    all_pokemon = game.get_all_pokemon()
                    available = game.get_available_pokemon()
                    if hasattr(current_screen, "selected_indices") and current_screen.selected_indices:
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
                            _scale_pokemon_level(opp, avg_level)
                    elif hasattr(current_screen, "selected_index") and current_screen.selected_index is not None:
                        p = all_pokemon[current_screen.selected_index]
                        player_team = [Pokemon.from_dict(p.to_dict())]
                        opp = Pokemon.from_dict(game.get_random_opponent().to_dict())
                        _scale_pokemon_level(opp, player_team[0].level)
                        opponent_team = [opp]
                    if player_team and opponent_team:
                        current_screen = CombatScreen(
                            game, player_team, opponent_team
                        )
                    else:
                        current_screen = MenuScreen(game)
                        next_state = GameState.MENU
                case GameState.RESULT:
                    # Get winner/loser and XP message from combat screen
                    xp_message = ""
                    if hasattr(current_screen, "winner"):
                        winner_name = current_screen.winner
                        combat = current_screen.combat
                        loser_name = combat.get_loser()
                        xp_message = getattr(current_screen, "xp_message", "")
                    game.save_game()
                    current_screen = ResultScreen(
                        game,
                        winner_name or "Unknown",
                        loser_name or "Unknown",
                        xp_message,
                    )
                case GameState.POKEDEX:
                    current_screen = PokedexScreen(game)
                case GameState.ADD_POKEMON:
                    current_screen = AddPokemonScreen(game)
                case GameState.SAVE_SELECT:
                    current_screen = SaveSelectScreen(game)
                case GameState.TEAM_SELECT:
                    current_screen = TeamSelectScreen(game)        
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
