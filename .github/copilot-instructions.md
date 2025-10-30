# Geo Dash - AI Coding Agent Instructions

## Project Overview

A Geometry Dash clone built with Pygame featuring physics-validated obstacle generation, custom asset support, and modular architecture. The game auto-scrolls the player while they jump over procedurally generated obstacles.

## Critical Architecture Patterns

### Physics-First Design
All obstacle generation is constrained by **physics validation** - patterns must be provably completable:
- `core/physics.py` calculates max jump height (~85px) and distance (~360px) from `GRAVITY` and `JUMP_POWER` constants
- `PatternManager._validate_pattern()` simulates player movement through obstacle sequences before allowing patterns to load
- **Never** manually create obstacles without validating against `physics.can_jump_over()`, `physics.can_climb()`, or `physics.can_land_safely()`

### Modular Component System
The codebase avoids circular imports through lazy loading:
- `assets.py` provides the global `asset_manager` - import it **inside functions**, not at module level
- `Renderer` is imported **inside `Game.__init__()`** after pygame initialization
- Pattern: defer heavy imports until needed in methods

### Asset Loading with Graceful Fallbacks
All visual assets (sprites, backgrounds, ground) are **optional**:
- `AssetManager.load_image()` returns `None` if file not found - calling code must handle this
- Uses PIL/Pillow for format support if available, falls back to BMP-only pygame loading
- Procedural generation (gradient blocks, clouds) kicks in when custom assets missing
- Example: `self.custom_sprite = asset_manager.get_player_sprite()` → check if None before using

### Pattern System
Obstacle patterns live in `obstacle_patterns/*.json`:
```json
{
  "name": "Pattern Name",
  "obstacles": [
    {"height": 60, "width": 30, "gap_after": 200},
    {"height": 0, "width": 30, "gap_after": 0}  // gap_after=0 means stacked
  ]
}
```
- Patterns spawn **all obstacles at once** with relative positioning from `base_x`
- `gap_after: 0` creates stackable obstacles (towers/pyramids) - validate with `physics.can_climb()`
- 70% chance to use pattern vs. random generation in `ObstacleGenerator.generate_obstacle()`

## Development Workflows

### Running the Game
```bash
# Activate virtual environment first (if exists)
.venv/bin/python geo_dash.py

# Or use system Python
python geo_dash.py
```

### Configuration Changes
All tunable constants in `config.py`:
- Physics: `GRAVITY`, `JUMP_POWER`, `PLAYER_SPEED`
- Generation: `MIN_OBSTACLE_GAP`, `MAX_OBSTACLE_GAP`
- Visuals: Pastel color palette constants

**Important**: Changing physics constants invalidates existing patterns - revalidate with `PatternManager`

### Adding Custom Assets
Place files in `assets/` directory:
- `backgrounds/*.png` - Multiple backgrounds that cycle every 5 points
- `player.png` - 40x40px sprite
- `obstacle.png` - Scaled to fit obstacle dimensions
- `ground.png` - Tiled horizontally

No code changes needed - `AssetManager` auto-detects and loads on startup.

### Creating New Obstacle Patterns
1. Create `obstacle_patterns/new_pattern.json` with obstacle definitions
2. Run game - `PatternManager` auto-loads and validates on init
3. Check console output for validation errors (e.g., "height exceeds max")
4. Debug with physics constraints: max height ~85px, max gap ~360px, stacks need `can_climb()` clearance

## Key Conventions

### Double Jump Mechanics
Player has 2-jump capability:
- First jump: `JUMP_POWER` from ground (`jumps_used = 0`)
- Second jump: `JUMP_POWER * 0.9` mid-air (`jumps_used = 1`)
- Reset when `on_ground = True` in `Player.update()`

### Collision System
- All game objects provide `get_rect()` returning `pygame.Rect`
- `ObstacleGenerator.check_collision()` handles player-obstacle collision
- Player can land **on top** of obstacles - `y` position set to obstacle top, `on_ground = True`

### Score Persistence
- Distance-based: 1 point = 100 pixels traveled
- `ScoreManager` auto-saves high score to `save_data.json`
- Call `check_and_save_high_score()` on game over only

### Pygame 2.6.1 + Python 3.14 Bug
Font module has compatibility issues:
```python
try:
    self.font = pygame.font.Font(None, 36)
    self.font_available = True
except (NotImplementedError, ImportError):
    self.font_available = False
```
Always wrap font initialization in try-except and provide fallback rendering.

## Common Pitfalls

These are **patterns discovered in the existing codebase** that must be followed - they're not bugs, they're intentional design decisions:

1. **Don't validate obstacles visually** - trust physics calculations over "it looks jumpable"
   - The codebase uses `physics.can_jump_over()` etc., not manual pixel measurements
   
2. **Import `asset_manager` inside functions** to avoid circular dependencies
   - Example in `player.py`: `from assets import asset_manager` is inside `__init__()`, not at module level
   - Example in `obstacles.py`: Same pattern - lazy import to break circular dependency
   
3. **Check for None sprites** before blitting - `if self.custom_sprite:` pattern
   - `AssetManager.load_image()` returns `None` when file not found
   - All rendering code checks: `if self.custom_sprite: screen.blit(...)` else use procedural generation
   
4. **Patterns spawn all at once** - don't call `generate_obstacle()` per pattern obstacle
   - When a pattern is selected, all obstacles are created in one loop with relative positioning
   - See `ObstacleGenerator.generate_obstacle()` line ~70-90
   
5. **`gap_after: 0` is special** - means stacked/touching, not "no gap then random"
   - Zero gap triggers different physics validation (climbing vs jumping)
   - See `PatternManager._validate_pattern()` handling of stacked obstacles

## Testing & Debugging

No automated tests exist. Manual testing workflow:
1. Run game and play through patterns
2. Check console for physics validation output on startup
3. Modify `config.py` constants to stress-test patterns
4. Add `print()` statements in `PatternManager._validate_pattern()` to debug failures

For obstacle issues: temporarily set `MIN_OBSTACLE_GAP = MAX_OBSTACLE_GAP` to get consistent generation for testing.

## Version Control

**Do not commit or push to GitHub unless explicitly requested by the user.** Make changes locally and let the user review before suggesting commits.
