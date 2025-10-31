"""
Physics calculations for jump mechanics and obstacle validation.
"""

from game.config import GRAVITY, JUMP_POWER, PLAYER_SPEED, MIN_OBSTACLE_HEIGHT, GROUND_Y


class PhysicsCalculator:
    """Calculates jump physics for obstacle generation and validation."""
    
    def __init__(self):
        # Calculate max jumpable height based on jump physics
        # Maximum height = (jump_power^2) / (2 * gravity)
        max_jump_height = (abs(JUMP_POWER) ** 2) / (2 * GRAVITY)
        self.max_obstacle_height = int(max_jump_height * 0.7)  # 70% of max height for safety
        self.min_obstacle_height = MIN_OBSTACLE_HEIGHT
        
        # Calculate horizontal jump distance (time in air * horizontal speed)
        # Time to reach max height: time = jump_power / gravity
        time_to_peak = abs(JUMP_POWER) / GRAVITY
        total_air_time = time_to_peak * 2  # Up and down
        self.max_jump_distance = int(total_air_time * PLAYER_SPEED)
        
        # Minimum gap needed to land safely (accounting for jump recovery time)
        # Player needs a few frames to land and jump again
        self.min_safe_gap = int(PLAYER_SPEED * 10)  # 10 frames to recover
        
        print(f"Physics: Max jump height={self.max_obstacle_height}px, "
              f"Max jump distance={self.max_jump_distance}px, "
              f"Min safe gap={self.min_safe_gap}px")
    
    def can_jump_over(self, height, gap):
        """Check if a jump can clear an obstacle of given height and gap."""
        if height > self.max_obstacle_height:
            return False
        if gap > self.max_jump_distance:
            return False
        return True
    
    def can_land_safely(self, gap, platform_width):
        """Check if landing on a platform is safe given the gap and platform width."""
        # Very wide platforms are always safe
        if platform_width >= 60:
            return True
        # Regular platforms need minimum safe gap
        return gap >= self.min_safe_gap
    
    def can_climb(self, height_diff):
        """Check if player can jump UP onto a stacked obstacle."""
        # Can jump up to 60% of max height from current position
        return height_diff <= self.max_obstacle_height * 0.6
    
    def can_forward_jump_up(self, vertical_diff):
        """Check if player can jump UP while jumping forward (gap jump)."""
        # When jumping forward, we can't jump as high
        max_forward_jump_height = self.max_obstacle_height * 0.4
        return abs(vertical_diff) <= max_forward_jump_height


# Global physics calculator instance
physics = PhysicsCalculator()
