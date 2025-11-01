# Ontbrekende Afbeeldingen - Overzicht

Plekken waar rechthoekjes met kruisjes verschijnen (ontbrekende afbeeldingen/iconen):

## 1. **Nieuwe Speler Selectie Scherm**
- **Locatie**: `game/geo_dash.py` - `show_name_selection()`
- **Probleem**: Mogelijk pijltje links/rechts iconen
- **Status**: Gebruikt alleen tekst (geen afbeeldingen nodig)

## 2. **Bonuspunten Popup (bij landen op platform)**
- **Locatie**: `game/visual_effects.py` - `ScorePopup`
- **Probleem**: Geen afbeeldingen, alleen tekst
- **Status**: Gebruikt alleen tekst (geen afbeeldingen nodig)

## 3. **Streak Indicator (combo's)**
- **Locatie**: `game/visual_effects.py` - `StreakIndicator`
- **Probleem**: Emoji's (🔥, ⚡, ✨) renderen als kruisjes als font ze niet ondersteunt
- **Emoji's gebruikt**:
  - 🔥 "UNSTOPPABLE" (10+ combo)
  - ⚡ "ON FIRE" (5+ combo)  
  - ✨ "STREAK" (3+ combo)
  - 💔 "STREAK LOST" (broken streak)
- **Oplossing**: Icoon afbeeldingen maken als alternatief

## 4. **Pattern Succes/Fail Indicators**
- **Locatie**: Console output (geen visuele UI)
- **Status**: Alleen console logging (✅✅✅)

## 5. **Game Over Scherm**
- **Locatie**: `game/renderer.py` - `draw_game_over()`
- **Probleem**: Mogelijk menu iconen
- **Status**: Gebruikt alleen tekst (geen afbeeldingen nodig)

## 6. **Pijltjes in UI (↑↓←→)**
- **Locatie**: `game/renderer.py` - verschillende menu's
- **Probleem**: Unicode pijltjes (↑/↓) kunnen als kruisjes renderen
- **Waar gebruikt**:
  - "↑/↓ om te selecteren" (game over menu)
  - "Gebruik ↑↓ Pijltjestoetsen" (pause menu)
- **Oplossing**: Icoon afbeeldingen maken of tekst vervangen

## 7. **Difficulty Selection**
- **Locatie**: `game/geo_dash.py` - `show_difficulty_menu()`
- **Status**: Gebruikt alleen tekst

## Aanbevolen Placeholder Iconen

Maak de volgende iconen (32x32px PNG met transparantie):

### Streak/Combo Iconen:
1. `fire-icon.png` - Vuur icoon voor UNSTOPPABLE (🔥 vervanger)
2. `lightning-icon.png` - Bliksem icoon voor ON FIRE (⚡ vervanger)
3. `star-icon.png` - Ster icoon voor STREAK (✨ vervanger)
4. `broken-heart-icon.png` - Gebroken hart voor LOST (💔 vervanger)

### UI Iconen:
5. `arrow-up.png` - Pijl omhoog
6. `arrow-down.png` - Pijl omlaag
7. `arrow-left.png` - Pijl links
8. `arrow-right.png` - Pijl rechts

### Menu Iconen:
9. `menu-select-indicator.png` - Menu selectie indicator (optioneel)
10. `challenge-icon.png` - Challenge/uitdaging icoon

## Tijdelijke Oplossing

Voor nu: vervang emoji's door simpele ASCII tekst in visual_effects.py:
- 🔥 → "[FIRE]" of "***"
- ⚡ → "[ZAP]" of ">>>"
- ✨ → "[STAR]" of "+++"
- 💔 → "[X]" of "---"
- ↑↓ → "OP/NEER" of "UP/DOWN"
