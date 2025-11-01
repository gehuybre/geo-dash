#!/usr/bin/env python3
"""
Fix SVG viewBox to remove padding around the actual content.
This ensures obstacles sit flush on the ground and collision is accurate.
"""

import os
import re
import xml.etree.ElementTree as ET

svg_dir = "assets/obstacles/extracted-obstacles"

# Register namespaces to preserve them
ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('svg', 'http://www.w3.org/2000/svg')
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
ET.register_namespace('serif', 'http://www.serif.com/')

for filename in sorted(os.listdir(svg_dir)):
    if not filename.endswith('.svg'):
        continue
    
    filepath = os.path.join(svg_dir, filename)
    
    try:
        # Read the file
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract viewBox using regex (simpler than XML parsing for this)
        viewbox_match = re.search(r'viewBox="([^"]+)"', content)
        if not viewbox_match:
            print(f"⚠ No viewBox found in {filename}")
            continue
        
        viewbox_str = viewbox_match.group(1)
        parts = viewbox_str.split()
        if len(parts) != 4:
            print(f"⚠ Invalid viewBox in {filename}: {viewbox_str}")
            continue
        
        x, y, w, h = map(float, parts)
        
        # Remove 10px padding from all sides
        # Original viewBox: "300.0 250.0 120.0 120.0" for 3x3 (100x100 content + 10px padding each side)
        # New viewBox should be: "310.0 260.0 100.0 100.0"
        PADDING = 10
        new_x = x + PADDING
        new_y = y + PADDING
        new_w = w - 2 * PADDING
        new_h = h - 2 * PADDING
        
        # Make sure we don't go negative
        if new_w <= 0 or new_h <= 0:
            print(f"⚠ Padding too large for {filename}, skipping")
            continue
        
        new_viewbox = f"{new_x} {new_y} {new_w} {new_h}"
        
        # Replace viewBox
        new_content = content.replace(f'viewBox="{viewbox_str}"', f'viewBox="{new_viewbox}"')
        
        if new_content != content:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"✓ Fixed {filename}: viewBox {viewbox_str} → {new_viewbox}")
        
    except Exception as e:
        print(f"✗ Error processing {filename}: {e}")

print("\nDone fixing SVG viewBoxes!")
