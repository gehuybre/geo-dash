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
from .visual_effects import VisualEffectsManager
from managers.score_manager import ScoreManager
from systems.input_handler import InputHandler


class Game:
    """Main game class coordinating all systems."""
    
    def __init__(self):
        # Import renderer here after pygame is fully initialized
        from .renderer import Renderer
        
        # Set up borderless fullscreen window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.paused = False
        self.pause_menu_option = 0  # 0=Resume, 1=Restart, 2=Difficulty, 3=Main Menu
        self.difficulty = None  # Will be set by menu
        self.player_name = None  # Will be set by name selection
        
        # Show player name selection first
        self.player_name = self.show_name_selection()
        
        # Show difficulty menu
        self.difficulty = self.show_difficulty_menu()
        
        # Initialize game systems with selected difficulty and player name
        self.player = Player(PLAYER_START_X, GROUND_Y)
        self.obstacle_generator = ObstacleGenerator(difficulty=self.difficulty)
        self.renderer = Renderer(self.screen)
        self.score_manager = ScoreManager(player_name=self.player_name)
        self.input_handler = InputHandler()
        
        # Visual effects manager
        self.effects = VisualEffectsManager()
    
    def show_name_selection(self):
        """Show player name selection menu and return selected/entered name."""
        from .renderer import Renderer
        temp_renderer = Renderer(self.screen)
        
        # Load existing players from score manager
        temp_score = ScoreManager()
        existing_players = temp_score.get_all_players()
        player_names = [name for name, _ in existing_players] if existing_players else []
        
        # Add "New Player" option
        options = player_names + ["+ New Player"]
        selected = 0
        input_mode = False  # Are we typing a new name?
        new_name = ""
        
        menu_running = True
        while menu_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "Guest"
                
                if event.type == pygame.KEYDOWN:
                    if input_mode:
                        # Typing new name
                        if event.key == pygame.K_RETURN and len(new_name) > 0:
                            menu_running = False
                        elif event.key == pygame.K_ESCAPE:
                            input_mode = False
                            new_name = ""
                        elif event.key == pygame.K_BACKSPACE:
                            new_name = new_name[:-1]
                        elif event.unicode.isalnum() or event.unicode in (' ', '-', '_'):
                            if len(new_name) < 15:  # Max 15 characters
                                new_name += event.unicode
                    else:
                        # Selecting from list
                        if event.key == pygame.K_UP:
                            selected = (selected - 1) % len(options)
                        elif event.key == pygame.K_DOWN:
                            selected = (selected + 1) % len(options)
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            if selected == len(options) - 1:  # "New Player"
                                input_mode = True
                                new_name = ""
                            else:
                                return player_names[selected]
            
            # Draw menu
            self.screen.fill(SKY_BLUE)
            
            if temp_renderer.font_available:
                title_font = pygame.font.SysFont('Comic Sans MS', 60)
                title_text = title_font.render("SELECT PLAYER", True, BLACK)
                title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
                self.screen.blit(title_text, title_rect)
                
                if input_mode:
                    # Show input box
                    prompt_font = pygame.font.SysFont('Comic Sans MS', 40)
                    prompt_text = prompt_font.render("Enter your name:", True, BLACK)
                    prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
                    self.screen.blit(prompt_text, prompt_rect)
                    
                    # Input box
                    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 50)
                    pygame.draw.rect(self.screen, WHITE, input_box)
                    pygame.draw.rect(self.screen, BLACK, input_box, 3)
                    
                    # Show typed name
                    name_font = pygame.font.SysFont('Comic Sans MS', 36)
                    name_text = name_font.render(new_name + "|", True, BLACK)
                    name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, 325))
                    self.screen.blit(name_text, name_rect)
                    
                    # Instructions
                    hint_font = pygame.font.SysFont('Comic Sans MS', 24)
                    hint_text = hint_font.render("Press ENTER to confirm, ESC to cancel", True, (100, 100, 100))
                    hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
                    self.screen.blit(hint_text, hint_rect)
                else:
                    # Show player list
                    option_font = pygame.font.SysFont('Comic Sans MS', 40)
                    for i, option in enumerate(options):
                        y_pos = 220 + i * 60
                        
                        # Show high score for existing players
                        if i < len(player_names):
                            score = existing_players[i][1]
                            text = f"{option} (Best: {score})"
                        else:
                            text = option
                        
                        color = YELLOW if i == selected else BLACK
                        option_text = option_font.render(text, True, color)
                        option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
                        self.screen.blit(option_text, option_rect)
                        
                        # Selection indicator
                        if i == selected:
                            pygame.draw.polygon(self.screen, YELLOW, [
                                (option_rect.left - 40, y_pos),
                                (option_rect.left - 20, y_pos - 15),
                                (option_rect.left - 20, y_pos + 15)
                            ])
                    
                    # Instructions
                    hint_font = pygame.font.SysFont('Comic Sans MS', 24)
                    hint_text = hint_font.render("UP/DOWN to select, ENTER to confirm", True, (100, 100, 100))
                    hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
                    self.screen.blit(hint_text, hint_rect)
            else:
                # Fallback text rendering
                temp_renderer._draw_simple_text("SELECT PLAYER", SCREEN_WIDTH // 2 - 120, 100, BLACK, 24)
                
                if input_mode:
                    temp_renderer._draw_simple_text("Enter your name:", SCREEN_WIDTH // 2 - 120, 250, BLACK, 18)
                    temp_renderer._draw_simple_text(new_name + "|", SCREEN_WIDTH // 2 - 100, 320, BLACK, 20)
                    temp_renderer._draw_simple_text("ENTER=confirm ESC=cancel", SCREEN_WIDTH // 2 - 140, 400, (100, 100, 100), 14)
                else:
                    for i, option in enumerate(options):
                        y_pos = 220 + i * 50
                        if i < len(player_names):
                            score = existing_players[i][1]
                            text = f"{option} ({score})"
                        else:
                            text = option
                        color = YELLOW if i == selected else BLACK
                        temp_renderer._draw_simple_text(text, SCREEN_WIDTH // 2 - 100, y_pos, color, 18)
                    
                    temp_renderer._draw_simple_text("UP/DOWN ENTER", SCREEN_WIDTH // 2 - 100, 500, (100, 100, 100), 14)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        return new_name if new_name else "Guest"
    
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
        
        # Handle pause menu
        if self.input_handler.is_pause_pressed():
            if not self.game_over:
                self.paused = not self.paused  # Toggle pause
                if not self.paused:
                    self.pause_menu_option = 0  # Reset selection when unpausing
        
        if self.paused:
            # Navigate pause menu
            if self.input_handler.is_up_pressed():
                self.pause_menu_option = (self.pause_menu_option - 1) % 4
            elif self.input_handler.is_down_pressed():
                self.pause_menu_option = (self.pause_menu_option + 1) % 4
            elif self.input_handler.is_select_pressed():
                self.handle_pause_menu_selection()
        elif not self.game_over:
            # Normal gameplay
            if self.input_handler.is_jump_pressed():
                self.player.jump()
        else:
            # Game over - restart on space
            if self.input_handler.is_jump_pressed():
                self.reset_game()
        
        if self.input_handler.is_restart_pressed():
            self.reset_game()
    
    def handle_pause_menu_selection(self):
        """Handle pause menu option selection."""
        if self.pause_menu_option == 0:  # Resume
            self.paused = False
        elif self.pause_menu_option == 1:  # Restart
            self.reset_game()
            self.paused = False
        elif self.pause_menu_option == 2:  # Select Difficulty
            self.paused = False
            self.difficulty = self.show_difficulty_menu()
            self.reset_game()
        elif self.pause_menu_option == 3:  # Main Menu (restart with difficulty select)
            self.paused = False
            self.difficulty = self.show_difficulty_menu()
            self.reset_game()

    
    def reset_game(self):
        """Reset game to initial state."""
        from .renderer import Renderer
        
        self.game_over = False
        self.player = Player(PLAYER_START_X, GROUND_Y)
        self.obstacle_generator = ObstacleGenerator(difficulty=self.difficulty)
        self.renderer = Renderer(self.screen)
        self.score_manager.reset()
        self.effects.clear()  # Clear all visual effects
    
    def update(self):
        """Update game state."""
        if not self.game_over and not self.paused:
            # Track previous combo for comparison
            previous_combo = self.player.combo_streak
            
            self.player.update()
            self.obstacle_generator.update()
            self.renderer.update()  # Update background scrolling
            
            # Update distance and score
            self.score_manager.update_distance(PLAYER_SPEED)
            
            # Award landing bonus if player just landed (with combo multiplier)
            if self.player.just_landed:
                bonus_points = self.score_manager.add_landing_bonus(self.player.combo_streak)
                
                # Create floating combo number popup
                self.effects.add_score_popup(
                    self.player.x + self.player.width // 2,
                    self.player.y - 20,
                    bonus_points,
                    self.player.combo_streak
                )
                
                # Show streak indicator for combos of 3+
                if self.player.combo_streak >= 3:
                    self.effects.add_streak_indicator(self.player.combo_streak)
            
            # Check if streak was broken (combo went from high to 0)
            if previous_combo >= 3 and self.player.combo_streak == 0:
                self.effects.add_streak_broken(
                    self.player.x + self.player.width // 2,
                    self.player.y - 40,
                    previous_combo
                )
            
            # Update visual effects
            self.effects.update()
            
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
        
        # Draw all visual effects (popups, streaks, particles)
        self.effects.draw(self.screen)
        
        self.renderer.draw_ui(score, high_score, 
                             show_instructions=(score < 5 and not self.game_over and not self.paused),
                             current_pattern=self.obstacle_generator.current_pattern_name,
                             player_name=self.player_name)
        
        if self.paused:
            self.renderer.draw_pause_menu(self.pause_menu_option)
        elif self.game_over:
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
