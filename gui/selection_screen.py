"""Selection screen module -- choose a Pokemon for battle."""

import os

import pygame

from game_state import GameState
from gui.base_screen import BaseScreen
from gui.constants import Constants


class SelectionScreen(BaseScreen):
    """Screen for choosing which Pokemon to battle with.

    Displays available Pokemon in a scrollable grid with sprites and stats.
    """

    def __init__(self, game):
        """Initialize the selection screen.

        Args:
            game: The Game instance.
        """
        super().__init__(game)
        self.font_title = pygame.font.SysFont("arial", 32, bold=True)
        self.font_name = pygame.font.SysFont("arial", 18, bold=True)
        self.font_stat = pygame.font.SysFont("arial", 14)
        self.font_button = pygame.font.SysFont("arial", 20)
        self.selected_index = None
        self.scroll_offset = 0
        self.sprites = {}
        self._load_sprites()

        # Back button
        self.back_button = pygame.Rect(20, 20, 100, 36)
        # Confirm button
        self.confirm_button = pygame.Rect(
            Constants.SCREEN_WIDTH // 2 - 80, Constants.SCREEN_HEIGHT - 60, 160, 40
        )

    def _load_sprites(self):
        """Load all available Pokemon sprites into memory."""
        for pokemon in self.game.get_all_pokemon():
            path = pokemon.sprite_path
            if path and os.path.isfile(path):
                try:
                    img = pygame.image.load(path)
                    self.sprites[pokemon.name] = pygame.transform.scale(img, (80, 80))
                except pygame.error:
                    pass

    def handle_events(self, events):
        """Handle clicks on Pokemon cards, back, and confirm buttons.

        Returns:
            GameState or None: COMBAT if confirmed, MENU if back, else None.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Back button
                if self.back_button.collidepoint(event.pos):
                    return GameState.MENU

                # Confirm button
                if self.selected_index is not None:
                    if self.confirm_button.collidepoint(event.pos):
                        return GameState.COMBAT

                # Card click (only unlocked Pokemon can be selected)
                pokemon_list = self.game.get_all_pokemon()
                cols = 4
                start_x = 40
                start_y = 80 - self.scroll_offset
                for i, _pokemon in enumerate(pokemon_list):
                    col = i % cols
                    row = i // cols
                    x = start_x + col * (Constants.CARD_WIDTH + Constants.CARD_PADDING)
                    y = start_y + row * (Constants.CARD_HEIGHT + Constants.CARD_PADDING)
                    card_rect = pygame.Rect(
                        x, y, Constants.CARD_WIDTH, Constants.CARD_HEIGHT
                    )
                    if card_rect.collidepoint(event.pos) and not _pokemon.locked:
                        self.selected_index = i

            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset -= event.y * 30
                self.scroll_offset = max(0, self.scroll_offset)
        return None

    def update(self):
        """Reload sprites if the list changed."""

    def draw(self, surface):
        """Draw the Pokemon selection grid."""
        surface.fill(Constants.WHITE)

        # Title
        title = self.font_title.render("Choose your Pokemon", True, Constants.BLACK)
        surface.blit(title, (Constants.SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        # Back button
        pygame.draw.rect(
            surface, Constants.DARK_GRAY, self.back_button,
            border_radius=Constants.BUTTON_RADIUS,
        )
        back_label = self.font_stat.render("< Back", True, Constants.WHITE)
        surface.blit(back_label, back_label.get_rect(center=self.back_button.center))

        # Pokemon cards (includes locked, shown greyed out)
        pokemon_list = self.game.get_all_pokemon()
        cols = 4
        start_x = 40
        start_y = 80 - self.scroll_offset

        for i, pokemon in enumerate(pokemon_list):
            col = i % cols
            row = i // cols
            x = start_x + col * (Constants.CARD_WIDTH + Constants.CARD_PADDING)
            y = start_y + row * (Constants.CARD_HEIGHT + Constants.CARD_PADDING)

            # Skip cards above visible area
            if y + Constants.CARD_HEIGHT < 70 or y > Constants.SCREEN_HEIGHT:
                continue

            # Card background
            is_selected = i == self.selected_index
            is_locked = pokemon.locked
            if is_locked:
                bg_color = (200, 200, 200)
                border_color = (160, 160, 160)
            elif is_selected:
                bg_color = Constants.LIGHT_GRAY
                border_color = Constants.BLUE
            else:
                bg_color = Constants.LIGHT_GRAY
                border_color = Constants.GRAY
            card_rect = pygame.Rect(x, y, Constants.CARD_WIDTH, Constants.CARD_HEIGHT)
            pygame.draw.rect(surface, bg_color, card_rect, border_radius=6)
            pygame.draw.rect(surface, border_color, card_rect, width=3, border_radius=6)

            # Sprite
            if pokemon.name in self.sprites:
                sprite = self.sprites[pokemon.name]
                surface.blit(sprite, (x + Constants.CARD_WIDTH // 2 - 40, y + 5))
            else:
                # Placeholder circle
                pygame.draw.circle(
                    surface, Constants.GRAY,
                    (x + Constants.CARD_WIDTH // 2, y + 45), 30,
                )

            # Locked overlay text
            if is_locked:
                lock_surf = self.font_stat.render("LOCKED", True, (120, 120, 120))
                surface.blit(
                    lock_surf,
                    (x + Constants.CARD_WIDTH // 2 - lock_surf.get_width() // 2, y + 45),
                )

            # Name
            name_color = (160, 160, 160) if is_locked else Constants.BLACK
            name_surf = self.font_name.render(pokemon.name, True, name_color)
            surface.blit(
                name_surf,
                (x + Constants.CARD_WIDTH // 2 - name_surf.get_width() // 2, y + 90),
            )

            # Type badge(s)
            badge_y = y + 112
            total_width = sum(
                self.font_stat.size(t)[0] + 16 for t in pokemon.types
            ) + 4 * (len(pokemon.types) - 1)
            badge_x = x + Constants.CARD_WIDTH // 2 - total_width // 2
            for ptype in pokemon.types:
                color = Constants.TYPE_COLORS.get(ptype, Constants.GRAY)
                tw, th = self.font_stat.size(ptype)
                badge_rect = pygame.Rect(badge_x, badge_y, tw + 16, th + 4)
                pygame.draw.rect(surface, color, badge_rect, border_radius=4)
                type_surf = self.font_stat.render(ptype, True, Constants.WHITE)
                surface.blit(type_surf, (badge_x + 8, badge_y + 2))
                badge_x += tw + 20

            # Stats line
            stat_text = f"HP:{pokemon.hp} ATK:{pokemon.attack} DEF:{pokemon.defense}"
            stat_surf = self.font_stat.render(stat_text, True, Constants.DARK_GRAY)
            surface.blit(
                stat_surf,
                (x + Constants.CARD_WIDTH // 2 - stat_surf.get_width() // 2, y + 135),
            )

        # Confirm button
        if self.selected_index is not None:
            pygame.draw.rect(
                surface, Constants.GREEN, self.confirm_button,
                border_radius=Constants.BUTTON_RADIUS,
            )
            confirm_label = self.font_button.render("Confirm", True, Constants.WHITE)
            surface.blit(
                confirm_label,
                confirm_label.get_rect(center=self.confirm_button.center),
            )

            # Show selected name
            sel_pokemon = pokemon_list[self.selected_index]
            sel_text = self.font_stat.render(
                f"Selected: {sel_pokemon.name}", True, Constants.BLUE
            )
            surface.blit(
                sel_text,
                (Constants.SCREEN_WIDTH // 2 - sel_text.get_width() // 2,
                 Constants.SCREEN_HEIGHT - 90),
            )
