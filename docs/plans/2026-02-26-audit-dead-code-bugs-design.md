# Design : Audit Code Mort et Bugs -- pokemonv1

Date : 2026-02-26

## Contexte

Audit complet du codebase Pokemon (23 fichiers Python). 18 items identifies :
5 dead code, 12 bugs, 1 info conserve (backgrounds).

## Decisions d'architecture

| Decision | Choix | Raison |
|----------|-------|--------|
| Sync XP post-combat | `Game.sync_from_combat()` | Garde copies, centralise la logique dans le modele |
| XP en combat equipe | Cumulee en fin de combat | Compteur KO, pas d'evolution mid-combat |
| Reset roster (new_game) | Charger depuis `pokemon.json` source | Deterministe, ecrase le runtime |
| `__str__()` methods | Supprimer | Zero dead code strict |
| Branches `move=None` | Rendre `move` obligatoire | Supprimer les branches mortes, coherence API |
| Bouton Team Battle | Masquer si < 3 Pokemon | Plus clair que griser |
| Format `pokemon_state.json` | Objet `{pokemon_list, evolution_count}` | Persister evolution_count, backward compat |

## Section 1 : Systeme XP/Combat (B2, B3, B6)

### Probleme
Les copies profondes isolent le combat mais l'XP/niveaux/evolutions restent
sur les copies et sont perdus apres le combat.

### Solution

1. `CombatScreen.__init__` : ajouter `self.player_original_indices` (list[int])
   et `self.player_ko_count = 0`.

2. `main.py` : passer les indices originaux lors de la creation du CombatScreen.

3. `_do_player_attack()` : incrementer `self.player_ko_count` a chaque KO adversaire.

4. `_finish_battle()` : calculer l'XP totale basee sur `player_ko_count` et
   les niveaux des adversaires KO. Appliquer `gain_xp()` sur le Pokemon actif
   du joueur. Detecter evolution (changement de nom) et appeler
   `game.record_evolution()` + `game.unlock_pokemon()`.

5. `Game.sync_from_combat(player_team, original_indices)` : synchronise
   xp, level, xp_to_next_level, max_hp, attack, defense, name, sprite_path,
   evolution_level, evolution_target, moves. HP remis a max_hp. Appelle
   `_save_pokemon()`.

6. `main.py` transition COMBAT -> RESULT : appeler `game.sync_from_combat()`
   avant `game.save_game()`.

### Fichiers : `combat_screen.py`, `game.py`, `main.py`

## Section 2 : Fix combat flow (B1, B5)

### B1 -- Adversaire attaque apres KO
Dans `_do_player_attack()`, ajouter `return` apres `self._next_alive_opponent()`
dans le bloc `else` du KO non-final. Le joueur retrouve son tour.

### B5 -- Forfait affiche "No winner yet!"
Dans `_finish_battle()`, detecter le forfait (deux Pokemon vivants + winner set)
et court-circuiter : `self.xp_message = "You forfeited - no XP gained."` sans
appeler la logique XP.

### Fichiers : `combat_screen.py`

## Section 3 : Persistance et reset (B4, B12, B8, B10)

### B4 -- new_game() ne reset pas
`new_game()` charge explicitement `POKEMON_SOURCE_PATH`, ignore le runtime.
Appelle `_save_pokemon()` pour ecraser `pokemon_state.json`.

### B12 -- evolution_count pas persiste
`_save_pokemon()` sauvegarde `{"pokemon_list": [...], "evolution_count": N}`.
`_load_pokemon()` gere les deux formats (liste legacy et objet).

### B8 -- Pokemon joueur pas dans Pokedex
Dans `handle_events()` transition RESULT : boucler sur `self.player_team`
en plus de `self.opponent_team` pour `register_to_pokedex()`.

### B10 -- Pas de check doublon nom
`Game.add_pokemon()` retourne False si un Pokemon avec le meme nom existe.
`AddPokemonScreen._try_save()` affiche l'erreur.

### Fichiers : `game.py`, `combat_screen.py`, `add_pokemon_screen.py`

## Section 4 : UX et optimisations (B9, B7, B11)

### B9 -- Bouton Team Battle masque
`MenuScreen.draw()` ne dessine pas le bouton si < 3 Pokemon. Le check dans
`handle_events()` reste en garde de securite.

### B7 -- Double copie adversaire
`main.py` ligne 93 : `opp = game.get_random_opponent()` directement.

### B11 -- Re-check legendaires
`_check_legendary_unlocks()` : early return si Mewtwo et Mew deja deverrouilles.

### Fichiers : `menu_screen.py`, `main.py`, `game.py`

## Section 5 : Code mort (D1, D2, D3, D4, D5)

### D1 -- success_message
Supprimer `self.success_message = ""` et le commentaire associe.

### D2/D3 -- __str__() methods
Supprimer `Pokemon.__str__()` et `Move.__str__()`.

### D4 -- Branches move=None
Rendre `move` obligatoire dans `Combat.calculate_damage()` et `Combat.attack()`.
Supprimer les branches `else` mortes. Adapter `get_type_multiplier()` aussi.

### D5 -- Branche "pas de moves"
Supprimer le `if self.player.moves:` / `else` dans `handle_events()`.
Garder directement le contenu du if.

### Fichiers : `add_pokemon_screen.py`, `pokemon.py`, `move.py`, `combat.py`, `combat_screen.py`

## Resume des fichiers modifies

| Fichier | Items |
|---------|-------|
| `gui/combat_screen.py` | B1, B2, B3, B5, B6, B8, D5 |
| `models/game.py` | B2, B3, B4, B10, B11, B12 |
| `main.py` | B2, B3, B7 |
| `models/combat.py` | D4 |
| `gui/add_pokemon_screen.py` | B10, D1 |
| `gui/menu_screen.py` | B9 |
| `models/pokemon.py` | D2 |
| `models/move.py` | D3 |
