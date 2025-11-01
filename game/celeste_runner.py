"""
Celeste Runner - Main game file.
A wall-jumping auto-scroller platformer.
"""

import pygame
import os

# Initialize Pygame first
pygame.init()

from .config import *
from .player_celeste import Player
from .walls import WallGenerator
from .camera import Camera
from managers.score_manager import ScoreManager


def _load_font(size, bold=False):
    """Helper to load custom font or fallback to system font."""
    try:
        font_path = FONT_BOLD if bold and os.path.exists(FONT_BOLD) else FONT_REGULAR
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
        else:
            return pygame.font.SysFont('Arial', size, bold=bold)
    except:
        return pygame.font.SysFont('Arial', size, bold=bold)


class Game:
    """Main game class for Celeste Runner."""
    
    def __init__(self):
        # Set up display
        display_flags = pygame.SCALED
        if VSYNC:
            display_flags |= pygame.SCALED
        if HARDWARE_ACCEL:
            display_flags |= pygame.HWSURFACE | pygame.DOUBLEBUF
        
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            display_flags,
            vsync=1 if VSYNC else 0
        )
        pygame.display.set_caption(GAME_TITLE)
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.paused = False
        
        # Show difficulty menu
        self.difficulty = self.show_difficulty_menu()
        
        # Show player name selection
        self.player_name = self.show_name_selection()
        
        # Initialize game systems
        self.reset_game()
        
        print(f"🎮 Celeste Runner initialized")
        print(f"   Player: {self.player_name}")
        print(f"   Difficulty: {self.difficulty}")
    
    def reset_game(self):
        """Reset game to initial state."""
        self.player = Player(PLAYER_START_X, GROUND_Y - 200)
        self.camera = Camera()
        self.wall_generator = WallGenerator(difficulty=self.difficulty)
        self.score_manager = ScoreManager(player_name=self.player_name)
        self.game_over = False
        self.death_reason = ""
    
    def show_difficulty_menu(self):
        """Show difficulty selection menu."""
        difficulties = ["easy", "medium", "hard"]
        difficulty_labels = {
            "easy": "MAKKELIJK",
            "medium": "GEMIDDELD",
            "hard": "MOEILIJK"
        }
        descriptions = {
            "easy": "Meer ruimte tussen muren",
            "medium": "Uitdaging in balans",
            "hard": "Maximale moeilijkheid"
        }
        
        selected = 1  # Default to medium
        
        menu_running = True
        while menu_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "medium"
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(difficulties)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(difficulties)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        menu_running = False
            
            # Draw menu
            self.screen.fill(SKY_BLUE)
            
            try:
                title_font = _load_font(60, bold=True)
                title_text = title_font.render("KIES MOEILIJKHEID", True, BLACK)
                title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
                self.screen.blit(title_text, title_rect)
                
                # Options
                option_font = _load_font(48, bold=True)
                for i, difficulty in enumerate(difficulties):
                    color = YELLOW if i == selected else WHITE
                    text = option_font.render(difficulty_labels[difficulty], True, color)
                    rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 80))
                    self.screen.blit(text, rect)
                    
                    if i == selected:
                        # Draw arrow
                        pygame.draw.polygon(self.screen, YELLOW, [
                            (rect.left - 40, rect.centery),
                            (rect.left - 20, rect.centery - 15),
                            (rect.left - 20, rect.centery + 15)
                        ])
                
                # Description
                desc_font = _load_font(28)
                desc_text = desc_font.render(descriptions[difficulties[selected]], True, (100, 100, 100))
                desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, 520))
                self.screen.blit(desc_text, desc_rect)
                
                # Instructions
                inst_font = _load_font(24)
                inst_text = inst_font.render("↑↓ om te kiezen, ENTER om te bevestigen", True, (80, 80, 80))
                inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
                self.screen.blit(inst_text, inst_rect)
            except:
                # Fallback if fonts fail
                pass
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        return difficulties[selected]
    
    def show_name_selection(self):
        """Show player name selection menu."""
        temp_score = ScoreManager()
        existing_players = temp_score.get_all_players()
        player_names = [name for name, _ in existing_players] if existing_players else []
        
        options = player_names + ["+ Nieuwe Speler"]
        selected = 0
        input_mode = False
        new_name = ""
        
        menu_running = True
        while menu_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "Guest"
                
                if event.type == pygame.KEYDOWN:
                    if input_mode:
                        if event.key == pygame.K_RETURN and len(new_name) > 0:
                            menu_running = False
                        elif event.key == pygame.K_ESCAPE:
                            input_mode = False
                            new_name = ""
                        elif event.key == pygame.K_BACKSPACE:
                            new_name = new_name[:-1]
                        elif event.unicode.isalnum() or event.unicode in (' ', '-', '_'):
                            if len(new_name) < 15:
                                new_name += event.unicode
                    else:
                        if event.key == pygame.K_UP:
                            selected = (selected - 1) % len(options)
                        elif event.key == pygame.K_DOWN:
                            selected = (selected + 1) % len(options)
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            if selected == len(options) - 1:
                                input_mode = True
                                new_name = ""
                            else:
                                return player_names[selected]
            
            # Draw menu
            self.screen.fill(SKY_BLUE)
            
            try:
                title_font = _load_font(60, bold=True)
                title_text = title_font.render("KIES SPELER", True, BLACK)
                title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
                self.screen.blit(title_text, title_rect)
                
                if input_mode:
                    prompt_font = _load_font(36)
                    prompt_text = prompt_font.render("Voer je naam in:", True, BLACK)
                    prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
                    self.screen.blit(prompt_text, prompt_rect)
                    
                    # Input box
                    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 50)
                    pygame.draw.rect(self.screen, WHITE, input_box)
                    pygame.draw.rect(self.screen, BLACK, input_box, 3)
                    
                    name_font = _load_font(32)
                    name_text = name_font.render(new_name + "|", True, BLACK)
                    name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, 325))
                    self.screen.blit(name_text, name_rect)
                else:
                    option_font = _load_font(36)
                    for i, option in enumerate(options):
                        y_pos = 220 + i * 60
                        
                        if i < len(player_names):
                            score = existing_players[i][1]
                            text = f"{option} (Beste: {score})"
                        else:
                            text = option
                        
                        color = YELLOW if i == selected else BLACK
                        option_text = option_font.render(text, True, color)
                        option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
                        self.screen.blit(option_text, option_rect)
                        
                        if i == selected:
                            pygame.draw.polygon(self.screen, YELLOW, [
                                (option_rect.left - 40, y_pos),
                                (option_rect.left - 20, y_pos - 15),
                                (option_rect.left - 20, y_pos + 15)
                            ])
            except:
                pass
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        return new_name if new_name else "Guest"
    
    def handle_input(self):
        """Handle player input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                
                elif self.paused:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        self.paused = False
                    elif event.key == pygame.K_r:
                        self.reset_game()
                        self.paused = False
                
                else:  # Playing
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        self.paused = True
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
                        # Jump/wall jump
                        self.player.jump()
    
    def update(self):
        """Update game state."""
        if self.game_over or self.paused:
            return
        
        # Update camera (auto-scroll)
        self.camera.update()
        
        # Update player
        self.player.update(self.camera.x)
        
        # Update walls
        self.wall_generator.update(self.camera.x)
        
        # Check wall collisions
        wall, side = self.wall_generator.check_collisions(self.player)
        
        if wall and side:
            # Player is touching a wall
            self.player.enter_wall_slide(side)
        else:
            # Player not touching any wall
            if self.player.state == Player.STATE_WALL_SLIDING:
                self.player.exit_wall_slide()
        
        # Check death conditions
        self._check_death()
    
    def _check_death(self):
        """Check if player has died."""
        # Death by floor touch
        if self.player.on_ground or self.player.y + self.player.height >= GROUND_Y:
            self.game_over = True
            self.death_reason = "Raakte de dodelijke vloer!"
            self._handle_death()
        
        # Death by falling off left side of screen
        elif self.camera.is_off_screen_left(self.player.x):
            self.game_over = True
            self.death_reason = "Viel achter het scherm!"
            self._handle_death()
    
    def _handle_death(self):
        """Handle player death."""
        score = self.camera.get_score()
        self.score_manager.check_and_save_high_score(score)
        print(f"💀 Game Over! Score: {score} - {self.death_reason}")
    
    def draw(self):
        """Draw game state."""
        # Clear screen with sky
        self.screen.fill(SKY_BLUE)
        
        # Draw ground (lethal floor)
        ground_rect = pygame.Rect(0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y)
        pygame.draw.rect(self.screen, GROUND_DANGER, ground_rect)
        pygame.draw.rect(self.screen, GROUND_DARK, ground_rect, 5)  # Border
        
        # Draw danger indicator on floor
        self._draw_danger_pattern(ground_rect)
        
        # Draw walls
        self.wall_generator.draw(self.screen, self.camera.x)
        
        # Draw player
        self.player.draw(self.screen, self.camera.x)
        
        # Draw UI
        self._draw_ui()
        
        # Draw game over or pause screen
        if self.game_over:
            self._draw_game_over()
        elif self.paused:
            self._draw_pause_menu()
    
    def _draw_danger_pattern(self, ground_rect):
        """Draw warning stripes on lethal floor."""
        stripe_width = 40
        for i in range(0, SCREEN_WIDTH, stripe_width * 2):
            stripe_rect = pygame.Rect(i, ground_rect.top, stripe_width, ground_rect.height)
            pygame.draw.rect(self.screen, DEATH_RED, stripe_rect)
    
    def _draw_ui(self):
        """Draw UI elements."""
        try:
            font = _load_font(36, bold=True)
            
            # Score
            score = self.camera.get_score()
            score_text = font.render(f"Afstand: {score}m", True, BLACK)
            self.screen.blit(score_text, (20, 20))
            
            # Speed indicator
            speed_percent = int((self.camera.speed / MAX_AUTO_SCROLL_SPEED) * 100)
            speed_text = font.render(f"Snelheid: {speed_percent}%", True, BLACK)
            self.screen.blit(speed_text, (20, 60))
            
            # High score
            high_score = self.score_manager.get_high_score()
            if high_score > 0:
                high_score_text = font.render(f"Beste: {high_score}m", True, (100, 100, 100))
                self.screen.blit(high_score_text, (SCREEN_WIDTH - 220, 20))
        except:
            pass
    
    def _draw_game_over(self):
        """Draw game over screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        try:
            # Game Over text
            title_font = _load_font(80, bold=True)
            title_text = title_font.render("GAME OVER", True, DEATH_RED)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(title_text, title_rect)
            
            # Death reason
            reason_font = _load_font(32)
            reason_text = reason_font.render(self.death_reason, True, WHITE)
            reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(reason_text, reason_rect)
            
            # Score
            score = self.camera.get_score()
            score_font = _load_font(48, bold=True)
            score_text = score_font.render(f"Afstand: {score}m", True, YELLOW)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(score_text, score_rect)
            
            # High score
            high_score = self.score_manager.get_high_score()
            if score >= high_score:
                new_record_text = score_font.render("NIEUW RECORD!", True, YELLOW)
                record_rect = new_record_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
                self.screen.blit(new_record_text, record_rect)
            
            # Instructions
            inst_font = _load_font(28)
            inst_text = inst_font.render("SPATIE = Opnieuw | ESC = Afsluiten", True, WHITE)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            self.screen.blit(inst_text, inst_rect)
        except:
            pass
    
    def _draw_pause_menu(self):
        """Draw pause menu."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        try:
            # Paused text
            title_font = _load_font(72, bold=True)
            title_text = title_font.render("GEPAUZEERD", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(title_text, title_rect)
            
            # Instructions
            inst_font = _load_font(32)
            inst1 = inst_font.render("ESC/P = Doorgaan", True, WHITE)
            inst2 = inst_font.render("R = Opnieuw starten", True, WHITE)
            
            inst1_rect = inst1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            inst2_rect = inst2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
            
            self.screen.blit(inst1, inst1_rect)
            self.screen.blit(inst2, inst2_rect)
        except:
            pass
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()


def main():
    """Main entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
