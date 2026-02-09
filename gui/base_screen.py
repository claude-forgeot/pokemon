"""Base screen module -- abstract base class for all game screens."""

from abc import ABC, abstractmethod


class BaseScreen(ABC):
    """Abstract base class for all game screens.

    POO: ABSTRACT CLASS and INHERITANCE -- this class uses ABC (Abstract Base
    Class) to define an interface that all screens MUST follow. The @abstractmethod
    decorator marks methods that subclasses are REQUIRED to implement. You cannot
    create a BaseScreen directly (BaseScreen() raises an error); you must create
    a subclass like MenuScreen that implements all abstract methods.

    INHERITANCE means a child class (MenuScreen) automatically gets everything
    from its parent (BaseScreen) and can add or override behavior. The child
    "is-a" BaseScreen.
    """

    def __init__(self, game):
        """Initialize with a reference to the Game instance.

        Args:
            game: The Game instance holding all game state.
        """
        self.game = game

    @abstractmethod
    def handle_events(self, events):
        """Process Pygame events (clicks, keys, etc.).

        Args:
            events: List of pygame.event.Event from pygame.event.get().

        Returns:
            GameState or None: The next state to transition to,
                or None to stay on this screen.
        """

    @abstractmethod
    def update(self):
        """Update screen logic (animations, timers, etc.).

        Called once per frame before draw().
        """

    @abstractmethod
    def draw(self, surface):
        """Render this screen to the given surface.

        Args:
            surface: The pygame.Surface to draw on (usually the main window).
        """
