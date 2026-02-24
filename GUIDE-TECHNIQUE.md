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
  pokemon.py           # Classe Pokemon (stats, XP, evolution)
  combat.py            # Classe Combat (degats, types, XP)
  pokedex.py           # Classe Pokedex (collection de Pokemon rencontres)
  type_chart.py        # Classe TypeChart (multiplicateurs de types)
  gui/
    base_screen.py     # Classe abstraite BaseScreen
    constants.py       # Constantes visuelles (couleurs, tailles)
    menu_screen.py     # Ecran menu principal
    selection_screen.py # Selection d'un Pokemon (1v1)
    team_select_screen.py # Selection d'equipe (3-6 Pokemon)
    combat_screen.py   # Ecran de combat
    result_screen.py   # Ecran de resultats
    save_select_screen.py # Ecran de chargement de sauvegarde
    pokedex_screen.py  # Ecran du Pokedex
    add_pokemon_screen.py # Ajout de Pokemon via PokeAPI
  utils/
    api_client.py      # Client PokeAPI
    file_handler.py    # Utilitaire lecture/ecriture JSON
  scripts/
    populate_pokemon.py # Script de peuplement initial via PokeAPI
  data/
    pokemon.json       # Liste des Pokemon disponibles
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

### Pokemon (pokemon.py)

Represente un Pokemon avec ses stats et son systeme XP.

**Attributs** : name, hp, max_hp, level, attack, defense, types, sprite_path,
xp, xp_to_next_level, evolution_level, evolution_target

**Methodes cles** :
- `take_damage(amount)` / `is_alive()` / `heal()`
- `gain_xp(amount)` : ajoute XP, declenche level_up si seuil atteint
- `level_up()` : +1 level, +5 HP, +3 ATK, +2 DEF, soin complet
- `try_evolve()` : verifie si le niveau d'evolution est atteint
- `to_dict()` / `from_dict(data)` : serialisation JSON

### Combat (combat.py)

Gere un combat entre deux Pokemon.

**Methodes requises par le sujet** :
1. `get_type_multiplier(attacker, defender)` : efficacite des types
2. `calculate_damage(attacker, defender)` : formule de degats
3. `attack(attacker, defender)` : execution d'une attaque (miss 10%)
4. `get_winner()` / `get_loser()`
5. `register_to_pokedex(pokemon, pokedex)`

**Ajout XP** :
- `award_xp_to_winner()` : attribue XP = 20 + 2 x niveau_perdant

### Game (game.py)

Gestionnaire global : charge les Pokemon, gere le Pokedex, les sauvegardes.

**Save/Load** (par Nelly) :
- `save_game()` : sauvegarde dans `saves/save_YYYYMMDD_HHMMSS.json`
- `load_game(filepath)` : restaure Pokemon + Pokedex depuis un fichier
- `get_save_files()` / `delete_save(filepath)`

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

---

*Document mis a jour incrementalement. Derniere mise a jour : Bloc 1 (Integration).*
