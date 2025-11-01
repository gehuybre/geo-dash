"""
Game configuration and constants.
Modify these values to customize gameplay.
Celeste Runner - Wall-jumping auto-scroller edition.
"""

# Screen settings
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 60

# Performance settings
ENABLE_DIRTY_RECTS = False  # Experimental: only update changed regions
VSYNC = True  # Enable VSync for smoother frame pacing
HARDWARE_ACCEL = True  # Use hardware acceleration if available

# Colors - adapted for wall-jumping aesthetic
SKY_BLUE = (173, 216, 230)
SKY_LIGHT = (223, 240, 250)
GROUND_DANGER = (200, 50, 50)  # Lethal floor color
GROUND_DARK = (150, 30, 30)
PLAYER_PINK = (255, 182, 193)
PLAYER_OUTLINE = (255, 150, 170)
WALL_COLOR = (180, 180, 200)  # Neutral wall color
WALL_HIGHLIGHT = (220, 220, 240)  # Wall when player can grab
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 223, 0)
DEATH_RED = (255, 50, 50)

# Core Physics - Celeste Runner Style
GRAVITY = 0.8  # Falling gravity
WALL_SLIDE_GRAVITY = 0.2  # Slower gravity while sliding on wall
WALL_JUMP_X_FORCE = 8  # Horizontal speed when jumping off wall
WALL_JUMP_Y_FORCE = -14  # Vertical speed when jumping off wall
AIR_RESISTANCE = 0.96  # Multiplier for horizontal velocity each frame

# Auto-scroll settings
AUTO_SCROLL_SPEED = 3  # Camera moves right automatically (pixels/frame)
AUTO_SCROLL_ACCELERATION = 0.002  # Speed increases over time
MAX_AUTO_SCROLL_SPEED = 8  # Maximum scroll speed

# Player settings
GROUND_Y = 750  # Y position of lethal floor
PLAYER_SIZE = 40
PLAYER_START_X = 200  # Start position (camera-relative)

# Wall mechanics
WALL_CLING_TIME = 8  # Frames player can cling to wall before sliding
WALL_JUMP_COYOTE_TIME = 6  # Frames after leaving wall to still wall-jump
WALL_WIDTH = 30  # Default wall thickness
MIN_WALL_HEIGHT = 60  # Minimum wall height to grab
MAX_WALL_HEIGHT = 400  # Maximum wall height

# Level generation settings
MIN_WALL_GAP = 100  # Minimum horizontal distance between walls
MAX_WALL_GAP = 280  # Maximum horizontal distance between walls
WALL_SPAWN_DISTANCE = SCREEN_WIDTH + 200  # Spawn walls this far ahead

# Asset paths
ASSETS_DIR = "assets"
PLAYER_SPRITE_PATH = f"{ASSETS_DIR}/player.png"
WALL_SPRITE_PATH = f"{ASSETS_DIR}/wall.png"
BACKGROUND_PATH = f"{ASSETS_DIR}/background.png"

# Font paths
FONT_DIR = f"{ASSETS_DIR}/fonts"
FONT_REGULAR = f"{FONT_DIR}/Mochibop-Demo.ttf"
FONT_BOLD = f"{FONT_DIR}/MochibopBold-Demo.ttf"

# Visual settings
BACKGROUND_SCROLL_SPEED_MULTIPLIER = 0.3  # Background parallax

# Debug settings
SHOW_DEBUG_INFO = True  # Show wall positions, player state, etc.

# Game settings
GAME_TITLE = "Celeste Runner 🧗"
