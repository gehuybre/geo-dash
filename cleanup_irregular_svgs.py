#!/usr/bin/env python3
"""
Clean up irregular obstacle SVGs:
1. Remove white background rectangles
2. Extract only colored shapes (purple/pink kawaii characters)
3. Center shapes in viewBox
4. Make background transparent
"""

import re
from pathlib import Path
import xml.etree.ElementTree as ET

def cleanup_svg(svg_path):
    """Clean up SVG by removing background and keeping only colored shapes."""
    
    # Parse SVG
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # Remove namespace for easier searching
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    
    # Find and remove white/background rectangles
    for elem in root.findall('.//{http://www.w3.org/2000/svg}rect', ns):
        fill = elem.get('style', '')
        if '#FFFFFF' in fill or 'fill:#FFFFFF' in fill or elem.get('fill') == '#FFFFFF':
            parent = root.find('.//{http://www.w3.org/2000/svg}rect[@style]...', ns)
            if parent is not None:
                parent.remove(elem)
    
    # Remove 'Background' group layer
    for group in root.findall('.//{http://www.w3.org/2000/svg}g', ns):
        if group.get('id') == 'Background':
            root.remove(group)
    
    # Save cleaned SVG
    tree.write(svg_path, encoding='utf-8', xml_declaration=True)
    print(f"✓ Cleaned: {svg_path.name}")

def main():
    svg_dir = Path('assets/obstacles/irregular-obstacles')
    
    if not svg_dir.exists():
        print(f"Directory not found: {svg_dir}")
        return 1
    
    svg_files = list(svg_dir.glob('*.svg'))
    
    if not svg_files:
        print("No SVG files found!")
        return 1
    
    print(f"Cleaning {len(svg_files)} SVG files...\n")
    
    for svg_file in svg_files:
        try:
            cleanup_svg(svg_file)
        except Exception as e:
            print(f"✗ Failed to clean {svg_file.name}: {e}")
    
    print(f"\n✅ Cleaned {len(svg_files)} SVG files")
    print("Now run: .venv/bin/python generate_irregular_spritesheet.py")
    
    return 0

if __name__ == '__main__':
    exit(main())
