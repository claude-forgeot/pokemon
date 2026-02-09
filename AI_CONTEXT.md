# Contexte projet -- Pokemon Battle Game

[Instruction a l'IA : ce document est un prompt autonome. Colle-le tel quel dans
n'importe quelle IA (ChatGPT, Claude, Gemini, etc.) pour reprendre le projet avec
tout le contexte necessaire. Aucun autre fichier n'est requis pour comprendre
l'architecture et les decisions de design.]

---

## 1. Description du projet

Jeu de combat Pokemon en Python avec interface graphique Pygame.
Projet pedagogique solo centre sur la POO (programmation orientee objet).
Le code inclut des docstrings pedagogiques en anglais dans chaque classe
pour expliquer les concepts OOP utilises.

Portee : combat 1v1 tour par tour, Pokedex anti-doublons, ajout de Pokemon
personnalises, table des 18 types officielle, sprites depuis PokeAPI.

---

## 2. Stack technique

| Composant | Detail |
|---|---|
| Langage | Python 3.10+ (requis pour match/case) |
| GUI | pygame-ce >= 2.5.0 (fork communautaire, API compatible pygame) |
| HTTP | requests >= 2.31.0 |
| Tests | pytest >= 7.0.0 |
| API externe | PokeAPI (https://pokeapi.co/api/v2) -- uniquement au premier lancement |
| Dependances | `pip install -r requirements.txt` |

---

## 3. Regles d'architecture

[REGLE STRICTE] **1 fichier = 1 classe. Aucune exception.**

- State Machine : enum `GameState` dans `game_state.py` gere les transitions.
- Chaque ecran herite de `BaseScreen` (ABC) et implemente 3 methodes abstraites :
  `handle_events(events)`, `update()`, `draw(surface)`.
- `main.py` contient UNIQUEMENT la boucle Pygame et le dispatch via `match/case`.
  Pas de classe dans main.py.
- Navigation : chaque ecran retourne le prochain `GameState` ou `None` (rester).

---

## 4. Arborescence fichiers

```
pokemonv1/
  main.py                        # Point d'entree (boucle Pygame + dispatch match/case)
  game_state.py                  # Enum GameState (MENU, SELECTION, COMBAT, etc.)
  pokemon.py                     # Classe Pokemon
  combat.py                      # Classe Combat (5 methodes exigees par le sujet)
  pokedex.py                     # Classe Pokedex (persistence + anti-doublon)
  type_chart.py                  # Classe TypeChart (18 types)
  game.py                        # Classe Game (orchestrateur)
  gui/
    __init__.py
    constants.py                 # Classe Constants (couleurs, dimensions, FPS)
    base_screen.py               # Classe abstraite BaseScreen (ABC)
    menu_screen.py               # Classe MenuScreen
    selection_screen.py          # Classe SelectionScreen
    combat_screen.py             # Classe CombatScreen
    result_screen.py             # Classe ResultScreen
    pokedex_screen.py            # Classe PokedexScreen
    add_pokemon_screen.py        # Classe AddPokemonScreen
  utils/
    __init__.py
    api_client.py                # Classe ApiClient (fetch PokeAPI + cache local)
    file_handler.py              # Classe FileHandler (lecture/ecriture JSON)
  scripts/
    __init__.py
    populate_pokemon.py          # Script init : peuple pokemon.json via PokeAPI (15 Pokemon)
  data/
    pokemon.json                 # Liste Pokemon jouables (genere par populate_pokemon.py)
    pokedex.json                 # Pokemon rencontres (genere en jeu, anti-doublons)
    type_chart.json              # Table 18x18 efficacite types (cache local)
    default_pokemon.json         # 10 Pokemon en dur, fallback si PokeAPI inaccessible
  assets/
    sprites/                     # Sprites Pokemon 96x96 (telecharges depuis PokeAPI)
  saves/                         # Fichiers sauvegarde (Roadmap 2, pas encore implemente)
  tests/
    __init__.py
    test_pokemon.py              # 9 tests
    test_combat.py               # 15 tests
    test_pokedex.py              # 8 tests
    test_type_chart.py           # 12 tests
    test_file_handler.py         # 7 tests
    test_api_client.py           # 5 tests
  requirements.txt               # pygame-ce, requests, pytest
  AI_CONTEXT.md                  # Ce fichier
  README.md                      # Instructions setup + diagramme Mermaid
```

---

## 5. Inventaire des classes (17 classes + 1 enum)

| Fichier | Classe | Role |
|---|---|---|
| `game_state.py` | GameState (Enum) | Etats de la state machine (MENU, SELECTION, COMBAT, RESULT, POKEDEX, ADD_POKEMON, QUIT) |
| `pokemon.py` | Pokemon | Creature avec name, hp, max_hp, level, attack, defense, types, sprite_path. Methodes : take_damage, is_alive, heal, to_dict, from_dict |
| `combat.py` | Combat | Gestion combat 1v1. 5 methodes exigees : get_type_multiplier, calculate_damage, attack, get_winner, get_loser + register_to_pokedex |
| `pokedex.py` | Pokedex | Registre Pokemon rencontres. Anti-doublon par nom. Persistence JSON. Backup automatique si corruption |
| `type_chart.py` | TypeChart | Table efficacite 18 types officiels. Chargement API ou fichier local. get_combined_multiplier pour double type |
| `game.py` | Game | Orchestrateur : charge Pokemon, TypeChart, Pokedex. Gere premier lancement et fallbacks |
| `gui/constants.py` | Constants | Parametres affichage : SCREEN_WIDTH=800, SCREEN_HEIGHT=600, FPS=60, couleurs, TYPE_COLORS |
| `gui/base_screen.py` | BaseScreen (ABC) | Interface abstraite. Constructor recoit `game`. 3 methodes abstraites : handle_events, update, draw |
| `gui/menu_screen.py` | MenuScreen | 3 boutons : Start Battle, Add Pokemon, Pokedex. Minimum 2 Pokemon pour lancer un combat |
| `gui/selection_screen.py` | SelectionScreen | Grille Pokemon avec sprites et stats. Retourne l'index selectionne |
| `gui/combat_screen.py` | CombatScreen | Sprites, barres PV, bouton Attack, log combat. Gere les tours et les messages d'efficacite |
| `gui/result_screen.py` | ResultScreen | Affiche vainqueur/perdant, bouton retour menu |
| `gui/pokedex_screen.py` | PokedexScreen | Liste scrollable des Pokemon rencontres, stats, types |
| `gui/add_pokemon_screen.py` | AddPokemonScreen | Champs texte (nom, HP, attaque, defense), selection types (max 2), validation |
| `utils/api_client.py` | ApiClient | Client PokeAPI. fetch_pokemon, fetch_type_data, download_sprite, fetch_pokemon_list |
| `utils/file_handler.py` | FileHandler | Methodes statiques : load_json, save_json, file_exists, create_backup |

---

## 6. Decisions de design (combat)

Ces decisions sont figees pour la Roadmap 1 :

| Aspect | Decision |
|---|---|
| Ordre des tours | Joueur attaque en premier, puis adversaire |
| Double type attaquant | Le type principal (index 0) est utilise pour l'attaque |
| Double type defenseur | Multiplicateurs combines (type1 * type2) |
| Formule degats | `max(1, (attaque * multiplicateur_type) - defense)` |
| Taux de miss | 10% fixe (`random < 0.1`) |
| Immunite (0x) | 0 degats, message "It had no effect!" |
| Minimum degats | 1 PV (sauf immunite) -- evite les combats infinis |

---

## 7. Fichiers de donnees

### Generes au runtime (exclus du repo, recrees automatiquement) :

| Fichier | Genere par | Contenu |
|---|---|---|
| `data/pokemon.json` | `scripts/populate_pokemon.py` (via PokeAPI) | 15 Pokemon jouables (Gen 1) |
| `data/pokedex.json` | Le jeu (a chaque combat) | Liste des Pokemon rencontres, anti-doublon par nom |
| `data/type_chart.json` | `scripts/populate_pokemon.py` ou `TypeChart.load_from_api()` | Matrice 18x18 d'efficacite des types |

### Essentiels (trackes dans le repo) :

| Fichier | Role |
|---|---|
| `data/default_pokemon.json` | 10 Pokemon en dur. Fallback utilise quand PokeAPI est inaccessible et que pokemon.json n'existe pas |

### Structure d'un Pokemon dans les JSON :

```json
{
  "name": "Charizard",
  "hp": 78,
  "level": 5,
  "attack": 84,
  "defense": 78,
  "types": ["fire", "flying"],
  "sprite_path": "assets/sprites/charizard.png"
}
```

---

## 8. Gestion erreurs et premier lancement

### Chaine de fallback au demarrage (game.py) :

1. Verifie si `data/pokemon.json` existe
2. Si absent : execute `scripts/populate_pokemon.py` (fetch PokeAPI)
3. Si l'API echoue (exception capturee silencieusement) : charge `data/default_pokemon.json`
4. Si le default est aussi absent : liste vide `[]`

### Autres cas :

| Cas | Comportement |
|---|---|
| `pokedex.json` absent | Pokedex demarre vide, fichier cree au premier ajout (creation paresseuse) |
| `pokedex.json` corrompu | Backup automatique (.bak), reset a vide |
| Moins de 2 Pokemon | Combat interdit, message "Add more Pokemon first (X/2 minimum)" |
| 0 Pokemon | Navigation possible vers Add Pokemon uniquement |
| Sprite introuvable | Pygame gere gracieusement (rectangle colore a la place) |

---

## 9. Etat actuel du projet

[DONE] **Roadmap 1 -- MVP complet**

- Toutes les exigences obligatoires du sujet sont implementees
- 56 tests unitaires passent (pytest)
- Flux complets fonctionnels :
  - Menu -> Selection -> Combat -> Result -> Menu
  - Menu -> Pokedex -> Menu
  - Menu -> Add Pokemon -> Menu
- Code conforme PEP 8, snake_case, docstrings anglais pedagogiques
- Diagramme de classes Mermaid dans README.md

---

## 10. Roadmap 2 [TODO]

### Etape 2.1 : Sauvegarde/Chargement
- `Game.save_game()` : JSON dans `saves/save_YYYYMMDD_HHMMSS.json`
  (pokedex, pokemon dispo, stats joueur)
- `Game.load_game()` : deserialise depuis fichier
- Menu modifie : "New Game" (reset pokedex) / "Load Save" / reste
- `gui/save_select_screen.py` : liste des sauvegardes, selection, suppression
- `GameState.SAVE_SELECT` ajoute a la state machine

### Etape 2.2 : Combat multi-Pokemon
- Selection equipe : choisir N Pokemon (3-6) avant combat
- `gui/team_select_screen.py` : multi-selection avec ordre
- Combat modifie : choix "Attack" / "Switch Pokemon" / "Forfeit"
- GUI combat : indicateur equipe restante (pokeballs pleines/vides)
- Adversaire a aussi une equipe (aleatoire)
- Victoire quand toute l'equipe adverse est KO

---

## 11. Roadmap 3 [TODO]

- **XP et niveaux** : XP gagne en combat, level up avec +stats, evolution a certains niveaux
- **Son et musique** : pygame.mixer, musique de fond, SFX (attaque, hit, miss, KO), volume ajustable
- **Animations combat** : sprite shake sur hit, flash blanc super-efficace, barre PV progressive, fade transitions
- **IA adversaire** : 3 difficultes (facile : attaque toujours / moyen : switch si desavantage type / difficile : calcule les meilleurs coups)
- **Table des types in-game** : ecran consultable avec matrice 18x18 coloree
- **Build .exe** : PyInstaller --onefile --noconsole --name PokemonV1

---

## 12. Comment lancer et tester

### Setup (une seule fois) :

```bash
# Creer et activer le venv
# Windows (Git Bash) :
py -m venv .venv && source .venv/Scripts/activate
# Linux :
python3 -m venv .venv && source .venv/bin/activate

# Installer les dependances
pip install -r requirements.txt

# (Optionnel) Peupler les donnees depuis PokeAPI
# Windows :
py scripts/populate_pokemon.py
# Linux :
python3 scripts/populate_pokemon.py
```

### Lancer le jeu :

```bash
# Windows :
py main.py
# Linux :
python3 main.py
```

### Lancer les tests :

```bash
# Windows :
py -m pytest tests/ -v
# Linux :
python3 -m pytest tests/ -v
```

---

## 13. Conventions de code

- **Style** : PEP 8 strict
- **Nommage** : snake_case pour fonctions/variables, PascalCase pour classes
- **Docstrings** : anglais, pedagogiques (expliquent les concepts OOP utilises)
- **Langue interface** : anglais (noms officiels EN : Charizard, pas Dracaufeu)
- **Pas d'emojis** : nulle part dans le code, les commentaires ou les fichiers generes
- **1 fichier = 1 classe** : regle stricte du sujet
- **Imports** : stdlib d'abord, puis third-party, puis locaux
- **Commande Python** : `py` sur Windows, `python3` sur Linux, jamais `python` seul
