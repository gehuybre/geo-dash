"""
Camera system for Celeste Runner - auto-scrolling with acceleration.
"""

from .config import *


class Camera:
    """Auto-scrolling camera that moves right and can accelerate."""
    
    def __init__(self):
        """Initialize camera at starting position."""
        self.x = 0  # Camera X offset (how far right we've scrolled)
        self.speed = AUTO_SCROLL_SPEED  # Current scroll speed
        self.target_speed = AUTO_SCROLL_SPEED  # Target speed for smooth acceleration
        
        # Track distance for score
        self.total_distance = 0
        
        print(f"📹 Camera initialized (speed: {self.speed})")
    
    def update(self):
        """Update camera position - scrolls automatically to the right."""
        # Smoothly accelerate towards target speed
        self.speed = self.speed * 0.95 + self.target_speed * 0.05
        
        # Move camera right
        self.x += self.speed
        self.total_distance += self.speed
        
        # Gradually increase target speed over time
        if self.target_speed < MAX_AUTO_SCROLL_SPEED:
            self.target_speed += AUTO_SCROLL_ACCELERATION
    
    def get_score(self):
        """Get current score based on distance traveled."""
        # 1 point per 100 pixels
        return int(self.total_distance / 100)
    
    def is_off_screen_left(self, x):
        """
        Check if an X position is off the left side of screen.
        
        Args:
            x: World X position to check
            
        Returns:
            bool: True if position is off-screen to the left
        """
        screen_x = x - self.x
        return screen_x < -50  # Small margin
    
    def world_to_screen(self, world_x, world_y=None):
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_x: World X position
            world_y: World Y position (optional, unchanged by camera)
            
        Returns:
            tuple: (screen_x, screen_y) if world_y provided, else just screen_x
        """
        screen_x = world_x - self.x
        if world_y is not None:
            return (screen_x, world_y)
        return screen_x
    
    def screen_to_world(self, screen_x, screen_y=None):
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_x: Screen X position
            screen_y: Screen Y position (optional, unchanged by camera)
            
        Returns:
            tuple: (world_x, world_y) if screen_y provided, else just world_x
        """
        world_x = screen_x + self.x
        if screen_y is not None:
            return (world_x, screen_y)
        return world_x
    
    def reset(self):
        """Reset camera to starting position and speed."""
        self.x = 0
        self.speed = AUTO_SCROLL_SPEED
        self.target_speed = AUTO_SCROLL_SPEED
        self.total_distance = 0
        print("📹 Camera reset")
