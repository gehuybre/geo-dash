#!/usr/bin/env python3
"""
Celeste Runner - Main Entry Point

A wall-jumping auto-scroller platformer inspired by Celeste and Temple Run.

The floor is lava! Wall jump your way to survival as the screen scrolls
relentlessly to the right. Miss a wall and fall behind, or touch the ground,
and it's game over.

Controls:
  SPACE/UP/W - Jump (context-aware: wall jump if on wall, otherwise air jump)
  ESC/P - Pause
  
Usage:
    python main_celeste.py
"""

if __name__ == "__main__":
    from game.celeste_runner import main
    main()
