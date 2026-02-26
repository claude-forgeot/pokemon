"""Animation manager module -- manages combat visual effects."""

import random


class AnimationManager:
    """Manages combat animations: shake, flash, and progressive HP bar.

    POO: This class demonstrates ENCAPSULATION -- all animation state
    (counters, colors, ratios) is kept private inside the object. The rest
    of the game only interacts through public methods (start_shake,
    start_flash, start_hp_animation, update, is_animating, etc.).

    Also demonstrates the UPDATE PATTERN used in game loops: every frame
    the game calls update(), which advances each active animation by one
    step. This decouples the animation logic from the rendering logic.

    Usage::

        anim = AnimationManager()

        # Trigger effects when a hit lands
        anim.start_shake(duration=12)
        anim.start_flash(color=(255, 255, 255), duration=8)
        anim.start_hp_animation(current_ratio=1.0, target_ratio=0.6)

        # In the game loop, each frame:
        anim.update()

        # In draw():
        dx, dy = anim.get_shake_offset()
        flash_color = anim.get_flash_color()
        hp_ratio = anim.current_hp_ratio
    """

    # How far the sprite can shake (pixels in each direction)
    SHAKE_AMPLITUDE = 6

    # How quickly the HP bar moves toward its target per frame (ratio per frame)
    HP_ANIM_SPEED = 0.02

    # How close current_hp_ratio must be to target to stop animating
    HP_ANIM_THRESHOLD = 0.005

    def __init__(self):
        """Initialise the AnimationManager with all animations idle."""
        # -- Shake state --
        # Number of frames the shake should still run for.
        self.shake_frames_remaining = 0
        # Current pixel offset applied to the sprite being shaken.
        self._shake_offset_x = 0
        self._shake_offset_y = 0

        # -- Flash state --
        # Number of frames the flash overlay should still be visible.
        self.flash_frames_remaining = 0
        # Initial duration used to fade the flash out linearly.
        self._flash_total_duration = 0
        # The base color of the flash (R, G, B).
        self._flash_color = None

        # -- HP bar animation state --
        # True while the HP bar is still animating toward its target.
        self.animating_hp = False
        # The displayed HP ratio (0.0 -- 1.0), updated each frame.
        self.current_hp_ratio = 0.0
        # The target HP ratio the bar is converging toward.
        self._target_hp_ratio = 0.0

    # ------------------------------------------------------------------
    # Public: trigger animation effects
    # ------------------------------------------------------------------

    def start_shake(self, duration: int = 10) -> None:
        """Begin a sprite shake effect.

        POO: This is a COMMAND method -- it changes state but returns nothing.
        The caller tells the object *what* to do, not *how* to do it.

        Args:
            duration: Number of frames the shake lasts (default 10).
        """
        self.shake_frames_remaining = duration
        self._update_shake_offset()

    def start_flash(self, color: tuple, duration: int = 8) -> None:
        """Begin a screen-overlay flash effect.

        The flash is rendered as a semi-transparent colored rectangle over
        the target sprite. It fades out linearly over ``duration`` frames.

        Args:
            color:    (R, G, B) base color for the flash.
            duration: Number of frames the flash lasts (default 8).
        """
        self._flash_color = color
        self.flash_frames_remaining = duration
        self._flash_total_duration = duration

    def start_hp_animation(self, current_ratio: float, target_ratio: float) -> None:
        """Begin progressive HP bar animation.

        Instead of jumping the HP bar instantly to its new value, this
        smoothly slides it from ``current_ratio`` to ``target_ratio``.

        Args:
            current_ratio: Starting HP ratio (0.0 -- 1.0).
            target_ratio:  Ending HP ratio (0.0 -- 1.0).
        """
        self.current_hp_ratio = float(current_ratio)
        self._target_hp_ratio = float(target_ratio)
        # Only animate if there is actually a visible difference
        if abs(self.current_hp_ratio - self._target_hp_ratio) > self.HP_ANIM_THRESHOLD:
            self.animating_hp = True
        else:
            self.current_hp_ratio = self._target_hp_ratio
            self.animating_hp = False

    # ------------------------------------------------------------------
    # Public: advance all animations by one frame
    # ------------------------------------------------------------------

    def update(self) -> None:
        """Advance every active animation by one frame.

        POO: This is the UPDATE PATTERN -- a single entry point called
        once per frame by the game loop. It keeps all time-based logic
        in one place instead of scattered across draw() calls.
        """
        self._update_shake()
        self._update_flash()
        self._update_hp()

    # ------------------------------------------------------------------
    # Public: query current animation state (used by draw methods)
    # ------------------------------------------------------------------

    def get_shake_offset(self) -> tuple:
        """Return the current (dx, dy) pixel offset for the shaking sprite.

        Returns:
            tuple: (dx, dy) in pixels. (0, 0) when shake is inactive.
        """
        if self.shake_frames_remaining > 0:
            return (self._shake_offset_x, self._shake_offset_y)
        return (0, 0)

    def get_flash_color(self):
        """Return the current flash color with alpha, or None if inactive.

        The alpha fades from full opacity down to 0 as the flash runs out.
        CombatScreen can blit a Surface of this color over the sprite.

        Returns:
            tuple or None: (R, G, B, alpha) while flashing, None otherwise.
        """
        if self.flash_frames_remaining <= 0 or self._flash_color is None:
            return None

        # Linear fade: full alpha at start, 0 at the last frame
        alpha = int(
            180 * (self.flash_frames_remaining / self._flash_total_duration)
        )
        r, g, b = self._flash_color
        return (r, g, b, alpha)

    def is_animating(self) -> bool:
        """Return True if any animation is currently running.

        POO: This is a QUERY method (returns information without side
        effects). CombatScreen can use it to block player input while
        animations are playing.

        Returns:
            bool: True if shake, flash, or HP bar animation is active.
        """
        return (
            self.shake_frames_remaining > 0
            or self.flash_frames_remaining > 0
            or self.animating_hp
        )

    # ------------------------------------------------------------------
    # Private helpers: one method per animation type
    # ------------------------------------------------------------------

    def _update_shake(self) -> None:
        """Advance the shake animation by one frame."""
        if self.shake_frames_remaining > 0:
            self.shake_frames_remaining -= 1
            if self.shake_frames_remaining > 0:
                self._update_shake_offset()
            else:
                self._shake_offset_x = 0
                self._shake_offset_y = 0

    def _update_shake_offset(self) -> None:
        """Randomise the current shake pixel offset."""
        amp = self.SHAKE_AMPLITUDE
        self._shake_offset_x = random.randint(-amp, amp)
        self._shake_offset_y = random.randint(-amp, amp)

    def _update_flash(self) -> None:
        """Advance the flash animation by one frame."""
        if self.flash_frames_remaining > 0:
            self.flash_frames_remaining -= 1

    def _update_hp(self) -> None:
        """Advance the HP bar animation by one frame.

        Uses linear interpolation: move current_hp_ratio toward
        _target_hp_ratio by HP_ANIM_SPEED each frame, and stop once
        the difference is below HP_ANIM_THRESHOLD.
        """
        if not self.animating_hp:
            return

        diff = self._target_hp_ratio - self.current_hp_ratio

        if abs(diff) <= self.HP_ANIM_THRESHOLD:
            self.current_hp_ratio = self._target_hp_ratio
            self.animating_hp = False
            return

        # Move toward the target by at most HP_ANIM_SPEED per frame
        step = min(self.HP_ANIM_SPEED, abs(diff))
        if diff < 0:
            step = -step
        self.current_hp_ratio += step
