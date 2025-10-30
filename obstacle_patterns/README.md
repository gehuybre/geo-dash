# Obstacle Patterns

This folder contains JSON files defining patterns and series of obstacles that can be used in the game.

**All patterns are automatically validated for physical possibility!** The game checks:
- Heights are jumpable
- Gaps are within jump distance
- Landing zones have safe recovery time
- Stacked blocks (gap=0) form climbable towers

## Pattern Format

Each pattern is defined in a JSON file with the following structure:

```json
{
  "name": "Pattern Name",
  "description": "Description of the pattern",
  "obstacles": [
    {
      "height": 50,
      "width": 30,
      "gap_after": 200
    },
    {
      "height": 70,
      "width": 35,
      "gap_after": 250
    }
  ]
}
```

## Fields

- **name**: A descriptive name for the pattern
- **description**: Explanation of what the pattern does
- **obstacles**: Array of obstacle definitions
  - **height**: Height of the obstacle in pixels (max ~85 pixels based on physics)
  - **width**: Width of the obstacle in pixels (30-100 recommended, wider = easier landing)
  - **gap_after**: Distance in pixels to the next obstacle
    - **0** = Stacked on top (creates climbable towers!)
    - **60+** = Minimum safe gap for landing and jumping again
    - **Max ~360** = Maximum jumpable distance

## Physics Constraints

The validation system ensures all patterns are completable:

1. **Max Jump Height**: ~85 pixels (calculated from jump power and gravity)
2. **Max Jump Distance**: ~360 pixels (based on air time and speed)
3. **Min Safe Gap**: 60 pixels (time needed to land and jump again)
4. **Stacked Blocks**: Use `gap_after: 0` to stack blocks vertically

## Pattern Types

### Platform Patterns
Wide blocks (60-100px) for easier landing:
```json
{"height": 50, "width": 80, "gap_after": 180}
```

### Staircase Patterns
Increasing heights with safe gaps:
```json
[
  {"height": 40, "width": 60, "gap_after": 120},
  {"height": 60, "width": 60, "gap_after": 120}
]
```

### Tower Patterns
Stacked blocks for climbing:
```json
[
  {"height": 30, "width": 80, "gap_after": 0},
  {"height": 60, "width": 80, "gap_after": 0},
  {"height": 90, "width": 80, "gap_after": 250}
]
```

## Examples

See the included example patterns:
- `climbing_stairs.json` - Wide platforms forming climbable stairs
- `platform_bridge.json` - Same-height platforms for timing practice
- `stack_tower.json` - Vertically stacked blocks
- `wide_steps.json` - Very wide platforms for safe landing
- `basic_stairs.json` - Simple staircase pattern
- `double_jump.json` - Two obstacles requiring consecutive jumps
- `spike_valley.json` - Tall-short-tall pattern
- `speed_test.json` - Rapid succession of obstacles

## Creating Custom Patterns

1. Copy an existing pattern JSON file
2. Modify the obstacles array
3. Save with a new name in this folder
4. Run the game - it will validate automatically!
5. Check console output for validation results

**Invalid patterns will be rejected with helpful error messages!**

## Usage

The game automatically:
- Loads all valid pattern files from this folder (70% chance per spawn)
- Validates each pattern for physical possibility
- Reports loading status and validation results in console
- Uses patterns alongside random generation for variety
