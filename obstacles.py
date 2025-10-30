"""
Obstacle classes and generation system with custom asset support and pattern loading.
"""

import pygame
import random
from config import *
from core.physics import physics
from managers.pattern_manager import PatternManager


class Obstacle:
    """Single obstacle with custom sprite support."""
    
    def __init__(self, x, height, width=30):
        # Import asset_manager here to avoid circular import issues
        from assets import asset_manager
        
        self.x = x
        self.height = height
        self.width = width
        self.y = GROUND_Y + PLAYER_SIZE - height
        self.passed = False
        
        # Try to load custom sprite
        self.custom_sprite = asset_manager.get_obstacle_sprite(self.width, self.height)
    
    def update(self):
        """Move obstacle left."""
        self.x -= PLAYER_SPEED
    
    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        """Draw obstacle using custom sprite or procedural generation."""
        if self.custom_sprite:
            screen.blit(self.custom_sprite, (self.x, self.y))
        else:
            self._draw_procedural(screen)
    
    def _draw_procedural(self, screen):
        """Draw using procedural generation (gradient purple block)."""
        # Draw cute obstacle with gradient effect
        for i in range(self.height):
            color_intensity = 216 - (i * 20 // self.height)
            color = (color_intensity, 191 - (i * 10 // self.height), 216)
            pygame.draw.rect(screen, color, (self.x, self.y + i, self.width, 1))
        
        # Outline
        pygame.draw.rect(screen, OBSTACLE_DARK, (self.x, self.y, self.width, self.height), 2, border_radius=5)
        
        # Add sparkles
        if random.random() < 0.1:
            star_x = self.x + random.randint(5, self.width - 5)
            star_y = self.y + random.randint(5, self.height - 5)
            pygame.draw.circle(screen, YELLOW, (star_x, star_y), 2)


class ObstacleGenerator:
    """Generates obstacles that are always jumpable, using patterns and random generation."""
    
    def __init__(self):
        self.obstacles = []
        self.pattern_manager = PatternManager()
        self.current_pattern_name = None  # Track current pattern for debugging

        
    def generate_obstacle(self):
        """Generate a new obstacle using patterns or random generation."""
        # Check if we should spawn a new obstacle
        if len(self.obstacles) == 0:
            should_spawn = True
            spawn_x = SCREEN_WIDTH
        else:
            # Find the rightmost obstacle
            rightmost = self.obstacles[-1]
            right_edge = rightmost.x + rightmost.width
            
            # Random gap for random obstacles
            min_spawn_distance = random.randint(MIN_OBSTACLE_GAP, MAX_OBSTACLE_GAP)
            should_spawn = right_edge < SCREEN_WIDTH - min_spawn_distance
            spawn_x = SCREEN_WIDTH
        
        if should_spawn:
            # Use patterns 100% of the time (no random generation)
            pattern = self.pattern_manager.get_random_pattern()
            if pattern:
                # Start a new pattern - spawn ALL obstacles at once
                self.current_pattern_name = pattern.get('name', 'Unknown Pattern')
                
                # Calculate initial spawn position
                if len(self.obstacles) > 0:
                    rightmost = self.obstacles[-1]
                    base_x = rightmost.x + rightmost.width + random.randint(MIN_OBSTACLE_GAP, MAX_OBSTACLE_GAP)
                else:
                    base_x = SCREEN_WIDTH
                
                # Spawn all pattern obstacles at once with correct relative positions
                current_x = base_x
                for pattern_obstacle in pattern['obstacles']:
                    height = min(pattern_obstacle['height'], physics.max_obstacle_height)
                    width = pattern_obstacle.get('width', 30)
                    
                    obstacle = Obstacle(current_x, height, width)
                    self.obstacles.append(obstacle)
                    
                    # Move x position forward for next obstacle in pattern
                    current_x += width + pattern_obstacle.get('gap_after', 0)
    
    def update(self):
        """Update all obstacles and generate new ones."""
        self.generate_obstacle()
        
        # Update and remove off-screen obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update()
            if obstacle.x < -obstacle.width:
                self.obstacles.remove(obstacle)
    
    def draw(self, screen):
        """Draw all obstacles."""
        for obstacle in self.obstacles:
            obstacle.draw(screen)
    
    def check_collision(self, player):
        """Check if player collides with sides of obstacles (not top - can land on them)."""
        player_rect = player.get_rect()
        player_is_on_obstacle = False
        
        for obstacle in self.obstacles:
            obstacle_rect = obstacle.get_rect()
            
            # Check if there's any overlap
            if player_rect.colliderect(obstacle_rect):
                # Get player's bottom and sides
                player_bottom = player_rect.bottom
                player_top = player_rect.top
                player_left = player_rect.left
                player_right = player_rect.right
                
                obstacle_top = obstacle_rect.top
                obstacle_left = obstacle_rect.left
                obstacle_right = obstacle_rect.right
                
                # Calculate overlap amounts
                overlap_bottom = player_bottom - obstacle_top
                overlap_top = obstacle_rect.bottom - player_top
                overlap_left = player_right - obstacle_left
                overlap_right = obstacle_right - player_left
                
                # If player is descending and mostly above the obstacle, it's a landing
                # Larger safe zone (20 pixels) for more forgiving landings, especially on wide blocks
                if player.velocity_y >= 0 and overlap_bottom <= 20:
                    # Landing on top - safe!
                    player.y = obstacle_top - player.height
                    player.velocity_y = 0
                    player.on_ground = True
                    player.is_jumping = False
                    player.jumps_used = 0  # Reset double jump on landing
                    player.has_double_jump = False
                    player.rotation = 0  # Stop rotation when on obstacle
                    player_is_on_obstacle = True
                    # No collision, just landing
                    continue
                else:
                    # Hit the side, bottom, or deep inside obstacle - that's a collision
                    return True
        
        # Also check if player is standing on an obstacle (within 1 pixel above it)
        # This helps maintain on_ground state even when not actively colliding
        if not player_is_on_obstacle:
            for obstacle in self.obstacles:
                obstacle_rect = obstacle.get_rect()
                # Check if player is directly above this obstacle
                if (player_rect.left < obstacle_rect.right and 
                    player_rect.right > obstacle_rect.left and
                    abs((player.y + player.height) - obstacle_rect.top) <= 2):
                    player_is_on_obstacle = True
                    player.on_ground = True
                    break
        
        # If player is not on ground level and not on any obstacle, they're in the air
        if not player_is_on_obstacle and player.y < GROUND_Y - 1:
            player.on_ground = False
        
        return False
    
    def get_score(self, player):
        """Get score for obstacles passed."""
        score = 0
        player_rect = player.get_rect()
        for obstacle in self.obstacles:
            if not obstacle.passed and obstacle.x + obstacle.width < player_rect.x:
                obstacle.passed = True
                score += 1
        return score
    
    def reset(self):
        """Reset obstacle generator."""
        self.obstacles = []
        self.next_obstacle_x = SCREEN_WIDTH + 200
