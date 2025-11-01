# Spritesheet System

## Overview

Geo Dash uses an optimized spritesheet system to load game assets efficiently. Instead of converting SVG files to PNG at runtime (which is slow), all sprites are pre-converted into spritesheets for instant loading.

## Performance Benefits

### Before Spritesheets (SVG Runtime Conversion)
- **First load**: 5-15ms per sprite (SVG → PNG conversion with cairosvg)
- **Cached load**: <1ms (from memory cache)
- **Dependency**: Requires `cairosvg` at runtime
- **Startup time**: Slow (many conversions)

### After Spritesheets (PNG from Sheet)
- **First load**: 0.5-2ms per sprite (extract from sheet + scale)
- **Cached load**: <0.01ms (from memory cache)
- **Dependency**: Only `Pillow` (for generation, not runtime)
- **Startup time**: Fast (1-2 large image loads)

**Result**: ~10-30x faster sprite loading! 🚀

## How It Works

### 1. Spritesheet Generation

Run the generator script to create spritesheets from your SVG files:

```bash
.venv/bin/python generate_spritesheet.py
```

This creates:
- `assets/spritesheets/obstacles.png` - All obstacle sprites in one image (1920x1920px)
- `assets/spritesheets/obstacles.json` - Metadata with sprite positions
- `assets/spritesheets/player_characters.png` - All player characters (480x40px strip)
- `assets/spritesheets/player_characters.json` - Character metadata

### 2. Spritesheet Structure

#### Obstacles Spritesheet
- **Layout**: 8x8 grid of cells (240x240px each)
- **Sprites**: 64 obstacle sprites (various sizes 1x1 to 8x8 grid units)
- **Naming**: Sprite name = `{grid_width}-{grid_height}` (e.g., "3-2" for 90x60px)
- **Centered**: Each sprite is centered in its cell for easy extraction

#### Player Characters Spritesheet
- **Layout**: Horizontal strip (12 sprites × 40px)
- **Sprites**: All player characters at 40x40px
- **Naming**: Original filename without `.svg` (e.g., "bloemetje")

### 3. Runtime Loading

The `AssetManager` automatically uses spritesheets if available:

```python
# In game code - no changes needed!
sprite = asset_manager.get_obstacle_sprite(90, 60)  # Gets "3-2" from sheet
player = asset_manager.get_player_sprite("bloemetje.svg")  # Gets from sheet
```

**Fallback**: If spritesheets don't exist, falls back to individual SVG loading.

## Metadata Format

### obstacles.json
```json
{
  "type": "obstacles",
  "cell_width": 240,
  "cell_height": 240,
  "cols": 8,
  "rows": 8,
  "sprites": {
    "3-2": {
      "x": 0,
      "y": 240,
      "width": 90,
      "height": 60,
      "grid_w": 3,
      "grid_h": 2,
      "cell_offset_x": 75,
      "cell_offset_y": 90
    }
  }
}
```

### player_characters.json
```json
{
  "type": "player_characters",
  "sprite_size": 40,
  "cols": 12,
  "rows": 1,
  "sprites": {
    "bloemetje": {
      "x": 0,
      "y": 0,
      "width": 40,
      "height": 40,
      "index": 0
    }
  }
}
```

## Adding New Sprites

### Adding Obstacle Sprites
1. Add SVG file to `assets/obstacles/extracted-obstacles/`
2. Name it `{grid_width}-{grid_height}.svg` (e.g., `5-3.svg`)
3. Run `generate_spritesheet.py` to regenerate

### Adding Player Characters
1. Add SVG file to `assets/player-characters/`
2. Name it descriptively (e.g., `new-character.svg`)
3. Run `generate_spritesheet.py` to regenerate

### Removing cairosvg Dependency

After generating spritesheets, you can remove `cairosvg` from runtime:

```bash
# Optional: Remove from requirements.txt (keep Pillow for other image loading)
# The game will still work - it uses spritesheets instead of SVG conversion
```

**Note**: Keep `cairosvg` installed if you want to regenerate spritesheets later.

## Caching Strategy

The `AssetManager` uses a multi-level cache:

1. **Spritesheet cache**: Loaded once at startup (2 images total)
2. **Extracted sprite cache**: Sprites extracted from sheet are cached by name + size
3. **Memory efficiency**: Only extracts sprites that are actually used

## Troubleshooting

### Spritesheets not loading
```
ℹ️  No spritesheets found, will use individual sprite loading
```
**Solution**: Run `generate_spritesheet.py` to create spritesheets.

### Sprite not found in sheet
The game falls back to SVG loading:
```
✓ Loaded obstacle sprite: 3-2.svg (scaled to 90x60px)
```
**Expected**: This is normal if you added new sprites but haven't regenerated sheets.

### Performance still slow
Check if spritesheets are actually being used:
```bash
.venv/bin/python main.py 2>&1 | grep "spritesheet"
```

Should see:
```
✅ Loaded obstacle spritesheet (64 sprites)
✅ Loaded player character spritesheet (12 sprites)
```

## Technical Details

### Why 240x240px cells?
- Maximum obstacle size: 8×8 grid units = 240×240px
- Uniform cell size simplifies extraction math
- Wasted space is minimal (sprites are centered in cells)

### Why horizontal strip for players?
- All player sprites are same size (40x40px)
- No wasted space needed
- Simpler extraction (just X offset)
- Smaller file size

### PNG Optimization
- `optimize=True` flag reduces file size by ~10-20%
- RGBA format preserves transparency
- No quality loss (lossless compression)

## File Sizes

Typical spritesheet sizes:
- **obstacles.png**: ~200-400KB (64 sprites at various sizes)
- **player_characters.png**: ~10-20KB (12 sprites at 40x40px)
- **Metadata JSON files**: ~5-15KB each

**Total**: ~250-450KB for all sprites vs hundreds of individual files!

## See Also

- [ASSETS_README.md](ASSETS_README.md) - General asset loading guide
- [OBSTACLE_PATTERNS_README.md](OBSTACLE_PATTERNS_README.md) - Obstacle pattern system
- `generate_spritesheet.py` - Spritesheet generator source code
