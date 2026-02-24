# Guide Technique -- Pokemon Battle

Guide complet du projet pour l'equipe et la soutenance.
Mis a jour incrementalement a chaque bloc d'integration.

---

## 1. Architecture du projet

### Structure des fichiers

```
pokemonv1/
  main.py              # Point d'entree, boucle Pygame, machine a etats
  game.py              # Gestionnaire global (Game) : Pokemon, Pokedex, saves
  game_state.py        # Enum des etats du jeu (GameState)
  pokemon.py           # Classe Pokemon (stats, XP, evolution, moves)
  combat.py            # Classe Combat (degats, types, XP, moves)
  move.py              # Classe Move (attaque avec type, puissance, precision)
  pokedex.py           # Classe Pokedex (collection de Pokemon rencontres)
  type_chart.py        # Classe TypeChart (multiplicateurs de types)
  gui/
    base_screen.py     # Classe parente BaseScreen
    constants.py       # Constantes visuelles (couleurs, tailles)
    menu_screen.py     # Ecran menu principal
    selection_screen.py # Selection d'un Pokemon (1v1)
    team_select_screen.py # Selection d'equipe (6 Pokemon)
    combat_screen.py   # Ecran de combat (moves, switch, forced switch)
    result_screen.py   # Ecran de resultats
    save_select_screen.py # Ecran de chargement de sauvegarde
    pokedex_screen.py  # Ecran du Pokedex
    add_pokemon_screen.py # Ajout de Pokemon via PokeAPI
  utils/
    api_client.py      # Client PokeAPI (Pokemon, species, moves, evolution)
    file_handler.py    # Utilitaire lecture/ecriture JSON
  scripts/
    populate_pokemon.py # Script de peuplement des 151 Pokemon Gen 1 via PokeAPI
  data/
    pokemon.json       # 151 Pokemon Gen 1 (stats, moves, evolutions, locked)
    default_pokemon.json # Pokemon par defaut (fallback sans API)
    type_chart.json    # Table des multiplicateurs de types
    pokedex.json       # Pokedex du joueur
  saves/               # Dossier des sauvegardes
  assets/              # Sprites et images
```

### Pattern principal : Machine a etats

Le jeu utilise une **machine a etats** dans `main.py`. Chaque etat correspond
a un ecran (MenuScreen, CombatScreen, etc.). Les transitions sont declenchees
par les valeurs retournees par `handle_events()`.

```
MENU -> SELECTION -> COMBAT -> RESULT -> MENU
     -> TEAM_SELECT -> COMBAT -> RESULT -> MENU
     -> SAVE_SELECT -> MENU
     -> POKEDEX -> MENU
     -> ADD_POKEMON -> MENU
```

### Pattern : Heritage (Screens)

Tous les ecrans heritent de `BaseScreen` qui definit 3 methodes :
- `handle_events(events)` : gestion des clics/touches
- `update()` : mise a jour logique (timers, animations)
- `draw(surface)` : affichage sur l'ecran Pygame

### Pattern : Composition (Combat)

La classe `Combat` contient des references vers les Pokemon et le TypeChart.
C'est de la **composition** ("has-a") plutot que de l'heritage ("is-a").

---

## 2. Classes principales

### Move (move.py)

Represente une attaque Pokemon avec son type, sa puissance et sa precision.

**Attributs** : name, move_type, power, accuracy

**Methodes** :
- `to_dict()` / `from_dict(data)` : serialisation JSON

Chaque Pokemon possede jusqu'a 4 moves charges depuis PokeAPI. Si un Pokemon
n'a pas de moves (vieille sauvegarde), des moves par defaut sont generes
automatiquement (Tackle + attaque du type principal).

### Pokemon (pokemon.py)

Represente un Pokemon avec ses stats, son systeme XP, ses moves et son
statut de verrouillage.

**Attributs** : name, hp, max_hp, level, attack, defense, types, sprite_path,
xp, xp_to_next_level, evolution_level, evolution_target, moves (list[Move]),
locked (bool), evolution_data (dict)

**Methodes cles** :
- `take_damage(amount)` / `is_alive()` / `heal()`
- `gain_xp(amount)` : ajoute XP, declenche level_up si seuil atteint
- `level_up()` : +1 level, +5 HP, +3 ATK, +2 DEF, soin complet, tente evolution
- `try_evolve()` : si le niveau d'evolution est atteint, met a jour nom, stats,
  types et sprite depuis `evolution_data`. Efface les donnees d'evolution apres
  pour eviter les doubles evolutions.
- `get_default_moves()` : genere Tackle + attaque du type si aucun move (backward compat)
- `to_dict()` / `from_dict(data)` : serialisation JSON (inclut moves, locked, evolution_data)

### Combat (combat.py)

Gere un combat entre deux Pokemon avec systeme de moves.

**Methodes requises par le sujet** :
1. `get_type_multiplier(attacker, defender, move)` : utilise le type du move si fourni
2. `calculate_damage(attacker, defender, move)` : formule Pokemon-like avec move
3. `attack(attacker, defender, move)` : execution d'une attaque avec precision du move
4. `get_winner()` / `get_loser()`
5. `register_to_pokedex(pokemon, pokedex)`

**Formule de degats** (avec move) :
```
base = ((2 * level / 5 + 2) * power * attack / defense) / 50 + 2
damage = int(base * type_multiplier)
```
Sans move (backward compat) : `max(1, int(attack * multiplier) - defense)`

**Ajout XP** :
- `award_xp_to_winner()` : attribue XP = 20 + 2 x niveau_perdant

### Game (game.py)

Gestionnaire global : charge les Pokemon, gere le Pokedex, les sauvegardes,
les evolutions et le verrouillage.

**Save/Load** (par Nelly) :
- `save_game()` : sauvegarde dans `saves/save_YYYYMMDD_HHMMSS.json`
- `load_game(filepath)` : restaure Pokemon + Pokedex + evolution_count
- `get_save_files()` / `delete_save(filepath)`

**Pokemon** :
- `get_available_pokemon()` : liste des Pokemon non-verrouilles
- `get_all_pokemon()` : liste complete (pour affichage avec Pokemon grise)
- `unlock_pokemon(name)` : deverrouille un Pokemon par son nom (apres evolution)
- `record_evolution()` : incremente le compteur et verifie les legendaires
- `check_legendary_unlocks()` : Mewtwo apres 10 evolutions, Mew apres Pokedex complet

---

## 3. Fonctionnalites

### MVP (Roadmap 1 -- main)
- Selection d'un Pokemon parmi 15 (chargeables via PokeAPI ou fichier par defaut)
- Combat 1v1 tour par tour avec systeme de types (18 types, multiplicateurs)
- Pokedex : enregistrement automatique des adversaires rencontres
- Ajout de nouveaux Pokemon via PokeAPI
- Affichage sprites, barres de vie, badges de types

### Save/Load (Roadmap 2.1 -- Nelly)
- Sauvegarde automatique apres chaque combat
- Ecran de selection de sauvegarde (Load Save)
- Suppression de sauvegardes
- Bouton New Game (reset Pokedex)

### Team Battle (Roadmap 2.2 -- Nelly)
- Selection de 3 a 6 Pokemon pour le combat
- Combat en equipe avec switch et forfait
- Indicateurs pokeball (vivant/KO) pour chaque equipe
- Auto-switch quand un Pokemon est KO

### XP et Evolution (Roadmap 3.1 -- Yasmine)
- Gain d'XP apres chaque victoire (formule : 20 + 2 x niveau_adversaire)
- Level-up automatique avec augmentation des stats
- Systeme d'evolution base sur le niveau
- Affichage XP dans le combat et les resultats

### 151 Pokemon Gen 1 + Evolution complete (Bloc 1b -- Claude)
- 151 Pokemon de la Gen 1 charges depuis PokeAPI (stats, types, sprites, moves)
- 92 Pokemon disponibles au depart (stade 1 + evolutions non-niveau)
- 59 Pokemon verrouilles (stade 2+ des evolutions par niveau + Mewtwo + Mew)
- Evolution par level-up : met a jour nom, stats, types, sprite. Deverrouille la forme evoluee.
- Pokemon a evolution non-niveau (pierre, echange) : formes finales disponibles directement
- Mewtwo : se deverrouille apres 10 evolutions
- Mew : se deverrouille quand le Pokedex est complet (151 entries)
- Pokemon verrouilles affiches en grise dans les ecrans de selection (non cliquables)

### Systeme de Moves (Bloc 1b -- Claude)
- Chaque Pokemon possede jusqu'a 4 moves charges depuis PokeAPI
- En combat, cliquer "Attack!" ouvre un sous-menu 2x2 avec les moves disponibles
- Chaque bouton affiche : nom du move, type (colore), puissance
- L'IA adversaire choisit un move aleatoire
- Backward compat : les Pokemon sans moves recoivent Tackle + attaque du type

### Formule de degats amelioree (Bloc 1b -- Claude)
- Avec move : formule Pokemon-like utilisant level, power, attack, defense, type_multiplier
- Sans move : fallback sur l'ancienne formule simple (backward compat)

### Scaling adversaires (Bloc 1b -- Claude)
- Les adversaires sont ajustes au niveau moyen de l'equipe du joueur
- Stats (HP, ATK, DEF) recalculees proportionnellement au nouveau niveau

### Equipe de 6 + choix au KO (Bloc 1b -- Claude)
- Equipe obligatoire de 6 Pokemon (au lieu de 3-6)
- Quand un Pokemon est KO, un menu de switch s'affiche (obligatoire)
- Le joueur doit choisir le suivant -- pas d'auto-switch

---

## 4. Notions utilisees

### A. Notions enseignees en cours
| Notion | Ou dans le code |
|--------|----------------|
| Variables, types | Partout (str, int, float, bool, list, dict) |
| Boucles for/while | Boucle de jeu (main.py), iteration sur les Pokemon |
| Conditions if/elif/else | Machine a etats, calculs de degats |
| Fonctions | Methodes de classes |
| Listes, dictionnaires | pokemon_list, to_dict/from_dict, saves |
| Classes, heritage | Pokemon, Combat, BaseScreen -> MenuScreen |
| JSON | Sauvegarde/chargement (file_handler.py) |
| API REST | PokeAPI (api_client.py) |
| Git | Branches, merge, commits conventionnels |

### B. Notions complementaires (ressources du sujet)
| Notion | Ou dans le code |
|--------|----------------|
| Heritage | Screens heritent de BaseScreen |
| Fichiers JSON | pokedex.json, pokemon.json, saves |

### C. Notions supplementaires (a expliquer si questionnees)
| Notion | Ou | Explication simple |
|--------|----|--------------------|
| Enum | game_state.py | Constantes nommees pour eviter les erreurs de frappe |
| @classmethod | pokemon.py (from_dict) | Constructeur alternatif qui recoit la classe |
| try/except | api_client.py, file_handler.py | Gestion d'erreurs reseau/fichier |
| Type hints | Partout | Annotations de type pour la lisibilite |

**Note Bloc 2** : les notions `match/case` et `ABC/@abstractmethod` ont ete retirees du code
et remplacees par des equivalents enseignes en cours (`if/elif/else` et heritage simple)
pour reduire le risque en soutenance.

### Lancement du jeu

Deux scripts sont fournis pour lancer le jeu :
- **Linux/Mac** : `./run.sh` -- cree le venv, installe les dependances, lance le jeu
- **Windows** : `run.bat` -- idem pour Windows

---

## 5. Difficultes rencontrees

### Integration des branches
**Probleme** : Le commit XP de Yasmine a accidentellement reverte les modifications
de Nelly dans 5 fichiers, supprimant le save/load et le team battle.

**Approche** : Au lieu de merger la branche yass (ce qui aurait reverte le travail
de Nelly), nous avons merge nelly d'abord puis copie manuellement uniquement les
ajouts XP de Yasmine.

**Solution** : Integration selective -- merge nelly-poke complet, puis ajout manuel
du code XP (pokemon.py + combat.py) avec correction des bugs.

**Resultat** : Toutes les fonctionnalites sont integrees et fonctionnelles.

### Bugs dans le code XP
**Probleme** : 3 bugs identifies dans le code XP de Yasmine :
1. `from_dict()` ne restaurait pas le XP (perdu au save/load)
2. `try_evolve()` affichait le mauvais nom
3. `award_xp_to_winner()` n'etait jamais appelee

**Solution** : Corrections ciblees avec tests unitaires pour chaque bug.

### Peuplement des 151 Pokemon
**Probleme** : Charger 151 Pokemon depuis PokeAPI avec stats, types, sprites,
4 moves et chaines d'evolution necessitait des centaines de requetes API.

**Approche** : Script `populate_pokemon.py` avec cache des moves et des chaines
d'evolution pour minimiser les appels API (263 moves uniques caches).

**Solution** : Fetch batch des 151 Pokemon avec cache, selection des 4 meilleurs
moves offensifs par Pokemon (level-up uniquement, pas de status moves).

**Resultat** : 151 Pokemon dans pokemon.json, 92 disponibles, 59 verrouilles.

### Backward compatibilite des moves
**Probleme** : Les vieilles sauvegardes n'ont pas de moves dans leurs Pokemon.
Charger un ancien save et lancer un combat ferait planter le jeu.

**Approche** : Generation automatique de moves par defaut dans `from_dict()`
quand la liste de moves est vide.

**Solution** : `get_default_moves()` genere Tackle (normal, 40 puissance) + une
attaque du type principal du Pokemon. Combat fonctionne sans et avec moves.

**Resultat** : Ancien et nouveau format de sauvegarde fonctionnent sans modification.

---

*Document mis a jour incrementalement. Derniere mise a jour : Bloc 4 (Documentation publique).*
