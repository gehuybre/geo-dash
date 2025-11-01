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
            (60, 60),   # Small (2x2 grid)
            (90, 90),   # Medium (3x3 grid)
            (120, 120), # Large (4x4 grid)
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
        
        print(f"\n🎨 Generating irregular obstacle spritesheet from {len(svg_files)} individual kawaii SVGs...")
        
        # Convert each SVG to PNG at ALL sizes for maximum variety
        # Each kawaii object gets 4 sizes: tiny, small, medium, large
        # Sizes are 10x larger for better visibility!
        sprites = []
        for svg_file in svg_files:
            # Create each kawaii object in multiple sizes
            for width, height, size_category in [
                (300, 300, 'tiny'),      # 10x10 grid (was 1x1)
                (600, 600, 'small'),     # 20x20 grid (was 2x2)
                (900, 900, 'medium'),    # 30x30 grid (was 3x3)
                (1200, 1200, 'large'),   # 40x40 grid (was 4x4)
            ]:
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
                    
                    # Crop to non-transparent bounding box to remove whitespace
                    bbox = img.getbbox()  # Get bounding box of non-transparent pixels
                    if bbox:
                        img = img.crop(bbox)
                        # Resize back to target size (this will center the shape)
                        final_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                        # Center the cropped image
                        paste_x = (width - img.width) // 2
                        paste_y = (height - img.height) // 2
                        final_img.paste(img, (paste_x, paste_y))
                        img = final_img
                    
                    # Store sprite info
                    sprite_name = f"{svg_file.stem}_{size_category}"
                    sprites.append({
                        'name': sprite_name,
                        'image': img,
                        'width': width,
                        'height': height,
                        'grid_width': width // 30,  # Grid cells (30px base unit)
                        'grid_height': height // 30,
                        'size_category': size_category
                    })
                    
                    print(f"  ✓ {sprite_name}: {width}x{height}px ({width//30}x{height//30} grid)")
                    
                except Exception as e:
                    print(f"  ✗ Failed to convert {svg_file.name} at {size_category}: {e}")
        
        if not sprites:
            print("No sprites generated!")
            return False
        
        # Calculate optimal sheet layout (simple row packing)
        # Much larger sheet to accommodate 10x sized sprites
        sheet_width = 4800  # Large enough for big kawaii objects
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
    # Use the extracted individual kawaii objects
    generator = IrregularSpriteSheetGenerator(
        svg_dir='assets/obstacles/extracted-kawaii',
        output_dir='assets/spritesheets'
    )
    
    success = generator.generate()
    
    if success:
        print("\n📝 Next steps:")
        print("1. Restart the game to see the new kawaii obstacles")
        print("2. Each of the 27 kawaii objects will be used as obstacles!")
        print("3. Enjoy pixel-perfect collision with variety!")
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
