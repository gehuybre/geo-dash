"""
Player class for Celeste Runner - wall-jumping mechanics.
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


class Player:
    """Player character with wall-jumping physics."""
    
    # Player states
    STATE_FALLING = "falling"
    STATE_WALL_SLIDING = "wall_sliding"
    STATE_WALL_JUMPING = "wall_jumping"
    
    def __init__(self, x, y, character_name=None):
        # Import asset_manager here to avoid circular import issues
        from .assets import asset_manager
        
        # Position and dimensions
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        
        # Velocity
        self.velocity_x = 0
        self.velocity_y = 0
        
        # State tracking
        self.state = self.STATE_FALLING
        self.wall_side = None  # 'left' or 'right' - which side of wall player is touching
        self.on_ground = False  # Dead if True (floor is lethal)
        
        # Wall mechanics
        self.wall_cling_timer = 0  # Frames player has clung to wall without sliding
        self.wall_coyote_timer = 0  # Frames since leaving wall (can still wall jump)
        self.can_wall_jump = False  # Can execute wall jump this frame
        
        # Jump buffering - remember input for a few frames
        self.jump_buffer = 0  # Frames to remember jump input
        
        # Visual
        self.rotation = 0  # Rotation angle for visual flair
        self.squish_x = 1.0  # Horizontal squish (for juice)
        self.squish_y = 1.0  # Vertical squish (for juice)
        
        # Character sprite
        self.character_name = character_name
        self.custom_sprite = asset_manager.get_player_sprite(character_name)
        
        # Collision mask for pixel-perfect collision
        self.collision_mask = None
        if self.custom_sprite:
            try:
                self.collision_mask = pygame.mask.from_surface(self.custom_sprite)
            except:
                self.collision_mask = None
        
        # Particles and effects
        self.wall_slide_particles = []  # Particles while sliding on wall
        
        print(f"🧗 Player initialized at ({x}, {y})")
    
    def set_character(self, character_name):
        """Change player character sprite."""
        from .assets import asset_manager
        self.character_name = character_name
        self.custom_sprite = asset_manager.get_player_sprite(character_name)
        
        if self.custom_sprite:
            try:
                self.collision_mask = pygame.mask.from_surface(self.custom_sprite)
            except:
                self.collision_mask = None
    
    def jump(self):
        """Execute context-aware jump (wall jump or buffered jump)."""
        # Buffer the jump input
        self.jump_buffer = 5  # Remember for 5 frames
        
        # Try to execute jump immediately
        self._try_execute_jump()
    
    def _try_execute_jump(self):
        """Try to execute a jump based on current state."""
        # Wall jump - highest priority
        if self.can_wall_jump and self.wall_side:
            from core.physics import physics
            vx, vy = physics.calculate_wall_jump_trajectory(self.wall_side)
            self.velocity_x = vx
            self.velocity_y = vy
            self.state = self.STATE_WALL_JUMPING
            self.wall_coyote_timer = 0  # Use up coyote time
            self.jump_buffer = 0  # Use up buffer
            self.can_wall_jump = False
            
            # Visual feedback
            self.squish_x = 1.3
            self.squish_y = 0.7
            
            print(f"🚀 Wall jump! Side: {self.wall_side}, vx: {vx}, vy: {vy}")
            return True
        
        # Wall coyote jump - can still jump shortly after leaving wall
        elif self.wall_coyote_timer > 0 and self.wall_coyote_timer <= WALL_JUMP_COYOTE_TIME:
            from core.physics import physics
            # Use the last wall side we were on
            vx, vy = physics.calculate_wall_jump_trajectory(self.wall_side)
            self.velocity_x = vx
            self.velocity_y = vy
            self.state = self.STATE_WALL_JUMPING
            self.wall_coyote_timer = 0
            self.jump_buffer = 0
            
            # Visual feedback
            self.squish_x = 1.3
            self.squish_y = 0.7
            
            print(f"⏰ Coyote wall jump! Side: {self.wall_side}")
            return True
        
        return False
    
    def update(self, camera_x):
        """
        Update player physics and state.
        
        Args:
            camera_x: Current camera X position (for death check)
        """
        # Update jump buffer
        if self.jump_buffer > 0:
            self.jump_buffer -= 1
            # Try to use buffered jump
            if self.can_wall_jump:
                self._try_execute_jump()
        
        # Update wall coyote timer
        if self.state != self.STATE_WALL_SLIDING:
            self.wall_coyote_timer += 1
            if self.wall_coyote_timer > WALL_JUMP_COYOTE_TIME:
                self.wall_coyote_timer = WALL_JUMP_COYOTE_TIME + 1  # Cap it
        
        # Apply gravity (different when wall sliding)
        if self.state == self.STATE_WALL_SLIDING:
            # Slower slide down wall
            self.velocity_y += WALL_SLIDE_GRAVITY
            
            # Update wall cling timer
            self.wall_cling_timer += 1
            if self.wall_cling_timer > WALL_CLING_TIME:
                # Start sliding after cling time expires
                pass  # Gravity already applied above
            
            # Can wall jump while sliding
            self.can_wall_jump = True
        else:
            # Normal gravity when falling/jumping
            self.velocity_y += GRAVITY
            self.can_wall_jump = False
        
        # Apply air resistance to horizontal velocity
        if self.state == self.STATE_WALL_JUMPING or self.state == self.STATE_FALLING:
            self.velocity_x *= AIR_RESISTANCE
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Check floor collision (death)
        if self.y + self.height >= GROUND_Y:
            self.on_ground = True
            # Don't stop player here - game will handle death
        
        # Update visual effects
        self._update_visual_effects()
        
        # Update rotation based on state
        if self.state == self.STATE_WALL_SLIDING:
            # No rotation while sliding
            if self.wall_side == 'left':
                self.rotation = -10  # Lean into wall
            else:
                self.rotation = 10
        elif self.state == self.STATE_WALL_JUMPING:
            # Rotate during jump arc
            self.rotation += 8
        else:
            # Free fall rotation
            if self.velocity_y > 0:
                self.rotation += 5
    
    def _update_visual_effects(self):
        """Update squish and other visual effects."""
        # Lerp squish back to normal
        self.squish_x = self.squish_x * 0.8 + 1.0 * 0.2
        self.squish_y = self.squish_y * 0.8 + 1.0 * 0.2
    
    def enter_wall_slide(self, wall_side):
        """
        Enter wall sliding state.
        
        Args:
            wall_side: 'left' or 'right'
        """
        if self.state != self.STATE_WALL_SLIDING or self.wall_side != wall_side:
            print(f"🧗 Entering wall slide on {wall_side} side")
            self.state = self.STATE_WALL_SLIDING
            self.wall_side = wall_side
            self.wall_cling_timer = 0
            self.wall_coyote_timer = 0
            self.can_wall_jump = True
            self.velocity_y = 0  # Stop vertical momentum when grabbing wall
            
            # Visual feedback
            self.squish_x = 0.8
            self.squish_y = 1.2
    
    def exit_wall_slide(self):
        """Exit wall sliding state."""
        if self.state == self.STATE_WALL_SLIDING:
            print(f"👋 Exiting wall slide")
            self.state = self.STATE_FALLING
            # Keep wall_side for coyote time
            self.wall_coyote_timer = 1  # Start coyote time
            self.can_wall_jump = False
    
    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def draw(self, screen, camera_x):
        """
        Draw the player.
        
        Args:
            screen: Pygame screen surface
            camera_x: Camera X offset
        """
        # Calculate screen position (camera-relative)
        screen_x = self.x - camera_x
        screen_y = self.y
        
        if self.custom_sprite:
            self._draw_custom_sprite(screen, screen_x, screen_y)
        else:
            self._draw_procedural(screen, screen_x, screen_y)
        
        # Draw debug info if enabled
        if SHOW_DEBUG_INFO:
            self._draw_debug_info(screen, screen_x, screen_y)
    
    def _draw_custom_sprite(self, screen, x, y):
        """Draw using custom loaded sprite."""
        sprite = self.custom_sprite
        
        # Apply squish
        width = int(self.width * self.squish_x)
        height = int(self.height * self.squish_y)
        sprite = pygame.transform.scale(sprite, (width, height))
        
        # Apply rotation
        if self.rotation != 0:
            sprite = pygame.transform.rotate(sprite, self.rotation)
        
        rect = sprite.get_rect(center=(x + self.width // 2, y + self.height // 2))
        screen.blit(sprite, rect)
    
    def _draw_procedural(self, screen, x, y):
        """Draw using procedural generation (cute cube with face)."""
        # Apply squish to dimensions
        width = int(self.width * self.squish_x)
        height = int(self.height * self.squish_y)
        
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw main body (pink square)
        pygame.draw.rect(surface, PLAYER_PINK, (0, 0, width, height), border_radius=8)
        pygame.draw.rect(surface, PLAYER_OUTLINE, (0, 0, width, height), 3, border_radius=8)
        
        # Draw face (scale to squished dimensions)
        # Eyes
        eye_size = int(6 * min(self.squish_x, self.squish_y))
        eye_y = int(15 * self.squish_y)
        pygame.draw.circle(surface, BLACK, (int(12 * self.squish_x), eye_y), eye_size)
        pygame.draw.circle(surface, BLACK, (int(28 * self.squish_x), eye_y), eye_size)
        
        # Highlight
        pygame.draw.circle(surface, WHITE, (int(14 * self.squish_x), eye_y - 2), max(2, eye_size // 3))
        pygame.draw.circle(surface, WHITE, (int(30 * self.squish_x), eye_y - 2), max(2, eye_size // 3))
        
        # Smile (changes based on state)
        if self.state == self.STATE_WALL_SLIDING:
            # Determined face while sliding
            pygame.draw.line(surface, BLACK, (int(10 * self.squish_x), int(25 * self.squish_y)),
                           (int(30 * self.squish_x), int(25 * self.squish_y)), 2)
        else:
            # Happy smile
            pygame.draw.arc(surface, BLACK, (int(10 * self.squish_x), int(15 * self.squish_y),
                                            int(20 * self.squish_x), int(15 * self.squish_y)),
                          0, math.pi, 2)
        
        # Rotate if needed
        if self.rotation != 0:
            surface = pygame.transform.rotate(surface, self.rotation)
        
        rect = surface.get_rect(center=(x + self.width // 2, y + self.height // 2))
        screen.blit(surface, rect)
    
    def _draw_debug_info(self, screen, x, y):
        """Draw debug information."""
        try:
            font = _load_font(16)
            debug_text = f"State: {self.state} | Wall: {self.wall_side} | VY: {self.velocity_y:.1f}"
            text_surface = font.render(debug_text, True, BLACK)
            screen.blit(text_surface, (x, y - 20))
        except:
            pass
