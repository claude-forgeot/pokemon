# Prompts Génération Backgrounds Pokemon

**Date** : 2026-02-26
**Outil cible** : Perplexity (ou autre générateur IA)
**Format** : PNG 800×600px (ratio 4:3)
**Style** : Illustrations modernes Pokemon (qualité TCG officielle)

---

## Spécifications Techniques Communes

### Dimensions & Format
- **Résolution** : 800×600 pixels
- **Ratio** : 4:3 (landscape)
- **Format fichier** : PNG haute résolution
- **Profondeur** : 24-bit couleur minimum

### Style Artistique
- **Référence** : Cartes Pokemon TCG modernes (2020s)
- **Qualité** : Illustrations officielles Pokemon (non pixel art)
- **Rendu** : Peinture digitale, bords nets, couleurs saturées
- **Profondeur** : Slight depth of field (arrière-plan légèrement flou)

### Contraintes UI
- Chaque prompt spécifie une **zone safe** à garder dégagée
- Éviter texte, logos, éléments UI dans les prompts
- Préférer gradients subtils vers les bords

---

## 🏠 Background 1 : Menu Principal

### Fichier Destination
`assets/backgrounds/main_menu.png`

### Écran Cible
`gui/menu_screen.py` (ligne 76 : `surface.fill(Constants.WHITE)`)

### Zone Safe UI
- Centre 400×300px : boutons menu (New Game, Load, Team Battle, Pokedex, Add Pokemon)
- Titre en haut centre (y=90)
- Infos en bas centre (y=565)

### Prompt Complet

```
Generate a vibrant Pokemon-themed background illustration in modern official
Pokemon art style (TCG/recent games quality), 800x600 pixels, landscape
orientation.

SCENE DESCRIPTION:
- Main setting: Outdoor Pokemon world landscape at golden hour (sunset lighting)
- Foreground (bottom 20%): Lush green grass field with 3-4 scattered Pokeballs
  lying in grass
- Midground (center 40%): Silhouettes of iconic Gen 1 Pokemon (Pikachu sitting,
  Charizard flying, Blastoise standing) playing together in the distance,
  about 50-100 meters away
- Background (top 40%): Purple-blue mountain range with Indigo Plateau Pokemon
  League stadium building visible on the highest peak
- Sky: Warm orange-pink-purple sunset gradient with 2-3 Pidgey flying in
  formation, scattered clouds

LIGHTING & ATMOSPHERE:
- Golden hour lighting (warm, soft shadows)
- Sun setting behind mountains (rim lighting on peaks)
- Warm glow on grass in foreground
- Peaceful, end-of-adventure-day feeling

STYLE REQUIREMENTS:
- Modern official Pokemon illustration quality (2020s TCG card artwork style,
  NOT Ken Sugimori watercolor, NOT pixel art)
- Vibrant, saturated colors (bright emerald greens, warm oranges, deep purples)
- Soft digital painting style with clean edges
- Slight depth of field effect (background mountains softer than foreground)
- Welcoming, nostalgic, adventurous atmosphere
- Professional illustration quality (could be official Pokemon promotional art)

COLOR PALETTE:
- Foreground grass: Bright emerald green (#2ecc71, #27ae60)
- Sky gradient: Orange (#f39c12) → Pink (#e91e63) → Purple (#9b59b6)
- Mountains: Deep purple-blue silhouettes (#34495e, #2c3e50)
- Pokeball red: #e74c3c
- Overall mood: Warm and inviting (avoid dark/moody tones)

TECHNICAL SPECS:
- Resolution: Exactly 800×600 pixels (4:3 ratio)
- No text, logos, or UI elements in the image
- Safe zone: Keep central 400×300px area (x:200-600, y:150-450) relatively
  clear and uncluttered for menu buttons overlay
- Composition: Rule of thirds, Pokemon silhouettes on left and right thirds,
  center relatively open
- No human characters

AVOID:
- Pixel art style
- Dark/gloomy atmosphere
- Overly detailed center area
- Text or watermarks
- Licensed character close-ups (keep Pokemon as distant silhouettes)

MOOD: Nostalgic Gen 1 feeling, welcoming, sense of adventure beginning,
"welcome home" atmosphere
```

### Intégration Code

Remplacer ligne 76 de `menu_screen.py` :
```python
# OLD
surface.fill(Constants.WHITE)

# NEW
if hasattr(self, 'background') and self.background:
    surface.blit(self.background, (0, 0))
else:
    surface.fill(Constants.WHITE)
```

Ajouter dans `__init__` :
```python
bg_path = os.path.join("assets", "backgrounds", "main_menu.png")
if os.path.exists(bg_path):
    self.background = pygame.image.load(bg_path).convert()
else:
    self.background = None
```

---

## 🔬 Background 2 : Pokedex (Laboratoire)

### Fichier Destination
`assets/backgrounds/pokedex_lab.png`

### Écran Cible
`gui/pokedex_screen.py` (ligne 51 : `surface.fill(Constants.WHITE)`)

### Zone Safe UI
- Bande verticale centrale 300px (x:250-550) : liste scrollable Pokemon
- Haut centre (y=25) : titre "Pokedex (X encountered)"
- Coin haut gauche : bouton Back

### Prompt Complet

```
Generate a modern Pokemon research laboratory interior background in official
Pokemon art style (TCG quality), 800x600 pixels, landscape orientation.

SCENE DESCRIPTION:
- Setting: Professor Oak's research laboratory interior, well-lit, organized,
  academic atmosphere
- Left side (200px): Tall wooden bookshelves (dark oak) filled with:
  * Pokemon research books (spines visible, various colors)
  * Scientific journals with Pokeball symbols
  * Specimen jars on middle shelves
  * Potted plants (small ferns) on top shelf
- Center area (300px KEEP CLEAR): Wall behind should be neutral light color
  (cream/light grey) with minimal detail
  * One framed Pokemon species chart poster (high on wall, partially visible)
  * Subtle world map outline in background
- Right side (200px): Modern lab equipment area:
  * Stainless steel lab bench/counter
  * Computer terminal/holographic display (showing abstract Pokemon data lines)
  * Microscope (modern, silver/white)
  * Pokeball analysis machine (custom device with glass dome)
  * Glass beakers and scientific equipment
  * Small labeled storage containers
- Floor: Clean white laboratory tiles with subtle grey grid lines
- Lighting: Bright, even illumination (fluorescent lab lighting from ceiling)

DETAILS TO INCLUDE:
- 3-4 Pokeballs placed on shelves (casually, not in focus)
- Computer screen on right showing abstract Pokemon silhouettes (blurred data)
- Reference books with visible Pokeball logo on spines
- White lab coat hanging on wall hook (left side)
- Small potted plants (adds warmth to scientific space)
- Clipboard with papers on lab bench
- Safety goggles on counter

STYLE REQUIREMENTS:
- Modern official Pokemon illustration style (clean, professional, TCG quality)
- Interior architecture perspective (slight 3-point perspective)
- Bright, inviting laboratory (NOT dark or ominous)
- Color scheme:
  * Dominant: Cool blues (#3498db) and clean whites (#ecf0f1)
  * Accent: Warm wood tones (#8b4513, #a0522d)
  * Pokeball reds (#e74c3c) as small color pops
- Professional scientific atmosphere but still Pokemon-universe aesthetic
- Clean, organized, scholarly environment (Professor Oak's workspace)

LIGHTING & ATMOSPHERE:
- Bright fluorescent lighting (cool white, even illumination)
- No harsh shadows (laboratory lighting is diffused)
- Slight highlights on metallic equipment (reflective surfaces)
- Warm natural wood contrasts with cool lab equipment

TECHNICAL SPECS:
- Resolution: Exactly 800×600 pixels (4:3 ratio)
- No text overlays or UI elements
- Safe zone: Keep central vertical strip (x:250-550, 300px wide) relatively
  clear and minimal detail for Pokemon entries list overlay
- Edge detail concentration: More visual interest on left and right thirds
- Slightly blurred edges/corners to focus attention on center

AVOID:
- Dark, creepy laboratory aesthetic
- Clutter or mess (keep it organized and professional)
- Close-up Pokemon characters
- Text on books/screens (keep abstract or blurred)
- Heavy shadows

MOOD: Scholarly, organized, scientific discovery, Professor Oak's trusted
workspace, academic research, Pokedex data collection headquarters
```

### Intégration Code

Remplacer ligne 51 de `pokedex_screen.py` :
```python
# OLD
surface.fill(Constants.WHITE)

# NEW
if hasattr(self, 'background') and self.background:
    surface.blit(self.background, (0, 0))
else:
    surface.fill(Constants.WHITE)
```

Ajouter dans `__init__` :
```python
bg_path = os.path.join("assets", "backgrounds", "pokedex_lab.png")
if os.path.exists(bg_path):
    self.background = pygame.image.load(bg_path).convert()
else:
    self.background = None
```

---

## 🏟️ Background 3 : Team Selection (Arène)

### Fichier Destination
`assets/backgrounds/team_arena.png`

### Écran Cible
`gui/team_select_screen.py` (ligne 97 : `surface.fill(Constants.WHITE)`)

### Zone Safe UI
- Centre 600×400px (x:100-700, y:100-500) : grille 5×N cartes Pokemon
- Haut centre (y=25) : titre "Choose your team (3-6)"
- Bas centre (y=540) : bouton "Start Battle!"

### Prompt Complet

```
Generate a Pokemon battle arena/training facility background in modern official
Pokemon art style (TCG quality), 800x600 pixels, landscape orientation.

SCENE DESCRIPTION:
- Setting: Indoor Pokemon battle training facility / team preparation tactical
  room, professional esports arena atmosphere
- Left side (100px): Team equipment area:
  * Modern high-tech lockers (dark blue metal, clean lines)
  * Pokeball storage rack system (organized cylindrical holders)
  * Small trophy shelf (subtle, not focal point)
  * Championship banners hanging on wall (abstract, blurred)
- Center area (600px MOSTLY CLEAR): Main tactical wall:
  * Large abstract tactical display board (top center, glowing blue hologram)
  * Battle field layout visualization (very abstract, geometric, blurred)
  * Clean dark grey/blue wall surface
  * Subtle team roster board (empty slots, high on wall)
- Right side (100px): Strategic command area:
  * Digital tactical screens on wall (abstract data displays, blue glow)
  * Modern coach's desk/podium (minimalist)
  * More Pokeball storage units (organized, cylindrical high-tech racks)
  * Computer terminal showing abstract stats
- Background (top portion): Large viewing window/glass wall showing:
  * Pokemon stadium arena beyond (visible through glass)
  * Stadium lights and seating (blurred, distant)
  * Sense of "war room overlooking battlefield"
- Floor: Modern sports facility flooring (dark blue-grey #2c3e50 with white
  line markings, professional arena aesthetic)
- Ceiling: Professional arena lighting (spotlights visible, cool white LED)

DETAILS TO INCLUDE:
- Pokeball storage units (organized in vertical cylindrical racks, glowing)
- Digital tactical screens with abstract blue glowing data (not readable text)
- Trophy case or championship banners (subtle, in left background)
- Team roster board with empty slots (abstract, high on wall)
- Professional lighting fixtures (LED spotlights, modern)
- Tactical diagrams on screens (abstract geometric shapes)
- Sense of "coach's strategic command center"

STYLE REQUIREMENTS:
- Modern official Pokemon art style (sleek, professional, competitive, TCG
  quality)
- Interior architecture perspective (wide angle, slight perspective)
- Color scheme:
  * Dominant: Deep navy blues (#2c3e50, #34495e), slate grays (#7f8c8d)
  * Accent: Bright electric blue (#3498db) for screens/tech
  * Highlight: Red (#e74c3c) and white (#ecf0f1) accents
  * Pokeball red as small color pops on storage units
- Professional sports facility aesthetic (esports arena, tactical room)
- Clean, high-tech, strategic war room feel
- Motivational/competitive championship atmosphere

LIGHTING & ATMOSPHERE:
- Cool LED lighting (bluish-white, professional arena lighting)
- Glowing tactical screens (blue hologram effect)
- Subtle rim lighting on equipment
- Focused, strategic, pre-battle tension
- "Championship finals preparation room" vibe

TECHNICAL SPECS:
- Resolution: Exactly 800×600 pixels (4:3 ratio)
- No text, logos, or readable UI elements
- Safe zone: Keep majority of center area clear (x:100-700, y:100-500,
  600×400px) for Pokemon card grid overlay
- Composition: Visual interest on left and right edges, darker corners with
  natural vignette effect, lighter center
- Perspective: Slight wide-angle looking into the room

AVOID:
- Cluttered or messy room
- Bright cheerful colors (keep professional/competitive)
- Close-up Pokemon characters
- Readable text on screens (keep abstract)
- Overly dark/gloomy (should feel professional, not ominous)

MOOD: Competitive, strategic, pre-battle preparation, championship atmosphere,
tactical command center, professional esports arena backstage, "this is where
champions are made" feeling
```

### Intégration Code

Remplacer ligne 97 de `team_select_screen.py` :
```python
# OLD
surface.fill(Constants.WHITE)

# NEW
if hasattr(self, 'background') and self.background:
    surface.blit(self.background, (0, 0))
else:
    surface.fill(Constants.WHITE)
```

Ajouter dans `__init__` après ligne 22 :
```python
bg_path = os.path.join("assets", "backgrounds", "team_arena.png")
if os.path.exists(bg_path):
    self.background = pygame.image.load(bg_path).convert()
else:
    self.background = None
```

---

## 📋 Checklist Génération & Intégration

### Génération Images

- [ ] Copier Prompt 1 (Menu) dans Perplexity
- [ ] Générer image 800×600px
- [ ] Télécharger `main_menu.png`
- [ ] Vérifier zone centrale dégagée
- [ ] Copier Prompt 2 (Pokedex) dans Perplexity
- [ ] Générer image 800×600px
- [ ] Télécharger `pokedex_lab.png`
- [ ] Vérifier bande verticale centrale claire
- [ ] Copier Prompt 3 (Team Select) dans Perplexity
- [ ] Générer image 800×600px
- [ ] Télécharger `team_arena.png`
- [ ] Vérifier zone grille Pokemon dégagée

### Intégration Code

- [ ] Placer les 3 PNG dans `assets/backgrounds/`
- [ ] Modifier `gui/menu_screen.py` (lignes 14-20 + ligne 76)
- [ ] Modifier `gui/pokedex_screen.py` (lignes 18-24 + ligne 51)
- [ ] Modifier `gui/team_select_screen.py` (lignes 22-28 + ligne 97)
- [ ] Ajouter `import os` si manquant dans chaque fichier
- [ ] Tester le jeu : `python3 main.py`
- [ ] Vérifier affichage des 3 backgrounds
- [ ] Vérifier lisibilité des boutons/textes sur backgrounds
- [ ] Commit : `git add assets/backgrounds/ gui/`
- [ ] Commit : `git commit -m "feat: add 3 modern Pokemon backgrounds (menu, pokedex, team)"`

---

## 🎨 Conseils Génération IA

### Si Perplexity ne génère pas d'images
- Utiliser **Midjourney** : `/imagine [prompt]` + `--ar 4:3 --style raw --v 6`
- Utiliser **DALL-E 3** (ChatGPT Plus) : coller prompt directement
- Utiliser **Stable Diffusion** (ComfyUI/A1111) : adapter prompt avec keywords

### Ajustements Post-Génération
- **Redimensionner** si nécessaire : `800×600px` exact
- **Ajuster luminosité** si texte peu lisible dessus
- **Réduire saturation** si couleurs trop vives (UI difficile à lire)
- **Ajouter léger vignette** dans Photoshop/GIMP si nécessaire

### Itération
Si zone safe pas assez dégagée :
- Ajouter dans prompt : "with a large clear central area"
- Ou post-process : ajouter rectangle semi-transparent au centre

---

**Document créé le** : 2026-02-26
**Auteur** : Claude Sonnet 4.5
**Statut** : Prêt pour génération et intégration
