"""Menu screen module -- main menu with game options."""

import pygame

from models.game_state import GameState
from gui.base_screen import BaseScreen
from gui.constants import Constants, get_font


class MenuScreen(BaseScreen):
    """Main menu screen, buttons for all game actions."""

    def __init__(self, game):
        """Initialize the menu screen."""
        super().__init__(game)
        self.font_title = get_font(48, bold=True)
        self.font_button = get_font(24)
        self.font_small = get_font(16)
        self.message = ""
        self.message_timer = 0

        center_x = Constants.SCREEN_WIDTH // 2 - Constants.BUTTON_WIDTH // 2
        self.buttons = {
            "new_game": pygame.Rect(
                center_x, 200, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT
            ),
            "load_save": pygame.Rect(
                center_x, 270, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT
            ),
            "team_battle": pygame.Rect(
                center_x, 340, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT
            ),
            "pokedex": pygame.Rect(
                center_x, 410, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT
            ),
            "add_pokemon": pygame.Rect(
                center_x, 480, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT
            ),
        }
        self.hover_button = None

    def handle_events(self, events):
        """Handle mouse clicks on menu buttons."""
        mouse_pos = pygame.mouse.get_pos()
        self.hover_button = None
        for key, rect in self.buttons.items():
            if rect.collidepoint(mouse_pos):
                self.hover_button = key

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.buttons["new_game"].collidepoint(event.pos):
                    self.game.new_game()
                    return GameState.SELECTION
                if self.buttons["load_save"].collidepoint(event.pos):
                    return GameState.SAVE_SELECT
                if self.buttons["team_battle"].collidepoint(event.pos):
                    if len(self.game.get_available_pokemon()) < 3:
                        return None
                    return GameState.TEAM_SELECT
                if self.buttons["pokedex"].collidepoint(event.pos):
                    return GameState.POKEDEX
                if self.buttons["add_pokemon"].collidepoint(event.pos):
                    return GameState.ADD_POKEMON
        return None

    def update(self):
        """Update message timer."""
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = ""

    def draw(self, surface):
        """Draw the menu."""
        surface.fill(Constants.WHITE)

        title = self.font_title.render("Pokemon Battle", True, Constants.BLACK)
        title_rect = title.get_rect(center=(Constants.SCREEN_WIDTH // 2, 90))
        surface.blit(title, title_rect)

        subtitle = self.font_small.render(
            "Gotta catch 'em all!", True, Constants.DARK_GRAY
        )
        sub_rect = subtitle.get_rect(center=(Constants.SCREEN_WIDTH // 2, 140))
        surface.blit(subtitle, sub_rect)

        labels = {
            "new_game": "New Game",
            "load_save": "Load Save",
            "team_battle": "Team Battle",
            "pokedex": "Pokedex",
            "add_pokemon": "Add Pokemon",
        }
        for key, rect in self.buttons.items():
            color = Constants.BLUE if self.hover_button == key else Constants.DARK_GRAY
            pygame.draw.rect(surface, color, rect, border_radius=Constants.BUTTON_RADIUS)
            label = self.font_button.render(labels[key], True, Constants.WHITE)
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)

        count = len(self.game.get_available_pokemon())
        if count < 2:
            msg = f"Add more Pokemon first ({count}/2 minimum)"
            msg_color = Constants.RED
        else:
            msg = f"{count} Pokemon available"
            msg_color = Constants.DARK_GRAY
        info = self.font_small.render(msg, True, msg_color)
        info_rect = info.get_rect(center=(Constants.SCREEN_WIDTH // 2, 565))
        surface.blit(info, info_rect)

        pdex_msg = f"Pokedex: {self.game.pokedex.get_count()} encountered"
        pdex = self.font_small.render(pdex_msg, True, Constants.DARK_GRAY)
        pdex_rect = pdex.get_rect(center=(Constants.SCREEN_WIDTH // 2, 585))
        surface.blit(pdex, pdex_rect)

        if self.message:
            msg_surf = self.font_small.render(self.message, True, Constants.GREEN)
            msg_rect = msg_surf.get_rect(
                center=(Constants.SCREEN_WIDTH // 2, 520)
            )
            surface.blit(msg_surf, msg_rect)