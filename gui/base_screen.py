"""Base screen module -- parent class for all game screens."""

import os

import pygame

from gui.constants import Constants


class BaseScreen:
    """Parent class for all game screens.

    POO: INHERITANCE -- this class defines the interface that all screens
    follow. Each child class (MenuScreen, CombatScreen, etc.) inherits from
    BaseScreen and implements these three methods. The child "is-a" BaseScreen.

    The three methods (handle_events, update, draw) form the game loop pattern:
    each frame, the main loop calls them in order on the current screen.
    """

    def __init__(self, game):
        """Initialize with a reference to the Game instance.

        Args:
            game: The Game instance holding all game state.
        """
        self.game = game

    def handle_events(self, events):
        """Process Pygame events (clicks, keys, etc.).

        Args:
            events: List of pygame.event.Event from pygame.event.get().

        Returns:
            GameState or None: The next state to transition to,
                or None to stay on this screen.
        """
        pass

    def update(self):
        """Update screen logic (animations, timers, etc.).

        Called once per frame before draw().
        """
        pass

    def draw(self, surface):
        """Render this screen to the given surface.

        Args:
            surface: The pygame.Surface to draw on (usually the main window).
        """
        pass

    def _load_sprites(self, size=(80, 80)):
        """Load all Pokemon sprites into self.sprites dict.

        Args:
            size: Tuple (width, height) for sprite scaling.
        """
        self.sprites = {}
        for pokemon in self.game.get_all_pokemon():
            path = pokemon.sprite_path
            if path and os.path.isfile(path):
                try:
                    img = pygame.image.load(path)
                    self.sprites[pokemon.name] = pygame.transform.scale(img, size)
                except pygame.error:
                    pass

    @staticmethod
    def draw_type_badges(surface, font, types, x, y, padding=16, pad_inner=12, radius=4):
        """Draw colored type badges starting at (x, y).

        Args:
            surface: Pygame surface.
            font: Font for type text.
            types: List of type strings.
            x: Starting X position.
            y: Y position.
            padding: X spacing between badges.
            pad_inner: Horizontal padding inside badge.
            radius: Border radius.
        """
        badge_x = x
        for ptype in types:
            color = Constants.TYPE_COLORS.get(ptype, Constants.GRAY)
            tw, th = font.size(ptype)
            badge_rect = pygame.Rect(badge_x, y, tw + pad_inner, th + 2)
            pygame.draw.rect(surface, color, badge_rect, border_radius=radius)
            type_surf = font.render(ptype, True, Constants.WHITE)
            surface.blit(type_surf, (badge_x + pad_inner // 2, y + 1))
            badge_x += tw + pad_inner + 4
