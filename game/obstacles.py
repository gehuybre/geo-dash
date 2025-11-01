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
    
    def __init__(self, x, height, width=30, y_offset=0, is_killzone=False, hazard_type="lava", continuous_lava=False, prefer_irregular=False):
        # Import asset_manager here to avoid circular import issues
        from .assets import asset_manager
        
        self.x = x
        self.is_killzone = is_killzone  # Hazard floor marker
        self.hazard_type = hazard_type  # "lava" or "acid"
        self.continuous_lava = continuous_lava  # If True, extend to viewport bottom
        self.pattern_name = None  # Will be set by ObstacleGenerator for pattern tracking
        
        # Hazard floors always fill from grass to bottom for visual consistency  
        if is_killzone:
            self.width = width
            # Lava fills from just above grass line to ensure collision with walking player
            # Player bottom is at GROUND_Y + PLAYER_SIZE when walking
            # Start lava slightly higher to ensure overlap
            self.y = GROUND_Y + PLAYER_SIZE - 5  # Start 5px above grass line for collision
            self.height = SCREEN_HEIGHT - self.y  # Extend to bottom of screen
            self.y_offset = 0  # Sits on ground
            self.custom_sprite = None
            self.hazard_texture = asset_manager.get_hazard_texture(hazard_type)
            self.obstacle_pattern = None
        else:
            # Normal obstacles
            self.width = width
            self.height = height
            self.y_offset = y_offset  # Offset from ground (0 = ground obstacle, >0 = floating)
            self.y = GROUND_Y + PLAYER_SIZE - height - y_offset
            self.custom_sprite = asset_manager.get_obstacle_sprite(self.width, self.height, prefer_irregular=prefer_irregular)
            self.hazard_texture = None
            
            # Store sprite dimensions if they differ from collision box (for irregular kawaii sprites)
            self.sprite_width = self.width
            self.sprite_height = self.height
            self.sprite_y_offset = 0  # Default: no offset
            self.use_sprite_collision = False  # Default: use regular collision
            
            if self.custom_sprite:
                actual_sprite_width = self.custom_sprite.get_width()
                actual_sprite_height = self.custom_sprite.get_height()
                if actual_sprite_width != self.width or actual_sprite_height != self.height:
                    # Large irregular sprite - store its actual size for rendering
                    self.sprite_width = actual_sprite_width
                    self.sprite_height = actual_sprite_height
                    # Adjust y position so sprite bottom aligns with collision box bottom
                    # This makes large sprites extend upward from the collision point
                    self.sprite_y_offset = actual_sprite_height - self.height
                    self.use_sprite_collision = True  # Enable sprite-based collision
            
            # Load pattern for tiling
            self.obstacle_pattern = asset_manager.get_obstacle_pattern()
            # Random offset into the pattern for variety
            if self.obstacle_pattern:
                pattern_width = self.obstacle_pattern.get_width()
                pattern_height = self.obstacle_pattern.get_height()
                self.pattern_offset_x = random.randint(0, pattern_width - 1) if pattern_width > 0 else 0
                self.pattern_offset_y = random.randint(0, pattern_height - 1) if pattern_height > 0 else 0
            else:
                self.pattern_offset_x = 0
                self.pattern_offset_y = 0
            
            # Create collision mask for pixel-perfect collision with irregular shapes
            # IMPORTANT: Create mask AFTER determining sprite dimensions
            self.collision_mask = None
            if self.custom_sprite:
                try:
                    self.collision_mask = pygame.mask.from_surface(self.custom_sprite)
                except Exception as e:
                    print(f"⚠️  Could not create collision mask: {e}")
                    self.collision_mask = None
            
            # Calculate landing platform line for irregular obstacles
            self.landing_platform_y = None
            self.platform_left = None  # Leftmost solid pixel at platform height
            self.platform_right = None  # Rightmost solid pixel at platform height
            if self.collision_mask and self.use_sprite_collision:
                self.landing_platform_y = self._calculate_landing_platform()
        
        self.passed = False
        
        # Landing visual effects for platforms/bars
        self.landing_squish = 0  # 0-1, amount of squish effect
        self.landing_glow = 0  # 0-255, glow intensity
        self.landing_blink = 0  # Counter for blink effect
    
    def _calculate_landing_platform(self):
        """
        Calculate the Y coordinate of the landing platform for irregular obstacles.
        Finds the first substantial horizontal landing surface from the top.
        
        Returns: Y coordinate in world space, or None if no platform found.
        """
        if not self.collision_mask:
            return None
        
        mask_width = self.collision_mask.get_size()[0]
        mask_height = self.collision_mask.get_size()[1]
        
        # Sample points across the width to find topmost pixels
        sample_points = max(20, mask_width // 2)  # Sample densely to find platforms
        topmost_pixels = []
        
        for i in range(sample_points):
            x = int((i / sample_points) * mask_width)
            if x >= mask_width:
                x = mask_width - 1
            
            # Find topmost solid pixel in this column
            for y in range(mask_height):
                try:
                    if self.collision_mask.get_at((x, y)):
                        topmost_pixels.append((x, y))
                        break
                except IndexError:
                    break
        
        if not topmost_pixels:
            return None
        
        # Find the first substantial horizontal platform
        # Group pixels by their Y coordinate and find which Y has the most horizontal coverage
        y_coverage = {}
        tolerance = 10  # Pixels within ±10 are considered same height
        
        for x, y in topmost_pixels:
            # Find or create a height group
            found_group = False
            for group_y in y_coverage:
                if abs(y - group_y) <= tolerance:
                    y_coverage[group_y].append(x)
                    found_group = True
                    break
            if not found_group:
                y_coverage[y] = [x]
        
        # Find the highest platform that has good horizontal coverage (at least 40% of width)
        min_coverage = mask_width * 0.4
        platform_y = None
        
        for y in sorted(y_coverage.keys()):  # Sort from top to bottom
            x_list = y_coverage[y]
            if len(x_list) >= min_coverage / sample_points * len(topmost_pixels):
                # This is a substantial horizontal surface
                platform_y = y
                break
        
        # Fallback: if no substantial platform found, use the minimum Y (topmost point)
        if platform_y is None:
            platform_y = min(y for x, y in topmost_pixels)
        
        # Convert to world coordinates
        sprite_y = self.y - self.sprite_y_offset
        world_platform_y = sprite_y + platform_y
        
        # Debug output for first few obstacles
        if random.random() < 0.1:  # Print for ~10% of obstacles
            print(f"🎯 Platform: sprite={self.sprite_width}x{self.sprite_height}, "
                  f"platform_y_local={platform_y}, world={world_platform_y}, coverage={len(y_coverage)}")
        
        return world_platform_y
    
    def update(self):
        """Move obstacle left and update visual effects."""
        self.x -= PLAYER_SPEED
        
        # Decay landing effects
        if self.landing_squish > 0:
            self.landing_squish *= 0.85
        if self.landing_glow > 0:
            self.landing_glow *= 0.9
        if self.landing_blink > 0:
            self.landing_blink -= 1
    
    def trigger_landing_effect(self):
        """Trigger visual landing effects when player lands on this obstacle."""
        self.landing_squish = 0.25  # Start at 25% squish
        self.landing_glow = 180  # Bright glow
        self.landing_blink = 6  # Blink for 6 frames
    
    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_sprite_rect(self):
        """Get the full sprite rectangle (for large irregular sprites, this includes the offset area)."""
        if self.use_sprite_collision:
            sprite_y = self.y - self.sprite_y_offset
            return pygame.Rect(self.x, sprite_y, self.sprite_width, self.sprite_height)
        else:
            return self.get_rect()
    
    def check_pixel_collision(self, player_rect, player_mask=None):
        """
        Check pixel-perfect collision with player.
        Returns True if there's a collision, False otherwise.
        
        Args:
            player_rect: pygame.Rect of the player
            player_mask: pygame.mask.Mask of the player (optional)
        """
        if not self.collision_mask:
            # Fall back to rect collision if no mask available
            return self.get_rect().colliderect(player_rect)
        
        # For large irregular sprites, use the sprite dimensions and offset
        if getattr(self, 'use_sprite_collision', False):
            sprite_y_offset = getattr(self, 'sprite_y_offset', 0)
            sprite_y = self.y - sprite_y_offset
            
            # Create sprite rect for collision detection
            sprite_rect = pygame.Rect(self.x, sprite_y, self.sprite_width, self.sprite_height)
            
            # Quick reject if rects don't overlap
            if not sprite_rect.colliderect(player_rect):
                return False
            
            if player_mask:
                # Pixel-perfect collision with both masks
                offset = (player_rect.x - self.x, player_rect.y - sprite_y)
                overlap = self.collision_mask.overlap(player_mask, offset)
                if overlap is None:
                    return False
                
                # Allow some overlaps for forgiving collisions (~10x10 pixels)
                overlap_area = self.collision_mask.overlap_area(player_mask, offset)
                return overlap_area > 100  # ~10x10 pixels minimum overlap
            else:
                # Check if player rect overlaps with any pixel in obstacle mask
                overlap_rect = sprite_rect.clip(player_rect)
                if overlap_rect.width == 0 or overlap_rect.height == 0:
                    return False
                
                # Check mask at overlap area
                for dy in range(overlap_rect.height):
                    for dx in range(overlap_rect.width):
                        mask_x = overlap_rect.x - self.x + dx
                        mask_y = overlap_rect.y - sprite_y + dy
                        if (0 <= mask_x < self.sprite_width and 
                            0 <= mask_y < self.sprite_height and
                            self.collision_mask.get_at((mask_x, mask_y))):
                            return True
                return False
        else:
            # Regular sized sprite - use standard collision
            if player_mask:
                # Pixel-perfect collision with both masks
                offset = (player_rect.x - self.x, player_rect.y - self.y)
                overlap = self.collision_mask.overlap(player_mask, offset)
                if overlap is None:
                    return False
                
                # Allow significant overlaps (~10x10 pixels) for more forgiving collisions
                overlap_area = self.collision_mask.overlap_area(player_mask, offset)
                return overlap_area > 100  # ~10x10 pixels minimum overlap to count as collision
            else:
                # Check if player rect overlaps with any pixel in obstacle mask
                overlap_rect = self.get_rect().clip(player_rect)
                if overlap_rect.width == 0 or overlap_rect.height == 0:
                    return False
            
            # Check pixels in the overlap area
            for px in range(overlap_rect.left, overlap_rect.right):
                for py in range(overlap_rect.top, overlap_rect.bottom):
                    local_x = px - self.x
                    local_y = py - self.y
                    if 0 <= local_x < self.width and 0 <= local_y < self.height:
                        if self.collision_mask.get_at((local_x, local_y)):
                            return True
            return False
    
    def can_land_on_top(self, player_rect, player_mask=None):
        """
        Check if player can land on top of this obstacle.
        Uses pre-calculated landing platform for irregular shapes, or pixel-perfect detection as fallback.
        
        Returns: (can_land, landing_y) tuple
        """
        # Use pre-calculated landing platform for irregular obstacles
        if self.landing_platform_y is not None and self.use_sprite_collision:
            platform_y = self.landing_platform_y
            # More forgiving landing zone for irregular shapes (35 pixels)
            if player_rect.bottom >= platform_y - 35 and player_rect.bottom <= platform_y + 15:
                # Check horizontal overlap - but ONLY with actual platform area, not entire sprite
                # Use pixel-perfect check at the player's horizontal position
                player_center_x = player_rect.centerx
                local_x = player_center_x - self.x
                
                # Check if player's center is within sprite bounds
                if 0 <= local_x < self.sprite_width:
                    # Calculate platform Y in mask coordinates
                    sprite_y = self.y - self.sprite_y_offset
                    mask_y = int(platform_y - sprite_y)
                    
                    # Check if there's actually a solid pixel at this position
                    if self.collision_mask and 0 <= mask_y < self.collision_mask.get_size()[1]:
                        # Check in a small horizontal range around player center
                        for dx in range(-5, 6):  # Check 11 pixels around center
                            check_x = int(local_x) + dx
                            if 0 <= check_x < self.sprite_width:
                                # Check a few pixels vertically around platform line
                                for dy in range(-3, 4):
                                    check_y = mask_y + dy
                                    if 0 <= check_y < self.collision_mask.get_size()[1]:
                                        try:
                                            if self.collision_mask.get_at((check_x, check_y)):
                                                return True, platform_y
                                        except IndexError:
                                            pass
            return False, None
        
        if not self.collision_mask:
            # Fall back to simple top collision with LARGER safe zone
            rect = self.get_rect()
            # Increased from 10 to 25 pixels for more forgiving landings
            if player_rect.bottom >= rect.top and player_rect.bottom <= rect.top + 25:
                if player_rect.right > rect.left and player_rect.left < rect.right:
                    return True, rect.top
            return False, None
        
        # For large irregular sprites, use sprite dimensions and offset
        if self.use_sprite_collision:
            sprite_y = self.y - self.sprite_y_offset
            sprite_width = self.sprite_width
            sprite_height = self.sprite_height
        else:
            sprite_y = self.y
            sprite_width = self.width
            sprite_height = self.height
        
        # For pixel-perfect collision, find the topmost pixel
        # Check a column under the player's center
        player_center_x = player_rect.centerx
        local_x = player_center_x - self.x
        
        if local_x < 0 or local_x >= sprite_width:
            return False, None
        
        # Clamp local_x to mask bounds
        mask_width = self.collision_mask.get_size()[0]
        mask_height = self.collision_mask.get_size()[1]
        local_x = int(max(0, min(local_x, mask_width - 1)))
        
        # Find topmost solid pixel in this column
        for local_y in range(mask_height):
            try:
                if self.collision_mask.get_at((local_x, local_y)):
                    world_y = sprite_y + local_y
                    # Check if player is falling onto this point with LARGER safe zone
                    # Increased from 5 to 25 pixels for very forgiving landings on irregular shapes
                    if player_rect.bottom >= world_y - 25 and player_rect.bottom <= world_y + 25:
                        return True, world_y
                    break
            except IndexError:
                # Safety check - if we go out of bounds, stop
                break
        
        return False, None
    
    def draw(self, screen):
        """Draw obstacle using custom sprite or procedural generation."""
        if self.is_killzone:
            self._draw_hazard_bar(screen)
        elif self.custom_sprite:
            self._draw_custom_sprite(screen)
        else:
            self._draw_procedural(screen)
    
    def _draw_procedural(self, screen):
        """Draw using pattern fill or procedural generation (gradient purple block) with landing effects."""
        # Calculate squish dimensions
        squish_factor = 1 - (self.landing_squish * 0.4)  # Max 10% height reduction
        squish_height = int(self.height * squish_factor)
        squish_y_offset = self.height - squish_height
        
        # Draw glow effect if active
        if self.landing_glow > 20:
            glow_size = 8
            for i in range(3):
                glow_alpha = int(self.landing_glow * (1 - i * 0.3))
                glow_surface = pygame.Surface((self.width + glow_size*2, squish_height + glow_size*2), pygame.SRCALPHA)
                color = (255, 255, 100, glow_alpha)  # Yellow glow
                pygame.draw.rect(glow_surface, color, glow_surface.get_rect(), border_radius=8)
                screen.blit(glow_surface, (self.x - glow_size, self.y + squish_y_offset - glow_size))
        
        # Use pattern if available, otherwise use gradient
        if self.obstacle_pattern:
            # Create a surface for the obstacle with the pattern tiled
            obstacle_surface = pygame.Surface((self.width, squish_height))
            
            pattern_width = self.obstacle_pattern.get_width()
            pattern_height = self.obstacle_pattern.get_height()
            
            # Tile the pattern across the obstacle with random offset
            # Start tiling from the random offset position
            start_y = -self.pattern_offset_y
            for tile_y in range(start_y, squish_height, pattern_height):
                start_x = -self.pattern_offset_x
                for tile_x in range(start_x, self.width, pattern_width):
                    # Calculate source rectangle from pattern (what part to copy)
                    src_x = max(0, -tile_x)
                    src_y = max(0, -tile_y)
                    src_width = min(pattern_width - src_x, self.width - max(0, tile_x))
                    src_height = min(pattern_height - src_y, squish_height - max(0, tile_y))
                    
                    # Calculate destination position on obstacle surface
                    dest_x = max(0, tile_x)
                    dest_y = max(0, tile_y)
                    
                    if src_width > 0 and src_height > 0:
                        src_rect = pygame.Rect(src_x, src_y, src_width, src_height)
                        obstacle_surface.blit(self.obstacle_pattern, (dest_x, dest_y), src_rect)
            
            screen.blit(obstacle_surface, (self.x, self.y + squish_y_offset))
        else:
            # Fallback: Draw cute obstacle with gradient effect
            for i in range(squish_height):
                color_intensity = 216 - (i * 20 // squish_height)
                color = (color_intensity, 191 - (i * 10 // squish_height), 216)
                pygame.draw.rect(screen, color, (self.x, self.y + squish_y_offset + i, self.width, 1))
        
        # Blink effect - brighter color
        if self.landing_blink > 0 and self.landing_blink % 2 == 0:
            blink_surface = pygame.Surface((self.width, squish_height), pygame.SRCALPHA)
            blink_surface.fill((255, 255, 150, 100))  # Yellow tint
            screen.blit(blink_surface, (self.x, self.y + squish_y_offset))
        
        # Outline
        pygame.draw.rect(screen, OBSTACLE_DARK, (self.x, self.y + squish_y_offset, self.width, squish_height), 2, border_radius=5)
        
        # Add sparkles (only if obstacle is tall enough)
        if squish_height >= 20 and random.random() < 0.1:
            star_x = self.x + random.randint(5, max(6, self.width - 5))
            star_y = self.y + squish_y_offset + random.randint(5, max(6, squish_height - 5))
            pygame.draw.circle(screen, YELLOW, (star_x, star_y), 2)
    
    def _draw_custom_sprite(self, screen):
        """Draw custom sprite with landing effects and two-tone rendering for irregular obstacles."""
        # Calculate squish dimensions
        squish_factor = 1 - (self.landing_squish * 0.4)  # Max 40% squish reduction
        squish_height = int(self.sprite_height * squish_factor)
        squish_y_offset = self.sprite_height - squish_height
        
        # Calculate render position (for large irregular sprites, extend upward)
        sprite_y_offset = getattr(self, 'sprite_y_offset', 0)
        render_y = self.y - sprite_y_offset + squish_y_offset
        
        # Draw glow effect if active
        if self.landing_glow > 20:
            glow_size = 8
            
            # For irregular sprites with landing platforms, only glow around the platform area
            if self.use_sprite_collision and self.landing_platform_y is not None and self.platform_left is not None and self.platform_right is not None:
                # Use the ACTUAL platform width we measured!
                actual_platform_width = self.platform_right - self.platform_left
                glow_width = actual_platform_width + 20  # Add small margin (10px each side)
                glow_height = min(squish_height, self.height * 2)  # Max 2x collision box height
                
                # Position glow at the platform location
                glow_x_offset = self.platform_left - 10  # Account for margin
                
                for i in range(3):
                    glow_alpha = int(self.landing_glow * (1 - i * 0.3))
                    glow_surface = pygame.Surface((glow_width + glow_size*2, glow_height + glow_size*2), pygame.SRCALPHA)
                    color = (255, 255, 100, glow_alpha)  # Yellow glow
                    pygame.draw.rect(glow_surface, color, glow_surface.get_rect(), border_radius=8)
                    screen.blit(glow_surface, (self.x + glow_x_offset - glow_size, render_y + squish_height - glow_height - glow_size))
            elif self.use_sprite_collision and self.landing_platform_y is not None:
                # Fallback if platform extent not calculated yet
                glow_width = min(self.sprite_width, self.width * 3)  # Max 3x collision box width
                glow_height = min(squish_height, self.height * 2)  # Max 2x collision box height
                
                # Center the glow horizontally on the sprite
                glow_x_offset = (self.sprite_width - glow_width) // 2
                
                for i in range(3):
                    glow_alpha = int(self.landing_glow * (1 - i * 0.3))
                    glow_surface = pygame.Surface((glow_width + glow_size*2, glow_height + glow_size*2), pygame.SRCALPHA)
                    color = (255, 255, 100, glow_alpha)  # Yellow glow
                    pygame.draw.rect(glow_surface, color, glow_surface.get_rect(), border_radius=8)
                    screen.blit(glow_surface, (self.x + glow_x_offset - glow_size, render_y + squish_height - glow_height - glow_size))
            else:
                # Regular glow for normal sprites
                for i in range(3):
                    glow_alpha = int(self.landing_glow * (1 - i * 0.3))
                    glow_surface = pygame.Surface((self.sprite_width + glow_size*2, squish_height + glow_size*2), pygame.SRCALPHA)
                    color = (255, 255, 100, glow_alpha)  # Yellow glow
                    pygame.draw.rect(glow_surface, color, glow_surface.get_rect(), border_radius=8)
                    screen.blit(glow_surface, (self.x - glow_size, render_y - glow_size))
        
        # Scale sprite to squish dimensions
        if squish_factor < 0.99:  # Only scale if there's noticeable squish
            sprite_to_draw = pygame.transform.scale(self.custom_sprite, (self.sprite_width, squish_height))
        else:
            sprite_to_draw = self.custom_sprite
        
        # Two-tone rendering for irregular obstacles with landing platforms
        if self.landing_platform_y is not None and self.use_sprite_collision:
            # Calculate where the platform line intersects the sprite
            platform_y_local = self.landing_platform_y - render_y
            
            # Debug first obstacle with platform
            if not hasattr(self, '_debug_printed'):
                self._debug_printed = True
                print(f"\n🎨 Two-tone rendering debug:")
                print(f"  sprite size: {self.sprite_width}x{self.sprite_height}")
                print(f"  collision_mask size: {self.collision_mask.get_size() if self.collision_mask else 'None'}")
                print(f"  squish_height: {squish_height}, squish_factor: {squish_factor}")
                print(f"  render_y: {render_y}, platform_y_local: {platform_y_local}")
                print(f"  platform_y (world): {self.landing_platform_y}")
                print(f"  Condition check: 0 < {platform_y_local} < {squish_height} = {0 < platform_y_local < squish_height}")
            
            if 0 < platform_y_local < squish_height:
                # Create two surfaces for above and below the platform
                above_height = int(platform_y_local)
                below_height = squish_height - above_height
                
                if not hasattr(self, '_debug_printed2'):
                    self._debug_printed2 = True
                    print(f"  ✅ Two-tone active! above_height={above_height}, below_height={below_height}")
                
                # Draw decorative portion above platform (lighter/transparent)
                if above_height > 0:
                    above_surface = sprite_to_draw.subsurface(pygame.Rect(0, 0, self.sprite_width, above_height)).copy()
                    above_surface.set_alpha(120)  # 47% opacity - clearly decorative
                    screen.blit(above_surface, (self.x, render_y))
                
                # Draw platform line indicator - simple line across the sprite width
                platform_line_y = render_y + above_height
                
                # Use ORIGINAL mask coordinates to find where solid pixels actually are
                mask_y_position = int(above_height * (self.sprite_height / squish_height))  # Scale back to original mask coordinates
                
                if not hasattr(self, '_debug_mask_check'):
                    self._debug_mask_check = True
                    print(f"🔍 Mask check: above_height={above_height}, mask_y_position={mask_y_position}")
                    print(f"   sprite_height={self.sprite_height}, squish_height={squish_height}")
                
                # Find only the horizontal extents where there are solid pixels
                if self.collision_mask and mask_y_position < self.collision_mask.get_size()[1]:
                    mask_width = self.collision_mask.get_size()[0]
                    
                    # Find leftmost and rightmost solid pixels at platform height
                    leftmost = None
                    rightmost = None
                    
                    for x in range(mask_width):
                        # Check if there's a solid pixel at or near this x position
                        has_pixel = False
                        for y_check in range(max(0, mask_y_position - 2), min(mask_y_position + 3, self.collision_mask.get_size()[1])):
                            try:
                                if self.collision_mask.get_at((x, y_check)):
                                    has_pixel = True
                                    break
                            except IndexError:
                                pass
                        
                        if has_pixel:
                            if leftmost is None:
                                leftmost = x
                            rightmost = x
                    
                    # Store platform extents for use in glow effect
                    if leftmost is not None and rightmost is not None:
                        self.platform_left = leftmost
                        self.platform_right = rightmost
                    
                    # Draw a single line from leftmost to rightmost solid pixel
                    if leftmost is not None and rightmost is not None and (rightmost - leftmost) > 5:
                        # Debug output for first obstacle
                        if not hasattr(self, '_debug_line'):
                            self._debug_line = True
                            print(f"🟡 Platform line: leftmost={leftmost}, rightmost={rightmost}, width={rightmost-leftmost}")
                            print(f"   Drawing from world x={self.x + leftmost} to x={self.x + rightmost}")
                            print(f"   Sprite: x={self.x}, width={self.sprite_width}, mask_width={mask_width}")
                        
                        # Simple golden line across the platform
                        pygame.draw.line(screen, (255, 223, 100, 200), 
                                       (self.x + leftmost, platform_line_y), 
                                       (self.x + rightmost, platform_line_y), 3)  # Thicker for visibility

                
                # Draw solid portion below platform (full opacity - landable)
                if below_height > 0:
                    below_surface = sprite_to_draw.subsurface(pygame.Rect(0, above_height, self.sprite_width, below_height)).copy()
                    screen.blit(below_surface, (self.x, platform_line_y))
            else:
                # Platform line outside sprite bounds - draw normally
                screen.blit(sprite_to_draw, (self.x, render_y))
        else:
            # No landing platform or regular sprite - draw normally
            screen.blit(sprite_to_draw, (self.x, render_y))
        
        # Blink effect - brighter overlay
        if self.landing_blink > 0 and self.landing_blink % 2 == 0:
            blink_surface = pygame.Surface((self.sprite_width, squish_height), pygame.SRCALPHA)
            blink_surface.fill((255, 255, 150, 100))  # Yellow tint
            screen.blit(blink_surface, (self.x, render_y))
    
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
    
    def __init__(self, difficulty="hard", score_manager=None):
        self.obstacles = []
        self.difficulty = difficulty  # "easy", "medium", or "hard"
        self.pattern_manager = PatternManager(difficulty=difficulty)
        self.current_pattern_name = None  # Track current pattern for debugging
        self.score_manager = score_manager  # For tracking pattern stats
        self.current_pattern_obstacles = []  # Track obstacles from current pattern

        
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
                # If there was a previous pattern, mark it as completed
                # (since we're starting a new one, the player must have survived the previous one)
                if self.current_pattern_name and self.score_manager:
                    self.score_manager.complete_pattern(self.current_pattern_name)
                    print(f"✅✅✅ PATTERN COMPLETED: {self.current_pattern_name} ✅✅✅")
                
                # Start a new pattern - spawn ALL obstacles at once
                pattern_name = pattern.get('name', 'Unknown Pattern')
                print(f"🆕 Starting new pattern: {pattern_name}")
                self.current_pattern_name = pattern_name
                
                # Track pattern start with score manager
                if self.score_manager:
                    self.score_manager.start_pattern(pattern_name)
                
                # Clear previous pattern obstacle tracking
                self.current_pattern_obstacles = []
                
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
                                # Don't track hazard obstacles for pattern completion
                    
                    # Create the platform/bar
                    prefer_irregular = pattern_obstacle.get('prefer_irregular', False)
                    obstacle = Obstacle(current_x, height, width, y_offset, False, 'lava', False, prefer_irregular)
                    obstacle.pattern_name = pattern_name  # Tag obstacle with pattern name
                    self.obstacles.append(obstacle)
                    self.current_pattern_obstacles.append(obstacle)  # Track for completion
                    
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
                        # Don't track hazard obstacles for pattern completion
                    
                    # Move x position forward for next obstacle in pattern
                    current_x += width + gap_after
                    prev_gap_hazard = gap_hazard  # Remember for next iteration (floor below next floating platform)
    
    def update(self):
        """Update all obstacles and generate new ones."""
        # Update and remove off-screen obstacles FIRST
        for obstacle in self.obstacles[:]:
            obstacle.update()
            # For large irregular sprites, use sprite_width for removal check
            removal_width = obstacle.sprite_width if obstacle.use_sprite_collision else obstacle.width
            if obstacle.x < -removal_width:
                self.obstacles.remove(obstacle)
        
        # Then generate new obstacles (which checks for pattern completion)
        self.generate_obstacle()
    
    def draw(self, screen):
        """Draw all obstacles."""
        for obstacle in self.obstacles:
            obstacle.draw(screen)
    
    def check_collision(self, player):
        """Check if player collides with obstacles using pixel-perfect detection for irregular shapes."""
        player_rect = player.get_rect()
        player_is_on_obstacle = False
        
        for obstacle in self.obstacles:
            # For large irregular sprites, use the full sprite rect for initial collision check
            if obstacle.use_sprite_collision:
                obstacle_rect = obstacle.get_sprite_rect()
            else:
                obstacle_rect = obstacle.get_rect()
            
            # Quick rect check first for performance
            if not player_rect.colliderect(obstacle_rect):
                continue
            
            # Hazard bars (killzones) kill player on ANY contact
            if obstacle.is_killzone:
                return True  # Instant death - no landing allowed
            
            # For obstacles with custom sprites, use pixel-perfect collision
            if obstacle.collision_mask and player.collision_mask:
                # Check if player can land on top using pixel-perfect detection
                can_land, landing_y = obstacle.can_land_on_top(player_rect, player.collision_mask)
                
                if can_land and player.velocity_y >= 0:
                    # Landing on top - safe!
                    player.y = landing_y - player.height
                    player.velocity_y = 0
                    player.on_ground = True
                    player.is_jumping = False
                    player.jumps_used = 0  # Reset double jump on landing
                    player.has_double_jump = False
                    player.rotation = 0  # Stop rotation when on obstacle
                    
                    # Trigger landing visual effects on the OBSTACLE (only if just landed on NEW obstacle)
                    if player.current_obstacle != obstacle:  # Landing on a different obstacle
                        obstacle.trigger_landing_effect()
                        player.just_landed = True  # Flag for scoring bonus
                        player.combo_streak += 1  # Increase combo for platform landing
                        player.last_landed_on_ground = False
                        player.current_obstacle = obstacle  # Track this obstacle
                    
                    player_is_on_obstacle = True
                    continue
                elif obstacle.check_pixel_collision(player_rect, player.collision_mask):
                    # Check if this is a side/bottom collision (deadly) vs top collision (safe)
                    # If player is descending and near the top, treat as safe landing zone
                    overlap_from_top = player_rect.bottom - obstacle_rect.top
                    if player.velocity_y >= 0 and overlap_from_top <= 40:
                        # Close to landing - give them the benefit of the doubt, set them on top
                        player.y = obstacle_rect.top - player.height
                        player.velocity_y = 0
                        player.on_ground = True
                        player.is_jumping = False
                        player.jumps_used = 0
                        player.has_double_jump = False
                        player.rotation = 0
                        
                        if player.current_obstacle != obstacle:
                            obstacle.trigger_landing_effect()
                            player.just_landed = True
                            player.combo_streak += 1
                            player.last_landed_on_ground = False
                            player.current_obstacle = obstacle
                        
                        player_is_on_obstacle = True
                        continue
                    else:
                        # Side or bottom collision - deadly!
                        # For large irregular sprites, need to calculate offset correctly
                        if obstacle.use_sprite_collision:
                            sprite_y = obstacle.y - obstacle.sprite_y_offset
                            offset_x = player_rect.x - obstacle.x
                            offset_y = player_rect.y - sprite_y
                        else:
                            offset_x = player_rect.x - obstacle.x
                            offset_y = player_rect.y - obstacle.y
                        
                        overlap_area = obstacle.collision_mask.overlap_area(player.collision_mask, (offset_x, offset_y))
                        if overlap_area > 100:
                            return True  # Significant side/bottom collision = death
                        # Small side touch - ignore it
                        continue
            else:
                # Fall back to rectangle collision for obstacles without sprites
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
                # Increased safe zone from 20 to 30 pixels for more forgiving landings
                if player.velocity_y >= 0 and overlap_bottom <= 30:
                    # Landing on top - safe!
                    player.y = obstacle_top - player.height
                    player.velocity_y = 0
                    player.on_ground = True
                    player.is_jumping = False
                    player.jumps_used = 0  # Reset double jump on landing
                    player.has_double_jump = False
                    player.rotation = 0  # Stop rotation when on obstacle
                    
                    # Trigger landing visual effects on the OBSTACLE (only if just landed on NEW obstacle)
                    if player.current_obstacle != obstacle:  # Landing on a different obstacle
                        obstacle.trigger_landing_effect()
                        player.just_landed = True  # Flag for scoring bonus
                        player.combo_streak += 1  # Increase combo for platform landing
                        player.last_landed_on_ground = False
                        player.current_obstacle = obstacle  # Track this obstacle
                    
                    player_is_on_obstacle = True
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
