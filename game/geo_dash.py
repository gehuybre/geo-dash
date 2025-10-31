"""
Cute Geo Dash - A modular, customizable Geometry Dash clone.
Main game file that coordinates all game systems.
"""

import pygame

# Initialize Pygame first
pygame.init()

from .config import *
from .player import Player
from .obstacles import ObstacleGenerator
from managers.score_manager import ScoreManager
from systems.input_handler import InputHandler


class Game:
    """Main game class coordinating all systems."""
    
    def __init__(self):
        # Import renderer here after pygame is fully initialized
        from .renderer import Renderer
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.difficulty = None  # Will be set by menu
        
        # Show difficulty menu first
        self.difficulty = self.show_difficulty_menu()
        
        # Initialize game systems with selected difficulty
        self.player = Player(PLAYER_START_X, GROUND_Y)
        self.obstacle_generator = ObstacleGenerator(difficulty=self.difficulty)
        self.renderer = Renderer(self.screen)
        self.score_manager = ScoreManager()
        self.input_handler = InputHandler()
    
    def show_difficulty_menu(self):
        """Show difficulty selection menu and return selected difficulty."""
        from .renderer import Renderer
        temp_renderer = Renderer(self.screen)
        
        difficulties = ["easy", "medium", "hard"]
        selected = 1  # Default to medium
        
        menu_running = True
        while menu_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "hard"  # Default
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        selected = (selected - 1) % len(difficulties)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        selected = (selected + 1) % len(difficulties)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        menu_running = False
            
            # Draw menu
            self.screen.fill(SKY_BLUE)
            
            # Title
            if temp_renderer.font_available:
                title_font = pygame.font.Font(None, 72)
                title_text = title_font.render("SELECT DIFFICULTY", True, BLACK)
                title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
                self.screen.blit(title_text, title_rect)
                
                # Options
                option_font = pygame.font.Font(None, 56)
                for i, difficulty in enumerate(difficulties):
                    color = YELLOW if i == selected else WHITE
                    text = option_font.render(difficulty.upper(), True, color)
                    rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 80))
                    self.screen.blit(text, rect)
                    
                    # Draw indicator
                    if i == selected:
                        pygame.draw.polygon(self.screen, YELLOW, [
                            (rect.left - 40, rect.centery),
                            (rect.left - 20, rect.centery - 15),
                            (rect.left - 20, rect.centery + 15)
                        ])
                
                # Instructions
                inst_font = pygame.font.Font(None, 36)
                inst_text = inst_font.render("↑/↓ to select, ENTER to confirm", True, WHITE)
                inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
                self.screen.blit(inst_text, inst_rect)
                
                # Difficulty descriptions
                desc_font = pygame.font.Font(None, 32)
                descriptions = {
                    "easy": "Wider platforms (+25%)",
                    "medium": "Balanced challenge (+15%)",
                    "hard": "Original difficulty"
                }
                desc_text = desc_font.render(descriptions[difficulties[selected]], True, (180, 180, 180))
                desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
                self.screen.blit(desc_text, desc_rect)
            else:
                # Fallback rendering when fonts not available
                temp_renderer._draw_simple_text("SELECT DIFFICULTY", SCREEN_WIDTH // 2 - 180, 150, BLACK, 32)
                
                # Options with simple text
                descriptions = {
                    "easy": "Wider platforms +25%",
                    "medium": "Balanced challenge +15%",
                    "hard": "Original difficulty"
                }
                
                for i, difficulty in enumerate(difficulties):
                    color = YELLOW if i == selected else WHITE
                    y_pos = 300 + i * 80
                    temp_renderer._draw_simple_text(difficulty.upper(), SCREEN_WIDTH // 2 - 60, y_pos, color, 24)
                    
                    # Draw indicator
                    if i == selected:
                        pygame.draw.polygon(self.screen, YELLOW, [
                            (SCREEN_WIDTH // 2 - 100, y_pos + 10),
                            (SCREEN_WIDTH // 2 - 80, y_pos),
                            (SCREEN_WIDTH // 2 - 80, y_pos + 20)
                        ])
                
                # Instructions
                temp_renderer._draw_simple_text("UP/DOWN to select  ENTER to confirm", SCREEN_WIDTH // 2 - 250, 550, WHITE, 18)
                
                # Description for selected difficulty
                temp_renderer._draw_simple_text(descriptions[difficulties[selected]], SCREEN_WIDTH // 2 - 150, 500, (180, 180, 180), 16)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        return difficulties[selected]
        
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
        from .renderer import Renderer
        
        self.game_over = False
        self.player = Player(PLAYER_START_X, GROUND_Y)
        self.obstacle_generator = ObstacleGenerator(difficulty=self.difficulty)
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
        self.renderer.draw_ground()  # Draw ground first
        self.obstacle_generator.draw(self.screen)  # Then obstacles (including lava) on top
        self.player.draw(self.screen)  # Player on top of everything
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


def main():
    """Main entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
