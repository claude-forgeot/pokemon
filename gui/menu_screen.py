"""Menu screen module -- main menu with game options."""

import pygame

from models.game_state import GameState
from gui.base_screen import BaseScreen
from gui.constants import Constants


class MenuScreen(BaseScreen):
    """Main menu screen, buttons for all game actions."""

    def __init__(self, game):
        """Initialize the menu screen."""
        super().__init__(game)
        self.font_title = self.constants.get_font(48, bold=True)
        self.font_button = self.constants.get_font(24)
        self.font_small = self.constants.get_font(16)

        self.save_message = ""
        self.save_message_timer = 0

        self._build_buttons()
        self.hover_button = None

    def _build_buttons(self):
        """Build the button dict with dynamic Y positions based on visibility."""
        center_x = Constants.SCREEN_WIDTH // 2 - Constants.BUTTON_WIDTH // 2
        spacing = 60
        y = 200

        self.buttons = {}
        self.labels = {}

        # Continuer -- only if a save exists
        if self.game.has_save():
            self.buttons["continue_game"] = pygame.Rect(
                center_x, y, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT
            )
            self.labels["continue_game"] = "Continue"
            y += spacing

        self.buttons["new_game"] = pygame.Rect(
            center_x, y, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT
        )
        self.labels["new_game"] = "New Game"
        y += spacing

        self.buttons["save_game"] = pygame.Rect(
            center_x, y, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT
        )
        self.labels["save_game"] = "Save Game"
        y += spacing

        # Team Battle -- only if >= 3 available
        if len(self.game.get_available_pokemon()) >= 3:
            self.buttons["team_battle"] = pygame.Rect(
                center_x, y, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT
            )
            self.labels["team_battle"] = "Team Battle"
            y += spacing

        self.buttons["pokedex"] = pygame.Rect(
            center_x, y, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT
        )
        self.labels["pokedex"] = "Pokedex"
        y += spacing

        self.buttons["add_pokemon"] = pygame.Rect(
            center_x, y, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT
        )
        self.labels["add_pokemon"] = "Add Pokemon"

    def handle_events(self, events):
        """Handle mouse clicks on menu buttons."""
        mouse_pos = pygame.mouse.get_pos()
        self.hover_button = None
        for key, rect in self.buttons.items():
            if rect.collidepoint(mouse_pos):
                self.hover_button = key

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if "continue_game" in self.buttons and self.buttons["continue_game"].collidepoint(event.pos):
                    return GameState.SELECTION
                if self.buttons["new_game"].collidepoint(event.pos):
                    self.game.new_game()
                    return GameState.SELECTION
                if self.buttons["save_game"].collidepoint(event.pos):
                    self.game.save_game()
                    self.save_message = "Game saved!"
                    self.save_message_timer = 120  # ~2s at 60 FPS
                    self._build_buttons()  # Rebuild to show "Continuer" if first save
                    return None
                if "team_battle" in self.buttons and self.buttons["team_battle"].collidepoint(event.pos):
                    return GameState.TEAM_SELECT
                if self.buttons["pokedex"].collidepoint(event.pos):
                    return GameState.POKEDEX
                if self.buttons["add_pokemon"].collidepoint(event.pos):
                    return GameState.ADD_POKEMON
        return None

    def update(self):
        """Update save message timer."""
        if self.save_message_timer > 0:
            self.save_message_timer -= 1
            if self.save_message_timer == 0:
                self.save_message = ""

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

        for key, rect in self.buttons.items():
            color = Constants.BLUE if self.hover_button == key else Constants.DARK_GRAY
            pygame.draw.rect(surface, color, rect, border_radius=Constants.BUTTON_RADIUS)
            label = self.font_button.render(self.labels[key], True, Constants.WHITE)
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)

        # Save confirmation message
        if self.save_message:
            msg = self.font_button.render(self.save_message, True, Constants.GREEN)
            msg_rect = msg.get_rect(center=(Constants.SCREEN_WIDTH // 2, 170))
            surface.blit(msg, msg_rect)

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
