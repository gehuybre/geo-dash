"""
Game configuration and constants.
Modify these values to customize gameplay.
"""

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors - cute pastel palette
SKY_BLUE = (173, 216, 230)
SKY_LIGHT = (223, 240, 250)
GROUND_GREEN = (144, 238, 144)
GROUND_DARK = (100, 200, 100)
PLAYER_PINK = (255, 182, 193)
PLAYER_OUTLINE = (255, 150, 170)
OBSTACLE_PURPLE = (216, 191, 216)
OBSTACLE_DARK = (180, 150, 180)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 223, 0)
HEART_RED = (255, 105, 180)

# Physics settings
GRAVITY = 0.8
PLAYER_SPEED = 6
JUMP_POWER = -15

# Player settings
GROUND_Y = 450
PLAYER_SIZE = 40
PLAYER_START_X = 100

# Obstacle generation settings
MIN_OBSTACLE_GAP = 200
MAX_OBSTACLE_GAP = 400
MIN_OBSTACLE_HEIGHT = 20
# Max obstacle height is calculated dynamically based on jump physics

# Asset paths
ASSETS_DIR = "assets"
PLAYER_SPRITE_PATH = f"{ASSETS_DIR}/player.png"
OBSTACLE_SPRITE_PATH = f"{ASSETS_DIR}/obstacle.png"
BACKGROUND_PATH = f"{ASSETS_DIR}/background.png"
GROUND_SPRITE_PATH = f"{ASSETS_DIR}/ground.png"

# Visual settings
BACKGROUND_SCROLL_SPEED_MULTIPLIER = 0.3  # Background scrolls at 30% of player speed (parallax effect)

# Debug settings
SHOW_PATTERN_DEBUG = True  # Toggle to show/hide current pattern name

# Game settings
GAME_TITLE = "Cute Geo Dash 🌟"
