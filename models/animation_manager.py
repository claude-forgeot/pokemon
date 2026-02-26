"""Animation manager module -- manages combat visual effects."""

import random


class AnimationManager:
    """Manages combat animations: shake, flash, and progressive HP bar.

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

    SHAKE_AMPLITUDE = 6
    HP_ANIM_SPEED = 0.02
    HP_ANIM_THRESHOLD = 0.005

    def __init__(self):
        """Initialise the AnimationManager with all animations idle."""
        self.shake_frames_remaining = 0
        self._shake_offset_x = 0
        self._shake_offset_y = 0

        self.flash_frames_remaining = 0
        self._flash_total_duration = 0
        self._flash_color = None

        self.animating_hp = False
        self.current_hp_ratio = 0.0
        self._target_hp_ratio = 0.0

    def start_shake(self, duration=10):
        """Begin a sprite shake effect.

        Args:
            duration: Number of frames the shake lasts (default 10).
        """
        self.shake_frames_remaining = duration
        self._update_shake_offset()

    def start_flash(self, color, duration=8):
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

    def start_hp_animation(self, current_ratio, target_ratio):
        """Begin progressive HP bar animation.

        Instead of jumping the HP bar instantly to its new value, this
        smoothly slides it from ``current_ratio`` to ``target_ratio``.

        Args:
            current_ratio: Starting HP ratio (0.0 -- 1.0).
            target_ratio:  Ending HP ratio (0.0 -- 1.0).
        """
        self.current_hp_ratio = float(current_ratio)
        self._target_hp_ratio = float(target_ratio)
        if abs(self.current_hp_ratio - self._target_hp_ratio) > self.HP_ANIM_THRESHOLD:
            self.animating_hp = True
        else:
            self.current_hp_ratio = self._target_hp_ratio
            self.animating_hp = False

    def update(self):
        """Advance every active animation by one frame."""
        self._update_shake()
        self._update_flash()
        self._update_hp()

    def get_shake_offset(self):
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

        Returns:
            tuple or None: (R, G, B, alpha) while flashing, None otherwise.
        """
        if self.flash_frames_remaining <= 0 or self._flash_color is None:
            return None

        alpha = int(
            180 * (self.flash_frames_remaining / self._flash_total_duration)
        )
        r, g, b = self._flash_color
        return (r, g, b, alpha)

    def is_animating(self):
        """Return True if any animation is currently running.

        Returns:
            bool: True if shake, flash, or HP bar animation is active.
        """
        return (
            self.shake_frames_remaining > 0
            or self.flash_frames_remaining > 0
            or self.animating_hp
        )

    def _update_shake(self):
        """Advance the shake animation by one frame."""
        if self.shake_frames_remaining > 0:
            self.shake_frames_remaining -= 1
            if self.shake_frames_remaining > 0:
                self._update_shake_offset()
            else:
                self._shake_offset_x = 0
                self._shake_offset_y = 0

    def _update_shake_offset(self):
        """Randomise the current shake pixel offset."""
        amp = self.SHAKE_AMPLITUDE
        self._shake_offset_x = random.randint(-amp, amp)
        self._shake_offset_y = random.randint(-amp, amp)

    def _update_flash(self):
        """Advance the flash animation by one frame."""
        if self.flash_frames_remaining > 0:
            self.flash_frames_remaining -= 1

    def _update_hp(self):
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

        step = min(self.HP_ANIM_SPEED, abs(diff))
        if diff < 0:
            step = -step
        self.current_hp_ratio += step
