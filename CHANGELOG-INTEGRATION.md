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
