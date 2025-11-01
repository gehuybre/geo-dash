"""
Pattern loading and validation for obstacle generation.
"""

import json
import os
from game.config import GROUND_Y
from managers.bar_type_manager import bar_type_manager


class PatternManager:
    """Manages loading of obstacle patterns.
    Patterns are pre-validated by the pattern generator."""
    
    def __init__(self, patterns_dir="obstacle_patterns", difficulty="hard"):
        self.patterns_dir = patterns_dir
        self.difficulty = difficulty  # "easy", "medium", or "hard"
        self.patterns = self._load_patterns()
        print(f"Loaded {len(self.patterns)} obstacle patterns for difficulty: {difficulty}")
    
    def _load_patterns(self):
        """Load obstacle patterns from JSON files matching the selected difficulty.
        Patterns are pre-validated by the pattern generator, so no validation needed here."""
        patterns = []
        
        if not os.path.exists(self.patterns_dir):
            print(f"Patterns directory '{self.patterns_dir}' not found")
            return patterns
        
        difficulty_suffix = f"_{self.difficulty}"  # e.g., "_easy", "_medium", "_hard"
        
        for filename in os.listdir(self.patterns_dir):
            if filename.endswith('.json'):
                # Only load patterns matching the selected difficulty
                if not filename.endswith(f"{difficulty_suffix}.json"):
                    continue
                
                filepath = os.path.join(self.patterns_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        pattern_data = json.load(f)
                        # Resolve bar_type references to actual dimensions
                        pattern_data = self._resolve_bar_types(pattern_data)
                        # Load pattern (pre-validated by generator)
                        if 'obstacles' in pattern_data and isinstance(pattern_data['obstacles'], list):
                            patterns.append(pattern_data)
                            print(f"✓ Loaded pattern: {pattern_data.get('name', filename)}")
                        else:
                            print(f"✗ Invalid pattern format in {filename}")
                except (json.JSONDecodeError, IOError) as e:
                    print(f"✗ Failed to load pattern {filename}: {e}")
        
        return patterns
    
    def _resolve_bar_types(self, pattern_data):
        """
        Resolve bar_type and gap_type references to actual width/height/gap values.
        Supports both legacy format (explicit width/height/gap_after) and new format (bar_type/gap_type).
        Now also supports floating platforms with y_offset and irregular sprites.
        """
        obstacles = pattern_data.get('obstacles', [])
        resolved_obstacles = []
        
        # Check if this pattern prefers irregular sprites
        metadata = pattern_data.get('metadata', {})
        uses_irregular = metadata.get('uses_irregular_sprites', False) or metadata.get('type') == 'irregular'
        
        for obs in obstacles:
            resolved_obs = obs.copy()
            
            # Mark if this pattern uses irregular sprites
            if uses_irregular:
                resolved_obs['prefer_irregular'] = True
            
            # Check if this obstacle uses bar_type reference
            if 'bar_type' in obs:
                bar_type = obs['bar_type']
                dimensions = bar_type_manager.get_bar_dimensions(bar_type)
                
                if dimensions:
                    # Handle both (width, height) and (width, height, y_offset) tuples
                    if len(dimensions) == 3:
                        width, height, y_offset = dimensions
                        if 'y_offset' not in obs:
                            resolved_obs['y_offset'] = y_offset
                    else:
                        width, height = dimensions
                        
                    # Only override if not explicitly set
                    if 'width' not in obs:
                        resolved_obs['width'] = width
                    if 'height' not in obs:
                        resolved_obs['height'] = height
                else:
                    # Bar type not found, use defaults
                    if 'width' not in obs:
                        resolved_obs['width'] = 30
                    if 'height' not in obs:
                        resolved_obs['height'] = 30
            
            # Check if this obstacle uses gap_type reference
            if 'gap_type' in obs:
                gap_type = obs['gap_type']
                gap_distance = bar_type_manager.get_gap_distance(gap_type)
                gap_hazard = bar_type_manager.get_gap_hazard(gap_type)
                
                if gap_distance is not None:
                    # Only override if not explicitly set
                    if 'gap_after' not in obs:
                        resolved_obs['gap_after'] = gap_distance
                else:
                    # Gap type not found, use default
                    if 'gap_after' not in obs:
                        resolved_obs['gap_after'] = 200
                
                # Set gap_hazard if specified in gap_type
                if gap_hazard is not None:
                    if 'gap_hazard' not in obs:
                        resolved_obs['gap_hazard'] = gap_hazard
            
            # Ensure width and height exist (for legacy patterns)
            if 'width' not in resolved_obs:
                resolved_obs['width'] = 30
            if 'height' not in resolved_obs:
                resolved_obs['height'] = 30
            if 'y_offset' not in resolved_obs:
                resolved_obs['y_offset'] = 0  # Default to ground
            
            resolved_obstacles.append(resolved_obs)
        
        pattern_data['obstacles'] = resolved_obstacles
        return pattern_data
    
    def get_random_pattern(self):
        """Get a random pattern from loaded patterns."""
        import random
        if self.patterns:
            return random.choice(self.patterns)
        return None
    
    def get_pattern_count(self):
        """Get the number of loaded patterns."""
        return len(self.patterns)

