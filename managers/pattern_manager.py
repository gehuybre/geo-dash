"""
Pattern loading and validation for obstacle generation.
"""

import json
import os
from config import GROUND_Y
from core.physics import physics


class PatternManager:
    """Manages loading and validation of obstacle patterns."""
    
    def __init__(self, patterns_dir="obstacle_patterns"):
        self.patterns_dir = patterns_dir
        self.patterns = self._load_patterns()
        print(f"Loaded {len(self.patterns)} obstacle patterns")
    
    def _load_patterns(self):
        """Load obstacle patterns from JSON files."""
        patterns = []
        
        if not os.path.exists(self.patterns_dir):
            print(f"Patterns directory '{self.patterns_dir}' not found")
            return patterns
        
        for filename in os.listdir(self.patterns_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.patterns_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        pattern_data = json.load(f)
                        # Validate pattern
                        if 'obstacles' in pattern_data and isinstance(pattern_data['obstacles'], list):
                            # Validate pattern is physically possible
                            if self._validate_pattern(pattern_data):
                                patterns.append(pattern_data)
                                print(f"✓ Loaded pattern: {pattern_data.get('name', filename)}")
                            else:
                                print(f"✗ Pattern validation failed: {pattern_data.get('name', filename)}")
                        else:
                            print(f"✗ Invalid pattern format in {filename}")
                except (json.JSONDecodeError, IOError) as e:
                    print(f"✗ Failed to load pattern {filename}: {e}")
        
        return patterns
    
    def _validate_pattern(self, pattern_data):
        """Validate that a pattern is physically possible to complete with jump sequences."""
        obstacles_data = pattern_data.get('obstacles', [])
        
        if not obstacles_data:
            return False
        
        # Simulate player position and state through the pattern
        player_x = 0
        player_y = GROUND_Y  # Start on ground
        player_on_ground = True
        
        for i, obs_data in enumerate(obstacles_data):
            height = obs_data.get('height', 0)
            width = obs_data.get('width', 30)
            gap_after = obs_data.get('gap_after', 0)
            
            # Check 1: Height must be jumpable from ground
            if height > physics.max_obstacle_height:
                print(f"  - Obstacle {i}: height {height} exceeds max {physics.max_obstacle_height}")
                return False
            
            # Current obstacle position
            obstacle_x = player_x
            obstacle_y = GROUND_Y - height
            obstacle_top = obstacle_y
            
            # Check if player can reach this obstacle
            if i > 0:
                prev_obs = obstacles_data[i - 1]
                prev_height = prev_obs.get('height', 0)
                prev_width = prev_obs.get('width', 30)
                prev_gap = prev_obs.get('gap_after', 0)
                prev_top = GROUND_Y - prev_height
                
                # If gap is 0, this is stacked on previous obstacle
                if prev_gap == 0:
                    # Stacked: player can walk onto it if height difference is climbable
                    height_diff = height - prev_height
                    
                    if height_diff > 0:
                        # Need to jump UP onto the stack
                        if not physics.can_climb(height_diff):
                            print(f"  - Obstacle {i}: stack height increase {height_diff} too steep")
                            return False
                    
                    # Player is now on top of previous obstacle
                    player_y = prev_top
                    player_on_ground = True
                else:
                    # There's a gap - need to jump
                    # Check if gap is jumpable
                    if prev_gap > physics.max_jump_distance:
                        print(f"  - Obstacle {i-1}: gap {prev_gap} exceeds max jump distance {physics.max_jump_distance}")
                        return False
                    
                    # Check if gap allows safe landing
                    if not physics.can_land_safely(prev_gap, width):
                        print(f"  - Obstacle {i-1}: gap {prev_gap} less than min safe gap {physics.min_safe_gap} for narrow platform")
                        return False
                    
                    # Check if we can jump from previous height to this height
                    vertical_diff = prev_top - obstacle_top  # Negative if jumping up
                    
                    if vertical_diff < 0:  # Jumping UP
                        jump_up_height = abs(vertical_diff)
                        
                        if not physics.can_forward_jump_up(jump_up_height):
                            print(f"  - Obstacle {i}: upward jump {jump_up_height}px too high from gap")
                            return False
                    
                    # Player lands on this obstacle
                    player_y = obstacle_top
                    player_on_ground = True
            
            # Move player position forward
            player_x += width + gap_after
        
        # Pattern is valid!
        return True
    
    def get_random_pattern(self):
        """Get a random pattern from loaded patterns."""
        import random
        if self.patterns:
            return random.choice(self.patterns)
        return None
    
    def get_pattern_count(self):
        """Get the number of loaded patterns."""
        return len(self.patterns)
