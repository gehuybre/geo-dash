"""
Asset management system for loading custom sprites and images.
Falls back to procedural generation if assets are not found.
"""

import pygame
import os
import json
from .config import *

# Try to import PIL for better image loading support
try:
    from PIL import Image as PILImage
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: PIL/Pillow not available, only BMP files supported")

# Try to import cairosvg for SVG support (only needed for fallback)
try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False
    # SVG support will be limited without cairosvg


class AssetManager:
    """Manages loading and caching of game assets."""
    
    def __init__(self):
        self.assets = {}
        self.use_custom_assets = True
        
        # Spritesheet support
        self.spritesheets = {}
        self.spritesheet_metadata = {}
        self._load_spritesheets()
    
    def _load_spritesheets(self):
        """Load all spritesheets and their metadata."""
        spritesheet_dir = f"{ASSETS_DIR}/spritesheets"
        
        if not os.path.exists(spritesheet_dir):
            print("ℹ️  No spritesheets found, will use individual sprite loading")
            return
        
        # Load obstacle spritesheet
        obstacles_sheet = f"{spritesheet_dir}/obstacles.png"
        obstacles_meta = f"{spritesheet_dir}/obstacles.json"
        
        if os.path.exists(obstacles_sheet) and os.path.exists(obstacles_meta):
            try:
                # Load image with pygame - don't convert yet (will be done when extracting sprites)
                sheet_img = pygame.image.load(obstacles_sheet)
                self.spritesheets['obstacles'] = sheet_img
                with open(obstacles_meta, 'r') as f:
                    self.spritesheet_metadata['obstacles'] = json.load(f)
                print(f"✅ Loaded obstacle spritesheet ({len(self.spritesheet_metadata['obstacles']['sprites'])} sprites)")
            except Exception as e:
                print(f"⚠️  Could not load obstacle spritesheet: {e}")
        
        # Load player character spritesheet
        player_sheet = f"{spritesheet_dir}/player_characters.png"
        player_meta = f"{spritesheet_dir}/player_characters.json"
        
        if os.path.exists(player_sheet) and os.path.exists(player_meta):
            try:
                # Load image with pygame - don't convert yet
                sheet_img = pygame.image.load(player_sheet)
                self.spritesheets['player_characters'] = sheet_img
                with open(player_meta, 'r') as f:
                    self.spritesheet_metadata['player_characters'] = json.load(f)
                print(f"✅ Loaded player character spritesheet ({len(self.spritesheet_metadata['player_characters']['sprites'])} sprites)")
            except Exception as e:
                print(f"⚠️  Could not load player character spritesheet: {e}")
    
    def _get_sprite_from_sheet(self, sheet_name, sprite_name, target_size=None):
        """
        Extract a sprite from a spritesheet.
        
        Args:
            sheet_name: Name of the spritesheet ('obstacles' or 'player_characters')
            sprite_name: Name of the sprite in the metadata
            target_size: Optional (width, height) to scale the sprite to
            
        Returns:
            pygame.Surface or None if not found
        """
        if sheet_name not in self.spritesheets or sheet_name not in self.spritesheet_metadata:
            return None
        
        metadata = self.spritesheet_metadata[sheet_name]
        if sprite_name not in metadata['sprites']:
            return None
        
        sprite_data = metadata['sprites'][sprite_name]
        
        # Create a cache key
        cache_key = f"sheet_{sheet_name}_{sprite_name}"
        if target_size:
            cache_key += f"_{target_size[0]}x{target_size[1]}"
        
        if cache_key in self.assets:
            return self.assets[cache_key]
        
        # For obstacles, sprites are centered in cells, so we need to account for cell_offset
        if 'cell_offset_x' in sprite_data and 'cell_offset_y' in sprite_data:
            # Extract from the centered position within the cell
            rect = pygame.Rect(
                sprite_data['x'] + sprite_data['cell_offset_x'],
                sprite_data['y'] + sprite_data['cell_offset_y'],
                sprite_data['width'],
                sprite_data['height']
            )
        else:
            # For player characters (no offset), just use x, y directly
            rect = pygame.Rect(
                sprite_data['x'],
                sprite_data['y'],
                sprite_data['width'],
                sprite_data['height']
            )
        
        # Create surface and extract sprite
        sprite = pygame.Surface((sprite_data['width'], sprite_data['height']), pygame.SRCALPHA)
        sprite.blit(self.spritesheets[sheet_name], (0, 0), rect)
        
        # Convert for better performance
        sprite = sprite.convert_alpha()
        
        # Scale if needed
        if target_size and target_size != (sprite_data['width'], sprite_data['height']):
            sprite = pygame.transform.scale(sprite, target_size)
        
        self.assets[cache_key] = sprite
        return sprite
        
    def load_image(self, path, size=None):
        """
        Load an image from the given path.
        Uses PIL/Pillow if available for better format support.
        Uses cairosvg for SVG files if available.
        
        Args:
            path: Path to the image file
            size: Optional tuple (width, height) to resize the image
            
        Returns:
            pygame.Surface or None if file not found
        """
        # Create cache key that includes size to avoid size conflicts
        cache_key = f"{path}_{size[0]}x{size[1]}" if size else path
        
        if cache_key in self.assets:
            return self.assets[cache_key]
        
        if not os.path.exists(path):
            return None
        
        try:
            # Handle SVG files specially
            if path.lower().endswith('.svg'):
                if HAS_CAIROSVG and HAS_PIL:
                    # Convert SVG to PNG in memory using cairosvg
                    import io
                    if size:
                        width, height = size
                    else:
                        width, height = 150, 150  # Default SVG size
                    
                    # Convert SVG to PNG bytes
                    png_data = cairosvg.svg2png(url=path, output_width=width, output_height=height)
                    
                    # Load PNG bytes with PIL
                    pil_image = PILImage.open(io.BytesIO(png_data))
                    if pil_image.mode != 'RGBA':
                        pil_image = pil_image.convert('RGBA')
                    
                    # Convert PIL image to pygame surface
                    mode = pil_image.mode
                    size_tuple = pil_image.size
                    data = pil_image.tobytes()
                    image = pygame.image.fromstring(data, size_tuple, mode)
                    # Convert for optimal blitting performance
                    image = image.convert_alpha()
                else:
                    print(f"Warning: SVG support requires cairosvg and Pillow. Cannot load {path}")
                    return None
            
            # If PIL is available, use it to load and convert images
            elif HAS_PIL and not path.lower().endswith('.bmp'):
                pil_image = PILImage.open(path)
                # Convert to RGBA mode for transparency support
                if pil_image.mode != 'RGBA':
                    pil_image = pil_image.convert('RGBA')
                # Resize if requested
                if size:
                    pil_image = pil_image.resize(size, PILImage.Resampling.LANCZOS)
                # Convert PIL image to pygame surface
                mode = pil_image.mode
                size_tuple = pil_image.size
                data = pil_image.tobytes()
                image = pygame.image.fromstring(data, size_tuple, mode)
                # Convert for optimal blitting performance
                image = image.convert_alpha()
            else:
                # Fall back to pygame's native loading (BMP only without SDL_image)
                image = pygame.image.load(path)
                # Convert to pygame surface format
                if image.get_alpha():
                    image = image.convert_alpha()
                else:
                    image = image.convert()
                
                if size:
                    image = pygame.transform.scale(image, size)
            
            self.assets[cache_key] = image
            return image
        except (pygame.error, Exception) as e:
            print(f"Could not load image {path}: {e}")
            return None
    
    def get_player_sprite(self, character_name=None):
        """
        Get player sprite from spritesheet or individual file.
        
        Args:
            character_name: Name of the character file (e.g., 'bloemetje.svg') or None for default
        
        Returns:
            pygame.Surface or None if not found
        """
        if character_name:
            # Remove .svg extension if present
            sprite_name = character_name.replace('.svg', '')
            
            # Try to get from spritesheet first
            sprite = self._get_sprite_from_sheet('player_characters', sprite_name, (PLAYER_SIZE, PLAYER_SIZE))
            if sprite:
                return sprite
            
            # Fall back to individual file loading
            character_path = f"{ASSETS_DIR}/player-characters/{character_name}"
            return self.load_image(character_path, (PLAYER_SIZE, PLAYER_SIZE))
        else:
            # Fall back to default player.png
            return self.load_image(PLAYER_SPRITE_PATH, (PLAYER_SIZE, PLAYER_SIZE))
    
    def get_available_characters(self):
        """
        Get list of available player character files.
        Checks spritesheet first, then individual files.
        
        Returns:
            List of character filenames (e.g., ['bloemetje.svg', ...])
        """
        characters = []
        
        # Check if we have spritesheet metadata
        if 'player_characters' in self.spritesheet_metadata:
            # Return character names from spritesheet metadata (add .svg extension for compatibility)
            sprite_names = sorted(self.spritesheet_metadata['player_characters']['sprites'].keys())
            characters = [f"{name}.svg" for name in sprite_names]
            print(f"Found {len(characters)} player characters from spritesheet")
            return characters
        
        # Fall back to file scanning
        characters_dir = f"{ASSETS_DIR}/player-characters"
        
        if os.path.exists(characters_dir) and os.path.isdir(characters_dir):
            # Load all SVG files from the player-characters directory
            svg_files = [f for f in os.listdir(characters_dir) 
                        if f.lower().endswith('.svg')]
            
            characters = sorted(svg_files)
            print(f"Found {len(characters)} player characters from directory")
        else:
            print(f"Player characters directory not found: {characters_dir}")
        
        return characters
    
    def get_obstacle_sprite(self, width, height):
        """
        Get obstacle sprite from spritesheet or individual file.
        For 30px base unit (8x8 grid): converts pixel dimensions to grid coordinates.
        Example: 90x60 pixels = 3x2 grid units -> sprite name "3-2"
        
        Args:
            width: Obstacle width in pixels
            height: Obstacle height in pixels
            
        Returns:
            pygame.Surface or None if not found
        """
        # Base unit is 30px (from bar_types.json)
        BASE_UNIT = 30
        
        # Convert pixel dimensions to grid units
        grid_width = round(width / BASE_UNIT)
        grid_height = round(height / BASE_UNIT)
        
        # Sprite name: {width}-{height}
        sprite_name = f"{grid_width}-{grid_height}"
        
        # Try to get from spritesheet first
        sprite = self._get_sprite_from_sheet('obstacles', sprite_name, (width, height))
        if sprite:
            return sprite
        
        # Fall back to individual SVG loading
        svg_filename = f"{sprite_name}.svg"
        svg_path = f"{ASSETS_DIR}/obstacles/extracted-obstacles/{svg_filename}"
        
        # Try to load the exact SVG
        sprite = self.load_image(svg_path, (width, height))
        
        if sprite:
            print(f"✓ Loaded obstacle sprite: {svg_filename} (scaled to {width}x{height}px)")
            return sprite
        
        # If exact size doesn't exist, try to create composite from 1x1 blocks
        # Allow composites for any reasonable size (up to 15x8 for very wide obstacles)
        if grid_width <= 15 and grid_height <= 8:
            sprite = self._create_composite_sprite(grid_width, grid_height, width, height)
            if sprite:
                print(f"✓ Created composite obstacle sprite: {grid_width}x{grid_height} grid (scaled to {width}x{height}px)")
                return sprite
        
        print(f"✗ Obstacle sprite not found: {svg_filename} for {width}x{height}px ({grid_width}x{grid_height} grid)")
        return None
    
    def _create_composite_sprite(self, grid_width, grid_height, target_width, target_height):
        """
        Create a composite sprite by tiling 1x1 blocks.
        
        Args:
            grid_width: Width in grid units
            grid_height: Height in grid units
            target_width: Target width in pixels
            target_height: Target height in pixels
            
        Returns:
            pygame.Surface or None if base block not found
        """
        # Load the 1x1 base block
        base_block_path = f"{ASSETS_DIR}/obstacles/extracted-obstacles/1-1.svg"
        base_block = self.load_image(base_block_path, (30, 30))  # Load at base unit size
        
        if not base_block:
            return None
        
        # Create a surface for the composite
        composite = pygame.Surface((grid_width * 30, grid_height * 30), pygame.SRCALPHA)
        
        # Tile the 1x1 blocks
        for y in range(grid_height):
            for x in range(grid_width):
                composite.blit(base_block, (x * 30, y * 30))
        
        # Convert for optimal performance before scaling
        composite = composite.convert_alpha()
        
        # Scale to target dimensions
        if (grid_width * 30, grid_height * 30) != (target_width, target_height):
            composite = pygame.transform.scale(composite, (target_width, target_height))
        
        return composite
    
    def get_background_image(self):
        """Get background image, returns None to use procedural generation."""
        return self.load_image(BACKGROUND_PATH, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def get_background_images(self):
        """Get all background images from the backgrounds folder."""
        backgrounds = []
        backgrounds_dir = f"{ASSETS_DIR}/backgrounds"
        
        if os.path.exists(backgrounds_dir) and os.path.isdir(backgrounds_dir):
            # Load all image files from the backgrounds directory
            image_files = [f for f in os.listdir(backgrounds_dir) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            
            print(f"Found {len(image_files)} potential background images: {image_files}")
            
            for filename in sorted(image_files):
                path = os.path.join(backgrounds_dir, filename)
                print(f"Attempting to load: {path}")
                bg = self.load_image(path, (SCREEN_WIDTH, SCREEN_HEIGHT))
                if bg:
                    print(f"✓ Successfully loaded: {filename}")
                    backgrounds.append(bg)
                else:
                    print(f"✗ Failed to load: {filename}")
        else:
            print(f"Backgrounds directory not found: {backgrounds_dir}")
        
        # If no backgrounds found, try single background.png
        if len(backgrounds) == 0:
            print("No backgrounds loaded from folder, trying single background.png")
            single_bg = self.get_background_image()
            if single_bg:
                backgrounds.append(single_bg)
        
        print(f"Total backgrounds loaded: {len(backgrounds)}")
        return backgrounds if len(backgrounds) > 0 else None
    
    def get_ground_sprite(self):
        """Get ground sprite for tiling, returns None to use procedural generation."""
        return self.load_image(GROUND_SPRITE_PATH)
    
    def get_hazard_texture(self, hazard_type="lava"):
        """
        Get hazard floor texture.
        
        Args:
            hazard_type: "lava" or "acid"
            
        Returns:
            pygame.Surface or None if not found
        """
        hazard_paths = {
            "lava": f"{ASSETS_DIR}/hazards/lava.jpg",
            "acid": f"{ASSETS_DIR}/hazards/acid.png",
        }
        
        # Default to lava if unknown type
        path = hazard_paths.get(hazard_type, hazard_paths["lava"])
        return self.load_image(path)
    
    def get_midground_decorations(self):
        """
        Get all midground decoration SVGs from cutesy-midground folder.
        These will be rendered with parallax scrolling between background and game objects.
        
        Returns:
            List of tuples: [(surface, filename), ...] or None if no decorations found
        """
        decorations = []
        midground_dir = f"{ASSETS_DIR}/cutesy-midground"
        
        if os.path.exists(midground_dir) and os.path.isdir(midground_dir):
            # Load all SVG files from the midground directory
            svg_files = [f for f in os.listdir(midground_dir) 
                        if f.lower().endswith('.svg')]
            
            print(f"Found {len(svg_files)} midground decorations: {svg_files}")
            
            for filename in sorted(svg_files):
                path = os.path.join(midground_dir, filename)
                # Load SVG and scale to reasonable size (150x150 for decorations)
                decoration = self.load_image(path, (150, 150))
                if decoration:
                    print(f"✓ Loaded midground decoration: {filename}")
                    decorations.append((decoration, filename))
                else:
                    print(f"✗ Failed to load: {filename}")
        else:
            print(f"Midground directory not found: {midground_dir}")
        
        print(f"Total midground decorations loaded: {len(decorations)}")
        return decorations if len(decorations) > 0 else None
    
    def get_obstacle_pattern(self):
        """
        Get obstacle pattern image for tiling across obstacles.
        Pattern is scaled down to 10% of original size for better tiling.
        
        Returns:
            pygame.Surface or None if pattern not found
        """
        pattern_path = f"{ASSETS_DIR}/obstacles/obstacle-pattern-1.png"
        pattern = self.load_image(pattern_path)
        if pattern:
            # Scale down to 10% of original size (reduce by 90%)
            original_width = pattern.get_width()
            original_height = pattern.get_height()
            new_width = int(original_width * 0.1)
            new_height = int(original_height * 0.1)
            pattern = pygame.transform.scale(pattern, (new_width, new_height))
            print(f"✓ Loaded obstacle pattern: obstacle-pattern-1.png (scaled to {new_width}x{new_height})")
        else:
            print(f"✗ Obstacle pattern not found: {pattern_path}")
        return pattern


# Global asset manager instance
asset_manager = AssetManager()
