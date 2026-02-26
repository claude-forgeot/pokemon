"""Result screen module -- displays battle outcome."""

import pygame

from models.game_state import GameState
from gui.base_screen import BaseScreen
from gui.constants import Constants


class ResultScreen(BaseScreen):
    """Displays the winner and loser after a battle, with a return button."""

    def __init__(self, game, winner_name, loser_name, xp_message=""):
        """Initialize the result screen.

        Args:
            game: The Game instance.
            winner_name: Name of the winning Pokemon.
            loser_name: Name of the losing Pokemon.
            xp_message: XP gain message from combat.
        """
        super().__init__(game)
        self.winner_name = winner_name
        self.loser_name = loser_name
        self.xp_message = xp_message
        self.font_title = self.constants.get_font(40, bold=True)
        self.font_info = self.constants.get_font(22)
        self.font_button = self.constants.get_font(22)

        self.menu_button = pygame.Rect(
            Constants.SCREEN_WIDTH // 2 - 100,
            Constants.SCREEN_HEIGHT - 170,
            200, 50,
        )

    def handle_events(self, events):
        """Handle click on the return-to-menu button.

        Returns:
            GameState or None: MENU if button clicked.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_button.collidepoint(event.pos):
                    return GameState.MENU
        return None

    def draw(self, surface):
        """Draw the result screen with winner/loser info."""
        surface.fill(Constants.WHITE)

        # Title
        title = self.font_title.render("Battle Over!", True, Constants.BLACK)
        title_rect = title.get_rect(center=(Constants.SCREEN_WIDTH // 2, 80))
        surface.blit(title, title_rect)

        # Winner
        win_text = self.font_info.render(
            f"Winner: {self.winner_name}", True, Constants.GREEN
        )
        win_rect = win_text.get_rect(center=(Constants.SCREEN_WIDTH // 2, 170))
        surface.blit(win_text, win_rect)

        # Loser
        lose_text = self.font_info.render(
            f"Defeated: {self.loser_name}", True, Constants.RED
        )
        lose_rect = lose_text.get_rect(center=(Constants.SCREEN_WIDTH // 2, 220))
        surface.blit(lose_text, lose_rect)

        # XP message
        if self.xp_message:
            xp_text = self.font_info.render(self.xp_message, True, Constants.BLUE)
            xp_rect = xp_text.get_rect(center=(Constants.SCREEN_WIDTH // 2, 270))
            surface.blit(xp_text, xp_rect)

        # Pokedex info
        pdex_y = 320 if self.xp_message else 280
        pdex_text = self.font_info.render(
            f"Pokedex entries: {self.game.pokedex.get_count()}",
            True, Constants.DARK_GRAY,
        )
        pdex_rect = pdex_text.get_rect(center=(Constants.SCREEN_WIDTH // 2, pdex_y))
        surface.blit(pdex_text, pdex_rect)

        # Return button
        pygame.draw.rect(
            surface, Constants.BLUE, self.menu_button,
            border_radius=Constants.BUTTON_RADIUS,
        )
        btn_label = self.font_button.render("Back to Menu", True, Constants.WHITE)
        surface.blit(btn_label, btn_label.get_rect(center=self.menu_button.center))
