"""Combat screen module -- battle interface with attack button and HP bars."""

import os

import pygame

from combat import Combat
from game_state import GameState
from gui.base_screen import BaseScreen
from gui.constants import Constants


class CombatScreen(BaseScreen):
    """Battle screen: two Pokemon face to face, attack button, combat log.

    POO: This screen demonstrates the state machine sub-pattern -- the combat
    itself has phases: "player_turn", "opponent_turn", "waiting", "finished".
    """

    def __init__(self, game, player_pokemon, opponent_pokemon):
        """Initialize the combat screen.

        Args:
            game: The Game instance.
            player_pokemon: The player's chosen Pokemon.
            opponent_pokemon: The randomly selected opponent.
        """
        super().__init__(game)
        self.player = player_pokemon
        self.opponent = opponent_pokemon
        self.combat = Combat(player_pokemon, opponent_pokemon, game.type_chart)

        self.font_name = pygame.font.SysFont("arial", 22, bold=True)
        self.font_stat = pygame.font.SysFont("arial", 16)
        self.font_log = pygame.font.SysFont("arial", 15)
        self.font_button = pygame.font.SysFont("arial", 22, bold=True)

        self.log_messages = []
        self.phase = "player_turn"  # player_turn, opponent_turn, finished
        self.turn_timer = 0
        self.winner = None

        # Attack button
        self.attack_button = pygame.Rect(
            Constants.SCREEN_WIDTH // 2 - 100,
            Constants.SCREEN_HEIGHT - 80,
            200, 50,
        )

        # Load sprites
        self.player_sprite = self._load_sprite(player_pokemon.sprite_path)
        self.opponent_sprite = self._load_sprite(opponent_pokemon.sprite_path)

    def _load_sprite(self, path):
        """Load and scale a sprite, returning None if unavailable."""
        if path and os.path.isfile(path):
            try:
                img = pygame.image.load(path)
                return pygame.transform.scale(img, (128, 128))
            except pygame.error:
                pass
        return None

    def _add_log(self, message):
        """Add a message to the combat log (keep last 6)."""
        self.log_messages.append(message)
        if len(self.log_messages) > 6:
            self.log_messages.pop(0)

    def handle_events(self, events):
        """Handle attack button clicks.

        Returns:
            GameState or None: RESULT when combat ends, else None.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.phase == "finished":
                    # Register opponent to pokedex
                    self.combat.register_to_pokedex(self.opponent, self.game.pokedex)
                    return GameState.RESULT

                if self.phase == "player_turn":
                    if self.attack_button.collidepoint(event.pos):
                        self._do_player_attack()
        return None

    def _do_player_attack(self):
        """Execute the player's attack, then opponent's if combat continues."""
        result = self.combat.attack(self.player, self.opponent)
        self._add_log(result["message"])

        if result["ko"]:
            self.winner = self.player.name
            self.phase = "finished"
            self._add_log(f"{self.player.name} wins!")
            return

        # Opponent's turn
        self.phase = "opponent_turn"
        opp_result = self.combat.attack(self.opponent, self.player)
        self._add_log(opp_result["message"])

        if opp_result["ko"]:
            self.winner = self.opponent.name
            self.phase = "finished"
            self._add_log(f"{self.opponent.name} wins!")
            return

        self.phase = "player_turn"

    def update(self):
        """No frame-by-frame update logic in MVP."""

    def draw(self, surface):
        """Draw the combat interface."""
        surface.fill(Constants.WHITE)

        # -- Opponent (top right) --
        self._draw_pokemon_panel(
            surface, self.opponent, self.opponent_sprite,
            x=Constants.SCREEN_WIDTH - 280, y=40, is_player=False,
        )

        # -- Player (bottom left) --
        self._draw_pokemon_panel(
            surface, self.player, self.player_sprite,
            x=50, y=220, is_player=True,
        )

        # -- VS label --
        vs_surf = self.font_name.render("VS", True, Constants.RED)
        surface.blit(
            vs_surf,
            (Constants.SCREEN_WIDTH // 2 - vs_surf.get_width() // 2, 180),
        )

        # -- Combat log --
        log_y = 400
        pygame.draw.rect(
            surface, Constants.LIGHT_GRAY,
            pygame.Rect(30, log_y, Constants.SCREEN_WIDTH - 60, 120),
            border_radius=6,
        )
        for i, msg in enumerate(self.log_messages):
            msg_surf = self.font_log.render(msg, True, Constants.BLACK)
            surface.blit(msg_surf, (40, log_y + 8 + i * 18))

        # -- Attack / Continue button --
        if self.phase == "finished":
            pygame.draw.rect(
                surface, Constants.BLUE, self.attack_button,
                border_radius=Constants.BUTTON_RADIUS,
            )
            btn_label = self.font_button.render("Continue", True, Constants.WHITE)
        else:
            color = Constants.RED if self.phase == "player_turn" else Constants.GRAY
            pygame.draw.rect(
                surface, color, self.attack_button,
                border_radius=Constants.BUTTON_RADIUS,
            )
            btn_label = self.font_button.render("Attack!", True, Constants.WHITE)
        surface.blit(
            btn_label, btn_label.get_rect(center=self.attack_button.center)
        )

    def _draw_pokemon_panel(self, surface, pokemon, sprite, x, y, is_player):
        """Draw one Pokemon's sprite, name, HP bar, and type badges.

        Args:
            surface: Pygame surface to draw on.
            pokemon: The Pokemon object.
            sprite: Loaded sprite Surface or None.
            x: X position of the panel.
            y: Y position of the panel.
            is_player: True if this is the player's panel (label "YOU").
        """
        # Sprite
        if sprite:
            surface.blit(sprite, (x, y))
        else:
            pygame.draw.rect(
                surface, Constants.LIGHT_GRAY,
                pygame.Rect(x, y, 128, 128), border_radius=8,
            )
            placeholder = self.font_stat.render("?", True, Constants.DARK_GRAY)
            surface.blit(placeholder, (x + 56, y + 52))

        # Info panel to the right of sprite
        info_x = x + 140
        info_y = y + 5

        # Name + label
        label = " (YOU)" if is_player else " (FOE)"
        name_surf = self.font_name.render(pokemon.name + label, True, Constants.BLACK)
        surface.blit(name_surf, (info_x, info_y))

        # HP bar
        bar_y = info_y + 30
        bar_width = 160
        bar_height = 16
        hp_ratio = pokemon.hp / pokemon.max_hp if pokemon.max_hp > 0 else 0
        if hp_ratio > 0.5:
            bar_color = Constants.HP_GREEN
        elif hp_ratio > 0.2:
            bar_color = Constants.HP_YELLOW
        else:
            bar_color = Constants.HP_RED

        # Background
        pygame.draw.rect(
            surface, Constants.GRAY,
            pygame.Rect(info_x, bar_y, bar_width, bar_height),
            border_radius=4,
        )
        # Filled portion
        if hp_ratio > 0:
            pygame.draw.rect(
                surface, bar_color,
                pygame.Rect(info_x, bar_y, int(bar_width * hp_ratio), bar_height),
                border_radius=4,
            )
        # HP text
        hp_text = f"{pokemon.hp}/{pokemon.max_hp}"
        hp_surf = self.font_stat.render(hp_text, True, Constants.BLACK)
        surface.blit(hp_surf, (info_x + bar_width + 8, bar_y - 1))

        # Types
        type_y = bar_y + 24
        badge_x = info_x
        for ptype in pokemon.types:
            color = Constants.TYPE_COLORS.get(ptype, Constants.GRAY)
            tw, th = self.font_stat.size(ptype)
            badge_rect = pygame.Rect(badge_x, type_y, tw + 12, th + 2)
            pygame.draw.rect(surface, color, badge_rect, border_radius=4)
            type_surf = self.font_stat.render(ptype, True, Constants.WHITE)
            surface.blit(type_surf, (badge_x + 6, type_y + 1))
            badge_x += tw + 16

        # Stats
        stat_y = type_y + 22
        stat_text = f"ATK: {pokemon.attack}  DEF: {pokemon.defense}  Lv.{pokemon.level}"
        stat_surf = self.font_stat.render(stat_text, True, Constants.DARK_GRAY)
        surface.blit(stat_surf, (info_x, stat_y))
