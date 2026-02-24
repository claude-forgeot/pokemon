"""Base screen module -- parent class for all game screens."""


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
