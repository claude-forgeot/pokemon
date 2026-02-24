"""Team select screen -- lets the player build a team before fighting."""

import os

import pygame

from game_state import GameState
from gui.base_screen import BaseScreen
from gui.constants import Constants


class TeamSelectScreen(BaseScreen):

    """Screen where the player picks 3-6 Pokemon for their team."""

    MIN_TEAM = 3
    MAX_TEAM = 6

    def __init__(self, game):
        """Initialize the team select screen.

        Args:
            game: The Game instance.
        """
        super().__init__(game)
        self.font_title = pygame.font.SysFont("arial", 32, bold=True)
        self.font_name = pygame.font.SysFont("arial", 16, bold=True)
        self.font_stat = pygame.font.SysFont("arial", 13)
        self.font_button = pygame.font.SysFont("arial", 20)
        self.font_info = pygame.font.SysFont("arial", 16)

        self.selected_indices = []
        self.scroll_offset = 0
        self.sprites = {}
        self._load_sprites()

        # Back button
        self.back_button = pygame.Rect(20, 20, 100, 36)
        # Confirm button
        self.confirm_button = pygame.Rect(
            Constants.SCREEN_WIDTH // 2 - 80,
            Constants.SCREEN_HEIGHT - 55, 160, 40
        )

    def _load_sprites(self):
        """Load all available Pokemon sprites into memory."""
        for pokemon in self.game.get_available_pokemon():
            path = pokemon.sprite_path
            if path and os.path.isfile(path):
                try:
                    img = pygame.image.load(path)
                    self.sprites[pokemon.name] = pygame.transform.scale(img, (64, 64))
                except pygame.error:
                    pass

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
                pokemon_list = self.game.get_available_pokemon()
                cols = 5
                start_x = 30
                start_y = 75 - self.scroll_offset
                card_w = 140
                card_h = 130
                padding = 10
                for i, _pokemon in enumerate(pokemon_list):
                    col = i % cols
                    row = i // cols
                    x = start_x + col * (card_w + padding)
                    y = start_y + row * (card_h + padding)
                    card_rect = pygame.Rect(x, y, card_w, card_h)
                    if card_rect.collidepoint(event.pos):
                        if i in self.selected_indices:
                            self.selected_indices.remove(i)
                        elif len(self.selected_indices) < self.MAX_TEAM:
                            self.selected_indices.append(i)

            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset -= event.y * 30
                self.scroll_offset = max(0, self.scroll_offset)
        return None

    def update(self):
        """No update logic needed."""

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

        # Pokemon cards
        pokemon_list = self.game.get_available_pokemon()
        cols = 5
        start_x = 30
        start_y = 75 - self.scroll_offset
        card_w = 140
        card_h = 130
        padding = 10

        for i, pokemon in enumerate(pokemon_list):
            col = i % cols
            row = i // cols
            x = start_x + col * (card_w + padding)
            y = start_y + row * (card_h + padding)

            if y + card_h < 65 or y > Constants.SCREEN_HEIGHT - 70:
                continue

            # Card background
            is_selected = i in self.selected_indices
            card_rect = pygame.Rect(x, y, card_w, card_h)

            if is_selected:
                pygame.draw.rect(surface, Constants.BLUE, card_rect, border_radius=6)
                # Show order number
                order = self.selected_indices.index(i) + 1
                order_surf = self.font_name.render(str(order), True, Constants.WHITE)
                surface.blit(order_surf, (x + 5, y + 5))
            else:
                pygame.draw.rect(surface, Constants.LIGHT_GRAY, card_rect, border_radius=6)

            border_color = Constants.BLUE if is_selected else Constants.GRAY
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

            # Name
            name_surf = self.font_name.render(pokemon.name, True, Constants.BLACK)
            surface.blit(
                name_surf,
                (x + card_w // 2 - name_surf.get_width() // 2, y + 75),
            )

            # Type badges
            badge_y = y + 93
            total_w = sum(self.font_stat.size(t)[0] + 12 for t in pokemon.types)
            badge_x = x + card_w // 2 - total_w // 2
            for ptype in pokemon.types:
                color = Constants.TYPE_COLORS.get(ptype, Constants.GRAY)
                tw, th = self.font_stat.size(ptype)
                badge_rect = pygame.Rect(badge_x, badge_y, tw + 12, th + 2)
                pygame.draw.rect(surface, color, badge_rect, border_radius=3)
                type_surf = self.font_stat.render(ptype, True, Constants.WHITE)
                surface.blit(type_surf, (badge_x + 6, badge_y + 1))
                badge_x += tw + 14

            # Stats
            stat_text = f"HP:{pokemon.hp} ATK:{pokemon.attack}"
            stat_surf = self.font_stat.render(stat_text, True, Constants.DARK_GRAY)
            surface.blit(
                stat_surf,
                (x + card_w // 2 - stat_surf.get_width() // 2, y + 112),
            )

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