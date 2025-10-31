"""
Bar type manager for loading and resolving reusable obstacle bar templates.
"""

import json
from core.physics import physics


class BarTypeManager:
    """Manages bar type definitions and resolves them to actual dimensions."""
    
    def __init__(self):
        self.bar_types = {}
        self.gap_types = {}
        self.base_width = 30
        self.base_height = 30  # Will be calculated from physics
        self._load_bar_types()
    
    def _load_bar_types(self):
        """Load bar type definitions from JSON file."""
        try:
            with open('data/bar_types.json', 'r') as f:
                data = json.load(f)
            
            # Get base unit configuration
            base_unit = data.get('base_unit', {})
            self.base_width = base_unit.get('width', 30)
            self.base_height = base_unit.get('height', 30)
            
            # Get gap unit configuration
            gap_unit = data.get('gap_unit', {})
            self.gap_unit_distance = gap_unit.get('base_distance', 100)
            
            # Load all bar type definitions
            self.bar_types = data.get('bar_types', {})
            
            # Load gap type definitions
            self.gap_types = data.get('gap_types', {})
            
            print(f"Bar Types: Loaded {len(self.bar_types)} bar types, {len(self.gap_types)} gap types")
            print(f"  Base unit: {self.base_width}px wide × {self.base_height}px tall")
            print(f"  Gap unit: {self.gap_unit_distance}px (multiplier-based)")
            
        except FileNotFoundError:
            print("Warning: bar_types.json not found, using defaults only")
            self.bar_types = {}
        except json.JSONDecodeError as e:
            print(f"Error: Could not parse bar_types.json: {e}")
            self.bar_types = {}
    
    def get_bar_dimensions(self, bar_type):
        """
        Get actual width and height for a bar type.
        Supports multiple formats:
        - Predefined types from bar_types.json
        - Dynamic: 'bar-{width}-{height}' (e.g., 'bar-2-3')
        - Floating: 'bar-{width}-{floor}-{ceiling}' (e.g., 'bar-4-2-5')
          floor = height from ground, ceiling = height from floor
        
        Args:
            bar_type: String name of bar type
        
        Returns:
            Tuple of (width, height, y_offset) in pixels
            y_offset is 0 for ground obstacles, >0 for floating platforms
        """
        # Try predefined bar types first
        if bar_type in self.bar_types:
            bar_def = self.bar_types[bar_type]
            width_mult = bar_def.get('width_multiplier', 1)
            height_mult = bar_def.get('height_multiplier', 1)
            
            width = int(self.base_width * width_mult)
            height = int(self.base_height * height_mult)
            
            # Check if it has floor offset (floating platform)
            floor_mult = bar_def.get('floor_multiplier', 0)
            y_offset = int(self.base_height * floor_mult)
            
            return (width, height, y_offset)
        
        # Try parsing dynamic formats
        if bar_type.startswith('bar-'):
            try:
                parts = bar_type.split('-')
                
                if len(parts) == 4:
                    # Floating platform: bar-{width}-{floor}-{ceiling}
                    width_mult = float(parts[1])
                    floor_mult = float(parts[2])
                    ceiling_mult = float(parts[3])
                    
                    width = int(self.base_width * width_mult)
                    y_offset = int(self.base_height * floor_mult)
                    height = int(self.base_height * ceiling_mult)
                    
                    return (width, height, y_offset)
                    
                elif len(parts) == 3:
                    # Ground obstacle: bar-{width}-{height}
                    width_mult = float(parts[1])
                    height_mult = float(parts[2])
                    
                    width = int(self.base_width * width_mult)
                    height = int(self.base_height * height_mult)
                    
                    return (width, height, 0)
            except (ValueError, IndexError):
                pass
        
        print(f"Warning: Unknown bar type '{bar_type}'")
        return None
    
    def list_bar_types(self):
        """Get list of all available bar type names."""
        return list(self.bar_types.keys())
    
    def get_bar_info(self, bar_type):
        """Get full information about a bar type including description."""
        if bar_type not in self.bar_types:
            return None
        
        bar_def = self.bar_types[bar_type].copy()
        width, height = self.get_bar_dimensions(bar_type)
        bar_def['actual_width'] = width
        bar_def['actual_height'] = height
        return bar_def
    
    def get_gap_distance(self, gap_type):
        """
        Get actual distance for a gap type.
        Supports both predefined types and dynamic format: 
        - 'gap-{multiplier}' (e.g., 'gap-1', 'gap-2.5')
        - 'gap-{multiplier}-{hazard}' (e.g., 'gap-1.75-lava', 'gap-2.0-acid', 'gap-2.25-none')
        
        Args:
            gap_type: String name of gap type
        
        Returns:
            Integer distance in pixels, or None if invalid format
        """
        # Try predefined gap types first
        if gap_type in self.gap_types:
            gap_def = self.gap_types[gap_type]
            multiplier = gap_def.get('multiplier', 1)
            distance = int(self.gap_unit_distance * multiplier)
            return distance
        
        # Try parsing dynamic format: gap-{multiplier} or gap-{multiplier}-{hazard}
        if gap_type.startswith('gap-'):
            try:
                parts = gap_type[4:].split('-')  # Remove 'gap-' prefix and split
                multiplier = float(parts[0])
                distance = int(self.gap_unit_distance * multiplier)
                return distance
            except (ValueError, IndexError):
                pass
        
        print(f"Warning: Unknown gap type '{gap_type}'")
        return None
    
    def get_gap_hazard(self, gap_type):
        """
        Get hazard type for a gap.
        Supports format: 'gap-{multiplier}-{hazard}' (e.g., 'gap-2.0-lava', 'gap-1.75-acid')
        
        Args:
            gap_type: String name of gap type
        
        Returns:
            Hazard type string ('lava', 'acid', 'none') or None if no hazard specified
        """
        # Try parsing dynamic format: gap-{multiplier}-{hazard}
        if gap_type.startswith('gap-'):
            try:
                parts = gap_type[4:].split('-')  # Remove 'gap-' prefix and split
                if len(parts) >= 2:
                    hazard = parts[1]  # Second part is hazard type
                    if hazard in ['lava', 'acid', 'none']:
                        return hazard if hazard != 'none' else None
            except (ValueError, IndexError):
                pass
        
        return None  # No hazard specified
    
    def list_gap_types(self):
        """Get list of all available gap type names."""
        return list(self.gap_types.keys())


# Global bar type manager instance
bar_type_manager = BarTypeManager()
