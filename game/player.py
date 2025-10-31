"""
Player class with support for custom sprites.
"""

import pygame
import math
import os
from .config import *


def _load_font(size, bold=False):
    """Helper to load custom font or fallback to system font."""
    try:
        font_path = FONT_BOLD if bold and os.path.exists(FONT_BOLD) else FONT_REGULAR
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
        else:
            return pygame.font.SysFont('Comic Sans MS', size, bold=bold)
    except:
        return pygame.font.SysFont('Comic Sans MS', size, bold=bold)


class ScorePopup:
    """Floating score text that appears when landing on platforms."""
    
    def __init__(self, x, y, points):
        self.x = x
        self.y = y
        self.points = points
        self.lifetime = 60  # Frames to live
        self.age = 0
        self.velocity_y = -2  # Float upward
    
    def update(self):
        """Update popup position and age."""
        self.age += 1
        self.y += self.velocity_y
        self.velocity_y += 0.05  # Slight gravity
        return self.age < self.lifetime
    
    def draw(self, screen):
        """Draw the floating score text."""
        # Fade out over time
        alpha = int(255 * (1 - self.age / self.lifetime))
        
        # Create text surface
        text = f"+{self.points}"
        font_size = 36 if self.points > 5 else 24
        
        # Try to use pygame font
        try:
            font = _load_font(font_size, bold=True)
            text_surface = font.render(text, True, YELLOW)
            text_surface.set_alpha(alpha)
            
            # Draw shadow
            shadow = font.render(text, True, BLACK)
            shadow.set_alpha(alpha // 2)
            screen.blit(shadow, (self.x + 2, self.y + 2))
            
            # Draw main text
            screen.blit(text_surface, (self.x, self.y))
        except:
            # Fallback to simple rendering
            pass


class Player:
    """Player character with physics and rendering."""
    
    def __init__(self, x, y):
        # Import asset_manager here to avoid circular import issues
        from .assets import asset_manager
        
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
        
        # Landing bonus and combo system
        self.just_landed = False  # Flag for landing bonus
        self.combo_streak = 0  # Number of consecutive platform landings without touching ground
        self.last_landed_on_ground = True  # Track if last landing was on ground
        
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
        
        # Reset just_landed flag (will be set by collision if landing)
        self.just_landed = False
        
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
            
            # Reset combo when landing on ground
            if not self.last_landed_on_ground:
                self.combo_streak = 0
                self.last_landed_on_ground = True
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
