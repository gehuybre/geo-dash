#!/usr/bin/env python3
"""
Spritesheet generator for Geo Dash.
Converts all SVG assets to optimized PNG spritesheets with metadata.
"""

import os
import json
import math
import io
from pathlib import Path

try:
    import cairosvg
    from PIL import Image
    HAS_REQUIREMENTS = True
except ImportError as e:
    print(f"Error: Missing required libraries: {e}")
    print("Install with: pip install cairosvg Pillow")
    HAS_REQUIREMENTS = False
    exit(1)


class SpriteSheetGenerator:
    """Generates optimized spritesheets from SVG files."""
    
    def __init__(self, output_dir="assets/spritesheets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_obstacle_spritesheet(self):
        """
        Generate spritesheet for obstacles.
        Each obstacle sprite is 30x30px per grid unit (max 8x8 grid = 240x240px per sprite).
        """
        print("\n🎨 Generating obstacle spritesheet...")
        
        obstacles_dir = Path("assets/obstacles/extracted-obstacles")
        if not obstacles_dir.exists():
            print(f"❌ Obstacles directory not found: {obstacles_dir}")
            return
        
        svg_files = sorted(obstacles_dir.glob("*.svg"))
        if not svg_files:
            print(f"❌ No SVG files found in {obstacles_dir}")
            return
        
        print(f"📦 Found {len(svg_files)} obstacle sprites")
        
        # Convert SVG to PNG in memory and calculate dimensions
        sprites = []
        max_width = 0
        max_height = 0
        
        for svg_file in svg_files:
            # Parse grid dimensions from filename (e.g., "3-2.svg" = 3x2 grid)
            name = svg_file.stem
            try:
                grid_w, grid_h = map(int, name.split('-'))
                pixel_width = grid_w * 30
                pixel_height = grid_h * 30
            except ValueError:
                print(f"⚠️  Skipping invalid filename: {svg_file.name}")
                continue
            
            # Convert SVG to PNG in memory
            png_data = cairosvg.svg2png(
                url=str(svg_file),
                output_width=pixel_width,
                output_height=pixel_height
            )
            
            img = Image.open(io.BytesIO(png_data)).convert('RGBA')
            
            sprites.append({
                'name': name,
                'image': img,
                'width': pixel_width,
                'height': pixel_height,
                'grid_w': grid_w,
                'grid_h': grid_h
            })
            
            max_width = max(max_width, pixel_width)
            max_height = max(max_height, pixel_height)
        
        # Calculate optimal spritesheet layout
        # Use a grid layout with consistent cell sizes
        cell_width = max_width
        cell_height = max_height
        cols = math.ceil(math.sqrt(len(sprites)))
        rows = math.ceil(len(sprites) / cols)
        
        sheet_width = cols * cell_width
        sheet_height = rows * cell_height
        
        print(f"📐 Spritesheet size: {sheet_width}x{sheet_height}px ({cols}x{rows} grid)")
        print(f"📐 Cell size: {cell_width}x{cell_height}px")
        
        # Create spritesheet
        spritesheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
        metadata = {
            'type': 'obstacles',
            'cell_width': cell_width,
            'cell_height': cell_height,
            'cols': cols,
            'rows': rows,
            'sprites': {}
        }
        
        # Place sprites
        for idx, sprite in enumerate(sprites):
            col = idx % cols
            row = idx // cols
            x = col * cell_width
            y = row * cell_height
            
            # Center sprite in cell
            offset_x = (cell_width - sprite['width']) // 2
            offset_y = (cell_height - sprite['height']) // 2
            
            spritesheet.paste(sprite['image'], (x + offset_x, y + offset_y), sprite['image'])
            
            # Store metadata
            metadata['sprites'][sprite['name']] = {
                'x': x,
                'y': y,
                'width': sprite['width'],
                'height': sprite['height'],
                'grid_w': sprite['grid_w'],
                'grid_h': sprite['grid_h'],
                'cell_offset_x': offset_x,
                'cell_offset_y': offset_y
            }
        
        # Save spritesheet
        output_path = self.output_dir / "obstacles.png"
        spritesheet.save(output_path, 'PNG', optimize=True)
        print(f"✅ Saved obstacle spritesheet: {output_path}")
        
        # Save metadata
        metadata_path = self.output_dir / "obstacles.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Saved obstacle metadata: {metadata_path}")
        
        return output_path, metadata_path
    
    def generate_player_spritesheet(self, sprite_size=40):
        """
        Generate spritesheet for player characters.
        All sprites are resized to sprite_size x sprite_size.
        """
        print(f"\n🎨 Generating player character spritesheet ({sprite_size}x{sprite_size}px per sprite)...")
        
        characters_dir = Path("assets/player-characters")
        if not characters_dir.exists():
            print(f"❌ Player characters directory not found: {characters_dir}")
            return
        
        svg_files = sorted(characters_dir.glob("*.svg"))
        if not svg_files:
            print(f"❌ No SVG files found in {characters_dir}")
            return
        
        print(f"📦 Found {len(svg_files)} player characters")
        
        # Convert all SVGs to PNGs
        sprites = []
        for svg_file in svg_files:
            png_data = cairosvg.svg2png(
                url=str(svg_file),
                output_width=sprite_size,
                output_height=sprite_size
            )
            img = Image.open(io.BytesIO(png_data)).convert('RGBA')
            sprites.append({
                'name': svg_file.stem,
                'image': img
            })
        
        # Calculate spritesheet dimensions (horizontal strip)
        cols = len(sprites)
        rows = 1
        sheet_width = cols * sprite_size
        sheet_height = sprite_size
        
        print(f"📐 Spritesheet size: {sheet_width}x{sheet_height}px")
        
        # Create spritesheet
        spritesheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
        metadata = {
            'type': 'player_characters',
            'sprite_size': sprite_size,
            'cols': cols,
            'rows': rows,
            'sprites': {}
        }
        
        # Place sprites
        for idx, sprite in enumerate(sprites):
            x = idx * sprite_size
            y = 0
            
            spritesheet.paste(sprite['image'], (x, y), sprite['image'])
            
            metadata['sprites'][sprite['name']] = {
                'x': x,
                'y': y,
                'width': sprite_size,
                'height': sprite_size,
                'index': idx
            }
        
        # Save spritesheet
        output_path = self.output_dir / "player_characters.png"
        spritesheet.save(output_path, 'PNG', optimize=True)
        print(f"✅ Saved player character spritesheet: {output_path}")
        
        # Save metadata
        metadata_path = self.output_dir / "player_characters.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Saved player character metadata: {metadata_path}")
        
        return output_path, metadata_path


def main():
    """Generate all spritesheets."""
    
    print("=" * 60)
    print("🚀 Geo Dash Spritesheet Generator")
    print("=" * 60)
    
    if not HAS_REQUIREMENTS:
        return
    
    generator = SpriteSheetGenerator()
    
    # Generate obstacle spritesheet
    try:
        generator.generate_obstacle_spritesheet()
    except Exception as e:
        print(f"❌ Error generating obstacle spritesheet: {e}")
        import traceback
        traceback.print_exc()
    
    # Generate player character spritesheet
    try:
        generator.generate_player_spritesheet()
    except Exception as e:
        print(f"❌ Error generating player character spritesheet: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Spritesheet generation complete!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("1. Check assets/spritesheets/ for generated files")
    print("2. Update AssetManager to use spritesheets")
    print("3. Remove cairosvg dependency from game runtime")


if __name__ == "__main__":
    main()
