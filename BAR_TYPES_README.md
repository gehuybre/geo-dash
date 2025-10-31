# Bar Types System

## Overview

The bar types system provides reusable obstacle templates that patterns can reference. This makes patterns easier to maintain, ensures visual consistency, and simplifies adding custom artwork in the future.

## Base Unit

All bar types are defined as multipliers of a **base unit**:
- **Width**: 30px (fixed)
- **Height**: ~32px (dynamically calculated as 1/3 of max jumpable height from physics)

## Bar Type Naming Convention

Bar types use the format: `bar-{width}-{height}`

- `{width}`: Width multiplier (e.g., `1`, `2`, `3.33`, `8`)
- `{height}`: Height multiplier (e.g., `0.5`, `1`, `1.5`, `2`, `3`)

### Examples:
- `bar-1-1`: Standard 1x1 bar (30px wide × 32px tall)
- `bar-2-1.5`: Wide medium bar (60px wide × 48px tall)
- `bar-8-1`: Large platform (240px wide × 32px tall)

## Available Bar Types

### Standard Bars (1x width)
- `bar-1-0.5`: Tiny (half height)
- `bar-1-0.75`: Spike-like
- `bar-1-1`: Standard base unit
- `bar-1-1.5`: Medium height
- `bar-1-2`: Tall (double height)
- `bar-1-2.5`: Very tall
- `bar-1-3`: Maximum jumpable height

### Wide Bars (2x width)
- `bar-2-1`: Wide short
- `bar-2-1.5`: Wide medium
- `bar-2-2`: Wide tall

### Extra Wide (3x+ width)
- `bar-3-1`: Extra wide short
- `bar-3-1.5`: Extra wide medium
- `bar-3.33-0.66`: Tower base (~100px × 20px)
- `bar-3.33-1`: Tower middle (~100px × 32px)

### Platforms (4x+ width)
- `bar-4-1`: Small platform (120px)
- `bar-4-1.5`: Tower top / Platform (120px)
- `bar-5-1`: Medium platform (150px)
- `bar-8-1`: Large platform (240px)

## Gap Types

Gap types define standard distances between obstacles:

- `gap-stack`: 0px - Obstacles touch/stack
- `gap-tiny`: 60px - Minimal gap, precise timing required
- `gap-small`: 100px - Easy jump
- `gap-medium`: 150px - Standard jump
- `gap-large`: 200px - Comfortable jump
- `gap-very-large`: 250px - Requires good timing
- `gap-extreme`: 300px - Near maximum jump distance

## Using in Patterns

### New Format (Recommended)

```json
{
  "name": "Your Pattern",
  "obstacles": [
    {
      "bar_type": "bar-1-2",
      "gap_type": "gap-medium"
    },
    {
      "bar_type": "bar-2-1.5",
      "gap_type": "gap-large"
    }
  ]
}
```

### Legacy Format (Still Supported)

```json
{
  "name": "Your Pattern",
  "obstacles": [
    {
      "height": 60,
      "width": 30,
      "gap_after": 180
    }
  ]
}
```

### Mixed Format

You can override bar_type dimensions if needed:

```json
{
  "bar_type": "bar-2-1",
  "height": 50,
  "gap_type": "gap-medium"
}
```

## Benefits

1. **Consistency**: All patterns use the same set of obstacle sizes
2. **Maintainability**: Change a bar type definition, update all patterns using it
3. **Future-Ready**: Easy to add custom artwork per bar type
4. **Physics-Based**: All dimensions automatically scale with game physics
5. **Readable**: `bar-2-1.5` is clearer than raw `width: 60, height: 48`

## Adding Custom Artwork (Future)

When ready to add artwork, you can map sprites to bar types:

```
assets/bars/
  bar-1-1.png
  bar-1-2.png
  bar-2-1.png
  ...
```

The obstacle renderer will automatically use the correct sprite based on the bar type.
