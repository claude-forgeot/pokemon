"""Combat screen -- battle interface with attack, switch, and forfeit."""

import os
import random

import pygame

from models.animation_manager import AnimationManager
from models.combat import Combat
from models.game_state import GameState
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
        self.xp_message = ""
        self.show_switch = False
        self.show_moves = False

        # Animation managers for visual effects
        self.player_anim = AnimationManager()
        self.opponent_anim = AnimationManager()

        # Opponent attack delay
        self.opponent_attack_delay = 1500
        self.opponent_attack_timer = 0
        self.waiting_for_opponent = False

        self.font_move = pygame.font.SysFont("arial", 14, bold=True)

        # Buttons
        btn_y = 540
        self.attack_button = pygame.Rect(155, btn_y, 150, 45)
        self.switch_button = pygame.Rect(325, btn_y, 150, 45)
        self.forfeit_button = pygame.Rect(495, btn_y, 150, 45)
        self.continue_button = pygame.Rect(300, btn_y, 200, 45)

        # Move buttons (built dynamically)
        self.move_buttons = []

        # Switch menu buttons (built when needed)
        self.switch_buttons = []

        # Load battle background
        bg_path = os.path.join("assets", "backgrounds", "battle_arena.png")
        if os.path.exists(bg_path):
            self.background = pygame.image.load(bg_path).convert()
        else:
            self.background = None

        # Load sprites
        self.player_sprite = self._load_sprite(self.player.sprite_path)
        self.opponent_sprite = self._load_sprite(self.opponent.sprite_path)

        # Initialize HP animation ratios
        self.player_anim.current_hp_ratio = self.player.hp / self.player.max_hp if self.player.max_hp > 0 else 1.0
        self.opponent_anim.current_hp_ratio = self.opponent.hp / self.opponent.max_hp if self.opponent.max_hp > 0 else 1.0

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

    def _get_flash_color(self, effective):
        """Return flash color based on move effectiveness."""
        if effective == "super":
            return (100, 255, 100)
        elif effective == "not_very":
            return (255, 100, 100)
        elif effective == "immune":
            return (150, 150, 150)
        return (255, 255, 255)

    def _next_alive_opponent(self):
        """Switch opponent to next alive Pokemon. Returns False if none left."""
        for i, p in enumerate(self.opponent_team):
            if p.is_alive() and i != self.opponent_index:
                self.opponent_index = i
                self.opponent = self.opponent_team[i]
                self.combat = Combat(self.player, self.opponent, self.game.type_chart)
                self.opponent_sprite = self._load_sprite(self.opponent.sprite_path)
                self.opponent_anim = AnimationManager()
                self.opponent_anim.current_hp_ratio = self.opponent.hp / self.opponent.max_hp if self.opponent.max_hp > 0 else 1.0
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

                # Block input during animations or opponent delay
                if self.waiting_for_opponent or self.player_anim.is_animating() or self.opponent_anim.is_animating():
                    return None

                # Finished state - click continue
                if self.phase == "finished":
                    for p in self.opponent_team:
                        self.combat.register_to_pokedex(p, self.game.pokedex)
                    return GameState.RESULT

                # Move menu is open
                if self.show_moves:
                    for move, btn in self.move_buttons:
                        if btn.collidepoint(event.pos):
                            self.show_moves = False
                            self._do_player_attack(move)
                            return None
                    # Click anywhere else closes move menu
                    self.show_moves = False
                    return None

                # Switch menu is open
                if self.show_switch:
                    for i, btn in self.switch_buttons:
                        if btn.collidepoint(event.pos):
                            if self.phase == "forced_switch":
                                # Forced switch: just switch, no opponent counter
                                self.player_index = i
                                self.player = self.player_team[i]
                                self.combat = Combat(
                                    self.player, self.opponent, self.game.type_chart
                                )
                                self.player_sprite = self._load_sprite(
                                    self.player.sprite_path
                                )
                                self._add_log(f"Go, {self.player.name}!")
                                self.phase = "player_turn"
                            else:
                                self._do_switch(i)
                            self.show_switch = False
                            return None
                    # Forced switch: cannot close without choosing
                    if self.phase != "forced_switch":
                        self.show_switch = False
                    return None

                # Player turn actions
                if self.phase == "player_turn":
                    if self.attack_button.collidepoint(event.pos):
                        if self.player.moves:
                            self.show_moves = True
                            self._build_move_buttons()
                        else:
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
                        self._finish_battle()

        return None

    def _build_move_buttons(self):
        """Create button rectangles for the player's current Pokemon's moves."""
        self.move_buttons = []
        moves = self.player.moves
        if not moves:
            return
        btn_w = 235
        btn_h = 42
        start_x = 160
        start_y = 260
        gap_x = 10
        gap_y = 8
        for idx, move in enumerate(moves[:4]):
            col = idx % 2
            row = idx // 2
            x = start_x + col * (btn_w + gap_x)
            y = start_y + row * (btn_h + gap_y)
            self.move_buttons.append((move, pygame.Rect(x, y, btn_w, btn_h)))

    def _pick_random_move(self, pokemon):
        """Pick a random move for the AI, or None if no moves."""
        if pokemon.moves:
            return random.choice(pokemon.moves)
        return None

    def _build_switch_buttons(self, alive_list):
        """Create button rectangles for the switch menu."""
        self.switch_buttons = []
        start_x = 260
        start_y = 164
        gap = 8
        for idx, (i, p) in enumerate(alive_list):
            btn = pygame.Rect(start_x, start_y + idx * (42 + gap), 280, 42)
            self.switch_buttons.append((i, btn))

    def _do_switch(self, new_index):
        """Switch player's active Pokemon and schedule opponent attack."""
        old_name = self.player.name
        self.player_index = new_index
        self.player = self.player_team[new_index]
        self.combat = Combat(self.player, self.opponent, self.game.type_chart)
        self.player_sprite = self._load_sprite(self.player.sprite_path)
        self._add_log(f"You switched {old_name} for {self.player.name}!")

        # Reset player HP animation for new Pokemon
        self.player_anim = AnimationManager()
        self.player_anim.current_hp_ratio = self.player.hp / self.player.max_hp if self.player.max_hp > 0 else 1.0

        # Schedule opponent attack after delay
        self.phase = "opponent_turn"
        self.waiting_for_opponent = True
        self.opponent_attack_timer = pygame.time.get_ticks()

    def _do_player_attack(self, move=None):
        """Execute player attack, trigger animations, schedule opponent."""
        result = self.combat.attack(self.player, self.opponent, move)
        self._add_log(result["message"])

        # Trigger animations on opponent
        if result["hit"]:
            self.opponent_anim.start_shake()
            self.opponent_anim.start_flash(
                self._get_flash_color(result["effective"])
            )
            hp_ratio = self.opponent.hp / self.opponent.max_hp if self.opponent.max_hp > 0 else 0
            self.opponent_anim.start_hp_animation(
                self.opponent_anim.current_hp_ratio, hp_ratio
            )

        if result["ko"]:
            if self._all_fainted(self.opponent_team):
                self.winner = self.player.name
                self._finish_battle()
                self._add_log("You win the battle!")
                return
            else:
                self._next_alive_opponent()

        # Schedule opponent attack after delay (instead of attacking immediately)
        self.phase = "opponent_turn"
        self.waiting_for_opponent = True
        self.opponent_attack_timer = pygame.time.get_ticks()

    def _do_opponent_attack(self):
        """Execute the opponent's attack (called after delay)."""
        self.waiting_for_opponent = False
        opp_move = self._pick_random_move(self.opponent)
        opp_result = self.combat.attack(self.opponent, self.player, opp_move)
        self._add_log(opp_result["message"])

        # Trigger animations on player
        if opp_result["hit"]:
            self.player_anim.start_shake()
            self.player_anim.start_flash(
                self._get_flash_color(opp_result["effective"])
            )
            hp_ratio = self.player.hp / self.player.max_hp if self.player.max_hp > 0 else 0
            self.player_anim.start_hp_animation(
                self.player_anim.current_hp_ratio, hp_ratio
            )

        if opp_result["ko"]:
            self._handle_player_faint()
            return

        self.phase = "player_turn"

    def _finish_battle(self):
        """Mark battle as finished, award XP, and track evolution."""
        self.phase = "finished"
        # Identify winner Pokemon before XP/evolution changes its name
        winner_name = self.combat.get_winner()
        winner_pokemon = (
            self.combat.player_pokemon
            if winner_name == self.combat.player_pokemon.name
            else self.combat.opponent_pokemon
        )
        old_name = winner_pokemon.name
        self.xp_message = self.combat.award_xp_to_winner()
        self._add_log(self.xp_message)
        # If the PLAYER's Pokemon evolved (its name changed), record it
        if winner_pokemon.name != old_name and winner_pokemon is self.combat.player_pokemon:
            unlock_msg = self.game.record_evolution()
            self.game.unlock_pokemon(winner_pokemon.name)
            if unlock_msg:
                self._add_log(unlock_msg)

    def _handle_player_faint(self):
        """Handle when current player Pokemon faints."""
        if self._all_fainted(self.player_team):
            self.winner = self.opponent.name
            self._finish_battle()
            self._add_log("You lost the battle!")
        else:
            # Open switch menu (forced -- player must choose)
            alive = [(i, p) for i, p in enumerate(self.player_team)
                     if p.is_alive() and i != self.player_index]
            if alive:
                self._add_log("Choose your next Pokemon!")
                self.phase = "forced_switch"
                self.show_switch = True
                self._build_switch_buttons(alive)
            else:
                # Should not happen (already checked _all_fainted)
                self.winner = self.opponent.name
                self._finish_battle()

    def update(self):
        """Update animations and opponent attack timer."""
        self.player_anim.update()
        self.opponent_anim.update()

        # Handle delayed opponent attack
        if self.waiting_for_opponent:
            elapsed = pygame.time.get_ticks() - self.opponent_attack_timer
            if elapsed >= self.opponent_attack_delay:
                self._do_opponent_attack()

    def draw(self, surface):
        """Draw the combat interface."""
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill(Constants.WHITE)

        opp_dx, opp_dy = self.opponent_anim.get_shake_offset()
        pl_dx, pl_dy = self.player_anim.get_shake_offset()

        # Opponent: info plate LEFT, sprite RIGHT
        opp_info_rect = pygame.Rect(20, 25, 340, 105)
        opp_sprite_pos = (652 + opp_dx, 30 + opp_dy)
        self._draw_pokemon_panel(
            surface, self.opponent, self.opponent_sprite,
            sprite_pos=opp_sprite_pos, info_rect=opp_info_rect,
            is_player=False, anim=self.opponent_anim,
        )
        self._draw_team_balls(surface, self.opponent_team, 652, 15)

        # VS label
        vs_surf = self.font_name.render("VS", True, Constants.RED)
        surface.blit(
            vs_surf,
            (Constants.SCREEN_WIDTH // 2 - vs_surf.get_width() // 2, 170),
        )

        # Player: sprite LEFT, info plate RIGHT
        pl_info_rect = pygame.Rect(440, 220, 340, 105)
        pl_sprite_pos = (20 + pl_dx, 200 + pl_dy)
        self._draw_pokemon_panel(
            surface, self.player, self.player_sprite,
            sprite_pos=pl_sprite_pos, info_rect=pl_info_rect,
            is_player=True, anim=self.player_anim,
        )
        self._draw_team_balls(surface, self.player_team, 20, 185)

        # Combat log
        log_y = 345
        pygame.draw.rect(
            surface, Constants.LIGHT_GRAY,
            pygame.Rect(20, log_y, 760, 110),
            border_radius=6,
        )
        for i, msg in enumerate(self.log_messages):
            msg_surf = self.font_log.render(msg, True, Constants.BLACK)
            surface.blit(msg_surf, (32, log_y + 8 + i * 20))

        # Buttons
        if self.phase == "finished":
            pygame.draw.rect(
                surface, Constants.BLUE, self.continue_button,
                border_radius=Constants.BUTTON_RADIUS,
            )
            btn_label = self.font_button.render("Continue", True, Constants.WHITE)
            surface.blit(btn_label, btn_label.get_rect(center=self.continue_button.center))
        else:
            color = Constants.RED if self.phase == "player_turn" else Constants.GRAY
            pygame.draw.rect(surface, color, self.attack_button,
                             border_radius=Constants.BUTTON_RADIUS)
            atk_label = self.font_button.render("Attack!", True, Constants.WHITE)
            surface.blit(atk_label, atk_label.get_rect(center=self.attack_button.center))

            has_alive = any(p.is_alive() and i != self.player_index
                           for i, p in enumerate(self.player_team))
            sw_color = Constants.BLUE if has_alive else Constants.GRAY
            pygame.draw.rect(surface, sw_color, self.switch_button,
                             border_radius=Constants.BUTTON_RADIUS)
            sw_label = self.font_button.render("Switch", True, Constants.WHITE)
            surface.blit(sw_label, sw_label.get_rect(center=self.switch_button.center))

            pygame.draw.rect(surface, Constants.DARK_GRAY, self.forfeit_button,
                             border_radius=Constants.BUTTON_RADIUS)
            ff_label = self.font_button.render("Forfeit", True, Constants.WHITE)
            surface.blit(ff_label, ff_label.get_rect(center=self.forfeit_button.center))

        # Move selection overlay
        if self.show_moves:
            overlay = pygame.Surface(
                (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 120))
            surface.blit(overlay, (0, 0))

            title = self.font_name.render("Choose a move:", True, Constants.WHITE)
            surface.blit(title, (Constants.SCREEN_WIDTH // 2 - title.get_width() // 2, 220))

            for move, btn in self.move_buttons:
                move_color = Constants.TYPE_COLORS.get(move.move_type, Constants.BLUE)
                pygame.draw.rect(surface, move_color, btn, border_radius=6)
                move_text = f"{move.name} ({move.move_type}) PWR:{move.power}"
                text_surf = self.font_move.render(move_text, True, Constants.WHITE)
                surface.blit(text_surf, text_surf.get_rect(center=btn.center))

        # Switch menu overlay
        if self.show_switch:
            overlay = pygame.Surface(
                (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 120))
            surface.blit(overlay, (0, 0))

            title = self.font_name.render("Switch to:", True, Constants.WHITE)
            surface.blit(title, (Constants.SCREEN_WIDTH // 2 - title.get_width() // 2, 134))

            for i, btn in self.switch_buttons:
                p = self.player_team[i]
                pygame.draw.rect(surface, Constants.BLUE, btn, border_radius=6)
                text = f"{p.name}  HP:{p.hp}/{p.max_hp}"
                text_surf = self.font_stat.render(text, True, Constants.WHITE)
                surface.blit(text_surf, text_surf.get_rect(center=btn.center))

        # Flash overlays on Pokemon sprites (with shake offsets)
        for anim, base_x, base_y, dx, dy in [
            (self.opponent_anim, 652, 30, opp_dx, opp_dy),
            (self.player_anim, 20, 200, pl_dx, pl_dy),
        ]:
            flash_color = anim.get_flash_color()
            if flash_color:
                flash_surf = pygame.Surface((128, 128), pygame.SRCALPHA)
                flash_surf.fill(flash_color)
                surface.blit(flash_surf, (base_x + dx, base_y + dy))

    def _draw_team_balls(self, surface, team, x, y):
        """Draw pokeball indicators for a team (filled = alive, empty = KO)."""
        for i, p in enumerate(team):
            center = (x + i * 22 + 10, y)
            if p.is_alive():
                pygame.draw.circle(surface, Constants.RED, center, 8)
            else:
                pygame.draw.circle(surface, Constants.GRAY, center, 8)
            pygame.draw.circle(surface, Constants.BLACK, center, 8, 1)

    def _draw_pokemon_panel(self, surface, pokemon, sprite, sprite_pos, info_rect, is_player, anim=None):
        """Draw one Pokemon's sprite and info plate."""
        # Sprite
        sx, sy = sprite_pos
        if sprite:
            surface.blit(sprite, (sx, sy))
        else:
            pygame.draw.rect(
                surface, Constants.LIGHT_GRAY,
                pygame.Rect(sx, sy, 128, 128), border_radius=8,
            )
            placeholder = self.font_stat.render("?", True, Constants.DARK_GRAY)
            surface.blit(placeholder, (sx + 56, sy + 52))

        # Info plate background
        pygame.draw.rect(surface, Constants.LIGHT_GRAY, info_rect, border_radius=8)

        ix = info_rect.x + 12
        iy = info_rect.y + 8

        # Name
        label = " (YOU)" if is_player else " (FOE)"
        name_surf = self.font_name.render(pokemon.name + label, True, Constants.BLACK)
        surface.blit(name_surf, (ix, iy))

        # HP bar
        bar_y = iy + 28
        bar_width = 160
        bar_height = 16
        if anim and anim.animating_hp:
            hp_ratio = anim.current_hp_ratio
        else:
            hp_ratio = pokemon.hp / pokemon.max_hp if pokemon.max_hp > 0 else 0
        if hp_ratio > 0.5:
            bar_color = Constants.HP_GREEN
        elif hp_ratio > 0.2:
            bar_color = Constants.HP_YELLOW
        else:
            bar_color = Constants.HP_RED

        pygame.draw.rect(
            surface, Constants.GRAY,
            pygame.Rect(ix, bar_y, bar_width, bar_height),
            border_radius=4,
        )
        if hp_ratio > 0:
            pygame.draw.rect(
                surface, bar_color,
                pygame.Rect(ix, bar_y, int(bar_width * hp_ratio), bar_height),
                border_radius=4,
            )
        hp_text = f"{pokemon.hp}/{pokemon.max_hp}"
        hp_surf = self.font_stat.render(hp_text, True, Constants.BLACK)
        surface.blit(hp_surf, (ix + bar_width + 8, bar_y - 1))

        # Type badges
        type_y = bar_y + 22
        self.draw_type_badges(
            surface, self.font_stat, pokemon.types,
            ix, type_y, padding=16, pad_inner=12, radius=4,
        )

        # Stats
        stat_y = type_y + 22
        stat_text = f"ATK:{pokemon.attack}  DEF:{pokemon.defense}  Lv.{pokemon.level}"
        stat_surf = self.font_stat.render(stat_text, True, Constants.DARK_GRAY)
        surface.blit(stat_surf, (ix, stat_y))

        # XP (player only)
        if is_player:
            xp_y = stat_y + 18
            xp_text = f"XP:{pokemon.xp}/{pokemon.xp_to_next_level}"
            xp_surf = self.font_stat.render(xp_text, True, Constants.DARK_GRAY)
            surface.blit(xp_surf, (ix, xp_y))
