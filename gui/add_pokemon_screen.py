"""Add Pokemon screen module -- form to create and add a custom Pokemon."""

import pygame

from game_state import GameState
from gui.base_screen import BaseScreen
from gui.constants import Constants
from type_chart import TypeChart


class AddPokemonScreen(BaseScreen):
    """Form screen to add a new custom Pokemon to the roster.

    Has text input fields for name, HP, attack, defense, and a type selector.
    """

    def __init__(self, game):
        """Initialize the add Pokemon form.

        Args:
            game: The Game instance.
        """
        super().__init__(game)
        self.font_title = pygame.font.SysFont("arial", 32, bold=True)
        self.font_label = pygame.font.SysFont("arial", 18)
        self.font_input = pygame.font.SysFont("arial", 20)
        self.font_button = pygame.font.SysFont("arial", 20)
        self.font_small = pygame.font.SysFont("arial", 14)

        # Input fields: {field_name: {"value": str, "rect": Rect, "active": bool}}
        field_x = 300
        self.fields = {
            "name": {"value": "", "rect": pygame.Rect(field_x, 120, 220, 32), "active": False},
            "hp": {"value": "50", "rect": pygame.Rect(field_x, 170, 220, 32), "active": False},
            "attack": {"value": "50", "rect": pygame.Rect(field_x, 220, 220, 32), "active": False},
            "defense": {"value": "50", "rect": pygame.Rect(field_x, 270, 220, 32), "active": False},
        }
        self.field_labels = {
            "name": "Name:",
            "hp": "HP:",
            "attack": "Attack:",
            "defense": "Defense:",
        }

        # Type selection
        self.available_types = TypeChart.TYPES
        self.selected_types = []
        self.type_buttons = []
        self._build_type_buttons()

        # Action buttons
        self.save_button = pygame.Rect(
            Constants.SCREEN_WIDTH // 2 - 160, Constants.SCREEN_HEIGHT - 70, 140, 44
        )
        self.back_button = pygame.Rect(
            Constants.SCREEN_WIDTH // 2 + 20, Constants.SCREEN_HEIGHT - 70, 140, 44
        )

        self.error_message = ""
        self.success_message = ""

    def _build_type_buttons(self):
        """Pre-compute the position of each type toggle button."""
        self.type_buttons = []
        cols = 6
        start_x = 60
        start_y = 335
        btn_w = 100
        btn_h = 26
        pad = 6
        for i, type_name in enumerate(self.available_types):
            col = i % cols
            row = i // cols
            x = start_x + col * (btn_w + pad)
            y = start_y + row * (btn_h + pad)
            self.type_buttons.append({
                "name": type_name,
                "rect": pygame.Rect(x, y, btn_w, btn_h),
            })

    def handle_events(self, events):
        """Handle text input, type toggles, save, and back.

        Returns:
            GameState or None: MENU if back or successful save.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Deactivate all fields
                for field in self.fields.values():
                    field["active"] = False

                # Check field clicks
                for field in self.fields.values():
                    if field["rect"].collidepoint(event.pos):
                        field["active"] = True

                # Type toggles
                for btn in self.type_buttons:
                    if btn["rect"].collidepoint(event.pos):
                        if btn["name"] in self.selected_types:
                            self.selected_types.remove(btn["name"])
                        elif len(self.selected_types) < 2:
                            self.selected_types.append(btn["name"])

                # Save button
                if self.save_button.collidepoint(event.pos):
                    return self._try_save()

                # Back button
                if self.back_button.collidepoint(event.pos):
                    return GameState.MENU

            if event.type == pygame.KEYDOWN:
                for field_name, field in self.fields.items():
                    if not field["active"]:
                        continue
                    if event.key == pygame.K_BACKSPACE:
                        field["value"] = field["value"][:-1]
                    elif event.key == pygame.K_TAB:
                        field["active"] = False
                    elif len(field["value"]) < 20:
                        if field_name == "name":
                            if event.unicode.isalpha() or event.unicode in " -":
                                field["value"] += event.unicode
                        else:
                            if event.unicode.isdigit():
                                field["value"] += event.unicode
        return None

    def _try_save(self):
        """Validate and save the new Pokemon. Returns MENU on success, None on error."""
        self.error_message = ""
        self.success_message = ""

        name = self.fields["name"]["value"].strip()
        if not name:
            self.error_message = "Name is required"
            return None

        try:
            hp = int(self.fields["hp"]["value"])
            attack = int(self.fields["attack"]["value"])
            defense = int(self.fields["defense"]["value"])
        except ValueError:
            self.error_message = "HP, Attack, Defense must be numbers"
            return None

        if hp < 1 or attack < 1 or defense < 1:
            self.error_message = "Stats must be at least 1"
            return None

        if not self.selected_types:
            self.error_message = "Select at least one type"
            return None

        pokemon_data = {
            "name": name.capitalize(),
            "hp": hp,
            "level": 5,
            "attack": attack,
            "defense": defense,
            "types": list(self.selected_types),
            "sprite_path": "",
        }
        self.game.add_pokemon(pokemon_data)
        self.success_message = f"{name.capitalize()} added!"
        return GameState.MENU

    def update(self):
        """No update logic needed."""

    def draw(self, surface):
        """Draw the add Pokemon form."""
        surface.fill(Constants.WHITE)

        # Title
        title = self.font_title.render("Add a Pokemon", True, Constants.BLACK)
        surface.blit(title, (Constants.SCREEN_WIDTH // 2 - title.get_width() // 2, 40))

        # Input fields
        for field_name, field in self.fields.items():
            label = self.font_label.render(
                self.field_labels[field_name], True, Constants.BLACK
            )
            surface.blit(label, (field["rect"].x - 140, field["rect"].y + 5))

            border_color = Constants.BLUE if field["active"] else Constants.GRAY
            pygame.draw.rect(surface, Constants.LIGHT_GRAY, field["rect"], border_radius=4)
            pygame.draw.rect(surface, border_color, field["rect"], width=2, border_radius=4)

            text_surf = self.font_input.render(field["value"], True, Constants.BLACK)
            surface.blit(text_surf, (field["rect"].x + 8, field["rect"].y + 5))

        # Type selection label
        type_label = self.font_label.render(
            f"Types (select 1-2): {', '.join(self.selected_types) or 'none'}",
            True, Constants.BLACK,
        )
        surface.blit(type_label, (60, 310))

        # Type buttons
        for btn in self.type_buttons:
            is_selected = btn["name"] in self.selected_types
            color = Constants.TYPE_COLORS.get(btn["name"], Constants.GRAY)
            if not is_selected:
                # Dim the color
                color = tuple(min(255, c + 100) for c in color)
            pygame.draw.rect(surface, color, btn["rect"], border_radius=4)
            if is_selected:
                pygame.draw.rect(
                    surface, Constants.BLACK, btn["rect"], width=2, border_radius=4
                )
            txt = self.font_small.render(btn["name"], True, Constants.WHITE)
            surface.blit(txt, txt.get_rect(center=btn["rect"].center))

        # Error / success messages
        if self.error_message:
            err = self.font_label.render(self.error_message, True, Constants.RED)
            surface.blit(err, (Constants.SCREEN_WIDTH // 2 - err.get_width() // 2, 460))
        if self.success_message:
            ok = self.font_label.render(self.success_message, True, Constants.GREEN)
            surface.blit(ok, (Constants.SCREEN_WIDTH // 2 - ok.get_width() // 2, 460))

        # Save button
        pygame.draw.rect(
            surface, Constants.GREEN, self.save_button,
            border_radius=Constants.BUTTON_RADIUS,
        )
        save_label = self.font_button.render("Save", True, Constants.WHITE)
        surface.blit(save_label, save_label.get_rect(center=self.save_button.center))

        # Back button
        pygame.draw.rect(
            surface, Constants.DARK_GRAY, self.back_button,
            border_radius=Constants.BUTTON_RADIUS,
        )
        back_label = self.font_button.render("Back", True, Constants.WHITE)
        surface.blit(back_label, back_label.get_rect(center=self.back_button.center))
