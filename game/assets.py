"""
Asset management system for loading custom sprites and images.
Falls back to procedural generation if assets are not found.
"""

import pygame
import os
from .config import *

# Try to import PIL for better image loading support
try:
    from PIL import Image as PILImage
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: PIL/Pillow not available, only BMP files supported")


class AssetManager:
    """Manages loading and caching of game assets."""
    
    def __init__(self):
        self.assets = {}
        self.use_custom_assets = True
        
    def load_image(self, path, size=None):
        """
        Load an image from the given path.
        Uses PIL/Pillow if available for better format support.
        
        Args:
            path: Path to the image file
            size: Optional tuple (width, height) to resize the image
            
        Returns:
            pygame.Surface or None if file not found
        """
        if path in self.assets:
            return self.assets[path]
        
        if not os.path.exists(path):
            return None
        
        try:
            # If PIL is available, use it to load and convert images
            if HAS_PIL and not path.lower().endswith('.bmp'):
                pil_image = PILImage.open(path)
                # Convert to RGB mode
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                # Resize if requested
                if size:
                    pil_image = pil_image.resize(size, PILImage.Resampling.LANCZOS)
                # Convert PIL image to pygame surface
                mode = pil_image.mode
                size_tuple = pil_image.size
                data = pil_image.tobytes()
                image = pygame.image.fromstring(data, size_tuple, mode)
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
            
            self.assets[path] = image
            return image
        except (pygame.error, Exception) as e:
            print(f"Could not load image {path}: {e}")
            return None
    
    def get_player_sprite(self):
        """Get player sprite, returns None to use procedural generation."""
        return self.load_image(PLAYER_SPRITE_PATH, (PLAYER_SIZE, PLAYER_SIZE))
    
    def get_obstacle_sprite(self, width, height):
        """Get obstacle sprite, returns None to use procedural generation."""
        sprite = self.load_image(OBSTACLE_SPRITE_PATH)
        if sprite:
            return pygame.transform.scale(sprite, (width, height))
        return None
    
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


# Global asset manager instance
asset_manager = AssetManager()
