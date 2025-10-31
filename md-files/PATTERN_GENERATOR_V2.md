# Pattern Generator V2 - Gameplay Design System

## Overview

The enhanced pattern generator (`pattern_generator_v2.py`) creates Geometry Dash patterns following professional gameplay design principles.

## Design Principles

### 🎯 Core Rules

1. **Pattern Length**: 20-40 blocks per pattern
2. **Resting Spaces**: 3-unit gaps between patterns for player recovery
3. **No Consecutive Heights**: Heights must ascend or descend, never repeat
4. **Extra-Wide Valleys**: Valley sections must be extra wide (8+ blocks)
5. **Killzones**: Floor hazards under platform sections to encourage platform use
6. **Modular Design**: Each pattern has distinct identity and rhythm

### 🎮 Gameplay Flow

- **Rhythm-Based**: Patterns align with musical timing
- **Progressive Challenge**: Early patterns easier, later ones harder
- **Learnable Repetition**: Players should recognize patterns
- **Risk-Reward**: Optional harder paths for skilled players
- **Smooth Transitions**: No abrupt gaps unless intentional

## Pattern Types

### 📊 Bar Patterns (Ground-Based)

1. **Rising Stairs Flow** (16 blocks)
   - Gradual ascending staircase
   - Rhythmic rest section
   - Tempo: Steady climb

2. **Valley Runner** (24 blocks)
   - Descend → Wide valley → Ascend
   - Extra wide valley (8 blocks) for momentum
   - Tempo: Medium

3. **Zigzag Rhythm Run** (24 blocks)
   - Alternating height pattern
   - Continuous flow
   - Tempo: Fast

### 🌟 Platform Patterns (Floating)

4. **Sky Climber** (28 blocks)
   - Rising platform section
   - **Floor killzones** beneath platforms
   - Tempo: Flowing jumps

5. **Wave Rider** (31 blocks)
   - Undulating platform heights
   - Wave between heights 2-3
   - Tempo: Medium flow

### 🎯 Mixed Patterns

6. **Challenge Medley** (31 blocks)
   - Bars → Platforms → Bars
   - Tests versatility
   - Tempo: Variable

7. **Progressive Climb** (32 blocks)
   - Easy → Medium → Hard → Rest
   - Gradual difficulty increase
   - Tempo: Building intensity

## Killzone System

### What Are Killzones?

Floor hazards (height 0) that appear under platform sections to encourage players to stay on platforms.

### Visual Design

- **Red/orange animated stripes**
- **Diagonal warning pattern**
- **Scrolling animation** for visibility
- **10px thin strip** on ground

### Implementation

```json
{
  "bar_type": "bar-2-0",
  "gap_type": "gap-0",
  "is_killzone": true
}
```

### Rendering

Killzones are rendered as animated warning patterns in `obstacles.py`:
- Base: Red (#FF3232)
- Stripes: Orange (#FF9600)
- Border: Dark red (#C80000)

## Height Sequencing

### Ascending Heights

```python
heights = ascending_heights(start=1, end=3, count=8)
# Result: [1, 1, 2, 2, 2, 3, 3, 3]
```

### Descending Heights

```python
heights = descending_heights(start=3, end=1, count=6)
# Result: [3, 3, 2, 2, 1, 1]
```

### Wave Pattern

```python
heights = wave_heights(min_h=2, max_h=3, count=10)
# Result: [2, 2, 3, 3, 3, 3, 3, 2, 2, 2]
```

### Zigzag Pattern

```python
heights = zigzag_heights(min_h=1, max_h=3, count=8)
# Result: [1, 2, 3, 2, 1, 2, 3, 2]
```

## Gap Sizing Guide

- `gap-0`: Stacked/touching obstacles
- `gap-1`: 100px (tight jumps)
- `gap-1.5`: 150px (standard jumps)
- `gap-2`: 200px (comfortable jumps)
- `gap-2.25`: 225px (max safe distance)
- `gap-3`: 300px (resting space)

**Warning**: Never exceed `gap-2.25` (225px) - this is the max jump distance!

## Usage

### Generate All Patterns

```bash
python pattern_generator_v2.py
```

### Output

```
✓ Created: rising_stairs_flow (16 blocks, bar)
✓ Created: valley_runner (24 blocks, bar)
✓ Created: zigzag_rhythm_run (24 blocks, bar)
✓ Created: sky_climber (28 blocks, platform)
✓ Created: wave_rider (31 blocks, platform)
✓ Created: challenge_medley (31 blocks, mixed)
✓ Created: progressive_climb (32 blocks, mixed)
```

## Pattern Metadata

Each pattern includes metadata for level design:

```json
{
  "name": "Sky Climber",
  "description": "Rising platform section with floor killzones",
  "obstacles": [...],
  "metadata": {
    "type": "platform",
    "length": 28,
    "rhythm": "Flowing jumps - stay high or die"
  }
}
```

## Creating Custom Patterns

### Example: Custom Bar Pattern

```python
def generate_my_pattern():
    obstacles = []
    
    # Ground run (5 blocks, ascending)
    for h in range(1, 4):
        obstacles.append(create_bar_obstacle(h, width=3, gap="gap-1.5"))
    
    # Rest section (3 blocks)
    for _ in range(3):
        obstacles.append(create_bar_obstacle(1, width=4, gap="gap-2"))
    
    add_resting_gap(obstacles, "gap-3")
    
    return create_pattern(
        "My Pattern",
        "Custom pattern description",
        obstacles,
        "bar",
        "Medium tempo"
    )
```

### Example: Platform Pattern with Killzones

```python
def generate_platform_challenge():
    obstacles = []
    
    # Climb up (3 blocks)
    for h in range(1, 4):
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    # Add killzones
    for _ in range(2):
        obstacles.append(create_killzone(width=2, gap="gap-0"))
    
    # Platforms (10 blocks at height 3)
    for _ in range(10):
        obstacles.append(create_platform_obstacle(3, width=5, gap="gap-1.5"))
    
    # Descend
    for h in range(3, 0, -1):
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    add_resting_gap(obstacles, "gap-3")
    
    return create_pattern(
        "Platform Challenge",
        "High platforms with killzone floor",
        obstacles,
        "platform",
        "Fast tempo - don't fall!"
    )
```

## Best Practices

### ✅ Do

- Keep patterns between 20-40 blocks
- Always add resting gaps (`gap-3`)
- Use ascending/descending height sequences
- Add killzones under platform sections
- Test patterns in-game before committing
- Give patterns descriptive names and rhythm hints

### ❌ Don't

- Create consecutive same-height obstacles
- Use gaps > 225px (max jump distance)
- Create narrow valleys (minimum 8 blocks wide)
- Mix bar types randomly without pattern
- Forget resting spaces between patterns
- Create patterns > 40 blocks (too overwhelming)

## Testing Patterns

1. Run generator: `python pattern_generator_v2.py`
2. Launch game: `python geo_dash.py`
3. Verify patterns load successfully
4. Check console for validation errors
5. Play-test for rhythm and feel
6. Adjust based on gameplay feedback

## Future Enhancements

Potential additions:
- **Moving platforms** with velocity
- **Rotating obstacles** for variety
- **Collectible coins** for risk-reward
- **Power-ups** (shields, speed boosts)
- **Enemy patterns** (moving hazards)
- **Boss patterns** (complex sequences)

## Files Modified

- `pattern_generator_v2.py` - New generator with design principles
- `obstacles.py` - Added killzone rendering and is_killzone flag
- `obstacle_patterns/*.json` - 7 new pattern files

## Pattern Statistics

| Pattern Name | Type | Length | Killzones | Difficulty |
|--------------|------|--------|-----------|------------|
| Rising Stairs Flow | Bar | 16 | No | Easy |
| Valley Runner | Bar | 24 | No | Medium |
| Zigzag Rhythm Run | Bar | 24 | No | Medium |
| Sky Climber | Platform | 28 | Yes | Hard |
| Wave Rider | Platform | 31 | Yes | Hard |
| Challenge Medley | Mixed | 31 | Yes | Hard |
| Progressive Climb | Mixed | 32 | Yes | Progressive |

---

**Created**: October 31, 2025  
**Version**: 2.0  
**Status**: Production Ready ✅
