"""Team select screen -- lets the player build a team before fighting."""

import pygame

from models.game_state import GameState
from gui.base_screen import BaseScreen
from gui.constants import Constants


class TeamSelectScreen(BaseScreen):

    """Screen where the player picks 3-6 Pokemon for their team."""

    MIN_TEAM = 3
    MAX_TEAM = 6
    COLS = 5
    CARD_START_X = 30
    CARD_START_Y = 75
    CARD_W = 140
    CARD_H = 130
    CARD_PAD = 10

    def __init__(self, game):
        """Initialize the team select screen.

        Args:
            game: The Game instance.
        """
        super().__init__(game)
        self.font_title = self.constants.get_font(32, bold=True)
        self.font_name = self.constants.get_font(16, bold=True)
        self.font_stat = self.constants.get_font(13)
        self.font_button = self.constants.get_font(20)
        self.font_info = self.constants.get_font(16)

        self.selected_indices = []
        self.scroll_offset = 0
        self.sprites = {}
        self._load_sprites((64, 64))

        # Back button
        self.back_button = pygame.Rect(20, 20, 100, 36)
        # Confirm button
        self.confirm_button = pygame.Rect(
            Constants.SCREEN_WIDTH // 2 - 80,
            Constants.SCREEN_HEIGHT - 55, 160, 40
        )

    def handle_events(self, events):
        """Clicks on Pokemon cards, back, and confirm buttons.

        Returns:
            GameState or None: COMBAT if confirmed, MENU if back, else None.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Back button
                if self.back_button.collidepoint(event.pos):
                    return GameState.MENU

                # Confirm button
                if len(self.selected_indices) >= self.MIN_TEAM:
                    if self.confirm_button.collidepoint(event.pos):
                        return GameState.COMBAT

                # Card click
                pokemon_list = self.game.get_all_pokemon()
                cols = self.COLS
                start_x = self.CARD_START_X
                start_y = self.CARD_START_Y - self.scroll_offset
                card_w = self.CARD_W
                card_h = self.CARD_H
                padding = self.CARD_PAD
                for i, _pokemon in enumerate(pokemon_list):
                    col = i % cols
                    row = i // cols
                    x = start_x + col * (card_w + padding)
                    y = start_y + row * (card_h + padding)
                    card_rect = pygame.Rect(x, y, card_w, card_h)
                    if card_rect.collidepoint(event.pos) and not _pokemon.locked:
                        if i in self.selected_indices:
                            self.selected_indices.remove(i)
                        elif len(self.selected_indices) < self.MAX_TEAM:
                            self.selected_indices.append(i)

            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset -= event.y * 30
                pokemon_list = self.game.get_all_pokemon()
                cols = self.COLS
                card_h = self.CARD_H
                padding = self.CARD_PAD
                rows = (len(pokemon_list) + cols - 1) // cols
                total_h = rows * (card_h + padding)
                max_scroll = max(0, total_h - Constants.SCREEN_HEIGHT + 120)
                self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
        return None

    def draw(self, surface):
        """Draw the team selection grid."""
        surface.fill(Constants.WHITE)

        # Title
        title = self.font_title.render("Choose your team (3-6)", True, Constants.BLACK)
        surface.blit(title, (Constants.SCREEN_WIDTH // 2 - title.get_width() // 2, 25))

        # Back button
        pygame.draw.rect(
            surface, Constants.DARK_GRAY, self.back_button,
            border_radius=Constants.BUTTON_RADIUS,
        )
        back_label = self.font_stat.render("< Back", True, Constants.WHITE)
        surface.blit(back_label, back_label.get_rect(center=self.back_button.center))

        # Pokemon cards (includes locked, shown greyed out)
        pokemon_list = self.game.get_all_pokemon()
        cols = self.COLS
        start_x = self.CARD_START_X
        start_y = self.CARD_START_Y - self.scroll_offset
        card_w = self.CARD_W
        card_h = self.CARD_H
        padding = self.CARD_PAD

        surface.set_clip(pygame.Rect(0, 60, 800, 440))
        for i, pokemon in enumerate(pokemon_list):
            col = i % cols
            row = i // cols
            x = start_x + col * (card_w + padding)
            y = start_y + row * (card_h + padding)

            if y + card_h < 65 or y > Constants.SCREEN_HEIGHT - 70:
                continue

            # Card background
            is_selected = i in self.selected_indices
            is_locked = pokemon.locked
            card_rect = pygame.Rect(x, y, card_w, card_h)

            if is_locked:
                pygame.draw.rect(surface, (200, 200, 200), card_rect, border_radius=6)
            elif is_selected:
                pygame.draw.rect(surface, Constants.BLUE, card_rect, border_radius=6)
                # Show order number with background
                order = self.selected_indices.index(i) + 1
                order_surf = self.font_name.render(str(order), True, Constants.WHITE)
                order_bg = pygame.Rect(x + 3, y + 3, order_surf.get_width() + 8, order_surf.get_height() + 4)
                pygame.draw.rect(surface, (30, 60, 160), order_bg, border_radius=4)
                surface.blit(order_surf, (x + 7, y + 5))
            else:
                pygame.draw.rect(surface, Constants.LIGHT_GRAY, card_rect, border_radius=6)

            if is_locked:
                border_color = (160, 160, 160)
            elif is_selected:
                border_color = Constants.BLUE
            else:
                border_color = Constants.GRAY
            pygame.draw.rect(surface, border_color, card_rect, width=2, border_radius=6)

            # Sprite
            if pokemon.name in self.sprites:
                sprite = self.sprites[pokemon.name]
                surface.blit(sprite, (x + card_w // 2 - 32, y + 8))
            else:
                pygame.draw.circle(
                    surface, Constants.GRAY,
                    (x + card_w // 2, y + 40), 24,
                )

            # Locked text with background
            if is_locked:
                lock_surf = self.font_stat.render("LOCKED", True, (120, 120, 120))
                lock_x = x + card_w // 2 - lock_surf.get_width() // 2
                lock_bg = pygame.Rect(lock_x - 4, y + 38, lock_surf.get_width() + 8, lock_surf.get_height() + 4)
                pygame.draw.rect(surface, (200, 200, 200), lock_bg, border_radius=3)
                surface.blit(lock_surf, (lock_x, y + 40))

            # Name
            name_color = (160, 160, 160) if is_locked else Constants.BLACK
            name_surf = self.font_name.render(pokemon.name, True, name_color)
            surface.blit(
                name_surf,
                (x + card_w // 2 - name_surf.get_width() // 2, y + 73),
            )

            # Type badges
            badge_y = y + 96
            total_w = 0
            for t in pokemon.types:
                total_w += self.font_stat.size(t)[0] + 14
            badge_x = x + card_w // 2 - total_w // 2
            self.draw_type_badges(
                surface, self.font_stat, pokemon.types,
                badge_x, badge_y, padding=4, pad_inner=12, radius=3,
            )

            # Stats
            stat_text = f"HP:{pokemon.hp} ATK:{pokemon.attack}"
            stat_surf = self.font_stat.render(stat_text, True, Constants.DARK_GRAY)
            surface.blit(
                stat_surf,
                (x + card_w // 2 - stat_surf.get_width() // 2, y + 112),
            )

        surface.set_clip(None)

        # Info text
        count = len(self.selected_indices)
        if count < self.MIN_TEAM:
            info_text = f"Select {self.MIN_TEAM - count} more Pokemon"
            info_color = Constants.RED
        else:
            info_text = f"{count} Pokemon selected (max {self.MAX_TEAM})"
            info_color = Constants.GREEN
        info_surf = self.font_info.render(info_text, True, info_color)
        surface.blit(
            info_surf,
            (Constants.SCREEN_WIDTH // 2 - info_surf.get_width() // 2,
             Constants.SCREEN_HEIGHT - 95),
        )

        # Confirm button
        if count >= self.MIN_TEAM:
            pygame.draw.rect(
                surface, Constants.GREEN, self.confirm_button,
                border_radius=Constants.BUTTON_RADIUS,
            )
            confirm_label = self.font_button.render("Start Battle!", True, Constants.WHITE)
            surface.blit(
                confirm_label,
                confirm_label.get_rect(center=self.confirm_button.center),
            )