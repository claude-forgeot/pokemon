"""Pokedex screen module -- displays encountered Pokemon."""

import pygame

from game_state import GameState
from gui.base_screen import BaseScreen
from gui.constants import Constants


class PokedexScreen(BaseScreen):
    """Screen showing all previously encountered Pokemon with their details."""

    def __init__(self, game):
        """Initialize the Pokedex screen.

        Args:
            game: The Game instance.
        """
        super().__init__(game)
        self.font_title = pygame.font.SysFont("arial", 32, bold=True)
        self.font_name = pygame.font.SysFont("arial", 20, bold=True)
        self.font_stat = pygame.font.SysFont("arial", 15)
        self.font_button = pygame.font.SysFont("arial", 18)
        self.scroll_offset = 0

        self.back_button = pygame.Rect(20, 20, 100, 36)

    def handle_events(self, events):
        """Handle back button and scrolling.

        Returns:
            GameState or None: MENU if back clicked.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.back_button.collidepoint(event.pos):
                    return GameState.MENU
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset -= event.y * 30
                self.scroll_offset = max(0, self.scroll_offset)
        return None

    def update(self):
        """No update logic needed."""

    def draw(self, surface):
        """Draw the Pokedex list with entries."""
        surface.fill(Constants.WHITE)

        # Back button
        pygame.draw.rect(
            surface, Constants.DARK_GRAY, self.back_button,
            border_radius=Constants.BUTTON_RADIUS,
        )
        back_label = self.font_stat.render("< Back", True, Constants.WHITE)
        surface.blit(back_label, back_label.get_rect(center=self.back_button.center))

        # Title + count
        entries = self.game.pokedex.get_all_entries()
        title_text = f"Pokedex ({len(entries)} encountered)"
        title = self.font_title.render(title_text, True, Constants.BLACK)
        surface.blit(
            title, (Constants.SCREEN_WIDTH // 2 - title.get_width() // 2, 25)
        )

        if not entries:
            empty = self.font_name.render(
                "No Pokemon encountered yet!", True, Constants.DARK_GRAY
            )
            surface.blit(
                empty,
                (Constants.SCREEN_WIDTH // 2 - empty.get_width() // 2, 250),
            )
            return

        # Draw entries as rows
        start_y = 80 - self.scroll_offset
        row_height = 60

        for i, entry in enumerate(entries):
            y = start_y + i * row_height
            if y + row_height < 70 or y > Constants.SCREEN_HEIGHT:
                continue

            # Row background (alternating)
            row_color = Constants.LIGHT_GRAY if i % 2 == 0 else Constants.WHITE
            row_rect = pygame.Rect(30, y, Constants.SCREEN_WIDTH - 60, row_height - 4)
            pygame.draw.rect(surface, row_color, row_rect, border_radius=4)

            # Number
            num_surf = self.font_stat.render(f"#{i + 1}", True, Constants.DARK_GRAY)
            surface.blit(num_surf, (45, y + 10))

            # Name
            name_surf = self.font_name.render(entry["name"], True, Constants.BLACK)
            surface.blit(name_surf, (90, y + 8))

            # Types
            badge_x = 90
            badge_y = y + 32
            for ptype in entry.get("types", []):
                color = Constants.TYPE_COLORS.get(ptype, Constants.GRAY)
                tw, th = self.font_stat.size(ptype)
                badge_rect = pygame.Rect(badge_x, badge_y, tw + 10, th + 2)
                pygame.draw.rect(surface, color, badge_rect, border_radius=3)
                type_surf = self.font_stat.render(ptype, True, Constants.WHITE)
                surface.blit(type_surf, (badge_x + 5, badge_y + 1))
                badge_x += tw + 14

            # Stats
            hp = entry.get("hp", "?")
            atk = entry.get("attack", "?")
            dfs = entry.get("defense", "?")
            stat_text = f"HP:{hp}  ATK:{atk}  DEF:{dfs}"
            stat_surf = self.font_stat.render(stat_text, True, Constants.DARK_GRAY)
            surface.blit(stat_surf, (Constants.SCREEN_WIDTH - 250, y + 20))
