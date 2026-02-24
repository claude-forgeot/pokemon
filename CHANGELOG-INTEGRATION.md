# Changelog Integration

Trace des modifications apportees au code des coequipiers lors de l'integration
sur la branche `claude`.

## Branche nelly-poke (Nelly) -- Merge complet

**Commits integres** :
- `4fc881c` : Save/load system (Roadmap 2.1) -- save_select_screen, menu mis a jour
- `72e6c50` : Team battle mode (Roadmap 2.2) -- team_select_screen, switch, forfait

**Fichiers ajoutes** :
- `gui/save_select_screen.py` (nouveau)
- `gui/team_select_screen.py` (nouveau)

**Fichiers modifies** :
- `game.py` : +81 lignes (save_game, load_game, get_save_files, delete_save)
- `game_state.py` : +2 etats (TEAM_SELECT, SAVE_SELECT)
- `gui/combat_screen.py` : refactoring complet pour support equipes (player_team/opponent_team au lieu de pokemon simples)
- `gui/menu_screen.py` : ajout boutons New Game, Load Save, Team Battle
- `main.py` : routing vers SaveSelectScreen et TeamSelectScreen

**Modifications par Claude** : aucune -- merge direct sans conflit.

---

## Branche yass (Yasmine) -- Integration manuelle (XP uniquement)

**Probleme** : le commit `dfd48b8` de Yasmine a reverte les modifications de Nelly
dans 5 fichiers (game.py, combat_screen.py, menu_screen.py, main.py, game_state.py).
Seuls les ajouts XP dans `pokemon.py` et `combat.py` etaient intacts.

**Strategie** : copie manuelle des ajouts XP, pas de merge de la branche yass.

### pokemon.py -- Ajouts XP (Yasmine) + Corrections (Claude)

**Code Yasmine integre** :
- `__init__` : ajout attributs `xp`, `xp_to_next_level`, `evolution_level`, `evolution_target`
- `gain_xp()` : accumulation XP avec level-up automatique
- `level_up()` : augmentation stats + soin complet + evolution
- `try_evolve()` : evolution si niveau atteint
- `to_dict()` : serialisation des champs XP
- `__str__()` : affichage XP

**Bug fixes par Claude** :
1. **`from_dict()` ne restaurait pas le XP** : `to_dict()` serialisait les champs XP
   mais `from_dict()` les ignorait. XP perdu au save/load. Fix : ajout restauration
   de `xp`, `xp_to_next_level`, `evolution_level`, `evolution_target` dans `from_dict()`.
2. **`try_evolve()` affichait le mauvais nom** : `self.name` etait modifie avant le print,
   donnant "Ivysaur evolved into Ivysaur". Fix : sauvegarder `old_name` avant mutation.
3. **Double evolution** : sans nettoyage, `try_evolve()` se declenchait a chaque level-up
   apres le niveau d'evolution. Fix : effacer `evolution_level`/`evolution_target` apres evolution.

### combat.py -- Ajout methode XP (Yasmine) + Branchement (Claude)

**Code Yasmine integre** :
- `BASE_XP_REWARD = 20` : constante de classe
- `award_xp_to_winner()` : calcul et attribution XP au gagnant

**Bug fix par Claude** :
4. **`award_xp_to_winner()` jamais appelee** : la methode existait mais rien ne l'invoquait.
   Fix : appel dans `combat_screen.py` via `_finish_battle()` a la fin de chaque combat.

### Fichiers crees par Claude pour l'integration

**gui/combat_screen.py** :
- Ajout `xp_message` attribut
- Ajout methode `_finish_battle()` : centralise fin de combat + appel `award_xp_to_winner()`
- Affichage XP dans le panel Pokemon pendant le combat

**gui/result_screen.py** :
- Parametre `xp_message` ajoute au constructeur
- Affichage du message XP sur l'ecran de resultat

**main.py** :
- Passage du `xp_message` de CombatScreen a ResultScreen via la transition RESULT

---

## Bloc 1b -- Ameliorations gameplay (Claude)

### Sujet 4 : 151 Pokemon + evolution complete

**Fichiers modifies** :
- `scripts/populate_pokemon.py` : reecrit pour fetcher les 151 Pokemon Gen 1 avec stats,
  types, sprites, 4 moves (level-up depuis PokeAPI), chaines d'evolution, champ locked
- `utils/api_client.py` : ajout `fetch_pokemon_species()`, `fetch_evolution_chain()`, `fetch_move()`
- `pokemon.py` : ajout attributs `moves` (list[Move]), `locked` (bool), `evolution_data` (dict).
  `try_evolve()` met a jour stats/types/sprite_path depuis evolution_data.
  `from_dict()` restaure tous les nouveaux champs (backward-compatible).
- `game.py` : `get_available_pokemon()` filtre les locked. Ajout `get_all_pokemon()`,
  `unlock_pokemon()`, `record_evolution()`, `check_legendary_unlocks()`, `evolution_count`.
  Save/load persiste `evolution_count`.
- `gui/selection_screen.py` et `gui/team_select_screen.py` : affichent les Pokemon locked
  en grise (non cliquables). Utilisent `get_all_pokemon()` pour les indices.
- `main.py` : utilise `get_all_pokemon()` pour resoudre les indices de selection.

**Regles de verrouillage** :
- Stades 2+ des evolutions par niveau : locked (ex: Ivysaur, Charmeleon, Charizard)
- Evolutions non-niveau (pierre, echange) : disponibles directement (ex: Raichu, Arcanine)
- Mewtwo : locked, debloque apres 10 evolutions
- Mew : locked, debloque quand le Pokedex est complet (151 entries)

### Sujet 1 : Systeme de moves

**Fichiers crees** :
- `move.py` : classe Move (name, move_type, power, accuracy, to_dict, from_dict)

**Fichiers modifies** :
- `pokemon.py` : `self.moves = []` (list[Move]). `get_default_moves()` genere Tackle + move du type
  si aucun move (backward compat vieux saves). Serialisation/deserialisation dans to_dict/from_dict.
- `combat.py` : `attack()`, `calculate_damage()`, `get_type_multiplier()` acceptent `move=None`.
  Si move fourni, utilise move.move_type et move.accuracy au lieu du type du Pokemon et miss chance.
- `gui/combat_screen.py` : clic sur "Attack!" ouvre un overlay 2x2 de moves colores par type.
  L'IA choisit un move aleatoire via `_pick_random_move()`.

### Sujet 2 : Formule de degats

**Fichier modifie** : `combat.py`
- Avec move : `int(((2*level/5+2) * power * attack / defense) / 50 + 2) * type_multiplier`
- Sans move (backward compat) : `max(1, int(attack * multiplier) - defense)`

### Sujet 3 : Scaling adversaires

**Fichier modifie** : `main.py`
- Fonction `_scale_pokemon_level()` ajuste level, HP, ATK, DEF proportionnellement.
- Appliquee aux adversaires pour matcher le level moyen de l'equipe du joueur.

### Sujet 5 : Equipe de 6 + choix au KO

**Fichiers modifies** :
- `gui/team_select_screen.py` : MIN_TEAM = 6, MAX_TEAM = 6
- `gui/combat_screen.py` : quand un Pokemon est KO, phase `forced_switch` qui ouvre le menu
  switch (obligatoire). Le joueur ne peut pas fermer le menu sans choisir.

---

## Bloc 2 -- Bug fixes et nettoyage (Claude)

### Bugs corriges

1. **`type_chart.json` non track** : etait dans `.gitignore`, un clone frais n'avait pas le fichier.
   Fix : retire du `.gitignore`, ajoute au repo.
2. **`AI_CONTEXT.md` dans le repo** : fichier inutile track par git. Fix : `git rm`.
3. **`test_window.py` et `.claude/`** : fichiers debug/config locaux. Fix : supprimes.
4. **`_try_populate()` silencieux** : `except Exception: pass` masquait toutes les erreurs.
   Fix : ajout `print("Warning: populate failed, using default_pokemon.json")`.
5. **Scroll sans borne** : `SelectionScreen` et `TeamSelectScreen` pouvaient scroller indefiniment.
   Fix : ajout borne max basee sur le nombre de Pokemon et la taille de l'ecran.
6. **`load_game()` accedait `_entries` prive** : `self.pokedex._entries.append(entry)` violait
   l'encapsulation. Fix : ajout methode publique `add_raw_entry()` dans `Pokedex`.

### Simplification notions

7. **`match/case` -> `if/elif/else`** : `main.py` utilisait `match/case` (Python 3.10+),
   remplace par `if/elif/else` enseigne en cours (J3).
8. **`ABC/@abstractmethod` -> heritage simple** : `base_screen.py` utilisait `from abc import ABC`,
   remplace par une classe parente normale avec methodes `pass`.

### Nettoyage repo

9. **`tests/` supprime** : tests unitaires non requis pour le rendu.
10. **`.venv/` doublon supprime** : seul `venv/` est conserve.
11. **`requirements.txt`** : pytest retire, ne contient plus que pygame-ce et requests.
12. **`run.sh` + `run.bat`** : scripts de lancement (venv auto, install deps, lance le jeu).
