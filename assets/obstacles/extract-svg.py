#!/usr/bin/env python3
"""
Extract individual obstacle SVGs from alle_rechthoeken_8x8-ingevuld.svg

This script extracts the 64 top-level obstacle groups (each containing a rectangle
background with decorative SVG artwork on top) and saves them as individual SVG files.

The naming scheme is w-h.svg where:
- w = width (1-8)
- h = height (1-8)
- Top left is 1-1, bottom right is 8-8
"""

import xml.etree.ElementTree as ET
import os
from pathlib import Path

def extract_obstacles():
    """Extract individual obstacle SVGs from the source file."""
    
    # Parse the source SVG
    input_file = Path(__file__).parent / "alle_rechthoeken_8x8-ingevuld.svg"
    tree = ET.parse(input_file)
    root = tree.getroot()
    
    # SVG namespace
    namespaces = {
        'svg': 'http://www.w3.org/2000/svg',
        'xlink': 'http://www.w3.org/1999/xlink',
        'serif': 'http://www.serif.com/'
    }
    
    # Register namespaces to preserve them in output
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)
    
    # Find all top-level <g> groups that contain a rectangle with a stroke
    # These are the obstacle groups we want to extract
    obstacles_with_positions = []
    
    # Iterate through all top-level groups (direct children of <svg>)
    for group in root.findall('./svg:g', namespaces):
        # Look for ANY rect with a stroke (could be nested)
        rects_with_stroke = []
        for rect in group.findall('.//svg:rect', namespaces):
            style = rect.get('style', '')
            if 'stroke:rgb(17,17,17)' in style or 'stroke: rgb(17,17,17)' in style:
                rects_with_stroke.append(rect)
        
        # Use the first rect with stroke found
        if rects_with_stroke:
            child = rects_with_stroke[0]
            x = float(child.get('x', 0))
            y = float(child.get('y', 0))
            width = float(child.get('width', 0))
            height = float(child.get('height', 0))
            obstacles_with_positions.append({
                'group': group,
                'rect': child,
                'x': x,
                'y': y,
                'width': width,
                'height': height
            })
    
    print(f"Found {len(obstacles_with_positions)} obstacles with rectangles")
    
    # Sort by y first (rows), then by x (columns)
    obstacles_with_positions.sort(key=lambda o: (o['y'], o['x']))
    
    # The grid is 8x8, let's determine the row/column based on y and x ranges
    # Find min/max x and y
    min_x = min(o['x'] for o in obstacles_with_positions)
    max_x = max(o['x'] for o in obstacles_with_positions)
    min_y = min(o['y'] for o in obstacles_with_positions)
    max_y = max(o['y'] for o in obstacles_with_positions)
    
    print(f"X range: {min_x} to {max_x}")
    print(f"Y range: {min_y} to {max_y}")
    
    # Calculate grid cell sizes
    x_step = (max_x - min_x) / 7  # 8 columns = 7 intervals
    y_step = (max_y - min_y) / 7  # 8 rows = 7 intervals
    
    print(f"Grid cell size: {x_step} x {y_step}")
    
    # Assign each obstacle to a grid position
    grid = {}
    for obs in obstacles_with_positions:
        # Calculate column (1-8) and row (1-8)
        col = min(8, max(1, int(round((obs['x'] - min_x) / x_step)) + 1))
        row = min(8, max(1, int(round((obs['y'] - min_y) / y_step)) + 1))
        
        grid[(col, row)] = obs
    
    print(f"Organized into {len(grid)} grid positions")
    
    # Create output directory
    output_dir = Path(__file__).parent / "extracted-obstacles"
    output_dir.mkdir(exist_ok=True)
    
    # Extract each obstacle from the grid
    extracted_count = 0
    
    for (col, row), obs in sorted(grid.items()):
        # Create filename using column-row format (width-height)
        filename = f"{col}-{row}.svg"
        output_path = output_dir / filename
        
        # Get the bounding box of this obstacle
        x, y, width, height = obs['x'], obs['y'], obs['width'], obs['height']
        
        # Add some padding
        padding = 10
        viewbox_x = x - padding
        viewbox_y = y - padding
        viewbox_width = width + 2 * padding
        viewbox_height = height + 2 * padding
        
        # Create a new SVG for this obstacle
        new_svg = ET.Element('svg', {
            'width': '100%',
            'height': '100%',
            'viewBox': f"{viewbox_x} {viewbox_y} {viewbox_width} {viewbox_height}",
            'version': '1.1',
            'xmlns': namespaces['svg'],
            'xmlns:xlink': namespaces['xlink'],
            'xmlns:serif': namespaces['serif'],
            'style': 'fill-rule:evenodd;clip-rule:evenodd;'
        })
        
        # Clone the obstacle group
        new_group = ET.Element('g')
        for child in obs['group']:
            new_group.append(child)
        new_svg.append(new_group)
        
        # Write to file
        new_tree = ET.ElementTree(new_svg)
        ET.indent(new_tree, space='    ')
        new_tree.write(output_path, encoding='UTF-8', xml_declaration=True)
        
        extracted_count += 1
        print(f"Extracted {filename} (grid pos {col},{row}) - position ({x}, {y}), size ({width}x{height})")
    
    print(f"\nSuccessfully extracted {extracted_count} obstacles to {output_dir}")
    print(f"Files are named using format: w-h.svg where w=width, h=height (1-8)")

if __name__ == "__main__":
    extract_obstacles()
