"""
Kivy Obstacle Widget
Ported from Pygame version to use Kivy graphics.
"""

from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty, BooleanProperty
from kivy.core.image import Image as CoreImage
import os
import random

from .config import *


class Obstacle(Widget):
    """Single obstacle widget."""
    
    def __init__(self, x, height, width=30, y_offset=0, is_killzone=False, hazard_type="lava", **kwargs):
        super(Obstacle, self).__init__(**kwargs)
        
        self.x = x
        self.is_killzone = is_killzone
        self.hazard_type = hazard_type
        self.width = width
        self.height = height
        self.y_offset = y_offset
        
        if is_killzone:
            # Killzone fills from ground to bottom
            self.y = 0
            self.height = GROUND_Y + PLAYER_SIZE - 5
        else:
            # Normal obstacle
            self.y = GROUND_Y + y_offset
        
        self.size = (self.width, self.height)
        self.pos = (self.x, self.y)
        self.passed = False
        
        # Visual effects
        self.landing_squish = 0
        self.landing_glow = 0
        self.landing_blink = 0
        
        # Set up graphics
        with self.canvas:
            if self.is_killzone:
                # Red hazard warning pattern
                Color(1, 0, 0, 0.7)
                self.rect = Rectangle(pos=self.pos, size=self.size)
            else:
                # Purple obstacle
                Color(*OBSTACLE_PURPLE)
                self.rect = Rectangle(pos=self.pos, size=self.size)
    
    def update(self, dt):
        """Move obstacle left and update visual effects."""
        self.x -= PLAYER_SPEED
        self.pos = (self.x, self.y)
        self.rect.pos = self.pos
        
        # Decay landing effects
        if self.landing_squish > 0:
            self.landing_squish *= 0.85
        if self.landing_glow > 0:
            self.landing_glow *= 0.9
        if self.landing_blink > 0:
            self.landing_blink -= 1
    
    def trigger_landing_effect(self):
        """Trigger visual landing effects when player lands on this obstacle."""
        self.landing_squish = 0.25
        self.landing_glow = 180
        self.landing_blink = 6
    
    def get_rect(self):
        """Get collision rectangle."""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'left': self.x,
            'right': self.x + self.width,
            'top': self.y + self.height,
            'bottom': self.y
        }


class ObstacleGenerator:
    """Generates obstacles using pattern system."""
    
    def __init__(self, difficulty="medium"):
        from managers.pattern_manager import PatternManager
        from managers.bar_type_manager import BarTypeManager
        
        self.obstacles = []
        self.pattern_manager = PatternManager(difficulty=difficulty)
        self.bar_type_manager = BarTypeManager()
        self.difficulty = difficulty
        self.base_x = SCREEN_WIDTH
        
    def generate_obstacle(self):
        """Generate next obstacle using pattern system."""
        # Get random pattern (pattern manager already filtered by difficulty)
        pattern = self.pattern_manager.get_random_pattern()
        
        if not pattern:
            return None
        
        # Generate all obstacles from pattern
        for obstacle_def in pattern['obstacles']:
            bar_type = obstacle_def.get('bar_type', 'bar-3-2')
            gap_type = obstacle_def.get('gap_type', 'gap-1.5')
            is_killzone = obstacle_def.get('is_killzone', False)
            hazard_type = obstacle_def.get('hazard_type', 'lava')
            
            # Get bar dimensions (returns tuple: width, height, y_offset)
            width, height, y_offset = self.bar_type_manager.get_bar_dimensions(bar_type)
            
            # Create obstacle
            obstacle = Obstacle(
                self.base_x,
                height,
                width,
                y_offset,
                is_killzone,
                hazard_type
            )
            self.obstacles.append(obstacle)
            
            # Calculate gap using bar_type_manager
            gap = self.bar_type_manager.get_gap_distance(gap_type)
            gap_hazard = self.bar_type_manager.get_gap_hazard(gap_type)
            
            # TODO: Handle gap hazards (lava/laser between obstacles)
            # For now, just use the gap distance
            
            self.base_x += width + (gap if gap else 150)
    
    def update(self, dt):
        """Update all obstacles."""
        for obstacle in self.obstacles[:]:
            obstacle.update(dt)
            if obstacle.x + obstacle.width < 0:
                self.obstacles.remove(obstacle)
        
        # Generate new obstacles when needed
        if not self.obstacles or self.obstacles[-1].x < SCREEN_WIDTH - 200:
            self.generate_obstacle()
    
    def check_collision(self, player):
        """Check collision between player and obstacles."""
        player_rect = player.get_rect()
        
        for obstacle in self.obstacles:
            if self._rects_collide(player_rect, obstacle.get_rect()):
                if obstacle.is_killzone:
                    return True  # Game over
                else:
                    # Check if landing on top
                    if player.velocity_y < 0 and player_rect['bottom'] <= obstacle.get_rect()['top']:
                        landed = player.land_on_obstacle(obstacle.y + obstacle.height, obstacle)
                        if landed:
                            obstacle.trigger_landing_effect()
                    else:
                        return True  # Side collision - game over
        
        return False
    
    def _rects_collide(self, rect1, rect2):
        """Check if two rectangles collide."""
        return (rect1['right'] > rect2['left'] and
                rect1['left'] < rect2['right'] and
                rect1['top'] > rect2['bottom'] and
                rect1['bottom'] < rect2['top'])
