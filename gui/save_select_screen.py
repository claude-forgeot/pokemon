"""Save select screen module -- list, load, and delete save files."""

import pygame

from models.game_state import GameState
from gui.base_screen import BaseScreen
from gui.constants import Constants, get_font


class SaveSelectScreen(BaseScreen):
    """Screen to list save files, load one, or delete one.

    POO: This class INHERITS from BaseScreen, just like MenuScreen.
    It implements the 3 required abstract methods: handle_events,
    update, and draw.
    """

    def __init__(self, game):
        """Initialize the save select screen.

        Args:
            game: The Game instance.
        """
        super().__init__(game)
        self.font_title = get_font(36, bold=True)
        self.font_item = get_font(20)
        self.font_small = get_font(16)
        self.saves = game.get_save_files()
        self.selected_index = None
        self.scroll_offset = 0
        self.message = ""
        self.message_timer = 0

        # Back button
        self.back_button = pygame.Rect(
            20, 20, 100, 40
        )

        # Load and Delete buttons
        btn_y = Constants.SCREEN_HEIGHT - 80
        self.load_button = pygame.Rect(
            Constants.SCREEN_WIDTH // 2 - 210, btn_y,
            200, 50
        )
        self.delete_button = pygame.Rect(
            Constants.SCREEN_WIDTH // 2 + 10, btn_y,
            200, 50
        )

    def handle_events(self, events):
        """Handle clicks on save entries, load, delete, and back buttons.

        Returns:
            GameState or None: MENU to go back, or None to stay.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Back button
                if self.back_button.collidepoint(event.pos):
                    return GameState.MENU

                # Click on a save entry
                for i, save in enumerate(self.saves):
                    entry_rect = pygame.Rect(
                        100, 100 + i * 50 - self.scroll_offset,
                        Constants.SCREEN_WIDTH - 200, 40
                    )
                    if entry_rect.collidepoint(event.pos):
                        self.selected_index = i

                # Load button
                if self.load_button.collidepoint(event.pos):
                    if self.selected_index is not None and self.selected_index < len(self.saves):
                        save = self.saves[self.selected_index]
                        try:
                            self.game.load_game(save["filepath"])
                            self.message = "Game loaded!"
                            self.message_timer = 120
                            return GameState.MENU
                        except Exception:
                            self.message = "Error loading save!"
                            self.message_timer = 120

                # Delete button
                if self.delete_button.collidepoint(event.pos):
                    if self.selected_index is not None and self.selected_index < len(self.saves):
                        save = self.saves[self.selected_index]
                        self.game.delete_save(save["filepath"])
                        self.saves = self.game.get_save_files()
                        self.selected_index = None
                        self.message = "Save deleted!"
                        self.message_timer = 120

            # Scroll with mouse wheel
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset -= event.y * 30
                max_scroll = max(0, len(self.saves) * 50 - 360)
                self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        return None

    def update(self):
        """Update message timer."""
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = ""

    def draw(self, surface):
        """Draw the save select screen."""
        surface.fill(Constants.WHITE)

        # Title
        title = self.font_title.render("Load Save", True, Constants.BLACK)
        title_rect = title.get_rect(center=(Constants.SCREEN_WIDTH // 2, 50))
        surface.blit(title, title_rect)

        # Back button
        pygame.draw.rect(surface, Constants.DARK_GRAY, self.back_button,
                         border_radius=Constants.BUTTON_RADIUS)
        back_text = self.font_small.render("Back", True, Constants.WHITE)
        back_rect = back_text.get_rect(center=self.back_button.center)
        surface.blit(back_text, back_rect)

        # Save entries
        if not self.saves:
            no_save = self.font_item.render(
                "No saves found.", True, Constants.DARK_GRAY
            )
            no_rect = no_save.get_rect(
                center=(Constants.SCREEN_WIDTH // 2, 250)
            )
            surface.blit(no_save, no_rect)
        else:
            for i, save in enumerate(self.saves):
                y = 100 + i * 50 - self.scroll_offset
                if y < 80 or y > Constants.SCREEN_HEIGHT - 140:
                    continue
                entry_rect = pygame.Rect(
                    100, y, Constants.SCREEN_WIDTH - 200, 40
                )
                # Highlight selected
                if i == self.selected_index:
                    pygame.draw.rect(surface, Constants.BLUE, entry_rect,
                                     border_radius=5)
                    text_color = Constants.WHITE
                else:
                    pygame.draw.rect(surface, Constants.LIGHT_GRAY, entry_rect,
                                     border_radius=5)
                    text_color = Constants.BLACK

                # Format date nicely
                date_str = save["date"]
                try:
                    display = (
                        f"{date_str[6:8]}/{date_str[4:6]}/{date_str[0:4]}"
                        f"  {date_str[9:11]}:{date_str[11:13]}:{date_str[13:15]}"
                    )
                except (IndexError, ValueError):
                    display = save["filename"]

                text = self.font_item.render(display, True, text_color)
                text_rect = text.get_rect(midleft=(entry_rect.x + 15, entry_rect.centery))
                surface.blit(text, text_rect)

        # Load button
        load_color = Constants.GREEN if self.selected_index is not None else Constants.GRAY
        pygame.draw.rect(surface, load_color, self.load_button,
                         border_radius=Constants.BUTTON_RADIUS)
        load_text = self.font_item.render("Load", True, Constants.WHITE)
        load_rect = load_text.get_rect(center=self.load_button.center)
        surface.blit(load_text, load_rect)

        # Delete button
        del_color = Constants.RED if self.selected_index is not None else Constants.GRAY
        pygame.draw.rect(surface, del_color, self.delete_button,
                         border_radius=Constants.BUTTON_RADIUS)
        del_text = self.font_item.render("Delete", True, Constants.WHITE)
        del_rect = del_text.get_rect(center=self.delete_button.center)
        surface.blit(del_text, del_rect)

        # Message
        if self.message:
            msg = self.font_small.render(self.message, True, Constants.BLUE)
            msg_rect = msg.get_rect(
                center=(Constants.SCREEN_WIDTH // 2, Constants.SCREEN_HEIGHT - 25)
            )
            surface.blit(msg, msg_rect)