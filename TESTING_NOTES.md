# Kivy Gameplay Testing Notes

## Current Status
- ✅ App launches successfully
- ✅ Patterns load (10 medium difficulty patterns)
- ✅ No startup crashes
- 🧪 Gameplay needs testing

## Test Checklist

### Visual Rendering
- [ ] Player character visible at correct position
- [ ] Obstacles appear and scroll left
- [ ] Ground/sky rendered properly
- [ ] Score displays in UI
- [ ] Game over screen appears

### Player Physics
- [ ] Player starts at correct Y position (250px from bottom)
- [ ] Gravity pulls player down correctly
- [ ] Jump power works (tap/click to jump)
- [ ] Double jump works
- [ ] Player lands on ground correctly

### Obstacles
- [ ] Obstacles generate from patterns
- [ ] Obstacles scroll left at correct speed
- [ ] Obstacle heights/widths match patterns
- [ ] Gaps between obstacles are correct
- [ ] Floating platforms (y_offset > 0) positioned correctly

### Collision Detection
- [ ] Player dies when hitting obstacle sides
- [ ] Player can land on top of obstacles
- [ ] Killzone obstacles trigger game over
- [ ] Collision detection accurate

### Score System
- [ ] Distance-based score increments
- [ ] Landing bonuses work
- [ ] Combo streaks tracked
- [ ] High score saves

### Touch Controls
- [ ] Tap anywhere to jump works
- [ ] Jump button visible and functional
- [ ] No lag in response

## Known Coordinate System Issues

### Pygame vs Kivy Y-Axis:
- **Pygame**: Y=0 at top, Y increases downward
- **Kivy**: Y=0 at bottom, Y increases upward

### Current Settings:
- `shared_config.py`: GROUND_Y = 650 (Pygame coords, for pattern manager)
- `kivy_game/config.py`: GROUND_Y = 250 (Kivy coords, 900 - 650)

### Potential Issues:
1. **Obstacle Y positioning**: Obstacles might be upside-down or off-screen
2. **Gravity direction**: Should be negative in Kivy (pulling down = decreasing Y)
3. **Collision rectangles**: May need Y-axis inversion

## Testing Commands

```bash
# Run the Kivy game
.venv/bin/python main.py

# Run the Pygame version for comparison
.venv/bin/python game/geo_dash.py
```

## Debug Output to Check

When running, look for:
- Pattern loading messages (should see 10 patterns)
- Obstacle generation happening
- Score updates
- Any error messages about coordinates

## Next Steps After Testing

1. If player/obstacles not visible → Fix Y-coordinate conversion
2. If gravity wrong direction → Invert gravity sign in player.update()
3. If collisions wrong → Fix collision rect calculations
4. If everything works → Add visual effects and polish!
