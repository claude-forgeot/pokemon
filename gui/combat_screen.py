"""Combat screen -- battle interface with attack, switch, and forfeit."""

import os
import random

import pygame

from combat import Combat
from game_state import GameState
from gui.base_screen import BaseScreen
from gui.constants import Constants


class CombatScreen(BaseScreen):
    """Battle screen with team support, switch, and forfeit options."""

    def __init__(self, game, player_team, opponent_team):
        """Initialize combat with two teams of Pokemon.

        Args:
            game: The Game instance.
            player_team: List of player's Pokemon.
            opponent_team: List of opponent's Pokemon.
        """
        super().__init__(game)
        self.player_team = player_team
        self.opponent_team = opponent_team
        self.player_index = 0
        self.opponent_index = 0
        self.player = self.player_team[0]
        self.opponent = self.opponent_team[0]
        self.combat = Combat(self.player, self.opponent, game.type_chart)

        self.font_name = pygame.font.SysFont("arial", 22, bold=True)
        self.font_stat = pygame.font.SysFont("arial", 16)
        self.font_log = pygame.font.SysFont("arial", 15)
        self.font_button = pygame.font.SysFont("arial", 20, bold=True)

        self.log_messages = []
        self.phase = "player_turn"
        self.winner = None
        self.show_switch = False

        # Buttons
        btn_y = Constants.SCREEN_HEIGHT - 75
        self.attack_button = pygame.Rect(50, btn_y, 150, 45)
        self.switch_button = pygame.Rect(220, btn_y, 150, 45)
        self.forfeit_button = pygame.Rect(390, btn_y, 150, 45)
        self.continue_button = pygame.Rect(
            Constants.SCREEN_WIDTH // 2 - 100, btn_y, 200, 45
        )

        # Switch menu buttons (built when needed)
        self.switch_buttons = []

        # Load sprites
        self.player_sprite = self._load_sprite(self.player.sprite_path)
        self.opponent_sprite = self._load_sprite(self.opponent.sprite_path)

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
        """Add a message to the combat log (keep last 5)."""
        self.log_messages.append(message)
        if len(self.log_messages) > 5:
            self.log_messages.pop(0)

    def _next_alive_opponent(self):
        """Switch opponent to next alive Pokemon. Returns False if none left."""
        for i, p in enumerate(self.opponent_team):
            if p.is_alive() and i != self.opponent_index:
                self.opponent_index = i
                self.opponent = self.opponent_team[i]
                self.combat = Combat(self.player, self.opponent, self.game.type_chart)
                self.opponent_sprite = self._load_sprite(self.opponent.sprite_path)
                self._add_log(f"Opponent sends {self.opponent.name}!")
                return True
        return False

    def _all_fainted(self, team):
        """Check if all Pokemon in a team are KO."""
        return all(not p.is_alive() for p in team)

    def handle_events(self, events):
        """Handle button clicks for attack, switch, forfeit."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # Finished state - click continue
                if self.phase == "finished":
                    for p in self.opponent_team:
                        self.combat.register_to_pokedex(p, self.game.pokedex)
                    return GameState.RESULT

                # Switch menu is open
                if self.show_switch:
                    for i, btn in self.switch_buttons:
                        if btn.collidepoint(event.pos):
                            self._do_switch(i)
                            self.show_switch = False
                            return None
                    # Click anywhere else closes switch menu
                    self.show_switch = False
                    return None

                # Player turn actions
                if self.phase == "player_turn":
                    if self.attack_button.collidepoint(event.pos):
                        self._do_player_attack()
                    elif self.switch_button.collidepoint(event.pos):
                        alive = [(i, p) for i, p in enumerate(self.player_team)
                                 if p.is_alive() and i != self.player_index]
                        if alive:
                            self.show_switch = True
                            self._build_switch_buttons(alive)
                    elif self.forfeit_button.collidepoint(event.pos):
                        self._add_log("You forfeited the battle!")
                        self.winner = self.opponent.name
                        self.phase = "finished"

        return None

    def _build_switch_buttons(self, alive_list):
        """Create button rectangles for the switch menu."""
        self.switch_buttons = []
        start_y = 300
        for idx, (i, p) in enumerate(alive_list):
            btn = pygame.Rect(
                Constants.SCREEN_WIDTH // 2 - 120,
                start_y + idx * 45,
                240, 38
            )
            self.switch_buttons.append((i, btn))

    def _do_switch(self, new_index):
        """Switch player's active Pokemon and let opponent attack."""
        old_name = self.player.name
        self.player_index = new_index
        self.player = self.player_team[new_index]
        self.combat = Combat(self.player, self.opponent, self.game.type_chart)
        self.player_sprite = self._load_sprite(self.player.sprite_path)
        self._add_log(f"You switched {old_name} for {self.player.name}!")

        # Opponent attacks after switch
        opp_result = self.combat.attack(self.opponent, self.player)
        self._add_log(opp_result["message"])
        if opp_result["ko"]:
            self._handle_player_faint()

    def _do_player_attack(self):
        """Execute player attack, then opponent attacks back."""
        result = self.combat.attack(self.player, self.opponent)
        self._add_log(result["message"])

        if result["ko"]:
            if self._all_fainted(self.opponent_team):
                self.winner = self.player.name
                self.phase = "finished"
                self._add_log("You win the battle!")
                return
            else:
                self._next_alive_opponent()

        # Opponent attacks back
        self.phase = "opponent_turn"
        opp_result = self.combat.attack(self.opponent, self.player)
        self._add_log(opp_result["message"])

        if opp_result["ko"]:
            self._handle_player_faint()
            return

        self.phase = "player_turn"

    def _handle_player_faint(self):
        """Handle when current player Pokemon faints."""
        if self._all_fainted(self.player_team):
            self.winner = self.opponent.name
            self.phase = "finished"
            self._add_log("You lost the battle!")
        else:
            # Auto-switch to next alive Pokemon
            for i, p in enumerate(self.player_team):
                if p.is_alive():
                    self.player_index = i
                    self.player = p
                    self.combat = Combat(self.player, self.opponent, self.game.type_chart)
                    self.player_sprite = self._load_sprite(self.player.sprite_path)
                    self._add_log(f"Go, {self.player.name}!")
                    self.phase = "player_turn"
                    break

    def update(self):
        """No frame update needed."""

    def draw(self, surface):
        """Draw the combat interface."""
        surface.fill(Constants.WHITE)

        # Opponent panel (top right)
        self._draw_pokemon_panel(
            surface, self.opponent, self.opponent_sprite,
            x=Constants.SCREEN_WIDTH - 280, y=30, is_player=False,
        )
        # Opponent team pokeballs
        self._draw_team_balls(surface, self.opponent_team, Constants.SCREEN_WIDTH - 280, 20)

        # Player panel (bottom left)
        self._draw_pokemon_panel(
            surface, self.player, self.player_sprite,
            x=50, y=200, is_player=True,
        )
        # Player team pokeballs
        self._draw_team_balls(surface, self.player_team, 50, 190)

        # VS label
        vs_surf = self.font_name.render("VS", True, Constants.RED)
        surface.blit(
            vs_surf,
            (Constants.SCREEN_WIDTH // 2 - vs_surf.get_width() // 2, 165),
        )

        # Combat log
        log_y = 380
        pygame.draw.rect(
            surface, Constants.LIGHT_GRAY,
            pygame.Rect(30, log_y, Constants.SCREEN_WIDTH - 60, 110),
            border_radius=6,
        )
        for i, msg in enumerate(self.log_messages):
            msg_surf = self.font_log.render(msg, True, Constants.BLACK)
            surface.blit(msg_surf, (40, log_y + 8 + i * 20))

        # Buttons
        if self.phase == "finished":
            pygame.draw.rect(
                surface, Constants.BLUE, self.continue_button,
                border_radius=Constants.BUTTON_RADIUS,
            )
            btn_label = self.font_button.render("Continue", True, Constants.WHITE)
            surface.blit(btn_label, btn_label.get_rect(center=self.continue_button.center))
        else:
            # Attack
            color = Constants.RED if self.phase == "player_turn" else Constants.GRAY
            pygame.draw.rect(surface, color, self.attack_button,
                             border_radius=Constants.BUTTON_RADIUS)
            atk_label = self.font_button.render("Attack!", True, Constants.WHITE)
            surface.blit(atk_label, atk_label.get_rect(center=self.attack_button.center))

            # Switch
            has_alive = any(p.is_alive() and i != self.player_index
                           for i, p in enumerate(self.player_team))
            sw_color = Constants.BLUE if has_alive else Constants.GRAY
            pygame.draw.rect(surface, sw_color, self.switch_button,
                             border_radius=Constants.BUTTON_RADIUS)
            sw_label = self.font_button.render("Switch", True, Constants.WHITE)
            surface.blit(sw_label, sw_label.get_rect(center=self.switch_button.center))

            # Forfeit
            pygame.draw.rect(surface, Constants.DARK_GRAY, self.forfeit_button,
                             border_radius=Constants.BUTTON_RADIUS)
            ff_label = self.font_button.render("Forfeit", True, Constants.WHITE)
            surface.blit(ff_label, ff_label.get_rect(center=self.forfeit_button.center))

        # Switch menu overlay
        if self.show_switch:
            overlay = pygame.Surface(
                (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 120))
            surface.blit(overlay, (0, 0))

            title = self.font_name.render("Switch to:", True, Constants.WHITE)
            surface.blit(title, (Constants.SCREEN_WIDTH // 2 - title.get_width() // 2, 260))

            for i, btn in self.switch_buttons:
                p = self.player_team[i]
                pygame.draw.rect(surface, Constants.BLUE, btn, border_radius=6)
                text = f"{p.name}  HP:{p.hp}/{p.max_hp}"
                text_surf = self.font_stat.render(text, True, Constants.WHITE)
                surface.blit(text_surf, text_surf.get_rect(center=btn.center))

    def _draw_team_balls(self, surface, team, x, y):
        """Draw pokeball indicators for a team (filled = alive, empty = KO)."""
        for i, p in enumerate(team):
            center = (x + i * 22 + 10, y)
            if p.is_alive():
                pygame.draw.circle(surface, Constants.RED, center, 8)
            else:
                pygame.draw.circle(surface, Constants.GRAY, center, 8)
            pygame.draw.circle(surface, Constants.BLACK, center, 8, 1)

    def _draw_pokemon_panel(self, surface, pokemon, sprite, x, y, is_player):
        """Draw one Pokemon's sprite, name, HP bar, and type badges."""
        if sprite:
            surface.blit(sprite, (x, y))
        else:
            pygame.draw.rect(
                surface, Constants.LIGHT_GRAY,
                pygame.Rect(x, y, 128, 128), border_radius=8,
            )
            placeholder = self.font_stat.render("?", True, Constants.DARK_GRAY)
            surface.blit(placeholder, (x + 56, y + 52))

        info_x = x + 140
        info_y = y + 5

        label = " (YOU)" if is_player else " (FOE)"
        name_surf = self.font_name.render(pokemon.name + label, True, Constants.BLACK)
        surface.blit(name_surf, (info_x, info_y))

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

        pygame.draw.rect(
            surface, Constants.GRAY,
            pygame.Rect(info_x, bar_y, bar_width, bar_height),
            border_radius=4,
        )
        if hp_ratio > 0:
            pygame.draw.rect(
                surface, bar_color,
                pygame.Rect(info_x, bar_y, int(bar_width * hp_ratio), bar_height),
                border_radius=4,
            )
        hp_text = f"{pokemon.hp}/{pokemon.max_hp}"
        hp_surf = self.font_stat.render(hp_text, True, Constants.BLACK)
        surface.blit(hp_surf, (info_x + bar_width + 8, bar_y - 1))

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

        stat_y = type_y + 22
        stat_text = f"ATK:{pokemon.attack}  DEF:{pokemon.defense}  Lv.{pokemon.level}"
        stat_surf = self.font_stat.render(stat_text, True, Constants.DARK_GRAY)
        surface.blit(stat_surf, (info_x, stat_y))
