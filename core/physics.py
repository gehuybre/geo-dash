"""
Physics calculations for wall-jump mechanics and level validation.
Celeste Runner physics: wall sliding, wall jumping, and auto-scroll momentum.
"""

from game.config import (
    GRAVITY, WALL_SLIDE_GRAVITY, WALL_JUMP_X_FORCE, WALL_JUMP_Y_FORCE,
    AUTO_SCROLL_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_Y
)
import math


class PhysicsCalculator:
    """Calculates wall-jump physics for level generation and validation."""
    
    def __init__(self):
        # Wall jump arc calculations
        # Maximum height when wall jumping = (wall_jump_y^2) / (2 * gravity)
        self.max_wall_jump_height = int((abs(WALL_JUMP_Y_FORCE) ** 2) / (2 * GRAVITY))
        
        # Horizontal distance during wall jump
        # Calculate time in air and multiply by horizontal velocity
        time_to_peak = abs(WALL_JUMP_Y_FORCE) / GRAVITY
        total_air_time = time_to_peak * 2
        self.max_wall_jump_distance = int(total_air_time * WALL_JUMP_X_FORCE)
        
        # Minimum wall-to-wall gap (accounting for reaction time and auto-scroll)
        # Player needs to react and execute wall jump before being scrolled off screen
        self.min_wall_gap = 80  # Minimum gap between walls
        self.max_wall_gap = self.max_wall_jump_distance * 0.8  # 80% of max for safety
        
        # Wall slide calculations
        # Time to slide down a wall from top to bottom
        # Using v = v0 + at, and d = v0*t + 0.5*a*t^2
        # Starting from rest (v0=0), distance = 0.5 * wall_slide_gravity * t^2
        
        # Maximum safe wall height for sliding
        # If wall is too tall, player might slide too long without input
        self.max_wall_height = 400  # Reasonable wall height
        self.min_wall_height = 60   # Minimum to grab onto
        
        # Calculate how long it takes to slide down max wall
        if WALL_SLIDE_GRAVITY > 0:
            slide_time = math.sqrt((2 * self.max_wall_height) / WALL_SLIDE_GRAVITY)
        else:
            slide_time = float('inf')
        self.max_slide_time_frames = int(slide_time)
        
        print(f"🧗 Celeste Runner Physics Initialized:")
        print(f"  Max wall jump height: {self.max_wall_jump_height}px")
        print(f"  Max wall jump distance: {self.max_wall_jump_distance}px")
        print(f"  Wall gap range: {self.min_wall_gap}px - {self.max_wall_gap}px")
        print(f"  Wall height range: {self.min_wall_height}px - {self.max_wall_height}px")
        print(f"  Auto-scroll speed: {AUTO_SCROLL_SPEED}px/frame")
    
    def can_reach_wall(self, gap_distance, height_difference=0):
        """
        Check if player can wall jump across a gap to reach next wall.
        
        Args:
            gap_distance: Horizontal distance between walls
            height_difference: Vertical offset (positive = next wall is higher)
        
        Returns:
            bool: True if gap is traversable via wall jump
        """
        if gap_distance < self.min_wall_gap:
            return False  # Too close, might cause issues
        if gap_distance > self.max_wall_gap:
            return False  # Too far to reach
        
        # Check vertical reach
        if abs(height_difference) > self.max_wall_jump_height * 0.7:
            return False  # Vertical difference too large
        
        return True
    
    def calculate_wall_jump_trajectory(self, wall_side):
        """
        Calculate initial velocity vector for wall jump.
        
        Args:
            wall_side: 'left' or 'right' - which side of wall player is on
        
        Returns:
            tuple: (velocity_x, velocity_y)
        """
        if wall_side == 'left':
            # Jumping off left wall - launch to the right
            vx = WALL_JUMP_X_FORCE
        else:
            # Jumping off right wall - launch to the left
            vx = -WALL_JUMP_X_FORCE
        
        vy = WALL_JUMP_Y_FORCE  # Always jump upward
        
        return (vx, vy)
    
    def is_valid_wall_layout(self, walls):
        """
        Validate a sequence of walls can be traversed via wall jumps.
        
        Args:
            walls: List of wall dictionaries with 'x', 'y', 'height' keys
        
        Returns:
            bool: True if layout is completable
        """
        if len(walls) < 2:
            return True  # Single wall or empty is valid
        
        for i in range(len(walls) - 1):
            current_wall = walls[i]
            next_wall = walls[i + 1]
            
            # Calculate gap and height difference
            gap = next_wall['x'] - (current_wall['x'] + 30)  # Assuming 30px wall width
            height_diff = next_wall.get('y', 0) - current_wall.get('y', 0)
            
            if not self.can_reach_wall(gap, height_diff):
                print(f"❌ Invalid wall gap: {gap}px (height diff: {height_diff}px)")
                return False
        
        return True
    
    def calculate_death_zone_y(self):
        """Calculate Y position where floor kills player."""
        return GROUND_Y
    
    def calculate_screen_edge_death_x(self, camera_x):
        """Calculate X position where left screen edge kills player."""
        return camera_x - 50  # Small margin before instant death


# Global physics calculator instance
physics = PhysicsCalculator()
