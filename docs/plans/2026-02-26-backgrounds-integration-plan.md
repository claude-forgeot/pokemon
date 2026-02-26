# Backgrounds Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate 3 modern Pokemon-style background images into Menu, Pokedex, and Team Select screens to enhance visual quality for project presentation.

**Architecture:** Load PNG backgrounds in each screen's `__init__` method (similar to existing CombatScreen pattern), blit to surface before drawing UI elements. Fallback to white fill if background missing (backward-compatible).

**Tech Stack:** Python 3.10+, Pygame-CE 2.5+, PNG images 800×600px

---

## Prerequisites

**Before starting implementation:**
- ✅ Design document created: `docs/plans/2026-02-26-audit-soutenance.md`
- ✅ Prompts document created: `docs/plans/2026-02-26-backgrounds-prompts.md`
- ⚠️ **REQUIRED**: 3 PNG images must be generated and placed in `assets/backgrounds/`

**Generate images first:**
1. Use prompts from `docs/plans/2026-02-26-backgrounds-prompts.md`
2. Generate with Perplexity/Midjourney/DALL-E 3
3. Download as PNG, verify 800×600px resolution
4. Name files: `main_menu.png`, `pokedex_lab.png`, `team_arena.png`

**If images not ready:** Skip to Task 1 to create placeholders for testing.

---

## Task 1: Prepare Background Assets

**Files:**
- Create: `assets/backgrounds/main_menu.png` (or placeholder)
- Create: `assets/backgrounds/pokedex_lab.png` (or placeholder)
- Create: `assets/backgrounds/team_arena.png` (or placeholder)

**Step 1: Verify assets/backgrounds/ directory exists**

Run:
```bash
ls -la assets/backgrounds/
```

Expected: Directory exists with `battle_arena.png` already present

**Step 2: Place generated images OR create placeholders**

**Option A - If images generated:**
```bash
# Move generated images to correct location
mv ~/Downloads/main_menu.png assets/backgrounds/
mv ~/Downloads/pokedex_lab.png assets/backgrounds/
mv ~/Downloads/team_arena.png assets/backgrounds/

# Verify dimensions
file assets/backgrounds/main_menu.png
file assets/backgrounds/pokedex_lab.png
file assets/backgrounds/team_arena.png
```

Expected output for each: `PNG image data, 800 x 600`

**Option B - If creating placeholders for testing:**
```bash
# Create solid color placeholders using ImageMagick (if available)
convert -size 800x600 xc:#3498db assets/backgrounds/main_menu.png
convert -size 800x600 xc:#ecf0f1 assets/backgrounds/pokedex_lab.png
convert -size 800x600 xc:#2c3e50 assets/backgrounds/team_arena.png
```

Or use Python to create placeholders:
```python
# create_placeholders.py
import pygame
pygame.init()

colors = {
    "main_menu.png": (52, 152, 219),      # Blue
    "pokedex_lab.png": (236, 240, 241),   # Light gray
    "team_arena.png": (44, 62, 80),       # Dark blue
}

for filename, color in colors.items():
    surface = pygame.Surface((800, 600))
    surface.fill(color)
    pygame.image.save(surface, f"assets/backgrounds/{filename}")
    print(f"Created {filename}")
```

Run: `python3 create_placeholders.py`

**Step 3: Verify all 4 backgrounds present**

Run:
```bash
ls -1 assets/backgrounds/
```

Expected output:
```
battle_arena.png
main_menu.png
pokedex_lab.png
team_arena.png
```

**Step 4: Stage assets (don't commit yet - commit all changes together at end)**

Run:
```bash
git add assets/backgrounds/main_menu.png
git add assets/backgrounds/pokedex_lab.png
git add assets/backgrounds/team_arena.png
```

Expected: Files staged (verify with `git status`)

---

## Task 2: Integrate Background - Menu Screen

**Files:**
- Modify: `gui/menu_screen.py:1-20` (imports + __init__)
- Modify: `gui/menu_screen.py:74-76` (draw method)

**Step 1: Add os import if missing**

Check if `import os` exists at top of `gui/menu_screen.py`.

If missing, add after line 2:
```python
"""Menu screen module -- main menu with game options."""

import os  # ADD THIS LINE

import pygame
```

**Step 2: Load background in __init__ method**

In `MenuScreen.__init__`, add background loading after line 20 (after `self.hover_button = None`):

```python
        self.hover_button = None

        # Load background image
        bg_path = os.path.join("assets", "backgrounds", "main_menu.png")
        if os.path.exists(bg_path):
            self.background = pygame.image.load(bg_path).convert()
        else:
            self.background = None
```

**Step 3: Replace surface.fill with background blit in draw()**

Find line 76 in `draw()` method:
```python
def draw(self, surface):
    """Draw the menu."""
    surface.fill(Constants.WHITE)  # REPLACE THIS LINE
```

Replace with:
```python
def draw(self, surface):
    """Draw the menu."""
    if self.background:
        surface.blit(self.background, (0, 0))
    else:
        surface.fill(Constants.WHITE)
```

**Step 4: Test menu screen manually**

Run:
```bash
python3 main.py
```

Expected:
- Game launches to menu screen
- Background image visible (or placeholder color if used)
- Menu buttons clearly visible over background
- No crashes or errors

Press ESC or close window to exit.

**Step 5: Verify changes**

Run:
```bash
git diff gui/menu_screen.py
```

Expected: Shows +import os, +background loading code, +conditional blit

---

## Task 3: Integrate Background - Pokedex Screen

**Files:**
- Modify: `gui/pokedex_screen.py:1-20` (imports + __init__)
- Modify: `gui/pokedex_screen.py:49-51` (draw method)

**Step 1: Add os import if missing**

Check if `import os` exists at top of `gui/pokedex_screen.py`.

If missing, add after line 2:
```python
"""Pokedex screen module -- displays encountered Pokemon."""

import os  # ADD THIS LINE

import pygame
```

**Step 2: Load background in __init__ method**

In `PokedexScreen.__init__`, add background loading after line 26 (after `self.back_button = pygame.Rect(20, 20, 100, 36)`):

```python
        self.back_button = pygame.Rect(20, 20, 100, 36)

        # Load background image
        bg_path = os.path.join("assets", "backgrounds", "pokedex_lab.png")
        if os.path.exists(bg_path):
            self.background = pygame.image.load(bg_path).convert()
        else:
            self.background = None
```

**Step 3: Replace surface.fill with background blit in draw()**

Find line 51 in `draw()` method:
```python
def draw(self, surface):
    """Draw the Pokedex list with entries."""
    surface.fill(Constants.WHITE)  # REPLACE THIS LINE
```

Replace with:
```python
def draw(self, surface):
    """Draw the Pokedex list with entries."""
    if self.background:
        surface.blit(self.background, (0, 0))
    else:
        surface.fill(Constants.WHITE)
```

**Step 4: Test pokedex screen manually**

Run:
```bash
python3 main.py
```

Steps:
1. Click "Pokedex" button in menu
2. Verify background visible
3. Verify back button works
4. Verify any Pokemon entries (if present) display correctly over background

Press ESC or click Back to return to menu.

**Step 5: Verify changes**

Run:
```bash
git diff gui/pokedex_screen.py
```

Expected: Shows +import os, +background loading code, +conditional blit

---

## Task 4: Integrate Background - Team Select Screen

**Files:**
- Modify: `gui/team_select_screen.py:1-20` (imports + __init__)
- Modify: `gui/team_select_screen.py:95-97` (draw method)

**Step 1: Add os import if missing**

Check if `import os` exists at top of `gui/team_select_screen.py`.

If missing, add after line 2:
```python
"""Team select screen -- lets the player build a team before fighting."""

import os  # ADD THIS LINE

import pygame
```

**Step 2: Load background in __init__ method**

In `TeamSelectScreen.__init__`, add background loading after line 41 (after `self.confirm_button = ...`):

```python
        self.confirm_button = pygame.Rect(
            Constants.SCREEN_WIDTH // 2 - 80,
            Constants.SCREEN_HEIGHT - 55, 160, 40
        )

        # Load background image
        bg_path = os.path.join("assets", "backgrounds", "team_arena.png")
        if os.path.exists(bg_path):
            self.background = pygame.image.load(bg_path).convert()
        else:
            self.background = None
```

**Step 3: Replace surface.fill with background blit in draw()**

Find line 97 in `draw()` method:
```python
def draw(self, surface):
    """Draw the team selection grid."""
    surface.fill(Constants.WHITE)  # REPLACE THIS LINE
```

Replace with:
```python
def draw(self, surface):
    """Draw the team selection grid."""
    if self.background:
        surface.blit(self.background, (0, 0))
    else:
        surface.fill(Constants.WHITE)
```

**Step 4: Test team select screen manually**

Run:
```bash
python3 main.py
```

Steps:
1. Click "Team Battle" button in menu
2. Verify background visible
3. Verify Pokemon cards clearly visible over background
4. Try selecting 3-6 Pokemon
5. Verify "Start Battle!" button appears
6. Click Back to return to menu

**Step 5: Verify changes**

Run:
```bash
git diff gui/team_select_screen.py
```

Expected: Shows +import os, +background loading code, +conditional blit

---

## Task 5: Comprehensive Manual Testing

**Files:**
- None (testing only)

**Step 1: Full game flow test**

Run:
```bash
python3 main.py
```

Test sequence:
1. **Menu screen** - verify background displays
2. Click "Pokedex" - verify background displays, click Back
3. Click "Team Battle" - verify background displays, click Back
4. Click "New Game" - goes to selection (may have white background - OK)
5. Select a Pokemon, battle starts
6. Verify combat background (battle_arena.png) still works
7. Complete or forfeit battle
8. Return to menu - verify background still works

**Step 2: Test backward compatibility (simulate missing backgrounds)**

Temporarily rename backgrounds:
```bash
mv assets/backgrounds/main_menu.png assets/backgrounds/main_menu.png.bak
mv assets/backgrounds/pokedex_lab.png assets/backgrounds/pokedex_lab.png.bak
mv assets/backgrounds/team_arena.png assets/backgrounds/team_arena.png.bak
```

Run game:
```bash
python3 main.py
```

Expected:
- Game launches normally (no crashes)
- Screens show white background (fallback behavior)
- All functionality works

Restore backgrounds:
```bash
mv assets/backgrounds/main_menu.png.bak assets/backgrounds/main_menu.png
mv assets/backgrounds/pokedex_lab.png.bak assets/backgrounds/pokedex_lab.png
mv assets/backgrounds/team_arena.png.bak assets/backgrounds/team_arena.png
```

**Step 3: Check for console errors**

Run game and navigate through all screens.

Expected:
- No pygame errors
- No FileNotFoundError
- No image loading errors
- Clean console output (warnings OK, errors not OK)

**Step 4: Visual quality check**

For each screen with new background:
- [ ] Background visible and correct size (800×600)
- [ ] Text/buttons readable over background
- [ ] No visual glitches (clipping, tearing, flickering)
- [ ] UI elements render on top of background correctly
- [ ] Colors harmonious (not clashing)

If text not readable: May need to adjust background brightness or add text shadows (document as future improvement, not critical for this task).

---

## Task 6: Final Commit & Documentation Update

**Files:**
- Commit: `assets/backgrounds/*.png`
- Commit: `gui/menu_screen.py`
- Commit: `gui/pokedex_screen.py`
- Commit: `gui/team_select_screen.py`
- Optional: Update `README.md` if backgrounds worth mentioning

**Step 1: Verify all changes staged**

Run:
```bash
git status
```

Expected output:
```
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   assets/backgrounds/main_menu.png
        new file:   assets/backgrounds/pokedex_lab.png
        new file:   assets/backgrounds/team_arena.png
        modified:   gui/menu_screen.py
        modified:   gui/pokedex_screen.py
        modified:   gui/team_select_screen.py
```

If not all files staged:
```bash
git add assets/backgrounds/
git add gui/menu_screen.py gui/pokedex_screen.py gui/team_select_screen.py
```

**Step 2: Review changes one final time**

Run:
```bash
git diff --staged
```

Verify:
- Only expected changes present
- No debug print statements left
- No commented-out code
- Clean, minimal changes

**Step 3: Create commit**

Run:
```bash
git commit -m "$(cat <<'EOF'
feat: add modern Pokemon backgrounds to 3 main screens

- Menu: outdoor Pokemon world landscape (golden hour)
- Pokedex: Professor Oak laboratory interior
- Team Select: battle arena tactical room

All backgrounds 800x600px, modern Pokemon TCG illustration style.
Backward-compatible: fallback to white fill if images missing.

Screens modified:
- gui/menu_screen.py: load + blit main_menu.png
- gui/pokedex_screen.py: load + blit pokedex_lab.png
- gui/team_select_screen.py: load + blit team_arena.png

Visual enhancement for project soutenance presentation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit created successfully

**Step 4: Verify commit**

Run:
```bash
git log -1 --stat
```

Expected: Shows commit with 6 files changed

**Step 5: Optional - Update README.md**

If backgrounds significantly improve presentation quality, consider adding note to README features section:

```markdown
## Features

- 151 Gen 1 Pokemon with stats, types, sprites, and moves
- Move-based combat with type effectiveness (18 types)
- ...existing features...
- **Modern Pokemon-style backgrounds** (menu, pokedex, team select)
```

If updated:
```bash
git add README.md
git commit -m "docs: mention new backgrounds in features list

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Create Summary Report

**Files:**
- Create: `docs/plans/2026-02-26-backgrounds-implementation-summary.md`

**Step 1: Create summary document**

```bash
cat > docs/plans/2026-02-26-backgrounds-implementation-summary.md << 'EOF'
# Backgrounds Integration - Implementation Summary

**Date:** 2026-02-26
**Feature:** Modern Pokemon backgrounds for Menu, Pokedex, Team Select screens
**Status:** ✅ Complete

---

## Changes Made

### Assets Added
- `assets/backgrounds/main_menu.png` (800×600px)
- `assets/backgrounds/pokedex_lab.png` (800×600px)
- `assets/backgrounds/team_arena.png` (800×600px)

### Code Modified
- `gui/menu_screen.py`: Added background loading + blitting
- `gui/pokedex_screen.py`: Added background loading + blitting
- `gui/team_select_screen.py`: Added background loading + blitting

### Pattern Used
Consistent pattern across all 3 screens:
1. Import `os` module
2. Load background in `__init__` with `os.path.join()`
3. Store as `self.background` (None if missing)
4. In `draw()`: `blit()` if present, else `fill(WHITE)` fallback

---

## Testing Performed

✅ Manual testing - all screens display backgrounds correctly
✅ Backward compatibility - graceful fallback if images missing
✅ No console errors or crashes
✅ UI elements readable over backgrounds
✅ Full game flow tested (menu → pokedex → team → combat → results)

---

## Visual Quality

**Menu Screen**
- Theme: Outdoor Pokemon world, golden hour sunset
- Mood: Welcoming, nostalgic, adventure beginning

**Pokedex Screen**
- Theme: Professor Oak's research laboratory
- Mood: Scholarly, organized, scientific discovery

**Team Select Screen**
- Theme: Battle arena tactical preparation room
- Mood: Competitive, strategic, championship atmosphere

---

## For Soutenance Presentation

**Key talking points:**
- Modern Pokemon TCG-quality illustrations
- 3 thematic backgrounds enhance immersion
- Backward-compatible design (no breaking changes)
- Follows existing pattern (CombatScreen already had background)

**Demo flow:**
1. Show menu with outdoor Pokemon world
2. Navigate to Pokedex (lab aesthetic)
3. Navigate to Team Select (arena aesthetic)
4. Start battle (existing battle_arena.png)

---

## Related Documents

- Design doc: `docs/plans/2026-02-26-audit-soutenance.md`
- Prompts doc: `docs/plans/2026-02-26-backgrounds-prompts.md`
- This plan: `docs/plans/2026-02-26-backgrounds-integration-plan.md`

---

**Implementation completed successfully.**
EOF
```

**Step 2: Stage and commit summary**

```bash
git add docs/plans/2026-02-26-backgrounds-implementation-summary.md
git commit -m "docs: implementation summary for backgrounds integration

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Completion Checklist

Before considering this feature complete, verify:

- [x] Task 1: 3 PNG backgrounds in `assets/backgrounds/` (800×600px)
- [x] Task 2: Menu screen loads and displays background
- [x] Task 3: Pokedex screen loads and displays background
- [x] Task 4: Team Select screen loads and displays background
- [x] Task 5: Full manual testing passed
- [x] Task 6: Changes committed with descriptive message
- [x] Task 7: Summary document created and committed

**Final verification:**
```bash
python3 main.py
# Navigate: Menu → Pokedex → Menu → Team Battle → Back
# All backgrounds should display correctly
```

---

## Troubleshooting

### Background not displaying
- Check file exists: `ls assets/backgrounds/[filename].png`
- Check dimensions: `file assets/backgrounds/[filename].png` (should be 800×600)
- Check pygame load errors in console

### Text not readable over background
- Background too bright/busy in safe zones
- Solution: Regenerate image with clearer safe zones OR add text shadow
- Quick fix: Add semi-transparent overlay in code (e.g., black 30% alpha rect)

### Game crashes on launch
- Check `import os` added to all 3 files
- Check no syntax errors: `python3 -m py_compile gui/menu_screen.py`
- Check pygame version: `pip show pygame-ce` (should be 2.5+)

### Placeholder backgrounds too plain
- Expected for testing - replace with AI-generated images using prompts doc
- Placeholders functional but not presentation-quality

---

**Plan complete.** Ready for implementation.
