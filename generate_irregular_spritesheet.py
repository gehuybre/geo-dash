#!/usr/bin/env python3
"""
Generate spritesheet from irregular obstacle SVGs.
Creates a tilemap with different sized sprites arranged efficiently.
"""

import os
import json
from pathlib import Path

try:
    import cairosvg
    from PIL import Image
    HAS_CAIRO = True
except ImportError:
    HAS_CAIRO = False
    print("Warning: cairosvg not available. Install with: pip install cairosvg pillow")


class IrregularSpriteSheetGenerator:
    """Generate spritesheet from irregular SVG obstacles."""
    
    def __init__(self, svg_dir, output_dir):
        self.svg_dir = Path(svg_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Different sprite sizes for variety (all multiples of 30 for grid alignment)
        self.sprite_sizes = [
            (60, 60),   # Small
            (90, 90),   # Medium
            (120, 120), # Large
        ]
    
    def generate(self):
        """Generate spritesheet from SVG files."""
        if not HAS_CAIRO:
            print("Error: cairosvg not installed. Cannot generate spritesheet.")
            return False
        
        # Get all SVG files
        svg_files = sorted(self.svg_dir.glob('*.svg'))
        if not svg_files:
            print(f"No SVG files found in {self.svg_dir}")
            return False
        
        print(f"\n🎨 Generating irregular obstacle spritesheet from {len(svg_files)} SVGs...")
        
        # Convert SVGs to PNGs at different sizes
        sprites = []
        for i, svg_file in enumerate(svg_files):
            for size_idx, (width, height) in enumerate(self.sprite_sizes):
                try:
                    # Convert SVG to PNG at specific size
                    png_data = cairosvg.svg2png(
                        url=str(svg_file),
                        output_width=width,
                        output_height=height
                    )
                    
                    # Open with PIL
                    from io import BytesIO
                    img = Image.open(BytesIO(png_data)).convert('RGBA')
                    
                    # Store sprite info
                    sprite_name = f"{svg_file.stem}_{size_idx}"
                    sprites.append({
                        'name': sprite_name,
                        'image': img,
                        'width': width,
                        'height': height,
                        'grid_width': width // 30,  # Grid cells (30px base unit)
                        'grid_height': height // 30,
                        'size_category': ['small', 'medium', 'large'][size_idx]
                    })
                    
                    print(f"  ✓ {sprite_name}: {width}x{height}px ({width//30}x{height//30} grid)")
                    
                except Exception as e:
                    print(f"  ✗ Failed to convert {svg_file.name} at size {width}x{height}: {e}")
        
        if not sprites:
            print("No sprites generated!")
            return False
        
        # Calculate optimal sheet layout (simple row packing)
        sheet_width = 1920  # Same as other spritesheets
        current_x = 0
        current_y = 0
        row_height = 0
        
        for sprite in sprites:
            if current_x + sprite['width'] > sheet_width:
                # Move to next row
                current_x = 0
                current_y += row_height
                row_height = 0
            
            sprite['x'] = current_x
            sprite['y'] = current_y
            current_x += sprite['width']
            row_height = max(row_height, sprite['height'])
        
        sheet_height = current_y + row_height
        
        # Create spritesheet
        print(f"\n📐 Creating spritesheet: {sheet_width}x{sheet_height}px")
        spritesheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
        
        # Paste sprites
        metadata = {
            'width': sheet_width,
            'height': sheet_height,
            'sprites': []
        }
        
        for sprite in sprites:
            spritesheet.paste(sprite['image'], (sprite['x'], sprite['y']))
            metadata['sprites'].append({
                'name': sprite['name'],
                'x': sprite['x'],
                'y': sprite['y'],
                'width': sprite['width'],
                'height': sprite['height'],
                'grid_width': sprite['grid_width'],
                'grid_height': sprite['grid_height'],
                'size_category': sprite['size_category']
            })
        
        # Save spritesheet
        output_png = self.output_dir / 'irregular_obstacles.png'
        spritesheet.save(output_png, 'PNG')
        print(f"✅ Saved spritesheet: {output_png}")
        
        # Save metadata
        output_json = self.output_dir / 'irregular_obstacles.json'
        with open(output_json, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Saved metadata: {output_json}")
        
        print(f"\n🎉 Generated {len(sprites)} irregular obstacle sprites!")
        return True


def main():
    generator = IrregularSpriteSheetGenerator(
        svg_dir='assets/obstacles/irregular-obstacles',
        output_dir='assets/spritesheets'
    )
    
    success = generator.generate()
    
    if success:
        print("\n📝 Next steps:")
        print("1. Load this spritesheet in AssetManager")
        print("2. Create obstacle patterns using these irregular shapes")
        print("3. Enjoy pixel-perfect collision with variety!")
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
