#!/usr/bin/env python3
"""Remove black borders from SVG files by removing stroke attributes."""

import os
import re

svg_dir = "assets/obstacles/extracted-obstacles"

for filename in os.listdir(svg_dir):
    if filename.endswith('.svg'):
        filepath = os.path.join(svg_dir, filename)
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Remove stroke and stroke-width from style attributes
        # Pattern: stroke:rgb(...);stroke-width:...px;
        content = re.sub(r';stroke:rgb\([^)]+\)', '', content)
        content = re.sub(r';stroke-width:[^;]+', '', content)
        content = re.sub(r'stroke:rgb\([^)]+\);?', '', content)
        content = re.sub(r'stroke-width:[^;]+;?', '', content)
        
        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Removed borders from: {filename}")

print("\nDone removing borders from SVG files!")
