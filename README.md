# 🌟 Cute Geo Dash

A cute, pastel-colored version of Geometry Dash built with Pygame! Now with **modular architecture**, **custom asset support**, and **physics-based validation**!

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.6.1-green)

## ✨ Features

- 🎮 Simple gameplay with double jump mechanic (SPACE to jump)
- 🎨 Adorable pastel graphics with cute character
- 🏃 Automatic forward movement
- 🎯 18 obstacle patterns validated for playability
- 📊 **Distance-based scoring** - earn 1 point per 100 pixels traveled
- 💾 **High score persistence** - scores saved automatically to JSON
- 🎭 **Obstacle patterns system** - define custom obstacle sequences
- ☁️ Animated clouds and grass details
- ✨ Sparkle effects on obstacles
- 🖼️ **Custom asset support** - use your own sprites and backgrounds!
- 🌅 **Parallax scrolling backgrounds** - smooth multi-layer depth
- 🧩 **Modular codebase** - easy to modify and extend
- ⏫ **Double jump** - second jump at 90% power for advanced movement
- 🏔️ **Climbable mountains** - stack obstacles to create towers

## 📁 Project Structure

```
geo-dash/
├── game/                # Core game modules
│   ├── geo_dash.py     # Main game class
│   ├── config.py       # Game settings and constants
│   ├── player.py       # Player character module
│   ├── obstacles.py    # Obstacle generation
│   ├── renderer.py     # Rendering and visual effects
│   └── assets.py       # Asset loading system
├── generators/          # Modular pattern generation
│   ├── physics_engine.py     # Physics calculations
│   ├── obstacle_builders.py  # Pattern building blocks
│   ├── pattern_library.py    # Pre-designed patterns
│   └── main.py              # Generator entry point
├── core/                # Game physics
│   └── physics.py      # Jump physics calculations
├── managers/            # Game state managers
│   ├── pattern_manager.py    # Pattern loading/validation
│   ├── bar_type_manager.py   # Bar type resolution
│   └── score_manager.py      # Scoring and persistence
├── systems/             # Game systems
│   └── input_handler.py      # Input processing
├── data/                # Configuration and save data
│   ├── bar_types.json  # Bar type definitions
│   └── save_data.json  # High score storage
├── assets/              # Game assets
│   ├── backgrounds/    # Background images
│   ├── obstacles/      # Obstacle sprites
│   └── player-characters/  # Player sprites
├── obstacle_patterns/   # JSON pattern definitions
├── archive/             # Old generators and patterns
├── md-files/           # Documentation
├── main.py             # Game entry point
└── requirements.txt    # Dependencies
```
├── assets/              # Custom sprites folder
│   ├── README.md       # Asset customization guide
│   ├── backgrounds/    # Multiple background images
│   ├── player.png      # (optional) Custom player sprite
│   ├── obstacle.png    # (optional) Custom obstacle sprite
│   └── ground.png      # (optional) Custom ground texture
├── obstacle_patterns/   # Obstacle pattern definitions
│   ├── README.md       # Pattern format guide
│   ├── basic_stairs.json
│   ├── double_jump.json
│   ├── spike_valley.json
│   └── speed_test.json
└── docs/               # Documentation files
```

## 🚀 Installation

1. Make sure you have Python 3.7+ installed
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎮 How to Play

1. Run the game:
```bash
python main.py
```

2. Select difficulty (Easy/Medium/Hard)
3. Press **SPACE** to jump over obstacles
4. Try to get the highest score possible!
5. Press **ESC** to quit or **R** to restart

## 🎨 Customization

### Easy Configuration

Edit `game/config.py` to customize gameplay:

```python
# Physics settings
GRAVITY = 0.8           # How fast player falls
PLAYER_SPEED = 6        # Scrolling speed
JUMP_POWER = -15        # Jump height

# Obstacle settings
MIN_OBSTACLE_GAP = 200  # Minimum space between obstacles
MAX_OBSTACLE_GAP = 400  # Maximum space between obstacles

# Colors
PLAYER_PINK = (255, 182, 193)
SKY_BLUE = (173, 216, 230)
# ... and more!
```

### Custom Assets

Add your own sprites to personalize the game!

1. **Navigate to the `assets/` folder**
2. **Add your images** with these exact names:
   - `player.png` - Custom player sprite (40x40px recommended)
   - `obstacle.png` - Custom obstacle sprite
   - `background.png` - Custom background (800x600px)
   - `ground.png` - Custom ground texture (will be tiled)

3. **Run the game** - it automatically loads your custom assets!

**Note:** If an asset is missing, the game uses cute built-in graphics. Mix and match!

See `assets/README.md` for detailed asset specifications.

## 🎯 Controls

- **SPACE** - Jump (or restart after game over)
- **R** - Restart game
- **ESC** - Quit game
- **↑/↓** - Navigate difficulty menu

## 🎲 Game Mechanics

- The player moves automatically from left to right
- Obstacles use **physics-validated patterns** (guaranteed playable)
- All obstacles are **guaranteed to be jumpable** based on the player's jump physics
- **Distance-based scoring** - earn 1 point per 100 pixels traveled
- **High score persistence** - your best score is automatically saved
- Backgrounds cycle every 5 points with smooth parallax scrolling
- The game ends when you collide with an obstacle

## 🎨 Pattern Generator

Generate new obstacle patterns with the modular pattern generator:

```bash
python -m generators.main
```

This creates physics-validated patterns in `obstacle_patterns/` with 3 difficulty variants each (easy/medium/hard).

**Features:**
- 10 unique pattern types (steady rhythm, wave rider, quick hops, etc.)
- Automatic physics validation (all jumps are provably completable)
- Difficulty scaling (+25% width for easy, +15% for medium)
- Modular architecture for easy customization

See `generators/README.md` for details on creating custom patterns.

### 🐛 Debug Mode

The game displays the current pattern name in the top-left corner to help you identify which patterns are fun or too difficult:

- **Toggle debug display**: Edit `config.py` and set `SHOW_PATTERN_DEBUG = False` to hide pattern names
- Pattern names appear in purple text below the score
- Use this to track which patterns you enjoy or find challenging!

## 🎭 Obstacle Patterns

Create custom obstacle sequences in the `obstacle_patterns/` folder:

```json
{
  "name": "Your Pattern",
  "description": "What it does",
  "obstacles": [
    {
      "height": 60,
      "width": 30,
      "gap_after": 180
    }
  ]
}
```

**Built-in patterns:**
- **Basic Stairs** - Ascending difficulty
- **Double Jump** - Consecutive jumps
- **Spike Valley** - Tall-short-tall sequence
- **Speed Test** - Rapid obstacles

The game automatically loads all JSON files from `obstacle_patterns/` and uses them with random generation for varied gameplay!

## 🔧 Code Architecture

The game is built with a modular architecture:

- **`config.py`** - All game constants and settings in one place
- **`assets.py`** - Asset manager with automatic fallback to procedural graphics
- **`player.py`** - Player physics and rendering
- **`obstacles.py`** - Obstacle generation and collision system
- **`renderer.py`** - All drawing operations (background, UI, effects)
- **`geo_dash.py`** - Main game loop coordinating all systems

This makes it easy to:
- Modify game behavior by editing config values
- Add new features by extending existing modules
- Swap out graphics by adding custom assets
- Understand and learn from the codebase

## 🛠️ Development

Want to extend the game? Here are some ideas:

- Add new obstacle types in `obstacles.py`
- Create power-ups in a new `powerups.py` module
- Add sound effects using pygame.mixer
- Implement different difficulty levels
- Create new player abilities
- Add particle effects

The modular structure makes adding features straightforward!

## � Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get playing and customizing in minutes!
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Full developer guide for extending the game
- **[CUSTOMIZATION_EXAMPLES.md](CUSTOMIZATION_EXAMPLES.md)** - Ideas and examples for custom assets
- **[assets/README.md](assets/README.md)** - Technical specifications for asset files

## �📝 License

Feel free to use, modify, and share this game!

Enjoy playing! 🎉
