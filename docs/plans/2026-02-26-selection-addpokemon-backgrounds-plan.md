# Selection & Add Pokemon Backgrounds Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Ajouter des backgrounds PNG aux écrans selection_screen et add_pokemon_screen pour compléter la cohérence visuelle du jeu.

**Architecture:** Suivre le pattern existant de menu_screen.py et team_select_screen.py - charger le PNG dans __init__, blitter dans draw() sans fallback. Modifications minimales (8 lignes de code total).

**Tech Stack:** Python 3.10+, Pygame-CE 2.5+, PNG backgrounds 800×600px

---

## Prerequisites

**Vérifier avant de commencer :**

```bash
# Vérifier que les PNG existent
ls -lh assets/backgrounds/battle_arena.png assets/backgrounds/pokedex_lab.png

# Vérifier qu'on est sur la bonne branche
git status

# Lancer le jeu pour voir l'état initial
python3 main.py
```

**Attendu :**
- `battle_arena.png` : 661 KB
- `pokedex_lab.png` : 478 KB
- Branche : mayeul-dev (ou votre branche de travail)
- Jeu se lance normalement

---

## Task 1: Ajouter Background à Selection Screen

**Files:**
- Modify: `gui/selection_screen.py:3` (import)
- Modify: `gui/selection_screen.py:26` (__init__)
- Modify: `gui/selection_screen.py:88` (draw)

**Step 1: Vérifier l'état actuel**

Lire le fichier pour confirmer les numéros de lignes :

```bash
head -n 30 gui/selection_screen.py
```

**Attendu :**
- Ligne 3 : `import pygame` (pas de `import os`)
- Ligne 26 : `super().__init__(game)`
- Ligne 88 : `surface.fill(Constants.WHITE)`

**Step 2: Ajouter l'import os**

Éditer `gui/selection_screen.py` ligne 3 :

```python
"""Selection screen module -- choose a Pokemon for battle."""

import os
import pygame
```

**Step 3: Charger le background dans __init__**

Éditer `gui/selection_screen.py` après ligne 26 :

```python
        super().__init__(game)

        # Load background image
        bg_path = os.path.join("assets", "backgrounds", "battle_arena.png")
        self.background = pygame.image.load(bg_path).convert()

        self.font_title = self.constants.get_font(32, bold=True)
```

**Step 4: Utiliser le background dans draw()**

Éditer `gui/selection_screen.py` ligne 88 :

```python
    def draw(self, surface):
        """Draw the Pokemon selection grid."""
        surface.blit(self.background, (0, 0))
```

**Step 5: Tester manuellement**

Lancer le jeu et tester :

```bash
python3 main.py
```

**Actions de test :**
1. Cliquer "New Game" → vérifie que background `battle_arena.png` s'affiche
2. Vérifie que les cartes Pokemon sont visibles par-dessus
3. Sélectionner un Pokemon, cliquer "Confirm" → va au combat
4. Retour au menu → cliquer "Continue" (si save existe) → vérifie background identique

**Attendu :**
- ✅ Background arena visible en plein écran
- ✅ Cartes Pokemon lisibles par-dessus
- ✅ Aucun crash, aucune erreur console
- ✅ Navigation fonctionne normalement

**Step 6: Vérifier les changements**

```bash
git diff gui/selection_screen.py
```

**Attendu :**
- +1 ligne : `import os`
- +3 lignes : chargement background
- 1 ligne modifiée : `surface.blit` au lieu de `surface.fill`

**Si tout OK, passer à Task 2. Ne pas commit encore (commit groupé à la fin).**

---

## Task 2: Ajouter Background à Add Pokemon Screen

**Files:**
- Modify: `gui/add_pokemon_screen.py:3` (import)
- Modify: `gui/add_pokemon_screen.py:23` (__init__)
- Modify: `gui/add_pokemon_screen.py:171` (draw)

**Step 1: Vérifier l'état actuel**

Lire le fichier pour confirmer les numéros de lignes :

```bash
head -n 30 gui/add_pokemon_screen.py
tail -n +165 gui/add_pokemon_screen.py | head -n 10
```

**Attendu :**
- Ligne 3 : `import pygame` (pas de `import os`)
- Ligne 23 : `super().__init__(game)`
- Ligne 171 : `surface.fill(Constants.WHITE)`

**Step 2: Ajouter l'import os**

Éditer `gui/add_pokemon_screen.py` ligne 3 :

```python
"""Add Pokemon screen module -- form to create and add a custom Pokemon."""

import os
import pygame
```

**Step 3: Charger le background dans __init__**

Éditer `gui/add_pokemon_screen.py` après ligne 23 :

```python
        super().__init__(game)

        # Load background image
        bg_path = os.path.join("assets", "backgrounds", "pokedex_lab.png")
        self.background = pygame.image.load(bg_path).convert()

        self.font_title = self.constants.get_font(32, bold=True)
```

**Step 4: Utiliser le background dans draw()**

Éditer `gui/add_pokemon_screen.py` ligne 171 :

```python
    def draw(self, surface):
        """Draw the add Pokemon form."""
        surface.blit(self.background, (0, 0))
```

**Step 5: Tester manuellement**

Lancer le jeu et tester :

```bash
python3 main.py
```

**Actions de test :**
1. Cliquer "Add Pokemon" → vérifie que background `pokedex_lab.png` s'affiche
2. Vérifie que le formulaire (champs texte) est lisible
3. Vérifie que les boutons de types sont visibles
4. Tester création d'un Pokemon :
   - Nom : "TestMon"
   - HP : 50
   - Attack : 50
   - Defense : 50
   - Types : Fire + Flying
   - Cliquer "Save"
5. Vérifier retour au menu sans erreur

**Attendu :**
- ✅ Background lab visible en plein écran
- ✅ Formulaire lisible par-dessus (texte noir sur fond clair)
- ✅ Création de Pokemon fonctionne
- ✅ Aucun crash, aucune erreur console

**Step 6: Vérifier les changements**

```bash
git diff gui/add_pokemon_screen.py
```

**Attendu :**
- +1 ligne : `import os`
- +3 lignes : chargement background
- 1 ligne modifiée : `surface.blit` au lieu de `surface.fill`

**Si tout OK, passer à Task 3.**

---

## Task 3: Tests Manuels Complets

**Files:**
- Test: Toute l'application (flow complet)

**Step 1: Test de régression - écrans existants**

Lancer le jeu :

```bash
python3 main.py
```

**Vérifier chaque écran :**

1. **Menu** → vérifie `main_menu.png` toujours OK
2. **Pokedex** → vérifie `pokedex_lab.png` toujours OK
3. **Team Battle** (si >= 3 Pokemon) → vérifie `team_arena.png` toujours OK
4. Lancer un combat → vérifie `battle_arena.png` toujours OK

**Attendu :**
- ✅ Tous les écrans existants fonctionnent normalement
- ✅ Aucune régression visuelle

**Step 2: Test des nouveaux backgrounds**

**Selection Screen :**
1. Menu → "New Game"
2. Vérifie background `battle_arena.png`
3. Scroll vers le bas (molette souris)
4. Sélectionne 2-3 Pokemon différents
5. "Confirm" → combat
6. Forfeit → retour menu
7. "Continue" → vérifie background identique

**Add Pokemon Screen :**
1. Menu → "Add Pokemon"
2. Vérifie background `pokedex_lab.png`
3. Teste lisibilité :
   - Champs de saisie
   - Labels (Name, HP, Attack, Defense)
   - Boutons de types (18 types)
   - Boutons Save/Back
4. Crée un Pokemon test :
   - Nom : "BackgroundTest"
   - HP : 100
   - Attack : 80
   - Defense : 70
   - Types : Water + Ice
   - Save
5. Vérifie Pokemon créé (compte Pokemon augmente dans menu)
6. "Add Pokemon" à nouveau → vérifie background toujours OK

**Attendu :**
- ✅ Backgrounds s'affichent correctement
- ✅ UI elements lisibles
- ✅ Fonctionnalités non régressées

**Step 3: Test de compatibilité visuelle**

Vérifier l'harmonie visuelle entre tous les écrans :

1. Naviguer : Menu → Selection → Combat (avec background arena)
2. Naviguer : Menu → Add Pokemon (background lab) → Menu → Pokedex (background lab)
3. Naviguer : Menu → Team Battle (background team_arena) → Combat

**Attendu :**
- ✅ Transitions visuelles cohérentes
- ✅ Pas de clash de couleurs
- ✅ Style uniforme (moderne Pokemon TCG)

**Step 4: Test des edge cases**

**Test scroll avec background :**
1. Selection screen : scroll rapide haut/bas → vérifie pas de tearing
2. Add Pokemon : aucun scroll (page statique) → OK

**Test multi-sélection :**
1. Selection screen : sélectionne/désélectionne rapidement → vérifie pas de visual glitches

**Test boutons sur background :**
1. Add Pokemon : clique tous les boutons de types → vérifie hover states visibles
2. Selection screen : boutons Back/Confirm → vérifie hover visible sur background

**Attendu :**
- ✅ Aucun glitch visuel
- ✅ Performance fluide (60 FPS)
- ✅ Interactivité normale

**Si tous les tests passent, passer à Task 4.**

---

## Task 4: Commit Final

**Files:**
- Commit: `gui/selection_screen.py`
- Commit: `gui/add_pokemon_screen.py`

**Step 1: Vérifier l'état git**

```bash
git status
```

**Attendu :**
```
On branch mayeul-dev
Changes not staged for commit:
  modified:   gui/selection_screen.py
  modified:   gui/add_pokemon_screen.py
```

**Step 2: Vérifier les diffs une dernière fois**

```bash
git diff gui/selection_screen.py gui/add_pokemon_screen.py
```

**Vérifier :**
- ✅ Seulement les changements attendus (8 lignes total)
- ✅ Pas de debug print oubliés
- ✅ Pas de code commenté
- ✅ Indentation correcte

**Step 3: Stager les fichiers**

```bash
git add gui/selection_screen.py gui/add_pokemon_screen.py
```

**Step 4: Créer le commit**

```bash
git commit -m "$(cat <<'EOF'
feat: add backgrounds to selection and add pokemon screens

Completes visual consistency by adding PNG backgrounds to the last
2 screens that were using white fill:

- Selection screen: battle_arena.png (prepares for combat)
- Add Pokemon screen: pokedex_lab.png (scientific research theme)

Pattern: Follow existing menu_screen.py approach (load in __init__,
blit in draw(), no fallback). Consistent with 4/6 existing screens.

Changes:
- gui/selection_screen.py: +4 lines (import, load, blit)
- gui/add_pokemon_screen.py: +4 lines (import, load, blit)

Tested: Manual testing of both screens + regression testing of all
other screens. No visual regressions, UI elements remain readable.

Visual enhancement for project soutenance presentation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

**Step 5: Vérifier le commit**

```bash
git log -1 --stat
```

**Attendu :**
```
commit <hash>
feat: add backgrounds to selection and add pokemon screens
...
 gui/add_pokemon_screen.py | 4 ++++
 gui/selection_screen.py   | 4 ++++
 2 files changed, 8 insertions(+)
```

**Step 6: Vérifier que le jeu fonctionne après commit**

```bash
python3 main.py
```

**Test rapide :**
1. New Game → vérifie background
2. Back → Add Pokemon → vérifie background
3. Back → Quitter

**Attendu :**
- ✅ Jeu fonctionne normalement
- ✅ Backgrounds visibles

---

## Completion Checklist

Avant de considérer la feature complète, vérifier :

- [x] Task 1: Selection screen a background `battle_arena.png`
- [x] Task 2: Add Pokemon screen a background `pokedex_lab.png`
- [x] Task 3: Tests manuels complets passent
- [x] Task 4: Commit créé avec message descriptif
- [x] Aucune régression sur les autres écrans
- [x] UI elements restent lisibles sur nouveaux backgrounds
- [x] Aucun crash, aucune erreur console

**Commande de vérification finale :**

```bash
# Vérifier le commit
git show --stat

# Lancer le jeu une dernière fois
python3 main.py
# Tester : Menu → New Game → Back → Add Pokemon → Back → Quit
```

**Si tout est vert, feature complète ! 🎉**

---

## Troubleshooting

### Problème : Background ne s'affiche pas

**Symptôme :** Écran blanc ou erreur au lancement

**Diagnostic :**
```bash
# Vérifier que le PNG existe
ls -l assets/backgrounds/battle_arena.png assets/backgrounds/pokedex_lab.png

# Vérifier les permissions
file assets/backgrounds/battle_arena.png
```

**Solution :**
- Si fichier manquant : Vérifier git, peut-être pas pull correctement
- Si permissions : `chmod 644 assets/backgrounds/*.png`

### Problème : Texte illisible sur background

**Symptôme :** Labels ou boutons difficiles à lire

**Diagnostic :** Background trop chargé dans les zones de UI

**Solution temporaire :**
Ajouter une semi-transparence sous les textes critiques :
```python
# Dans draw(), avant de blitter le texte
overlay = pygame.Surface((width, height), pygame.SRCALPHA)
overlay.fill((0, 0, 0, 80))  # Noir à 80/255 alpha
surface.blit(overlay, (x, y))
```

**Solution permanente :** Régénérer le PNG avec zones de "safe area" plus claires

### Problème : Performance dégradée

**Symptôme :** FPS chute, jeu lent

**Diagnostic :** Background rechargé à chaque frame

**Vérification :**
```python
# Dans draw(), vérifier qu'on fait SEULEMENT :
surface.blit(self.background, (0, 0))

# PAS :
# self.background = pygame.image.load(...)  # <- NE PAS faire ça dans draw()
```

**Solution :** S'assurer que le load est dans `__init__`, pas dans `draw()`

### Problème : Git merge conflicts

**Symptôme :** Conflicts sur gui/selection_screen.py ou gui/add_pokemon_screen.py

**Solution :**
```bash
# Voir les conflicts
git diff

# Résoudre manuellement, en gardant :
# - import os (ligne 3)
# - background loading (après super().__init__)
# - surface.blit (dans draw())

# Après résolution
git add <file>
git commit
```

---

**Plan complet. Prêt pour implémentation.**
