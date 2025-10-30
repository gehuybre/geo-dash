"""
Player class with support for custom sprites.
"""

import pygame
import math
from config import *


class Player:
    """Player character with physics and rendering."""
    
    def __init__(self, x, y):
        # Import asset_manager here to avoid circular import issues
        from assets import asset_manager
        
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.velocity_y = 0
        self.is_jumping = False
        self.on_ground = False
        self.rotation = 0
        self.has_double_jump = False  # Can use double jump
        self.jumps_used = 0  # Track number of jumps (0, 1, or 2)
        
        # Try to load custom sprite
        self.custom_sprite = asset_manager.get_player_sprite()
        
    def jump(self):
        """Make the player jump (supports double jump)."""
        # First jump: from ground
        if self.on_ground and self.jumps_used == 0:
            self.velocity_y = JUMP_POWER
            self.is_jumping = True
            self.on_ground = False
            self.jumps_used = 1
            self.has_double_jump = True
        # Second jump: in mid-air (double jump)
        elif self.has_double_jump and self.jumps_used == 1 and not self.on_ground:
            self.velocity_y = JUMP_POWER * 0.9  # Slightly weaker second jump
            self.jumps_used = 2
            self.has_double_jump = False
    
    def update(self):
        """Update player physics and position."""
        # Don't reset on_ground here - let collision detection handle it
        # This prevents flickering when standing on obstacles
        
        # Apply gravity
        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        
        # Check ground collision
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.velocity_y = 0
            self.is_jumping = False
            self.on_ground = True
            self.jumps_used = 0  # Reset jumps when on ground
            self.has_double_jump = False
            self.rotation = 0
        elif self.velocity_y > 0:
            # If falling and not on ground level, assume in air (will be corrected by collision)
            # Only set to False if actually falling, not if standing on obstacle
            if not self.on_ground:
                self.rotation = (self.rotation + 5) % 360
        else:
            # Rotate while jumping/rising
            self.rotation = (self.rotation + 5) % 360
    
    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        """Draw the player using custom sprite or procedural generation."""
        if self.custom_sprite:
            self._draw_custom_sprite(screen)
        else:
            self._draw_procedural(screen)
    
    def _draw_custom_sprite(self, screen):
        """Draw using custom loaded sprite."""
        sprite = self.custom_sprite
        
        # Rotate if jumping
        if not self.on_ground:
            sprite = pygame.transform.rotate(sprite, self.rotation)
            rect = sprite.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            screen.blit(sprite, rect)
        else:
            screen.blit(sprite, (self.x, self.y))
    
    def _draw_procedural(self, screen):
        """Draw using procedural generation (cute cube with face)."""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw main body (pink square)
        pygame.draw.rect(surface, PLAYER_PINK, (0, 0, self.width, self.height), border_radius=8)
        pygame.draw.rect(surface, PLAYER_OUTLINE, (0, 0, self.width, self.height), 3, border_radius=8)
        
        # Draw cute face
        # Eyes
        eye_size = 6
        pygame.draw.circle(surface, BLACK, (12, 15), eye_size)
        pygame.draw.circle(surface, BLACK, (28, 15), eye_size)
        pygame.draw.circle(surface, WHITE, (14, 13), 2)
        pygame.draw.circle(surface, WHITE, (30, 13), 2)
        
        # Cute smile
        pygame.draw.arc(surface, BLACK, (10, 15, 20, 15), 0, math.pi, 2)
        
        # Blush
        pygame.draw.circle(surface, (255, 160, 180), (5, 20), 3)
        pygame.draw.circle(surface, (255, 160, 180), (35, 20), 3)
        
        # Rotate if jumping
        if not self.on_ground:
            surface = pygame.transform.rotate(surface, self.rotation)
            rect = surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            screen.blit(surface, rect)
        else:
            screen.blit(surface, (self.x, self.y))
