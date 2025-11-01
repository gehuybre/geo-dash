# 🧗 Celeste Runner

A fast-paced wall-jumping auto-scroller where the floor is lava and survival depends on perfect timing.

## 🎮 How to Play

### The Concept
The screen scrolls relentlessly to the right. Your character can't stop or slow down - you can only **jump between walls** to stay alive. Touch the red floor or fall behind the screen edge, and it's game over.

### Controls
**Only one button!**

- **SPACE** / **↑** / **W** - Jump
  - When touching a wall → Launch wall jump
  - Just after leaving a wall → Coyote time jump
  - Early press → Buffered jump (executed when you hit wall)

**Pause & Menu**
- **ESC** / **P** - Pause game
- **R** - Restart (when paused)

### Wall Mechanics

#### Wall Sliding
When you touch a wall, you automatically grab on and slide down slowly. You have a brief moment (8 frames) where you cling without sliding - use this to time your next jump!

#### Wall Jumping
Press jump while on a wall to launch yourself away from it. The jump pushes you:
- **Horizontally**: Away from the wall (8 pixels/frame)
- **Vertically**: Upward (-14 pixels/frame)

Use wall jumps to chain between walls and keep moving forward!

#### Coyote Time
You have **6 frames** (~100ms) after leaving a wall where you can still execute a wall jump. This makes the controls feel more responsive and forgiving.

#### Jump Buffering
Press jump **up to 5 frames early** and it will be remembered. When you touch the next wall, the jump executes automatically. Great for fast-paced sections!

## 🚀 Running the Game

### Requirements
- Python 3.8+
- Pygame 2.0+

### Installation
```bash
# Clone the repository
cd geo-dash

# Install dependencies
pip install -r requirements.txt

# Run Celeste Runner
python main_celeste.py
```

### Or run the original Geo Dash
```bash
python main.py
```

## 🎯 Gameplay Tips

### For Beginners
1. **Don't panic** - The coyote time and jump buffering are very forgiving
2. **Practice rhythm** - Wall jumping has a natural rhythm once you get the feel
3. **Use wall cling** - Those first 8 frames on a wall let you wait for the perfect moment
4. **Start on Easy** - Wider gaps between walls = more time to react

### Advanced Techniques
1. **Buffer jumps** - Press jump before hitting the wall for instant launches
2. **Ride the coyote** - Leave the wall slightly before jumping for extra horizontal distance
3. **Speed reading** - Learn to read wall patterns ahead and plan your route
4. **Risk vs Reward** - Sometimes waiting on a wall is safer than rushing

## 🧱 Wall Types

### Normal Walls (Gray)
Standard walls - reliable and safe. These make up most of the level.

### Crumbly Walls (Brown)
Start cracking as soon as you touch them! You have **0.5 seconds** before they disappear completely. Don't linger!

### Slippery Walls (Ice Blue)
Reduced friction means you slide down faster. Plan your jumps quickly!

## 📊 Difficulty Levels

### Easy
- Wider gaps between walls (120-200px)
- 90% normal walls
- Fewer hazards
- Great for learning the mechanics

### Medium
- Standard gaps (100-280px)
- 70% normal walls
- Balanced challenge
- **Recommended for most players**

### Hard
- Tighter gaps (80-280px)
- Only 50% normal walls
- Maximum challenge
- For wall-jumping masters

## 🏆 Scoring

Your score is measured in **distance traveled**:
- Every 100 pixels = 1 meter
- No combos or bonuses - just pure survival
- High scores are saved per player
- Try to beat your personal best!

The camera also accelerates over time:
- Starts at 3 pixels/frame
- Increases to maximum 8 pixels/frame
- Makes longer runs increasingly difficult

## 🎨 Game Features

### Visual Feedback
- **Wall highlights** - Walls glow when you're touching them
- **Player rotation** - Spins during jumps, tilts during wall slides
- **Squish & stretch** - Character squashes on wall grabs, stretches on jumps
- **Danger floor** - Bright red with warning stripes - clearly lethal!

### Quality of Life
- **Instant restart** - Press SPACE on game over to try again immediately
- **Persistent high scores** - Track your best runs per player
- **Multiple player profiles** - Compete with friends and family
- **Smooth performance** - 60 FPS with VSync enabled

## 📖 Architecture

### File Structure
```
game/
  celeste_runner.py   # Main game loop and menus
  player_celeste.py   # Wall-jumping player mechanics
  walls.py            # Wall generation and collision
  camera.py           # Auto-scrolling camera system
  config.py           # Game constants and physics

core/
  physics.py          # Wall jump physics calculations

managers/
  score_manager.py    # High score persistence
```

### Design Philosophy

**Celeste Runner** follows these core principles:

1. **One Button, Infinite Depth** - Simple to learn, hard to master
2. **Continuous Momentum** - You never stop moving forward
3. **Precision Under Pressure** - The auto-scroll forces perfect timing
4. **Readable Fairness** - Every death should feel earned, not cheap

See [CELESTE_RUNNER_DESIGN.md](md-files/CELESTE_RUNNER_DESIGN.md) for full design documentation.

## 🔧 Configuration

Edit `game/config.py` to customize:

### Physics
```python
GRAVITY = 0.8                # Falling speed
WALL_SLIDE_GRAVITY = 0.2     # Wall sliding speed
WALL_JUMP_X_FORCE = 8        # Horizontal wall jump force
WALL_JUMP_Y_FORCE = -14      # Vertical wall jump force
```

### Auto-Scroll
```python
AUTO_SCROLL_SPEED = 3              # Initial camera speed
AUTO_SCROLL_ACCELERATION = 0.002   # Speed increase rate
MAX_AUTO_SCROLL_SPEED = 8          # Maximum camera speed
```

### Wall Generation
```python
MIN_WALL_GAP = 100          # Minimum gap between walls
MAX_WALL_GAP = 280          # Maximum gap between walls
MIN_WALL_HEIGHT = 60        # Minimum wall height
MAX_WALL_HEIGHT = 400       # Maximum wall height
```

**Warning**: Changing physics constants may make levels unbeatable! The wall generator validates all gaps against the physics system.

## 🐛 Troubleshooting

### Game runs too fast/slow
- Check VSync is enabled in `config.py`: `VSYNC = True`
- Ensure FPS is set to 60: `FPS = 60`

### Can't see fonts
- Custom fonts fallback to system Arial automatically
- Check `assets/fonts/` directory for font files

### Collision feels off
- Adjust `WALL_WIDTH` in `config.py` (default: 30px)
- Adjust coyote time: `WALL_JUMP_COYOTE_TIME` (default: 6 frames)

### Too difficult
- Start on Easy mode
- Increase `WALL_JUMP_COYOTE_TIME` for more forgiveness
- Increase `WALL_CLING_TIME` for longer wall grabs

## 🎯 Future Ideas

### Potential Features
- **Power-ups**: Double jump, dash, temporary slow-mo
- **Collectibles**: Optional orbs for bonus points
- **Checkpoints**: Save progress in marathon runs
- **Challenge mode**: Handcrafted difficult sequences
- **Leaderboards**: Online high score competition
- **Custom levels**: Level editor for community creations

### Additional Wall Types
- **Boost walls**: Launch player higher/further
- **Moving walls**: Shift vertically while player slides
- **Conveyor walls**: Push player up or down
- **Dash walls**: Grant temporary dash ability

## 🙏 Credits

Inspired by:
- **Celeste** - Wall mechanics and coyote time
- **Temple Run** - Auto-scroll pressure
- **Geometry Dash** - One-button simplicity
- **Super Meat Boy** - Tight controls and instant retry

## 📝 License

This project is open source. Feel free to modify and extend it!

## 🎮 Have Fun!

The key to mastering Celeste Runner is **rhythm**. Once you find the flow of wall jump → fall → grab → jump, you'll start seeing the walls as a dance floor rather than obstacles.

Don't give up! Every death teaches you something about timing and spacing.

**Good luck, and may your wall jumps be ever true! 🧗‍♀️**

---

**Version**: 1.0  
**Last Updated**: November 2025
