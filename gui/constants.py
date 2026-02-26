"""Constants module -- centralized game display constants."""

import pygame


class Constants:
    """Centralized game display constants."""

    # Window dimensions
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 60

    # Colors (R, G, B)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (220, 50, 50)
    GREEN = (50, 180, 50)
    BLUE = (50, 100, 220)
    GRAY = (180, 180, 180)
    LIGHT_GRAY = (220, 220, 220)
    DARK_GRAY = (100, 100, 100)
    SELECTED_BG = (200, 220, 255)

    # HP bar colors
    HP_GREEN = (34, 139, 34)
    HP_YELLOW = (218, 165, 32)
    HP_RED = (178, 34, 34)

    # UI constants
    BUTTON_WIDTH = 250
    BUTTON_HEIGHT = 50
    BUTTON_RADIUS = 8
    CARD_WIDTH = 150
    CARD_HEIGHT = 180
    CARD_PADDING = 15

    # Type colors for display
    TYPE_COLORS = {
        "normal": (168, 168, 120),
        "fire": (240, 128, 48),
        "water": (104, 144, 240),
        "electric": (248, 208, 48),
        "grass": (120, 200, 80),
        "ice": (152, 216, 216),
        "fighting": (192, 48, 40),
        "poison": (160, 64, 160),
        "ground": (224, 192, 104),
        "flying": (168, 144, 240),
        "psychic": (248, 88, 136),
        "bug": (168, 184, 32),
        "rock": (184, 160, 56),
        "ghost": (112, 88, 152),
        "dragon": (112, 56, 248),
        "dark": (112, 88, 72),
        "steel": (184, 184, 208),
        "fairy": (238, 153, 172),
    }

    def get_font(self, size, bold=False):
        """Return a cross-platform font using pygame's built-in default font.

        Args:
            size: Font size in pixels.
            bold: If True, use bold variant.

        Returns:
            A font object guaranteed to work on all platforms.
        """
        font = pygame.font.Font(None, size)
        font.set_bold(bold)
        return font
