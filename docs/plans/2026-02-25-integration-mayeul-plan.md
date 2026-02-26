# Integration selective mayeul-dev -- Plan d'implementation

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrer 3 elements de la branche mayeul-dev (animations, validation Move, delai adversaire) et mettre a jour la documentation.

**Architecture:** Ajout d'une classe AnimationManager dans models/, modification de Move pour la validation, et adaptation de CombatScreen pour les animations + delai. Aucun changement a la logique de combat, aux formules de degats, ou aux features existantes.

**Tech Stack:** Python 3.10+, pygame-ce 2.5+

---

### Task 1: Creer AnimationManager dans models/

**Files:**
- Create: `models/animation_manager.py`

**Step 1: Creer le fichier animation_manager.py**

Copier la classe depuis la branche Mayeul (`/tmp/pokemon-mayeul/animation_manager.py`) dans `models/animation_manager.py`. Le code est pret a l'emploi -- aucune modification necessaire.

```python
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
        self.shake_frames_remaining = 0
        self._shake_offset_x = 0
        self._shake_offset_y = 0

        # -- Flash state --
        self.flash_frames_remaining = 0
        self._flash_total_duration = 0
        self._flash_color = None

        # -- HP bar animation state --
        self.animating_hp = False
        self.current_hp_ratio = 0.0
        self._target_hp_ratio = 0.0

    def start_shake(self, duration: int = 10) -> None:
        """Begin a sprite shake effect.

        Args:
            duration: Number of frames the shake lasts (default 10).
        """
        self.shake_frames_remaining = duration
        self._update_shake_offset()

    def start_flash(self, color: tuple, duration: int = 8) -> None:
        """Begin a screen-overlay flash effect.

        Args:
            color:    (R, G, B) base color for the flash.
            duration: Number of frames the flash lasts (default 8).
        """
        self._flash_color = color
        self.flash_frames_remaining = duration
        self._flash_total_duration = duration

    def start_hp_animation(self, current_ratio: float, target_ratio: float) -> None:
        """Begin progressive HP bar animation.

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

    def update(self) -> None:
        """Advance every active animation by one frame."""
        self._update_shake()
        self._update_flash()
        self._update_hp()

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

    def is_animating(self) -> bool:
        """Return True if any animation is currently running.

        Returns:
            bool: True if shake, flash, or HP bar animation is active.
        """
        return (
            self.shake_frames_remaining > 0
            or self.flash_frames_remaining > 0
            or self.animating_hp
        )

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
        """Advance the HP bar animation by one frame."""
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
```

**Step 2: Verifier que l'import fonctionne**

Run: `cd /home/jawkah/Documents/Partage-Projets-SyncThing/Etudes/[ACTIF]Projet_Actuel/pokemonv1 && source venv/bin/activate && python3 -c "from models.animation_manager import AnimationManager; a = AnimationManager(); print('OK')"`
Expected: `OK`

---

### Task 2: Ajouter la validation dans Move.__init__

**Files:**
- Modify: `models/move.py:15-27`

**Step 1: Ajouter les validations**

Dans `models/move.py`, ajouter 4 lignes de validation au debut de `__init__` (apres la docstring, avant les affectations) :

```python
def __init__(self, name, move_type, power, accuracy):
    """Create a new Move instance.

    Args:
        name: Display name (e.g. "Thunderbolt").
        move_type: Elemental type (e.g. "electric").
        power: Base power (int, higher = more damage).
        accuracy: Hit chance as percentage (1-100).
    """
    if not name or not name.strip():
        raise ValueError("Move name cannot be empty")
    if not (0 <= accuracy <= 100):
        raise ValueError("Accuracy must be between 0 and 100")
    self.name = name
    self.move_type = move_type
    self.power = power
    self.accuracy = accuracy
```

**Step 2: Verifier que le jeu se lance sans regression**

Run: `cd /home/jawkah/Documents/Partage-Projets-SyncThing/Etudes/[ACTIF]Projet_Actuel/pokemonv1 && source venv/bin/activate && python3 -c "from models.move import Move; m = Move('Tackle', 'normal', 40, 100); print(m)"`
Expected: `Tackle (normal) PWR:40 ACC:100`

Run: `python3 -c "from models.move import Move; Move('', 'normal', 40, 100)"`
Expected: `ValueError: Move name cannot be empty`

---

### Task 3: Modifier CombatScreen -- animations + delai adversaire

**Files:**
- Modify: `gui/combat_screen.py`

C'est la tache la plus complexe. Modifications dans l'ordre :

**Step 1: Ajouter l'import AnimationManager**

A la ligne 9 de `gui/combat_screen.py`, ajouter :

```python
from models.animation_manager import AnimationManager
```

**Step 2: Ajouter les attributs d'animation et de delai dans __init__**

Apres `self.show_moves = False` (ligne 44), ajouter :

```python
        # Animation manager for visual effects (shake, flash, HP bar)
        self.player_anim = AnimationManager()
        self.opponent_anim = AnimationManager()

        # Opponent attack delay (milliseconds)
        self.opponent_attack_delay = 1500
        self.opponent_attack_timer = 0
        self.waiting_for_opponent = False
```

Initialiser les HP ratios apres le chargement des sprites (apres ligne 65) :

```python
        # Initialize HP animation ratios
        self.player_anim.current_hp_ratio = self.player.hp / self.player.max_hp
        self.opponent_anim.current_hp_ratio = self.opponent.hp / self.opponent.max_hp
```

**Step 3: Ajouter la methode helper _get_flash_color**

Ajouter cette methode dans la classe (par exemple apres `_add_log`) :

```python
    def _get_flash_color(self, effective):
        """Return flash color based on move effectiveness."""
        if effective == "super":
            return (100, 255, 100)
        elif effective == "not_very":
            return (255, 100, 100)
        elif effective == "immune":
            return (150, 150, 150)
        return (255, 255, 255)
```

**Step 4: Modifier _do_player_attack pour declencher les animations et le delai**

Remplacer la methode `_do_player_attack` par :

```python
    def _do_player_attack(self, move=None):
        """Execute player attack with a move, then schedule opponent attack."""
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
                # Reset opponent HP animation for new Pokemon
                self.opponent_anim = AnimationManager()
                self.opponent_anim.current_hp_ratio = self.opponent.hp / self.opponent.max_hp

        # Schedule opponent attack after delay
        self.phase = "opponent_turn"
        self.waiting_for_opponent = True
        self.opponent_attack_timer = pygame.time.get_ticks()
```

**Step 5: Ajouter la methode _do_opponent_attack (separee)**

Ajouter cette nouvelle methode :

```python
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
```

**Step 6: Modifier _do_switch pour animer l'attaque adversaire apres switch**

Dans `_do_switch`, remplacer les 3 dernieres lignes (attaque adversaire) par un scheduling :

```python
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
        self.player_anim.current_hp_ratio = self.player.hp / self.player.max_hp

        # Schedule opponent attack after delay
        self.phase = "opponent_turn"
        self.waiting_for_opponent = True
        self.opponent_attack_timer = pygame.time.get_ticks()
```

**Step 7: Modifier update() pour gerer les animations et le timer**

Remplacer la methode `update` :

```python
    def update(self):
        """Update animations and opponent attack timer."""
        self.player_anim.update()
        self.opponent_anim.update()

        # Handle delayed opponent attack
        if self.waiting_for_opponent:
            elapsed = pygame.time.get_ticks() - self.opponent_attack_timer
            if elapsed >= self.opponent_attack_delay:
                self._do_opponent_attack()
```

**Step 8: Modifier handle_events pour bloquer les inputs pendant les animations**

Au debut de `handle_events`, ajouter un garde (apres `for event in events:`) :

```python
    def handle_events(self, events):
        """Handle button clicks for attack, switch, forfeit."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # Block input during animations or opponent delay
                if self.waiting_for_opponent or self.player_anim.is_animating() or self.opponent_anim.is_animating():
                    # Exception: still allow "Continue" click when finished
                    if self.phase != "finished":
                        return None

                # ... reste du handle_events inchange
```

**Step 9: Modifier draw() pour appliquer shake et flash**

Dans `_draw_pokemon_panel`, appliquer le shake offset au sprite :

1. Modifier l'appel `_draw_pokemon_panel` pour l'adversaire dans `draw()` -- passer l'animation manager :

```python
        # Opponent panel (top right) -- with shake offset
        opp_dx, opp_dy = self.opponent_anim.get_shake_offset()
        self._draw_pokemon_panel(
            surface, self.opponent, self.opponent_sprite,
            x=Constants.SCREEN_WIDTH - 280 + opp_dx, y=30 + opp_dy,
            is_player=False, anim=self.opponent_anim,
        )
```

```python
        # Player panel (bottom left) -- with shake offset
        pl_dx, pl_dy = self.player_anim.get_shake_offset()
        self._draw_pokemon_panel(
            surface, self.player, self.player_sprite,
            x=50 + pl_dx, y=200 + pl_dy, is_player=True,
            anim=self.player_anim,
        )
```

2. Modifier la signature de `_draw_pokemon_panel` pour accepter `anim=None` et utiliser `anim.current_hp_ratio` pour la barre HP si disponible :

```python
    def _draw_pokemon_panel(self, surface, pokemon, sprite, x, y, is_player, anim=None):
        """Draw one Pokemon's sprite, name, HP bar, and type badges."""
        # ... sprite drawing unchanged ...

        # HP bar -- use animated ratio if available
        if anim and anim.animating_hp:
            hp_ratio = anim.current_hp_ratio
        else:
            hp_ratio = pokemon.hp / pokemon.max_hp if pokemon.max_hp > 0 else 0

        # ... rest unchanged, uses hp_ratio ...
```

3. Ajouter le flash overlay a la fin de `draw()`, apres les overlays moves/switch :

```python
        # Flash overlays (drawn on top of Pokemon panels)
        for anim, panel_rect in [
            (self.opponent_anim, pygame.Rect(Constants.SCREEN_WIDTH - 280, 30, 128, 128)),
            (self.player_anim, pygame.Rect(50, 200, 128, 128)),
        ]:
            flash_color = anim.get_flash_color()
            if flash_color:
                flash_surf = pygame.Surface((128, 128), pygame.SRCALPHA)
                flash_surf.fill(flash_color)
                surface.blit(flash_surf, panel_rect.topleft)
```

**Step 10: Reinitialiser les animations quand on switch d'adversaire**

Dans `_next_alive_opponent`, apres le changement de sprite, ajouter :

```python
        self.opponent_anim = AnimationManager()
        self.opponent_anim.current_hp_ratio = self.opponent.hp / self.opponent.max_hp
```

**Step 11: Tester manuellement**

Run: `cd /home/jawkah/Documents/Partage-Projets-SyncThing/Etudes/[ACTIF]Projet_Actuel/pokemonv1 && source venv/bin/activate && python3 main.py`

Verifier :
- Le sprite adversaire tremble quand on l'attaque
- Un flash colore apparait sur le sprite touche
- La barre de HP descend progressivement
- Il y a un delai avant l'attaque de l'adversaire (~1.5s)
- Les inputs sont bloques pendant les animations et le delai
- Le switch fonctionne toujours (forced switch + voluntary switch)
- Le forfait fonctionne toujours

---

### Task 4: Mettre a jour CHANGELOG-INTEGRATION.md

**Files:**
- Modify: `CHANGELOG-INTEGRATION.md`

**Step 1: Ajouter le Bloc 7**

Ajouter a la fin du fichier :

```markdown

---

## Bloc 7 -- Integration selective mayeul-dev (Claude)

### Contexte

Analyse comparative de la branche `mayeul-dev` avec la branche principale.
Sur 10 differences identifiees, 3 elements ont ete retenus pour integration.
Le design doc complet est dans `docs/plans/2026-02-25-integration-mayeul-design.md`.

### Elements integres

#### 1. AnimationManager (models/animation_manager.py)

**Source** : `mayeul-dev/animation_manager.py`
**Destination** : `models/animation_manager.py`

Classe autonome avec 3 systemes d'animation pour le combat :
- Shake : tremblement du sprite touche (6px amplitude, 10 frames)
- Flash : overlay colore selon l'efficacite (vert=super, rouge=pas tres, gris=immunite)
- HP animee : interpolation lineaire de la barre de vie (0.02 ratio/frame)

**Fichier modifie** : `gui/combat_screen.py`
- Import AnimationManager
- 2 instances (player_anim, opponent_anim) pour chaque cote du combat
- Animations declenchees apres chaque attaque dans `_do_player_attack()` et `_do_opponent_attack()`
- Shake applique au positionnement du sprite dans `draw()`
- Flash dessine en overlay sur le sprite touche
- Barre HP utilise `anim.current_hp_ratio` pendant l'animation
- Inputs bloques pendant les animations (`is_animating()`)

#### 2. Validation Move.__init__ (models/move.py)

**Source** : `mayeul-dev/move.py` (adapte -- sans PP)
**Modification** : 2 verifications ajoutees dans le constructeur
- `ValueError` si name vide ou blank
- `ValueError` si accuracy hors bornes 0-100

#### 3. Delai attaque adversaire (gui/combat_screen.py)

**Source** : `mayeul-dev/gui/combat_screen.py` (adapte)
**Modification** : L'attaque adversaire est declenchee apres un delai de 1500ms
au lieu d'etre instantanee. Utilise `pygame.time.get_ticks()` pour le timer.
L'attaque adversaire a ete separee dans une methode `_do_opponent_attack()`.

### Elements non retenus (avec justification)

| Element | Raison du rejet |
|---------|----------------|
| PP sur les moves | Garder le code simple pour la soutenance |
| AssetManager | Systeme actuel fonctionne, 151 sprites deja presents |
| Formule de degats Mayeul | Garder la formule Gen 1/2 (plus fidele, prend en compte le niveau) |
| Tests unitaires | Priorite a la simplicite et l'explicabilite du code |
| BaseScreen ABC | Heritage simple maintenu (colle au cours) |
| Organisation racine | models/ package conserve (meilleure structure) |
| API/requests | Supprimee au Bloc 6, pas de raison de reimporter |
```

---

### Task 5: Mettre a jour GUIDE-TECHNIQUE.md

**Files:**
- Modify: `GUIDE-TECHNIQUE.md`

**Step 1: Ajouter AnimationManager dans la section 2 (Classes principales)**

Apres la section Move (ligne ~87), ajouter :

```markdown
### AnimationManager (models/animation_manager.py)

Gere les animations visuelles du combat : tremblement des sprites,
flash d'efficacite et animation progressive de la barre de vie.

**Attributs de classe** : SHAKE_AMPLITUDE (6px), HP_ANIM_SPEED (0.02), HP_ANIM_THRESHOLD (0.005)

**Methodes publiques** :
- `start_shake(duration)` : declenche un tremblement du sprite
- `start_flash(color, duration)` : declenche un flash colore (overlay semi-transparent)
- `start_hp_animation(current_ratio, target_ratio)` : lance l'animation de la barre HP
- `update()` : avance toutes les animations d'une frame (appele chaque frame)
- `get_shake_offset()` : retourne le decalage (dx, dy) en pixels
- `get_flash_color()` : retourne (R, G, B, alpha) ou None
- `is_animating()` : True si au moins une animation est active

**POO** : Encapsulation (etat prive via prefixe _), pattern Update (une methode
appelee chaque frame qui avance l'etat interne), separation commande/requete
(start_* modifie l'etat, get_* le consulte).
```

**Step 2: Ajouter la section Animations dans la section 3 (Fonctionnalites)**

Apres "Equipe de 6 + choix au KO" (ligne ~203), ajouter :

```markdown
### Animations de combat (Bloc 7 -- Mayeul)
- Tremblement du sprite quand un Pokemon est touche
- Flash colore selon l'efficacite (vert=super efficace, rouge=pas tres, gris=immunite)
- Barre de vie qui descend progressivement au lieu de sauter
- Delai de 1.5 seconde avant l'attaque de l'adversaire
- Inputs bloques pendant les animations pour eviter les double-clics
```

**Step 3: Ajouter la validation dans les notions supplementaires**

Dans la section 4C (Notions supplementaires, ligne ~228), ajouter une ligne :

```markdown
| Validation (ValueError) | models/move.py | Programmation defensive : rejeter les donnees invalides |
```

**Step 4: Mettre a jour la mention "Derniere mise a jour" en fin de fichier**

Remplacer la derniere ligne par :

```markdown
*Document mis a jour incrementalement. Derniere mise a jour : Bloc 7 (integration selective mayeul-dev).*
```

**Step 5: Mettre a jour la section "Soigner l'affichage" et la reference API**

Dans la section notions enseignees en cours (section 4A), la ligne API REST mentionne que les donnees ont ete "recuperees depuis PokeAPI". Ajouter une precision :

```markdown
| API REST | Les donnees des 151 Pokemon ont ete recuperees depuis PokeAPI puis enregistrees dans pokemon.json. Les scripts API ont ete supprimes (Bloc 6), le fichier est maintenant statique. |
```

---

### Task 6: Verification finale et nettoyage

**Files:**
- Aucun nouveau fichier

**Step 1: Lancer le jeu et tester un combat complet**

Run: `cd /home/jawkah/Documents/Partage-Projets-SyncThing/Etudes/[ACTIF]Projet_Actuel/pokemonv1 && source venv/bin/activate && python3 main.py`

Checklist :
- [ ] Menu : tous les boutons fonctionnent
- [ ] Team Select : selection de 6 Pokemon, pas de crash
- [ ] Combat : attaque -> sprite adversaire tremble + flash + HP descend progressivement
- [ ] Combat : delai ~1.5s avant attaque adversaire
- [ ] Combat : attaque adversaire -> sprite joueur tremble + flash + HP descend
- [ ] Combat : switch volontaire fonctionne
- [ ] Combat : forced switch sur KO fonctionne
- [ ] Combat : forfait fonctionne
- [ ] Resultat : XP affiche correctement
- [ ] Save/Load : pas de regression

**Step 2: Supprimer le clone temporaire de Mayeul**

Run: `rm -rf /tmp/pokemon-mayeul`
