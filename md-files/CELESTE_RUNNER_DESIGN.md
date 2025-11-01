# Celeste Runner - Design Document

## Overview

**Celeste Runner** is a wall-jumping auto-scroller that transforms the original Geo Dash from a jumping-over-obstacles platformer into a fast-paced wall-to-wall survival game. The player automatically scrolls right and must chain wall jumps to stay alive - touching the floor or falling behind the screen edge means instant death.

## Core Design Pillars

### 1. **One Button, Infinite Depth**
- Single input: SPACE/UP/W to jump
- Context-aware behavior:
  - **On wall**: Launch a wall jump perpendicular to the wall
  - **In air (with coyote time)**: Execute late wall jump
  - **Buffered**: Remember jump input for 5 frames

### 2. **Continuous Momentum**
- Camera auto-scrolls right at 3px/frame, accelerating to 8px/frame
- Player has no manual horizontal control - only wall jumps change trajectory
- Falling behind the left screen edge = death
- Creates constant pressure and rhythm

### 3. **Precision Under Pressure**
- Wall slide mechanics slow descent (gravity: 0.2 vs 0.8 in air)
- Wall cling time: 8 frames before sliding starts
- Coyote time: 6 frames after leaving wall to still execute wall jump
- Jump buffering: 5 frames to remember early inputs

### 4. **Readable Fairness**
- Floor is bright red with warning stripes - clearly lethal
- Walls highlight when player can grab them
- Different wall types have distinct visual identities:
  - **Normal walls**: Neutral gray/blue
  - **Crumbly walls**: Brown, crack and disappear after 0.5 seconds
  - **Slippery walls**: Ice blue with sparkles

## Physics System

### Wall Jump Mechanics
```
Wall Jump Force:
  - Horizontal: 8px/frame (away from wall)
  - Vertical: -14px/frame (upward)
  
Gravity:
  - Falling: 0.8px/frame²
  - Wall sliding: 0.2px/frame²
  
Air Resistance:
  - Horizontal velocity × 0.96 each frame
```

### Calculated Constraints
- **Max wall jump height**: ~122px (based on gravity + jump force)
- **Max wall jump distance**: ~280px horizontal
- **Min wall gap**: 80-120px (difficulty dependent)
- **Max wall gap**: 200-280px (difficulty dependent)
- **Wall height range**: 60px (min grabbable) to 400px (max)

### Physics Validation
The `PhysicsCalculator` validates wall layouts before generation:
- Checks if gaps are reachable via wall jumps
- Validates vertical height differences
- Ensures no impossible sequences

## Player States

### State Machine
1. **FALLING** - Free fall with full gravity
2. **WALL_SLIDING** - Clinging to wall with reduced gravity
3. **WALL_JUMPING** - Mid-air after wall jump execution

### State Transitions
```
FALLING → WALL_SLIDING: When player touches wall
WALL_SLIDING → WALL_JUMPING: When jump pressed
WALL_JUMPING → FALLING: When horizontal velocity decays
WALL_SLIDING → FALLING: When player leaves wall without jumping
```

## Level Generation

### Wall Spawning
- Walls spawn at `camera_x + 1800px` (off-screen right)
- Random gaps between `min_gap` and `max_gap`
- Random heights between 60px and 400px
- 70% ground-based, 30% floating walls

### Wall Types (Difficulty-based)
**Easy Mode**:
- 90% normal walls
- 5% crumbly walls
- 5% slippery walls

**Medium Mode**:
- 70% normal walls
- 20% crumbly walls
- 10% slippery walls

**Hard Mode**:
- 50% normal walls
- 30% crumbly walls
- 20% slippery walls

### Procedural Generation
The `WallGenerator` continuously generates walls as the camera advances:
1. Remove walls that scrolled off-screen (left edge - 200px)
2. Generate new walls when `next_wall_x < camera_x + spawn_distance`
3. Randomly place walls within physics-validated constraints

## Camera System

### Auto-Scroll Behavior
- Starts at `AUTO_SCROLL_SPEED = 3px/frame`
- Accelerates by `0.002px/frame²`
- Caps at `MAX_AUTO_SCROLL_SPEED = 8px/frame`
- Smooth acceleration: `speed = speed * 0.95 + target * 0.05`

### Death Zones
- **Left edge**: Player X < camera_x - 50px
- **Floor**: Player Y + height >= GROUND_Y

### Score Calculation
- Distance-based: `score = total_pixels_traveled / 100`
- No bonuses or combos - pure survival distance

## Visual Design

### Color Palette
```python
SKY_BLUE = (173, 216, 230)      # Calm sky
GROUND_DANGER = (200, 50, 50)   # Lethal floor (red)
DEATH_RED = (255, 50, 50)       # Death warning stripes
WALL_COLOR = (180, 180, 200)    # Neutral walls
WALL_HIGHLIGHT = (220, 220, 240) # Walls when grabbable
PLAYER_PINK = (255, 182, 193)   # Player character
YELLOW = (255, 223, 0)          # UI highlights
```

### Visual Feedback
- **Wall sliding**: Player rotates 10° toward wall, squishes horizontally
- **Wall jumping**: Player rotates continuously, squishes vertically
- **Death**: Screen overlay darkens, death reason displayed
- **Floor danger**: Animated red/white diagonal stripes

## UI Elements

### HUD (Top-left)
- **Distance**: `Afstand: {score}m`
- **Speed**: `Snelheid: {percent}%` (shows scroll acceleration)

### HUD (Top-right)
- **High Score**: `Beste: {high_score}m`

### Game Over Screen
- Death reason (floor touch or fell behind)
- Current distance score
- "NEW RECORD!" if high score beaten
- Instructions to restart or quit

## Difficulty Settings

### Easy
- Wider wall gaps: 120-200px
- More normal walls (90%)
- Slower initial scroll speed

### Medium
- Standard gaps: 100-280px
- Balanced wall types (70% normal)
- Standard scroll speed

### Hard
- Tighter gaps: 80-280px
- More hazardous walls (50% normal)
- Faster scroll acceleration

## Technical Architecture

### File Structure
```
game/
  celeste_runner.py   # Main game loop
  player_celeste.py   # Wall-jumping player class
  walls.py            # Wall class and generator
  camera.py           # Auto-scrolling camera
  config.py           # Constants (updated for wall physics)
  
core/
  physics.py          # Wall jump physics calculator (rewritten)
  
managers/
  score_manager.py    # High score persistence (unchanged)
```

### Key Design Patterns

#### Physics-First Validation
All wall generation goes through `PhysicsCalculator.is_valid_wall_layout()`:
- Validates gaps are jumpable
- Checks vertical height differences
- Prevents impossible wall sequences

#### State-Based Player Control
Player uses state machine rather than boolean flags:
- Clearer transitions between wall slide → jump → fall
- Single source of truth for player behavior
- Easier to extend with new states (e.g., dash, grapple)

#### Camera-Relative Rendering
All world positions converted to screen space via `camera.world_to_screen()`:
- Player drawn at `player.x - camera.x`
- Walls drawn at `wall.x - camera.x`
- Enables infinite scrolling right

#### Graceful Fallbacks
- Custom fonts with system font fallback
- Sprite loading with procedural generation fallback
- All rendering wrapped in try-except for stability

## Controls Reference

### In-Game
- **SPACE / ↑ / W** - Jump (context-aware)
- **ESC / P** - Pause game

### Pause Menu
- **ESC / P** - Resume
- **R** - Restart

### Game Over
- **SPACE** - Play again
- **ESC** - Quit to desktop

## Future Expansion Ideas

### Additional Mechanics
1. **Double jump** - Single air jump after wall jump
2. **Dash** - Horizontal burst for emergency gap crossing
3. **Grapple points** - Special nodes to swing from
4. **Moving walls** - Walls that shift vertically

### Wall Types
1. **Boost walls** - Launch player higher/further
2. **Sticky walls** - Extended cling time
3. **Conveyor walls** - Push player up or down while sliding
4. **Dash walls** - Grant temporary dash ability

### Level Features
1. **Checkpoints** - Save progress in marathon mode
2. **Collectibles** - Optional orbs for bonus points
3. **Obstacles** - Hazards between walls (spikes, projectiles)
4. **Themed zones** - Visual variety every 1000m

### Gameplay Modes
1. **Endless Mode** - Current implementation
2. **Sprint Mode** - Fixed distance, fastest time wins
3. **Challenge Mode** - Handcrafted difficult sequences
4. **Zen Mode** - No death, practice wall jumping

## Performance Considerations

### Optimization Strategies
- **Dirty rects**: Only redraw changed screen regions (optional)
- **VSync**: Smooth frame pacing at 60 FPS
- **Hardware acceleration**: Use GPU for blitting
- **Wall culling**: Don't update walls far off-screen
- **Sprite caching**: Load sprites once at startup

### Target Performance
- **60 FPS** on modern hardware
- **Sub-16ms** frame time (1000ms / 60 frames)
- **Minimal GC pauses** (object pooling for particles)

## Accessibility

### Visual
- High contrast floor (red) vs walls (gray/blue)
- Large, readable fonts
- Clear state indicators (wall highlights)

### Input
- Single button gameplay
- Generous coyote time (6 frames = 100ms)
- Jump buffering (5 frames = 83ms)
- Forgiving wall collision (slightly extended hitboxes)

### Difficulty
- Three difficulty levels
- Persistent high scores per player
- Instant restart on death
- Optional debug mode showing physics info

## Credits & Inspiration

- **Celeste** - Wall slide and coyote time mechanics
- **Temple Run** - Auto-scroll pressure and momentum
- **Geometry Dash** - One-button simplicity and instant retry flow
- **Super Meat Boy** - Tight controls and readable death zones

---

**Version**: 1.0  
**Last Updated**: November 2025  
**Game Type**: Wall-jumping auto-scroller  
**Platform**: PC (Pygame)
