#!/usr/bin/env python3
"""
Extract individual kawaii objects from multi-object SVG files.
Each SVG contains multiple kawaii objects in separate groups.
This script extracts each group as a separate SVG file.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import re

# Register SVG namespace
ET.register_namespace('', 'http://www.w3.org/2000/svg')
SVG_NS = '{http://www.w3.org/2000/svg}'


def get_group_bounds(group):
    """Calculate bounding box of a group by parsing all path elements."""
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = float('-inf'), float('-inf')
    
    # Find all path elements in this group
    for path in group.iter(f'{SVG_NS}path'):
        d = path.get('d', '')
        # Extract numbers from path data (very basic parsing)
        numbers = re.findall(r'-?\d+\.?\d*', d)
        if numbers:
            coords = [float(n) for n in numbers]
            # Assume alternating x,y coordinates
            x_coords = coords[::2]
            y_coords = coords[1::2]
            if x_coords and y_coords:
                min_x = min(min_x, min(x_coords))
                max_x = max(max_x, max(x_coords))
                min_y = min(min_y, min(y_coords))
                max_y = max(max_y, max(y_coords))
    
    if min_x == float('inf'):
        return None
    
    # Add some padding
    padding = 10
    return {
        'x': min_x - padding,
        'y': min_y - padding,
        'width': max_x - min_x + 2 * padding,
        'height': max_y - min_y + 2 * padding
    }


def extract_kawaii_objects(svg_path, output_dir):
    """Extract individual kawaii objects from an SVG file."""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    svg_name = Path(svg_path).stem
    print(f"\n🎨 Processing: {svg_name}")
    
    # Find the Objects group (case-insensitive)
    objects_group = None
    for child in root:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        obj_id = child.get('id', '')
        if tag == 'g' and obj_id.upper() == 'OBJECTS':
            objects_group = child
            break
    
    if not objects_group:
        print(f"  ⚠️  No 'Objects' group found")
        return []
    
    # Get all sub-groups (each is a kawaii object)
    kawaii_groups = []
    for child in objects_group:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag == 'g':
            kawaii_groups.append(child)
    
    print(f"  Found {len(kawaii_groups)} kawaii objects")
    
    extracted_files = []
    
    # Extract each kawaii object as a separate SVG
    for idx, group in enumerate(kawaii_groups):
        # Calculate bounding box
        bounds = get_group_bounds(group)
        if not bounds:
            print(f"  ⚠️  Could not calculate bounds for object {idx}")
            continue
        
        # Create new SVG with just this object
        new_svg = ET.Element('svg')
        new_svg.set('version', '1.1')
        new_svg.set('viewBox', f"{bounds['x']} {bounds['y']} {bounds['width']} {bounds['height']}")
        new_svg.set('width', str(bounds['width']))
        new_svg.set('height', str(bounds['height']))
        
        # Copy the group into the new SVG
        new_svg.append(group)
        
        # Save to file
        output_file = output_dir / f"{svg_name}_{idx}.svg"
        new_tree = ET.ElementTree(new_svg)
        ET.indent(new_tree, space='  ')
        new_tree.write(output_file, encoding='utf-8', xml_declaration=True)
        
        extracted_files.append(output_file)
        print(f"  ✓ Extracted object {idx}: {output_file.name} ({bounds['width']:.0f}x{bounds['height']:.0f})")
    
    return extracted_files


def main():
    """Main extraction process."""
    input_dir = Path('assets/obstacles/irregular-obstacles')
    output_dir = Path('assets/obstacles/extracted-kawaii')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Extracting Individual Kawaii Objects from SVGs")
    print("=" * 60)
    
    # Get all SVG files
    svg_files = sorted(input_dir.glob('*.svg'))
    print(f"\nFound {len(svg_files)} SVG files to process")
    
    all_extracted = []
    for svg_file in svg_files:
        extracted = extract_kawaii_objects(svg_file, output_dir)
        all_extracted.extend(extracted)
    
    print("\n" + "=" * 60)
    print(f"✅ Extraction complete!")
    print(f"   Total kawaii objects extracted: {len(all_extracted)}")
    print(f"   Output directory: {output_dir}")
    print("=" * 60)
    
    print("\n💡 Next steps:")
    print("   1. Review extracted SVGs in assets/obstacles/extracted-kawaii/")
    print("   2. Run: python generate_irregular_spritesheet.py")
    print("   3. The spritesheet will use individual kawaii objects")


if __name__ == '__main__':
    main()
