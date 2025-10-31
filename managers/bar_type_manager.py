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
            with open('bar_types.json', 'r') as f:
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
        
        Args:
            bar_type: String name of bar type (e.g., 'short', 'wide_medium')
        
        Returns:
            Tuple of (width, height) in pixels, or None if bar type not found
        """
        if bar_type not in self.bar_types:
            print(f"Warning: Unknown bar type '{bar_type}'")
            return None
        
        bar_def = self.bar_types[bar_type]
        width_mult = bar_def.get('width_multiplier', 1)
        height_mult = bar_def.get('height_multiplier', 1)
        
        width = int(self.base_width * width_mult)
        height = int(self.base_height * height_mult)
        
        return (width, height)
    
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
        Get actual distance for a gap type using multiplier system.
        
        Args:
            gap_type: String name of gap type (e.g., 'gap-1', 'gap-2.5')
        
        Returns:
            Integer distance in pixels, or None if gap type not found
        """
        if gap_type not in self.gap_types:
            print(f"Warning: Unknown gap type '{gap_type}'")
            return None
        
        gap_def = self.gap_types[gap_type]
        multiplier = gap_def.get('multiplier', 1)
        distance = int(self.gap_unit_distance * multiplier)
        return distance
    
    def list_gap_types(self):
        """Get list of all available gap type names."""
        return list(self.gap_types.keys())


# Global bar type manager instance
bar_type_manager = BarTypeManager()
