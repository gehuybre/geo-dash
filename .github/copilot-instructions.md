# Geo Dash - AI Coding Agent Instructions

## Project Overview

A Geometry Dash clone built with Pygame featuring physics-validated obstacle generation, custom asset support, and modular architecture. The game auto-scrolls the player while they jump over procedurally generated obstacles.

## Project Structure

### 📁 Root Files
- **geo_dash.py** - Main game entry point, initializes pygame and runs game loop
- **config.py** - Global configuration (physics constants, colors, screen dimensions)
- **player.py** - Player class with jump mechanics and collision detection
- **obstacles.py** - Obstacle class and ObstacleGenerator with pattern loading
- **renderer.py** - Rendering system for game objects and UI
- **assets.py** - AssetManager for loading sprites, backgrounds, and custom graphics
- **requirements.txt** - Python dependencies (pygame, Pillow)
- **save_data.json** - Persistent high score storage
- **bar_types.json** - Bar type definitions (base unit: 30×30px)

### 📁 core/
Core game systems and physics calculations:
- **__init__.py** - Package initializer
- **physics.py** - Physics validator (max jump height/distance, climbing validation)

### 📁 managers/
Game state and data managers:
- **__init__.py** - Package initializer
- **pattern_manager.py** - Loads and validates obstacle patterns from JSON
- **bar_type_manager.py** - Resolves bar type references (bar-{width}-{height}, bar-{width}-{floor}-{ceiling})
- **score_manager.py** - Score tracking and high score persistence

### 📁 systems/
Input and control systems:
- **__init__.py** - Package initializer
- **input_handler.py** - Keyboard/mouse input processing

### 📁 obstacle_patterns/
JSON pattern definitions (20-40 blocks each):
- **Pattern files** - Marathon mixes, climbing patterns, platform sequences
- Each pattern has: name, description, obstacles array, metadata (type, length, rhythm)
- Examples: `marathon_mix_alpha.json`, `sky_climber.json`, `valley_runner.json`

### 📁 assets/
Visual resources organized by type:
- **backgrounds/** - Background images (cycle every 5 points)
- **hazards/** - SVG hazard graphics (6 types: spikes, saw, lava, electric, laser, poison)
- **obstacles/** - Custom obstacle sprites (optional)
- **player-characters/** - Player sprite alternatives (optional)
- **decoration/** - Decorative elements (optional)

### 📁 archive/
Historical patterns and deprecated code:
- **old-patterns/** - Previous pattern versions (34+ archived patterns)

### 📁 md-files/
Documentation markdown files:
- **ASSETS_README.md** - Asset loading guide
- **BACKGROUNDS_README.md** - Background system documentation
- **BAR_TYPES_README.md** - Bar type system explanation
- **DYNAMIC_BAR_TYPES.md** - Dynamic bar type format reference
- **OBSTACLE_PATTERNS_README.md** - Pattern creation guide
- **OLD_PATTERNS_README.md** - Archived patterns documentation
- **PATTERN_GENERATOR_V2.md** - V2 pattern generator design principles
- **HAZARD_GRAPHICS.md** - SVG hazard graphics reference

### 📁 Generators (Root)
Pattern generation scripts:
- **pattern_generator.py** - Original pattern generator (22 patterns)
- **pattern_generator_v2.py** - Enhanced generator with gameplay design principles (7 patterns)

## Critical Architecture Patterns

### Physics-First Design
All obstacle generation is constrained by **physics validation** - patterns must be provably completable:
- `core/physics.py` calculates max jump height (98px) and distance (225px) from `GRAVITY` and `JUMP_POWER` constants
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
  "description": "Pattern description for level designers",
  "obstacles": [
    {"bar_type": "bar-3-2", "gap_type": "gap-1.5"},
    {"bar_type": "bar-4-3-1", "gap_type": "gap-0"}
  ],
  "metadata": {
    "type": "bar|platform|mixed",
    "length": 25,
    "rhythm": "Rhythm hint for gameplay feel"
  }
}
```
- Patterns spawn **all obstacles at once** with relative positioning from `base_x`
- `gap_type: "gap-0"` creates stackable obstacles (towers/pyramids) - validate with `physics.can_climb()`
- Dynamic bar types: `bar-{width}-{height}` for ground, `bar-{width}-{floor}-{ceiling}` for floating platforms
- Dynamic gaps: `gap-{multiplier}` where multiplier × 100px = gap distance (max 2.25 = 225px)

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
Place files in `assets/` subdirectories:
- `backgrounds/*.png` or `*.jpg` - Multiple backgrounds that cycle every 5 points
- `hazards/*.svg` - Hazard graphics (6 types included: spikes, saw, lava, electric, laser, poison)
- `player-characters/player.png` - 40x40px sprite (optional)
- `obstacles/obstacle.png` - Scaled to fit obstacle dimensions (optional)
- `backgrounds/ground.png` - Tiled horizontally (optional)

No code changes needed - `AssetManager` auto-detects and loads on startup.

### Creating New Obstacle Patterns
1. Use `pattern_generator_v2.py` for gameplay-designed patterns following best practices
2. Or create `obstacle_patterns/new_pattern.json` manually with obstacle definitions
3. Run game - `PatternManager` auto-loads and validates on init
4. Check console output for validation errors (e.g., "height exceeds max")
5. Debug with physics constraints: max height 98px, max gap 225px, stacks need climbing validation

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
   - See `ObstacleGenerator.generate_obstacle()` - spawns entire pattern at once
   
5. **`gap_type: "gap-0"` is special** - means stacked/touching, not "no gap then random"
   - Zero gap triggers different physics validation (climbing vs jumping)
   - See `PatternManager._validate_pattern()` handling of stacked obstacles

6. **Killzones use height 0** - `bar-{width}-0` with `is_killzone: true` flag
   - Rendered as animated red/orange warning stripes on the floor
   - Used in platform patterns to encourage staying on platforms
   - See `Obstacle._draw_killzone()` for rendering logic

## Testing & Debugging

No automated tests exist. Manual testing workflow:
1. Run game and play through patterns
2. Check console for physics validation output on startup
3. Modify `config.py` constants to stress-test patterns
4. Add `print()` statements in `PatternManager._validate_pattern()` to debug failures

For obstacle issues: temporarily set `MIN_OBSTACLE_GAP = MAX_OBSTACLE_GAP` to get consistent generation for testing.

## Version Control

**Do not commit or push to GitHub unless explicitly requested by the user.** Make changes locally and let the user review before suggesting commits.
