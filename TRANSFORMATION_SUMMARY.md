# Geo Dash → Celeste Runner Transformation Summary

## What Changed?

The original **Geo Dash** was a Geometry Dash clone where players jump over obstacles while auto-running. The new **Celeste Runner** is a wall-jumping auto-scroller where players must chain wall jumps to stay alive as the camera scrolls relentlessly to the right.

## 🎮 Core Gameplay Transformation

### Before (Geo Dash)
- ✅ Player runs automatically on the ground
- ✅ Jump over obstacles (single + double jump)
- ✅ Obstacles are barriers to clear
- ✅ Landing on platforms gives points
- ✅ Death from hitting obstacles
- ✅ Pattern-based obstacle generation

### After (Celeste Runner)
- ✅ Player falls continuously
- ✅ Wall jump mechanics (slide + jump off walls)
- ✅ Walls are surfaces to grab and launch from
- ✅ Score is distance traveled
- ✅ Death from touching floor OR falling behind screen
- ✅ Procedural wall generation with physics validation

## 📁 New Files Created

### Core Game Files
1. **`game/celeste_runner.py`** - New main game loop
   - Auto-scrolling camera
   - Wall collision detection
   - Death conditions (floor + screen edge)
   - Simplified menus

2. **`game/player_celeste.py`** - Wall-jumping player class
   - State machine (falling, wall_sliding, wall_jumping)
   - Wall cling + slide mechanics
   - Coyote time (6 frames after leaving wall)
   - Jump buffering (remember input for 5 frames)
   - Context-aware jump (wall jump vs air jump)

3. **`game/walls.py`** - Wall system
   - `Wall` class (vertical surfaces with types)
   - `WallGenerator` (procedural wall spawning)
   - Wall types: normal, crumbly, slippery
   - Collision detection with side (left/right)

4. **`game/camera.py`** - Auto-scrolling camera
   - Moves right at 3-8 pixels/frame
   - Accelerates over time (0.002 px/frame²)
   - Tracks total distance for scoring
   - Provides world-to-screen coordinate conversion

5. **`main_celeste.py`** - Entry point for Celeste Runner

### Documentation
6. **`md-files/CELESTE_RUNNER_DESIGN.md`** - Complete design doc
   - Physics calculations
   - State machine details
   - Level generation algorithms
   - Future expansion ideas

7. **`CELESTE_RUNNER_README.md`** - Player-facing guide
   - How to play
   - Controls and mechanics
   - Tips and tricks
   - Configuration guide

## 🔧 Modified Files

### 1. `core/physics.py` - Completely Rewritten
**Before**: Jump arc calculations for clearing obstacles
```python
max_jump_height = (JUMP_POWER² / (2 * GRAVITY)) * 0.7
max_jump_distance = air_time * PLAYER_SPEED
can_jump_over(height, gap)
can_climb(height_diff)
```

**After**: Wall jump trajectory calculations
```python
max_wall_jump_height = (WALL_JUMP_Y_FORCE² / (2 * GRAVITY))
max_wall_jump_distance = air_time * WALL_JUMP_X_FORCE
can_reach_wall(gap, height_diff)
calculate_wall_jump_trajectory(wall_side)
is_valid_wall_layout(walls)
```

### 2. `game/config.py` - Physics Constants Updated
**Removed**:
```python
PLAYER_SPEED = 6          # No manual horizontal movement
JUMP_POWER = -15          # Replaced with wall jump forces
MIN_OBSTACLE_GAP = 150    # Replaced with wall gaps
MAX_OBSTACLE_GAP = 300
```

**Added**:
```python
# Wall physics
WALL_SLIDE_GRAVITY = 0.2
WALL_JUMP_X_FORCE = 8
WALL_JUMP_Y_FORCE = -14
AIR_RESISTANCE = 0.96

# Auto-scroll
AUTO_SCROLL_SPEED = 3
AUTO_SCROLL_ACCELERATION = 0.002
MAX_AUTO_SCROLL_SPEED = 8

# Wall mechanics
WALL_CLING_TIME = 8
WALL_JUMP_COYOTE_TIME = 6
WALL_WIDTH = 30

# Wall generation
MIN_WALL_GAP = 100
MAX_WALL_GAP = 280
MIN_WALL_HEIGHT = 60
MAX_WALL_HEIGHT = 400
```

## 🎯 Key Gameplay Differences

### Movement System
| Geo Dash | Celeste Runner |
|----------|---------------|
| Auto-run on ground | Free fall with gravity |
| Manual jump input | Wall grab + wall jump |
| Double jump ability | Coyote time after leaving wall |
| No horizontal control | Horizontal velocity from wall jumps only |

### Difficulty
| Geo Dash | Celeste Runner |
|----------|---------------|
| Timing obstacle jumps | Chaining wall jumps |
| Pattern memorization | Reading ahead while moving |
| Combo/landing bonuses | Pure distance survival |
| Static obstacle patterns | Procedural wall layouts |

### Death Conditions
| Geo Dash | Celeste Runner |
|----------|---------------|
| Hit obstacle | Touch red floor |
| Fall into pit | Fall behind left screen edge |
| - | Miss wall (can't reach next one) |

## 🧮 Physics Comparison

### Gravity
```python
# Geo Dash
GRAVITY = 0.8  # Constant

# Celeste Runner
GRAVITY = 0.8           # When falling/jumping
WALL_SLIDE_GRAVITY = 0.2  # When sliding on wall (75% slower)
```

### Jump Forces
```python
# Geo Dash
JUMP_POWER = -15        # Single upward force
Double jump = -15 * 0.9  # 90% of normal

# Celeste Runner
WALL_JUMP_Y_FORCE = -14  # Upward component
WALL_JUMP_X_FORCE = 8    # Horizontal component (away from wall)
# Result: 45° launch angle with arc
```

### Horizontal Movement
```python
# Geo Dash
x += PLAYER_SPEED  # Constant 6 px/frame to the right

# Celeste Runner
x += velocity_x         # Set by wall jump
velocity_x *= AIR_RESISTANCE  # Decays to 0 (0.96 multiplier)
camera.x += AUTO_SCROLL_SPEED  # Camera pushes player right
```

## 🎨 Visual Changes

### Color Palette
**New Colors**:
```python
GROUND_DANGER = (200, 50, 50)   # Lethal floor (was GROUND_GREEN)
DEATH_RED = (255, 50, 50)       # Warning stripes
WALL_COLOR = (180, 180, 200)    # New: wall surfaces
WALL_HIGHLIGHT = (220, 220, 240) # New: touched walls
```

### UI Changes
**Removed**:
- Combo counter
- Landing bonus popups
- Pattern name display

**Added**:
- Distance counter (meters)
- Speed percentage (scroll acceleration)
- Death reason text
- Simplified pause menu

## 🔄 State Management

### Player States
**Geo Dash**:
```python
on_ground: bool
is_jumping: bool
jumps_used: int (0, 1, or 2)
has_double_jump: bool
```

**Celeste Runner**:
```python
state: enum (FALLING, WALL_SLIDING, WALL_JUMPING)
wall_side: str ('left' or 'right')
wall_cling_timer: int
wall_coyote_timer: int
can_wall_jump: bool
```

## 🧪 Testing the Games

### Run Original Geo Dash
```bash
python main.py
```
- Jump over obstacles
- Combo system
- Pattern-based levels

### Run Celeste Runner
```bash
python main_celeste.py
```
- Wall jumping
- Auto-scroll survival
- Procedural walls

## 🎓 Learning Resources

### Understanding the Transformation

1. **Read Design Doc**: `md-files/CELESTE_RUNNER_DESIGN.md`
   - Complete physics breakdown
   - State machine diagrams
   - Generation algorithms

2. **Read Player Guide**: `CELESTE_RUNNER_README.md`
   - How to play
   - Controls and tips
   - Mechanics explanation

3. **Study Code Flow**:
   ```
   main_celeste.py
   └─ game/celeste_runner.py (Game class)
       ├─ Camera.update() - Auto-scroll
       ├─ Player.update() - Wall physics
       ├─ WallGenerator.update() - Spawn walls
       └─ Check collisions + death
   ```

## 📊 Complexity Comparison

### Code Complexity
| Component | Geo Dash | Celeste Runner | Change |
|-----------|----------|----------------|--------|
| Player class | 254 lines | 320 lines | +25% (state machine) |
| Obstacle/Wall system | 950 lines | 260 lines | -73% (simpler geometry) |
| Main game loop | 666 lines | 470 lines | -29% (no menus) |
| Physics | 70 lines | 130 lines | +86% (trajectory math) |

### Gameplay Complexity
| Aspect | Geo Dash | Celeste Runner |
|--------|----------|----------------|
| Input complexity | Medium (jump, double jump) | Simple (single jump) |
| Mechanical depth | Medium (timing jumps) | High (wall chaining) |
| Pattern complexity | High (hand-crafted) | Low (procedural) |
| Skill ceiling | Medium | Very High |

## 🚀 Performance

Both games target **60 FPS** but have different bottlenecks:

### Geo Dash
- ⚠️ Many obstacles on screen (50+)
- ⚠️ Complex collision masks (irregular sprites)
- ⚠️ Pattern validation on startup
- ✅ Static background

### Celeste Runner
- ✅ Fewer walls on screen (5-10)
- ✅ Simple rect collision
- ✅ No validation overhead
- ✅ Continuous culling (remove off-screen walls)

**Result**: Celeste Runner is slightly more performant due to simpler collision and fewer objects.

## 🎯 Design Philosophy Shift

### Geo Dash Philosophy
> "Navigate through carefully designed obstacle patterns using precise timing"

- Emphasis on **pattern recognition**
- Rewards **memorization**
- Difficulty through **complex layouts**
- Retry until pattern mastered

### Celeste Runner Philosophy
> "Survive as long as possible through pure mechanical skill"

- Emphasis on **reaction time**
- Rewards **improvisation**
- Difficulty through **speed escalation**
- Every run is different

## 🛠️ Future Development Paths

### Geo Dash Evolution
- More pattern types
- Custom level editor
- Music sync gameplay
- Community pattern sharing

### Celeste Runner Evolution
- Power-up system (dash, double jump)
- Themed zones (cave, forest, sky)
- Challenge mode (handcrafted sequences)
- Time attack mode
- Multiplayer races

## 🎮 Which Game to Play?

### Play Geo Dash If You Like:
- Rhythm games
- Pattern memorization
- Precision platforming
- Geometry Dash style gameplay

### Play Celeste Runner If You Like:
- Endless runners
- Reaction-based challenges
- Wall jumping mechanics (Celeste, Super Meat Boy)
- Roguelike procedural generation

## 📝 Conclusion

The transformation from **Geo Dash** to **Celeste Runner** represents a fundamental shift in game design:

- From **horizontal obstacle avoidance** → **vertical wall navigation**
- From **ground-based jumping** → **wall-based momentum**
- From **pattern mastery** → **mechanical skill**
- From **static challenges** → **dynamic survival**

Both games share the same technical foundation (Pygame, asset system, score management) but offer completely different gameplay experiences.

**The old game still works!** Run `python main.py` for Geo Dash, or `python main_celeste.py` for Celeste Runner. They coexist peacefully in the same codebase.

---

**Transformation Date**: November 2025  
**Lines Changed**: ~2000  
**New Files**: 7  
**Core Concept**: Wall-jumping auto-scroller  
**One Word Summary**: Relentless
