"""
Obstacle classes and generation system with custom asset support and pattern loading.
"""

import pygame
import random
from .config import *
from core.physics import physics
from managers.pattern_manager import PatternManager


class Obstacle:
    """Single obstacle with custom sprite support and floating platform capability."""
    
    def __init__(self, x, height, width=30, y_offset=0, is_killzone=False, hazard_type="lava", continuous_lava=False):
        # Import asset_manager here to avoid circular import issues
        from .assets import asset_manager
        
        self.x = x
        self.is_killzone = is_killzone  # Hazard floor marker
        self.hazard_type = hazard_type  # "lava" or "acid"
        self.continuous_lava = continuous_lava  # If True, extend to viewport bottom
        
        # Hazard floors are very low bars (15px tall) or full-height if continuous
        if is_killzone:
            self.width = width
            if continuous_lava:
                # Full height from ground to bottom of viewport (720px total viewport)
                self.height = 720 - (GROUND_Y + PLAYER_SIZE - 15)  # From just above grass to bottom
                self.y = GROUND_Y + PLAYER_SIZE - 15  # Start just above grass
            else:
                self.height = 15  # Very low bar
                self.y = GROUND_Y + PLAYER_SIZE - self.height  # Just above ground level
            self.y_offset = 0  # Sits on ground
            self.custom_sprite = None
            self.hazard_texture = asset_manager.get_hazard_texture(hazard_type)
        else:
            # Normal obstacles
            self.width = width
            self.height = height
            self.y_offset = y_offset  # Offset from ground (0 = ground obstacle, >0 = floating)
            self.y = GROUND_Y + PLAYER_SIZE - height - y_offset
            self.custom_sprite = asset_manager.get_obstacle_sprite(self.width, self.height)
            self.hazard_texture = None
        
        self.passed = False
    
    def update(self):
        """Move obstacle left."""
        self.x -= PLAYER_SPEED
    
    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        """Draw obstacle using custom sprite or procedural generation."""
        if self.is_killzone:
            self._draw_hazard_bar(screen)
        elif self.custom_sprite:
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
        
        # Add sparkles (only if obstacle is tall enough)
        if self.height >= 20 and random.random() < 0.1:
            star_x = self.x + random.randint(5, max(6, self.width - 5))
            star_y = self.y + random.randint(5, max(6, self.height - 5))
            pygame.draw.circle(screen, YELLOW, (star_x, star_y), 2)
    
    def _draw_hazard_bar(self, screen):
        """Draw low hazard bar (15px tall) that sits above the grass."""
        if self.hazard_texture:
            # Tile the hazard texture across the bar
            texture_width = self.hazard_texture.get_width()
            texture_height = self.hazard_texture.get_height()
            
            # Scale texture to fit the 15px height while maintaining aspect ratio
            scale_factor = self.height / texture_height
            scaled_width = int(texture_width * scale_factor)
            scaled_height = self.height
            scaled_texture = pygame.transform.scale(self.hazard_texture, (scaled_width, scaled_height))
            
            # Tile horizontally across the obstacle width
            for x_offset in range(0, self.width, scaled_width):
                clip_width = min(scaled_width, self.width - x_offset)
                if clip_width > 0:
                    clip_rect = pygame.Rect(0, 0, clip_width, scaled_height)
                    screen.blit(scaled_texture, (self.x + x_offset, self.y), clip_rect)
        else:
            # Fallback: glowing red/orange bar
            # Draw glow effect
            for i in range(3):
                glow_alpha = 100 - (i * 30)
                glow_surface = pygame.Surface((self.width + i*4, self.height + i*4), pygame.SRCALPHA)
                color = (255, 100, 0, glow_alpha)  # Orange glow
                pygame.draw.rect(glow_surface, color, glow_surface.get_rect(), border_radius=3)
                screen.blit(glow_surface, (self.x - i*2, self.y - i*2))
            
            # Main hazard bar - bright red/orange
            pygame.draw.rect(screen, (255, 50, 0), (self.x, self.y, self.width, self.height), border_radius=2)
            
            # Animated warning stripes
            stripe_offset = (pygame.time.get_ticks() // 100) % 20
            for stripe_x in range(-20, self.width + 20, 20):
                stripe_pos = stripe_x + stripe_offset
                pygame.draw.line(screen, (255, 150, 0), 
                               (self.x + stripe_pos, self.y), 
                               (self.x + stripe_pos - 10, self.y + self.height), 3)


class ObstacleGenerator:
    """Generates obstacles that are always jumpable, using patterns and random generation."""
    
    def __init__(self, difficulty="hard"):
        self.obstacles = []
        self.difficulty = difficulty  # "easy", "medium", or "hard"
        self.pattern_manager = PatternManager(difficulty=difficulty)
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
                prev_gap_hazard = None  # Track hazard from previous gap for floor below platforms
                
                for i, pattern_obstacle in enumerate(pattern['obstacles']):
                    height = min(pattern_obstacle['height'], physics.max_obstacle_height)
                    width = pattern_obstacle.get('width', 30)
                    y_offset = pattern_obstacle.get('y_offset', 0)
                    gap_after = pattern_obstacle.get('gap_after', 0)
                    gap_hazard = pattern_obstacle.get('gap_hazard', None)  # Hazard in gap BEFORE this obstacle
                    
                    # If this gap has a hazard, create a lava obstacle to fill the gap BEFORE this platform
                    if gap_hazard and i > 0 and gap_after > 0:
                        # The gap is the distance from the previous obstacle's right edge to current_x
                        # We need to look back to find how big the gap actually is
                        # For now, let's fill from the rightmost obstacle to current_x
                        if len(self.obstacles) > 0:
                            last_obstacle = self.obstacles[-1]
                            gap_start = last_obstacle.x + last_obstacle.width
                            gap_width = current_x - gap_start
                            
                            if gap_width > 0:  # Only create lava if there's actually a gap
                                lava_obstacle = Obstacle(
                                    x=gap_start,  # Start right after previous obstacle
                                    height=15,  # Low bar
                                    width=gap_width,
                                    y_offset=0,  # On ground
                                    is_killzone=True,
                                    hazard_type=gap_hazard,
                                    continuous_lava=False  # Regular 15px bars for now
                                )
                                self.obstacles.append(lava_obstacle)
                    
                    # Create the platform/bar
                    obstacle = Obstacle(current_x, height, width, y_offset, False, 'lava', False)
                    self.obstacles.append(obstacle)
                    
                    # If this is a floating platform (y_offset > 0), create hazard floor below it
                    # using the hazard type from the gap to its left
                    if y_offset > 0 and prev_gap_hazard:
                        floor_obstacle = Obstacle(
                            x=current_x,
                            height=15,  # Low bar
                            width=width,  # Same width as platform above
                            y_offset=0,  # On ground
                            is_killzone=True,
                            hazard_type=prev_gap_hazard,
                            continuous_lava=False
                        )
                        self.obstacles.append(floor_obstacle)
                    
                    # Move x position forward for next obstacle in pattern
                    current_x += width + gap_after
                    prev_gap_hazard = gap_hazard  # Remember for next iteration (floor below next floating platform)
    
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
        """Check if player collides with obstacles. Hazard bars kill on any contact."""
        player_rect = player.get_rect()
        player_is_on_obstacle = False
        
        for obstacle in self.obstacles:
            obstacle_rect = obstacle.get_rect()
            
            # Check if there's any overlap
            if player_rect.colliderect(obstacle_rect):
                # Hazard bars (killzones) kill player on ANY contact
                if obstacle.is_killzone:
                    return True  # Instant death - no landing allowed
                
                # Regular obstacles: check for landing vs collision
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
