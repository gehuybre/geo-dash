"""
Wall system for Celeste Runner - vertical surfaces for wall-jumping.
"""

import pygame
import random
from .config import *


class Wall:
    """A vertical wall that player can slide on and jump from."""
    
    def __init__(self, x, y, height, wall_type="normal"):
        """
        Create a wall.
        
        Args:
            x: X position (left edge)
            y: Y position (top of wall)
            height: Height of wall in pixels
            wall_type: "normal", "crumbly", or "slippery"
        """
        self.x = x
        self.y = y
        self.width = WALL_WIDTH
        self.height = height
        self.wall_type = wall_type
        
        # Visual properties
        if wall_type == "normal":
            self.color = WALL_COLOR
            self.highlight_color = WALL_HIGHLIGHT
        elif wall_type == "crumbly":
            self.color = (200, 150, 100)  # Brown
            self.highlight_color = (220, 180, 130)
            self.crumble_timer = 0
            self.is_crumbling = False
        elif wall_type == "slippery":
            self.color = (150, 200, 255)  # Ice blue
            self.highlight_color = (180, 220, 255)
        
        # State
        self.is_active = True
        self.player_touching = False
        
        # Load sprite if available
        from .assets import asset_manager
        self.custom_sprite = None  # Could load wall textures here
    
    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def check_player_collision(self, player_rect):
        """
        Check if player is touching this wall.
        
        Args:
            player_rect: Player's pygame.Rect
            
        Returns:
            str or None: 'left' if touching left side, 'right' if touching right side, None if not touching
        """
        if not self.is_active:
            return None
        
        wall_rect = self.get_rect()
        
        if not player_rect.colliderect(wall_rect):
            self.player_touching = False
            return None
        
        # Determine which side of wall player is on
        player_center_x = player_rect.centerx
        wall_center_x = wall_rect.centerx
        
        # Check if player is moving towards wall (or just touching)
        if player_center_x < wall_center_x:
            # Player is on left side of wall
            self.player_touching = True
            return 'left'
        else:
            # Player is on right side of wall
            self.player_touching = True
            return 'right'
    
    def update(self):
        """Update wall state (for crumbling walls, etc)."""
        if self.wall_type == "crumbly" and self.is_crumbling:
            self.crumble_timer += 1
            if self.crumble_timer > 30:  # Crumble after 30 frames (0.5 sec)
                self.is_active = False
    
    def trigger_crumble(self):
        """Start crumbling (for crumbly walls)."""
        if self.wall_type == "crumbly" and not self.is_crumbling:
            self.is_crumbling = True
            self.crumble_timer = 0
    
    def draw(self, screen, camera_x):
        """
        Draw the wall.
        
        Args:
            screen: Pygame screen surface
            camera_x: Camera X offset
        """
        if not self.is_active:
            return
        
        # Calculate screen position
        screen_x = self.x - camera_x
        
        # Don't draw if off-screen
        if screen_x + self.width < 0 or screen_x > SCREEN_WIDTH:
            return
        
        # Choose color based on state
        if self.player_touching:
            color = self.highlight_color
        else:
            color = self.color
        
        # Draw wall rectangle
        rect = pygame.Rect(int(screen_x), int(self.y), self.width, self.height)
        pygame.draw.rect(screen, color, rect)
        
        # Draw outline
        pygame.draw.rect(screen, BLACK, rect, 2)
        
        # Draw type-specific details
        if self.wall_type == "crumbly" and self.is_crumbling:
            # Draw cracks
            alpha = int((self.crumble_timer / 30) * 255)
            crack_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            crack_surface.fill((0, 0, 0, alpha))
            screen.blit(crack_surface, (screen_x, self.y))
        
        elif self.wall_type == "slippery":
            # Draw ice sparkles
            for i in range(3):
                sparkle_x = int(screen_x + self.width // 2)
                sparkle_y = int(self.y + (i + 1) * self.height // 4)
                pygame.draw.circle(screen, WHITE, (sparkle_x, sparkle_y), 2)


class WallGenerator:
    """Generates walls for the level as player progresses."""
    
    def __init__(self, difficulty="medium"):
        """
        Initialize wall generator.
        
        Args:
            difficulty: "easy", "medium", or "hard"
        """
        self.difficulty = difficulty
        self.walls = []
        self.next_wall_x = SCREEN_WIDTH  # Start generating walls off-screen
        
        # Difficulty settings
        if difficulty == "easy":
            self.min_gap = 120
            self.max_gap = 200
            self.wall_type_weights = {"normal": 0.9, "crumbly": 0.05, "slippery": 0.05}
        elif difficulty == "medium":
            self.min_gap = MIN_WALL_GAP
            self.max_gap = MAX_WALL_GAP
            self.wall_type_weights = {"normal": 0.7, "crumbly": 0.2, "slippery": 0.1}
        else:  # hard
            self.min_gap = 80
            self.max_gap = MAX_WALL_GAP
            self.wall_type_weights = {"normal": 0.5, "crumbly": 0.3, "slippery": 0.2}
        
        # Generate initial walls
        self._generate_initial_walls()
        
        print(f"🧱 WallGenerator initialized (difficulty: {difficulty})")
    
    def _generate_initial_walls(self):
        """Generate starting walls for the level."""
        # Create a starting wall for player to grab
        start_wall = Wall(
            x=PLAYER_START_X + 150,
            y=GROUND_Y - 250,
            height=250,
            wall_type="normal"
        )
        self.walls.append(start_wall)
        self.next_wall_x = start_wall.x + WALL_WIDTH + random.randint(self.min_gap, self.max_gap)
        
        # Generate a few more walls ahead
        for _ in range(5):
            self._generate_next_wall()
    
    def _generate_next_wall(self):
        """Generate the next wall in sequence."""
        from core.physics import physics
        
        # Random gap within limits
        gap = random.randint(self.min_gap, self.max_gap)
        
        # Random height
        height = random.randint(MIN_WALL_HEIGHT, MAX_WALL_HEIGHT)
        
        # Random y position (can be floating or ground-based)
        # Ground-based is more common
        if random.random() < 0.7:
            # Ground-based wall
            y = GROUND_Y - height
        else:
            # Floating wall (not touching ground)
            max_y = GROUND_Y - MIN_WALL_HEIGHT
            min_y = max_y - 300  # Don't go too high
            y = random.randint(min(min_y, max_y), max_y)
        
        # Choose wall type based on difficulty
        wall_type = random.choices(
            list(self.wall_type_weights.keys()),
            weights=list(self.wall_type_weights.values())
        )[0]
        
        # Create wall
        wall = Wall(
            x=self.next_wall_x,
            y=y,
            height=height,
            wall_type=wall_type
        )
        
        self.walls.append(wall)
        self.next_wall_x += WALL_WIDTH + gap
    
    def update(self, camera_x):
        """
        Update walls and generate new ones as camera advances.
        
        Args:
            camera_x: Current camera X position
        """
        # Update all walls
        for wall in self.walls:
            wall.update()
        
        # Remove walls that are far off-screen to the left
        self.walls = [wall for wall in self.walls if wall.x > camera_x - 200]
        
        # Generate new walls ahead of camera
        while self.next_wall_x < camera_x + WALL_SPAWN_DISTANCE:
            self._generate_next_wall()
    
    def check_collisions(self, player):
        """
        Check player collision with all walls.
        
        Args:
            player: Player instance
            
        Returns:
            Wall or None: Wall player is touching, or None
        """
        player_rect = player.get_rect()
        
        for wall in self.walls:
            if not wall.is_active:
                continue
            
            side = wall.check_player_collision(player_rect)
            if side:
                # Trigger crumble if applicable
                if wall.wall_type == "crumbly":
                    wall.trigger_crumble()
                
                return wall, side
        
        return None, None
    
    def draw(self, screen, camera_x):
        """
        Draw all walls.
        
        Args:
            screen: Pygame screen surface
            camera_x: Camera X offset
        """
        for wall in self.walls:
            wall.draw(screen, camera_x)
