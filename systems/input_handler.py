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
    
    def process_events(self):
        """Process pygame events and update input states."""
        # Reset single-frame events
        self.jump_pressed = False
        self.restart_pressed = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_requested = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.jump_pressed = True
                elif event.key == pygame.K_ESCAPE:
                    self.quit_requested = True
                elif event.key == pygame.K_r:
                    self.restart_pressed = True
    
    def is_quit_requested(self):
        """Check if quit was requested."""
        return self.quit_requested
    
    def is_jump_pressed(self):
        """Check if jump was pressed this frame."""
        return self.jump_pressed
    
    def is_restart_pressed(self):
        """Check if restart was pressed this frame."""
        return self.restart_pressed
