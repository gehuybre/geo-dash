# Dynamic Bar Types & Floating Platforms

## Overview

The bar type system now supports **dynamic bar types** without needing to predefine every combination in `bar_types.json`. You can use any width/height combination on the fly!

## Dynamic Bar Types

### Format: `bar-{width}-{height}`

Use any decimal multipliers directly in patterns:

```json
{
  "bar_type": "bar-2.5-3.2",
  "gap_type": "gap-1.8"
}
```

This creates:
- Width: `30px * 2.5 = 75px`
- Height: `80px * 3.2 = 256px`  
- Gap: `100px * 1.8 = 180px`

### Examples

```json
{
  "name": "Custom Pattern",
  "obstacles": [
    {"bar_type": "bar-1.5-2", "gap_type": "gap-1.5"},
    {"bar_type": "bar-3.7-4.2", "gap_type": "gap-2.3"},
    {"bar_type": "bar-0.8-1.2", "gap_type": "gap-0.5"}
  ]
}
```

**No need to define these in bar_types.json!** They work automatically.

## Floating Platforms

### Format: `bar-{width}-{floor}-{ceiling}`

Create platforms floating in mid-air!

- `{width}`: Platform width multiplier
- `{floor}`: Distance from ground multiplier (0 = on ground)
- `{ceiling}`: Platform height multiplier

```json
{"bar_type": "bar-4-2-1", "gap_type": "gap-2"}
```

This creates:
- Width: `30px * 4 = 120px`
- Floor offset: `80px * 2 = 160px` (platform floats 160px above ground)
- Height: `80px * 1 = 80px` (platform is 80px tall)

### Floating Platform Examples

```json
{
  "name": "Sky Bridge",
  "description": "Platforms floating in the air",
  "obstacles": [
    {"bar_type": "bar-5-3-1", "gap_type": "gap-2"},
    {"bar_type": "bar-4-3-1", "gap_type": "gap-2"},
    {"bar_type": "bar-5-3-1", "gap_type": "gap-2.5"}
  ]
}
```

```json
{
  "name": "Ceiling Spikes",
  "description": "Obstacles hanging from above",
  "obstacles": [
    {"bar_type": "bar-2-5-2", "gap_type": "gap-1.5"},
    {"bar_type": "bar-2-6-1", "gap_type": "gap-1.5"}
  ]
}
```

## Dynamic Gap Types

### Format: `gap-{multiplier}`

Use any multiplier:

```json
{"gap_type": "gap-1.75"}  // 175px gap
{"gap_type": "gap-0.25"}  // 25px gap  
{"gap_type": "gap-4.5"}   // 450px gap
```

## Benefits

### Before (Static)
Had to predefine every combination in `bar_types.json`:
```json
"bar-1-1": {"width_multiplier": 1, "height_multiplier": 1},
"bar-1-2": {"width_multiplier": 1, "height_multiplier": 2},
"bar-1-3": {"width_multiplier": 1, "height_multiplier": 3},
// ... 64 more entries
```

### After (Dynamic)
Just use what you need:
```json
{"bar_type": "bar-1-1", "gap_type": "gap-1"},
{"bar_type": "bar-2.3-4.7", "gap_type": "gap-1.8"}
```

## Pattern Generator Usage

```python
# Generate floating platform variations
def generate_sky_bridges():
    for floor_height in range(2, 6):
        obstacles = [
            {"bar_type": f"bar-4-{floor_height}-1", "gap_type": "gap-2"}
            for _ in range(5)
        ]
        obstacles[-1]["gap_type"] = "gap-2.5"
        
        pattern = create_pattern(
            f"Sky Bridge {floor_height}",
            f"Platforms floating at height {floor_height}",
            obstacles
        )
        save_pattern(pattern, f"sky_bridge_{floor_height}")
```

## Still Using bar_types.json?

Yes! Predefined types are still useful for:
1. **Named presets** - `"bar_type": "platform"` is clearer than `"bar-4-1"`
2. **Consistency** - Ensure common sizes are standardized
3. **Documentation** - Descriptions help understand intent

But now you can **mix and match**:
```json
{
  "obstacles": [
    {"bar_type": "bar-3-1", "gap_type": "gap-2"},
    {"bar_type": "bar-2.7-3.8", "gap_type": "gap-1.3"},
    {"bar_type": "bar-5-2-1", "gap_type": "gap-2"}
  ]
}
```

## Summary

✅ **Dynamic bar types**: `bar-{width}-{height}`  
✅ **Floating platforms**: `bar-{width}-{floor}-{ceiling}`  
✅ **Dynamic gaps**: `gap-{multiplier}`  
✅ **No pre-definition needed**  
✅ **Still supports predefined types from JSON**

**You can now create any obstacle configuration without editing `bar_types.json`!**
