"""Menu screen module -- main menu with 3 options."""

import pygame

from game_state import GameState
from gui.base_screen import BaseScreen
from gui.constants import Constants


class MenuScreen(BaseScreen):
    """Main menu screen with 3 buttons: Start Battle, Add Pokemon, Pokedex.

    POO: This class INHERITS from BaseScreen and implements all 3 abstract
    methods. 'super().__init__(game)' calls the parent's constructor to
    properly initialize the base class part of this object.
    """

    def __init__(self, game):
        """Initialize the menu screen.

        Args:
            game: The Game instance.
        """
        super().__init__(game)
        self.font_title = pygame.font.SysFont("arial", 48, bold=True)
        self.font_button = pygame.font.SysFont("arial", 24)
        self.font_small = pygame.font.SysFont("arial", 16)

        # Define button rectangles (centered horizontally)
        center_x = Constants.SCREEN_WIDTH // 2 - Constants.BUTTON_WIDTH // 2
        self.buttons = {
            "battle": pygame.Rect(
                center_x, 250, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT
            ),
            "add": pygame.Rect(
                center_x, 320, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT
            ),
            "pokedex": pygame.Rect(
                center_x, 390, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT
            ),
        }
        self.hover_button = None

    def handle_events(self, events):
        """Handle mouse clicks on menu buttons.

        Returns:
            GameState or None: Next state based on button clicked.
        """
        mouse_pos = pygame.mouse.get_pos()
        self.hover_button = None
        for key, rect in self.buttons.items():
            if rect.collidepoint(mouse_pos):
                self.hover_button = key

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.buttons["battle"].collidepoint(event.pos):
                    if len(self.game.get_available_pokemon()) < 2:
                        return None
                    return GameState.SELECTION
                if self.buttons["add"].collidepoint(event.pos):
                    return GameState.ADD_POKEMON
                if self.buttons["pokedex"].collidepoint(event.pos):
                    return GameState.POKEDEX
        return None

    def update(self):
        """No update logic needed for the menu."""

    def draw(self, surface):
        """Draw the menu: title, 3 buttons, and Pokemon count."""
        surface.fill(Constants.WHITE)

        # Title
        title = self.font_title.render("Pokemon Battle", True, Constants.BLACK)
        title_rect = title.get_rect(center=(Constants.SCREEN_WIDTH // 2, 120))
        surface.blit(title, title_rect)

        # Subtitle
        subtitle = self.font_small.render(
            "Gotta catch 'em all!", True, Constants.DARK_GRAY
        )
        sub_rect = subtitle.get_rect(center=(Constants.SCREEN_WIDTH // 2, 170))
        surface.blit(subtitle, sub_rect)

        # Buttons
        labels = {
            "battle": "Start Battle",
            "add": "Add Pokemon",
            "pokedex": "Pokedex",
        }
        for key, rect in self.buttons.items():
            color = Constants.BLUE if self.hover_button == key else Constants.DARK_GRAY
            pygame.draw.rect(surface, color, rect, border_radius=Constants.BUTTON_RADIUS)
            label = self.font_button.render(labels[key], True, Constants.WHITE)
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)

        # Pokemon count / warning
        count = len(self.game.get_available_pokemon())
        if count < 2:
            msg = f"Add more Pokemon first ({count}/2 minimum)"
            msg_color = Constants.RED
        else:
            msg = f"{count} Pokemon available"
            msg_color = Constants.DARK_GRAY
        info = self.font_small.render(msg, True, msg_color)
        info_rect = info.get_rect(center=(Constants.SCREEN_WIDTH // 2, 480))
        surface.blit(info, info_rect)

        # Pokedex count
        pdex_msg = f"Pokedex: {self.game.pokedex.get_count()} encountered"
        pdex = self.font_small.render(pdex_msg, True, Constants.DARK_GRAY)
        pdex_rect = pdex.get_rect(center=(Constants.SCREEN_WIDTH // 2, 510))
        surface.blit(pdex, pdex_rect)
