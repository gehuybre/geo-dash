"""
Input handling for game controls.
"""

import pygame


class InputHandler:
    """Handles keyboard and other input events."""
    
    def __init__(self):
        self.quit_requested = False
        self.jump_pressed = False
        self.restart_pressed = False
        self.pause_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.select_pressed = False
    
    def process_events(self):
        """Process pygame events and update input states."""
        # Reset single-frame events
        self.jump_pressed = False
        self.restart_pressed = False
        self.pause_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.select_pressed = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_requested = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.jump_pressed = True
                    self.select_pressed = True  # Space also selects in menus
                elif event.key == pygame.K_ESCAPE:
                    self.pause_pressed = True  # ESC toggles pause, doesn't quit
                elif event.key == pygame.K_r:
                    self.restart_pressed = True
                elif event.key == pygame.K_UP:
                    self.up_pressed = True
                elif event.key == pygame.K_DOWN:
                    self.down_pressed = True
    
    def is_quit_requested(self):
        """Check if quit was requested."""
        return self.quit_requested
    
    def is_jump_pressed(self):
        """Check if jump was pressed this frame."""
        return self.jump_pressed
    
    def is_restart_pressed(self):
        """Check if restart was pressed this frame."""
        return self.restart_pressed
    
    def is_pause_pressed(self):
        """Check if pause was pressed this frame."""
        return self.pause_pressed
    
    def is_up_pressed(self):
        """Check if up arrow was pressed this frame."""
        return self.up_pressed
    
    def is_down_pressed(self):
        """Check if down arrow was pressed this frame."""
        return self.down_pressed
    
    def is_select_pressed(self):
        """Check if select (space) was pressed this frame."""
        return self.select_pressed
