#!/usr/bin/env python3
"""Fix duplicate xmlns attributes in SVG files."""

import os
import re

svg_dir = "assets/obstacles/extracted-obstacles"

for filename in os.listdir(svg_dir):
    if filename.endswith('.svg'):
        filepath = os.path.join(svg_dir, filename)
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Remove all xmlns declarations from the svg tag and rebuild it cleanly
        # Extract the svg tag
        svg_tag_match = re.search(r'<svg[^>]*>', content)
        if svg_tag_match:
            old_svg_tag = svg_tag_match.group(0)
            
            # Extract all unique attributes (not xmlns related)
            attrs = {}
            
            # Extract viewBox, width, height, version, style
            for attr in ['viewBox', 'width', 'height', 'version', 'style']:
                match = re.search(rf'{attr}="([^"]*)"', old_svg_tag)
                if match:
                    attrs[attr] = match.group(1)
            
            # Build new clean svg tag with xmlns declarations only once
            new_svg_tag = '<svg'
            new_svg_tag += ' xmlns="http://www.w3.org/2000/svg"'
            new_svg_tag += ' xmlns:xlink="http://www.w3.org/1999/xlink"'
            new_svg_tag += ' xmlns:svg="http://www.w3.org/2000/svg"'
            new_svg_tag += ' xmlns:serif="http://www.serif.com/"'
            
            # Add other attributes
            for attr, value in sorted(attrs.items()):
                new_svg_tag += f' {attr}="{value}"'
            
            new_svg_tag += '>'
            
            # Replace old tag with new tag
            content = content.replace(old_svg_tag, new_svg_tag)
            
            if content != original_content:
                with open(filepath, 'w') as f:
                    f.write(content)
                print(f"Fixed: {filename}")

print("\nDone fixing SVG files!")
