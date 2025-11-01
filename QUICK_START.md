# 🚀 Quick Start - Celeste Runner

## Play Now!

```bash
# Navigate to project directory
cd /Users/gerthuybrechts/projects/geo-dash

# Activate virtual environment
source .venv/bin/activate  # or .venv/bin/activate on macOS/Linux

# Run Celeste Runner
python main_celeste.py
```

## First Time Setup

Already done! Your environment is ready to go.

## Controls

**ONE BUTTON**: `SPACE` (or `↑` or `W`)

That's it! The jump is context-aware:
- On wall → Wall jump
- In air → Uses coyote time if available
- Early press → Buffered for next wall

**Pause**: `ESC` or `P`

## Quick Tips

### 1. Don't Panic
You have generous coyote time (100ms) and jump buffering. The controls are more forgiving than they look!

### 2. Find the Rhythm
Wall jump → fall → grab → jump. Once you feel the rhythm, you'll start flowing.

### 3. Use Wall Cling
You cling to walls for 8 frames before sliding. Use this time to:
- Wait for the next wall to come into view
- Time your jump perfectly
- Catch your breath

### 4. Buffer Your Jumps
Press jump BEFORE you hit the wall. The game remembers your input for 5 frames and executes it automatically when you touch the wall. This keeps momentum high!

### 5. Watch the Floor
The red striped floor is INSTANT DEATH. Don't touch it!

### 6. Read Ahead
Look at the walls coming up, not just the one you're on. Plan your route 2-3 walls ahead.

## What's Your Goal?

**Survive as long as possible!**

- Score = distance in meters (100 pixels = 1m)
- Camera accelerates over time (gets faster the longer you survive)
- Try to beat your high score

## Difficulty Levels

- **Easy**: Wider gaps, more time to react
- **Medium**: Balanced challenge (recommended)
- **Hard**: Tight gaps, fast pace, many hazards

## Wall Types

- **Gray walls**: Normal, reliable
- **Brown walls**: Crumble after 0.5 seconds - don't stay!
- **Ice blue walls**: Slippery, slide faster

## What If I Die?

Press `SPACE` to instantly restart. No menus, no loading - just try again!

Death is part of learning. Each run teaches you something about timing and spacing.

## Want the Original Game?

```bash
python main.py
```

This runs the original Geo Dash (jump-over-obstacles style).

## Need Help?

See full documentation:
- **How to Play**: `CELESTE_RUNNER_README.md`
- **Design Details**: `md-files/CELESTE_RUNNER_DESIGN.md`
- **What Changed**: `TRANSFORMATION_SUMMARY.md`

## First Run Checklist

- [ ] Game loads and shows difficulty menu
- [ ] Walls appear on screen
- [ ] Player responds to SPACE key
- [ ] Wall jumping feels responsive
- [ ] Death happens when touching red floor
- [ ] Score increases as you progress

If any of these fail, check terminal output for errors.

## Troubleshooting

### Game too fast/slow
Edit `game/config.py`:
```python
AUTO_SCROLL_SPEED = 2  # Lower = slower (default: 3)
```

### Too difficult
Edit `game/config.py`:
```python
WALL_JUMP_COYOTE_TIME = 10  # More forgiveness (default: 6)
WALL_CLING_TIME = 15         # Longer wall cling (default: 8)
```

### Can't reach walls
Edit `game/config.py`:
```python
WALL_JUMP_X_FORCE = 10  # More horizontal power (default: 8)
```

## Have Fun! 🎮

Remember: **The floor is lava, the walls are your friends.**

Good luck! 🧗‍♀️
