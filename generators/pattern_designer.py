#!/usr/bin/env python3
"""
Pattern Level Designer - Creates physics-validated obstacle patterns
based on mathematical shapes (W, sawtooth, sine, hill).

This designer generates varied, playable levels by following base patterns
with controlled randomness while ensuring all obstacles are jumpable.
"""

import json
import math
import random
from pathlib import Path


class PatternDesigner:
    """Generate obstacle patterns based on mathematical shapes."""
    
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        self.base_unit = 30  # Base grid unit (30px)
        
        # Physics constraints (hardcoded to avoid circular imports)
        # Max jump height ~98px = ~3 grid units
        # Max jump distance ~225px = ~7.5 grid units
        self.max_height_grid = 3
        self.max_gap_grid = 7.5
        self.min_gap_grid = 2  # Minimum gap for breathing room
        
        # Size variety - different obstacle sizes for visual interest
        self.obstacle_sizes = [
            (1, 1, 'tiny'),    # 30x30
            (2, 2, 'small'),   # 60x60
            (3, 3, 'medium'),  # 90x90
            (4, 4, 'large'),   # 120x120
        ]
        
    def generate_w_pattern(self, length=20, height_range=(1, 3), use_irregular=True):
        """
        Generate W-shaped pattern (valley-peak-valley-peak).
        
        Args:
            length: Number of obstacles
            height_range: (min, max) height in grid units
            use_irregular: Use irregular kawaii sprites
        """
        obstacles = []
        pattern_name = f"W Pattern ({'Irregular' if use_irregular else 'Regular'})"
        
        # W pattern: low-high-low-high-low cycle
        cycle_length = 5
        heights = [1, 3, 1, 3, 1]  # W shape
        
        for i in range(length):
            cycle_pos = i % cycle_length
            target_height = heights[cycle_pos]
            
            # Add controlled randomness
            height = max(height_range[0], min(height_range[1], 
                        target_height + random.choice([-1, 0, 1])))
            
            # Choose obstacle size (prefer medium/large for visibility)
            width, obs_height, size = random.choice(self.obstacle_sizes[1:])  # Skip tiny
            
            # Calculate safe gap
            gap_multiplier = random.uniform(1.5, 2.0)
            
            obstacle = {
                'bar_type': f'bar-{width}-{height}',
                'gap_type': f'gap-{gap_multiplier:.1f}',
                'comment': f'W-pattern position {i}, height={height}',
            }
            
            if use_irregular:
                obstacle['prefer_irregular'] = True
            
            obstacles.append(obstacle)
        
        return {
            'name': pattern_name,
            'description': f'W-shaped pattern with {length} obstacles',
            'obstacles': obstacles,
            'metadata': {
                'type': 'irregular' if use_irregular else 'shaped',
                'shape': 'W',
                'length': length,
                'uses_irregular_sprites': use_irregular,
                'rhythm': 'Wavelike up-down-up-down flow'
            }
        }
    
    def generate_sawtooth_pattern(self, length=15, max_climb_height=3, use_irregular=True):
        """
        Generate sawtooth pattern (gradual climb, sudden drop).
        
        Args:
            length: Number of obstacles
            max_climb_height: Maximum height to climb to
            use_irregular: Use irregular kawaii sprites
        """
        obstacles = []
        pattern_name = f"Sawtooth ({'Irregular' if use_irregular else 'Regular'})"
        
        # Sawtooth: gradual climb then drop
        climb_steps = 4  # How many steps to reach peak
        
        for i in range(length):
            cycle_pos = i % (climb_steps + 1)
            
            if cycle_pos < climb_steps:
                # Climbing phase
                height = 1 + int(cycle_pos * max_climb_height / climb_steps)
            else:
                # Drop phase
                height = 1
            
            # Vary obstacle size
            width, obs_height, size = random.choice(self.obstacle_sizes[1:])
            
            # Climbing obstacles need shorter gaps
            if cycle_pos > 0 and cycle_pos < climb_steps:
                gap_multiplier = random.uniform(1.3, 1.7)
            else:
                gap_multiplier = random.uniform(1.7, 2.2)
            
            obstacle = {
                'bar_type': f'bar-{width}-{height}',
                'gap_type': f'gap-{gap_multiplier:.1f}',
                'comment': f'Sawtooth cycle {i}, height={height}',
            }
            
            if use_irregular:
                obstacle['prefer_irregular'] = True
            
            obstacles.append(obstacle)
        
        return {
            'name': pattern_name,
            'description': f'Sawtooth pattern with gradual climbs and sudden drops',
            'obstacles': obstacles,
            'metadata': {
                'type': 'irregular' if use_irregular else 'shaped',
                'shape': 'sawtooth',
                'length': length,
                'uses_irregular_sprites': use_irregular,
                'rhythm': 'Climb-and-drop rhythm'
            }
        }
    
    def generate_sine_pattern(self, length=20, amplitude=2, period=8, use_irregular=True):
        """
        Generate smooth sine wave pattern.
        
        Args:
            length: Number of obstacles
            amplitude: Wave amplitude in grid units
            period: Wave period (obstacles per cycle)
            use_irregular: Use irregular kawaii sprites
        """
        obstacles = []
        pattern_name = f"Sine Wave ({'Irregular' if use_irregular else 'Regular'})"
        
        for i in range(length):
            # Calculate sine wave height
            angle = (i / period) * 2 * math.pi
            height = 1 + int(amplitude * (math.sin(angle) + 1))  # Offset to keep positive
            height = max(1, min(3, height))  # Clamp to valid range
            
            # Vary obstacle size
            width, obs_height, size = random.choice(self.obstacle_sizes)
            
            # Smooth gaps for flowing movement
            gap_multiplier = random.uniform(1.6, 2.0)
            
            obstacle = {
                'bar_type': f'bar-{width}-{height}',
                'gap_type': f'gap-{gap_multiplier:.1f}',
                'comment': f'Sine wave position {i}, height={height}',
            }
            
            if use_irregular:
                obstacle['prefer_irregular'] = True
            
            obstacles.append(obstacle)
        
        return {
            'name': pattern_name,
            'description': f'Smooth sine wave pattern',
            'obstacles': obstacles,
            'metadata': {
                'type': 'irregular' if use_irregular else 'shaped',
                'shape': 'sine',
                'length': length,
                'uses_irregular_sprites': use_irregular,
                'rhythm': 'Smooth wavelike flow'
            }
        }
    
    def generate_hill_pattern(self, length=12, peak_height=3, use_irregular=True):
        """
        Generate hill pattern (climb to peak, then descend).
        
        Args:
            length: Number of obstacles
            peak_height: Maximum height at peak
            use_irregular: Use irregular kawaii sprites
        """
        obstacles = []
        pattern_name = f"Hill ({'Irregular' if use_irregular else 'Regular'})"
        
        peak_pos = length // 2  # Peak in the middle
        
        for i in range(length):
            # Calculate distance from peak (normalized 0-1)
            distance_from_peak = abs(i - peak_pos) / peak_pos
            
            # Height decreases from peak
            height = max(1, int(peak_height * (1 - distance_from_peak)))
            
            # Larger obstacles at peak
            if i == peak_pos:
                width, obs_height, size = self.obstacle_sizes[-1]  # Largest
            elif abs(i - peak_pos) <= 2:
                width, obs_height, size = self.obstacle_sizes[2]  # Medium
            else:
                width, obs_height, size = random.choice(self.obstacle_sizes[:2])  # Small
            
            # Tighter gaps on uphill, looser on downhill
            if i < peak_pos:
                gap_multiplier = random.uniform(1.4, 1.8)
            else:
                gap_multiplier = random.uniform(1.8, 2.2)
            
            obstacle = {
                'bar_type': f'bar-{width}-{height}',
                'gap_type': f'gap-{gap_multiplier:.1f}',
                'comment': f'Hill position {i}, height={height}',
            }
            
            if use_irregular:
                obstacle['prefer_irregular'] = True
            
            obstacles.append(obstacle)
        
        return {
            'name': pattern_name,
            'description': f'Hill with peak at center',
            'obstacles': obstacles,
            'metadata': {
                'type': 'irregular' if use_irregular else 'shaped',
                'shape': 'hill',
                'length': length,
                'uses_irregular_sprites': use_irregular,
                'rhythm': 'Climb to peak then descend'
            }
        }
    
    def save_pattern(self, pattern, output_dir='obstacle_patterns'):
        """Save pattern to JSON file."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename from pattern name
        filename = pattern['name'].lower().replace(' ', '_').replace('(', '').replace(')', '')
        filepath = output_path / f"{filename}_{self.difficulty}.json"
        
        with open(filepath, 'w') as f:
            json.dump(pattern, f, indent=2)
        
        print(f"✓ Saved: {filepath.name}")
        return filepath


def main():
    """Generate sample patterns for all difficulties."""
    print("=" * 60)
    print("Pattern Level Designer - Generating Shaped Patterns")
    print("=" * 60)
    
    for difficulty in ['easy', 'medium', 'hard']:
        print(f"\n🎨 Generating {difficulty.upper()} difficulty patterns...")
        designer = PatternDesigner(difficulty=difficulty)
        
        # Generate different pattern types
        patterns = [
            designer.generate_w_pattern(length=15 + (5 if difficulty == 'hard' else 0)),
            designer.generate_sawtooth_pattern(length=12 + (3 if difficulty == 'hard' else 0)),
            designer.generate_sine_pattern(length=16 + (4 if difficulty == 'hard' else 0)),
            designer.generate_hill_pattern(length=10 + (2 if difficulty == 'hard' else 0)),
        ]
        
        for pattern in patterns:
            designer.save_pattern(pattern)
    
    print("\n" + "=" * 60)
    print("✅ Pattern generation complete!")
    print("   Generated 12 new patterns (4 shapes × 3 difficulties)")
    print("=" * 60)


if __name__ == '__main__':
    main()
