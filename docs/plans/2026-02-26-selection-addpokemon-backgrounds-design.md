# Design : Ajout de Backgrounds aux Écrans Selection et Add Pokemon

**Date :** 2026-02-26
**Auteur :** Claude Sonnet 4.5
**Statut :** ✅ Approuvé par l'utilisateur

---

## Contexte

Le projet Pokemon dispose déjà de backgrounds PNG sur 4 écrans (menu, pokedex, team select, combat). Deux écrans utilisent encore un background blanc (`surface.fill(Constants.WHITE)`) :
- Selection screen (choix du Pokemon après "New Game"/"Continue")
- Add Pokemon screen (formulaire de création de Pokemon)

**Objectif :** Ajouter des backgrounds PNG à ces 2 écrans pour une cohérence visuelle complète avant la soutenance.

---

## Architecture

### Fichiers Impactés

**Modifications :**
1. `gui/selection_screen.py` - écran de sélection Pokemon
2. `gui/add_pokemon_screen.py` - formulaire d'ajout de Pokemon

**Assets utilisés :** (déjà présents dans `assets/backgrounds/`)
- `battle_arena.png` (661 KB) → pour selection_screen
- `pokedex_lab.png` (478 KB) → pour add_pokemon_screen

### Pattern de Conception

**Pattern choisi :** Approche sans fallback (identique à `menu_screen.py` et `team_select_screen.py`)

Justification :
- 4 écrans sur 6 utilisent déjà ce pattern
- Les PNG sont versionnés dans git
- Pas de cas d'usage où les PNG seraient manquants en production
- Code plus simple et cohérent

**Implémentation par écran :**
1. Import `os` en haut du fichier
2. Chargement dans `__init__` : `self.background = pygame.image.load(bg_path).convert()`
3. Utilisation dans `draw()` : `surface.blit(self.background, (0, 0))`

---

## Composants

### 1. Selection Screen

**Fichier :** `gui/selection_screen.py`

**Modifications :**

**Ligne 3 - Ajout import :**
```python
import os
import pygame
```

**Après ligne 26 - Chargement background dans __init__ :**
```python
super().__init__(game)

# Load background image
bg_path = os.path.join("assets", "backgrounds", "battle_arena.png")
self.background = pygame.image.load(bg_path).convert()

self.font_title = self.constants.get_font(32, bold=True)
```

**Ligne 88 - Remplacement fill par blit dans draw() :**
```python
def draw(self, surface):
    """Draw the Pokemon selection grid."""
    surface.blit(self.background, (0, 0))  # AVANT: surface.fill(Constants.WHITE)
```

**Background choisi :** `battle_arena.png`
- Thème : Arène de combat
- Cohérence : Prépare mentalement le joueur au combat qui suit la sélection

---

### 2. Add Pokemon Screen

**Fichier :** `gui/add_pokemon_screen.py`

**Modifications :**

**Ligne 3 - Ajout import :**
```python
import os
import pygame
```

**Après ligne 23 - Chargement background dans __init__ :**
```python
super().__init__(game)

# Load background image
bg_path = os.path.join("assets", "backgrounds", "pokedex_lab.png")
self.background = pygame.image.load(bg_path).convert()

self.font_title = self.constants.get_font(32, bold=True)
```

**Ligne 171 - Remplacement fill par blit dans draw() :**
```python
def draw(self, surface):
    """Draw the add Pokemon form."""
    surface.blit(self.background, (0, 0))  # AVANT: surface.fill(Constants.WHITE)
```

**Background choisi :** `pokedex_lab.png`
- Thème : Laboratoire du Prof Oak
- Cohérence : Évoque la recherche scientifique et la documentation des Pokemon

---

## Data Flow

**Aucune modification du data flow** - Les backgrounds sont purement visuels.

**Flux de chargement :**
1. Écran instancié → `__init__()` appelé
2. `pygame.image.load()` charge le PNG depuis le disque
3. `.convert()` optimise le format pour pygame
4. Image stockée dans `self.background`
5. À chaque frame, `draw()` blit l'image en position (0, 0)

**Performance :** Chargement unique à l'initialisation, pas de recharge par frame.

---

## Error Handling

**Stratégie :** Aucune gestion d'erreur (crash si PNG manquant)

**Justification :**
- Pattern cohérent avec `menu_screen.py` et `team_select_screen.py`
- PNG versionnés dans git → toujours présents
- Si PNG manquant = erreur de déploiement → crash explicite préférable

**Erreur attendue si PNG manquant :**
```
pygame.error: Couldn't open assets/backgrounds/battle_arena.png
```

**Résolution :** Vérifier que les PNG sont bien dans `assets/backgrounds/`.

---

## Testing

### Tests Manuels

**Test 1 - Selection Screen :**
1. `python3 main.py`
2. Cliquer "New Game" → vérifie background `battle_arena.png`
3. Vérifie lisibilité des cartes Pokemon
4. Scroll, sélection, navigation → fonctionnent normalement
5. "Back" → retour au menu

**Test 2 - Add Pokemon Screen :**
1. Menu → "Add Pokemon"
2. Vérifie background `pokedex_lab.png`
3. Vérifie lisibilité formulaire (texte blanc sur lab peut poser problème)
4. Créer un Pokemon → doit fonctionner
5. "Back" → retour au menu

### Critères de Succès

- ✅ Backgrounds s'affichent en plein écran (800×600)
- ✅ UI elements (texte, boutons) restent lisibles
- ✅ Pas de crash, pas d'erreur console
- ✅ Navigation fonctionne normalement
- ✅ Cohérence visuelle avec menu/pokedex/team/combat

### Tests Non Requis

- ❌ Tests unitaires (pas de logique métier modifiée)
- ❌ Tests de performance (chargement unique, impact négligeable)
- ❌ Tests de compatibilité (même pygame version, mêmes contraintes)

---

## Alternatives Considérées

### Alternative 1 : Fallback conditionnel
```python
if os.path.exists(bg_path):
    self.background = pygame.image.load(bg_path).convert()
else:
    self.background = None
```
**Rejeté :** Incohérent avec menu_screen et team_select, code plus verbeux.

### Alternative 2 : Refactoring BaseScreen
Centraliser la logique dans `base_screen.py` avec méthode `_load_background()`.

**Rejeté :** Scope trop large (6 fichiers), risque de bugs, overkill pour 2 backgrounds.

---

## Impacts

### Positifs
- ✅ Cohérence visuelle complète (100% des écrans ont un background)
- ✅ Présentation professionnelle pour la soutenance
- ✅ Changements minimes (8 lignes de code)
- ✅ Aucun impact sur la logique métier

### Risques
- ⚠️ Lisibilité du texte sur `pokedex_lab.png` (fond potentiellement trop chargé)
  - Mitigation : Test visuel, ajuster contraste si nécessaire
- ⚠️ Crash si PNG manquant
  - Mitigation : PNG versionnés, vérification lors du commit

---

## Métriques

**Complexité :**
- Lignes ajoutées : 6 (3 par écran)
- Lignes modifiées : 2 (1 par écran)
- Total : 8 lignes de code

**Taille assets :**
- `battle_arena.png` : 661 KB (déjà présent)
- `pokedex_lab.png` : 478 KB (déjà présent)
- Impact sur repo : 0 KB (assets déjà versionnés)

**Temps de développement estimé :**
- Implémentation : 10 minutes
- Tests manuels : 5 minutes
- Commit + documentation : 5 minutes
- Total : 20 minutes

---

## Prochaines Étapes

1. ✅ Design approuvé par l'utilisateur
2. ⏭️ Créer plan d'implémentation détaillé (via `writing-plans` skill)
3. ⏭️ Implémenter les modifications
4. ⏭️ Tests manuels complets
5. ⏭️ Commit avec message descriptif

---

**Design validé et prêt pour implémentation.**
