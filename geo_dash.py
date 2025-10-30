"""
Cute Geo Dash - A modular, customizable Geometry Dash clone.
Main game file that coordinates all game systems.
"""

import pygame

# Initialize Pygame first
pygame.init()

from config import *
from player import Player
from obstacles import ObstacleGenerator
from managers.score_manager import ScoreManager
from systems.input_handler import InputHandler


class Game:
    """Main game class coordinating all systems."""
    
    def __init__(self):
        # Import renderer here after pygame is fully initialized
        from renderer import Renderer
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        
        # Initialize game systems
        self.player = Player(PLAYER_START_X, GROUND_Y)
        self.obstacle_generator = ObstacleGenerator()
        self.renderer = Renderer(self.screen)
        self.score_manager = ScoreManager()
        self.input_handler = InputHandler()
        
    def handle_events(self):
        """Process input events."""
        self.input_handler.process_events()
        
        if self.input_handler.is_quit_requested():
            self.running = False
        
        if self.input_handler.is_jump_pressed():
            if not self.game_over:
                self.player.jump()
            else:
                self.reset_game()
        
        if self.input_handler.is_restart_pressed():
            self.reset_game()
    
    def reset_game(self):
        """Reset game to initial state."""
        from renderer import Renderer
        
        self.game_over = False
        self.player = Player(PLAYER_START_X, GROUND_Y)
        self.obstacle_generator = ObstacleGenerator()
        self.renderer = Renderer(self.screen)
        self.score_manager.reset()
    
    def update(self):
        """Update game state."""
        if not self.game_over:
            self.player.update()
            self.obstacle_generator.update()
            self.renderer.update()  # Update background scrolling
            
            # Update distance and score
            self.score_manager.update_distance(PLAYER_SPEED)
            
            # Check collision
            if self.obstacle_generator.check_collision(self.player):
                self.game_over = True
                self.score_manager.check_and_save_high_score()
    
    def draw(self):
        """Draw all game elements."""
        score = self.score_manager.get_score()
        high_score = self.score_manager.get_high_score()
        
        self.renderer.draw_background(score)
        self.renderer.draw_ground()
        self.obstacle_generator.draw(self.screen)
        self.player.draw(self.screen)
        self.renderer.draw_ui(score, high_score, 
                             show_instructions=(score < 5 and not self.game_over),
                             current_pattern=self.obstacle_generator.current_pattern_name)
        
        if self.game_over:
            self.renderer.draw_game_over(score)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
