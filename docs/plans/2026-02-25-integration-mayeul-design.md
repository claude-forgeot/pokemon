# Design : Integration selective de mayeul-dev

**Date** : 2026-02-25
**Contexte** : Integration d'elements choisis de la branche `mayeul-dev` dans la branche principale du projet pokemonv1, avant soutenance.

---

## Decisions prises

### Elements integres depuis mayeul-dev

| Element | Justification |
|---------|---------------|
| AnimationManager (shake, flash, HP animee) | Ameliore le rendu visuel ("Soigner l'affichage" -- consigne) |
| Validation Move.__init__ | Programmation defensive, bon point soutenance (encapsulation) |
| Delai attaque adversaire (1500ms) | Meilleure lisibilite du combat |

### Elements conserves de la branche actuelle (non remplaces)

| Element | Justification |
|---------|---------------|
| Pas de PP sur les moves | Garder simple |
| Pas d'AssetManager | Systeme actuel fonctionne, sprites 151 deja presents |
| Formule de degats Gen 1/2 | Plus fidele, prend en compte le niveau, meilleur scaling |
| Pas de tests unitaires | Code simple et explicable pour la soutenance |
| BaseScreen concrete + helpers | Colle au niveau du cours, helpers _load_sprites et draw_type_badges utiles |
| Organisation models/ | Meilleure structure, bon argument soutenance |
| Pas d'API/requests | Pas de dependance reseau, 151 Pokemon deja en local |

---

## Architecture des changements

### 1. Nouvelle classe : AnimationManager

**Fichier** : `models/animation_manager.py`

Classe autonome avec 3 systemes d'animation independants :
- **Shake** : deplacement aleatoire du sprite adversaire (amplitude 6px, duree 10 frames)
- **Flash** : overlay semi-transparent colore selon l'efficacite (vert=super, rouge=pas tres, gris=immunite, blanc=normal), fondu lineaire sur 8 frames
- **HP animee** : interpolation lineaire de la barre de HP (vitesse 0.02 ratio/frame)

Attributs :
- shake_frames_remaining, _shake_offset_x, _shake_offset_y
- flash_frames_remaining, _flash_total_duration, _flash_color
- animating_hp, current_hp_ratio, _target_hp_ratio

Methodes publiques :
- start_shake(duration=10)
- start_flash(color, duration=8)
- start_hp_animation(current_ratio, target_ratio)
- update() -- appele chaque frame
- get_shake_offset() -> (dx, dy)
- get_flash_color() -> (R, G, B, alpha) ou None
- is_animating() -> bool

### 2. Modification : Move.__init__ (validation)

**Fichier** : `models/move.py`

Ajout dans le constructeur :
- `if not name or not name.strip():` -> `raise ValueError("Move name cannot be empty")`
- `if not (0 <= accuracy <= 100):` -> `raise ValueError("Accuracy must be between 0 and 100")`

### 3. Modification : CombatScreen (animations + delai)

**Fichier** : `gui/combat_screen.py`

Changements :
- Ajouter un attribut `self.animation_manager = AnimationManager()`
- Ajouter `self.opponent_attack_delay = 1500` (ms)
- Ajouter `self.opponent_attack_timer = 0` et `self.waiting_for_opponent = False`
- Apres attaque joueur : declencher shake + flash + HP animation sur l'adversaire, passer en mode "waiting_for_opponent"
- Dans `update()` : appeler `animation_manager.update()`, gerer le timer du delai adversaire
- Apres attaque adversaire : declencher shake + flash + HP animation sur le joueur
- Dans `draw()` : appliquer le shake offset au sprite concerne, dessiner le flash overlay, utiliser `animation_manager.current_hp_ratio` pour les barres HP
- Bloquer les inputs joueur pendant les animations et le delai adversaire

### 4. Documentation

**CHANGELOG-INTEGRATION.md** : Ajouter Bloc 7 -- Integration selective mayeul-dev
**GUIDE-TECHNIQUE.md** : Mettre a jour pour refleter :
- Nouvelle classe AnimationManager
- Validation Move
- Delai adversaire
- Mise a jour Bloc 6 (suppression API/requests deja faite mais pas documentee)

---

## Ce qui ne change PAS

- 151 Pokemon avec moves, evolution, sprites
- Formule de degats Gen 1/2
- Combat 6v6 avec switch et forfait
- Save/load avec multiple slots
- Systeme legendaires (Mewtwo/Mew)
- Pokemon locked/unlocked
- Pokedex
- Structure models/ + gui/ + utils/
- BaseScreen concrete
- Dependance unique pygame-ce
