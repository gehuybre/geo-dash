"""
Rendering system for backgrounds, UI, and visual effects.
Supports custom background images.
"""

import pygame
import random
import os
from .config import *


class Renderer:
    """Handles all rendering operations."""
    
    def __init__(self, screen):
        # Import asset_manager here to avoid circular import issues
        from .assets import asset_manager
        
        self.screen = screen
        
        # Try to initialize fonts with custom Mochibop font
        try:
            # Try custom fonts from assets/fonts first
            if os.path.exists(FONT_REGULAR):
                self.font = pygame.font.Font(FONT_REGULAR, 36)
                self.big_font = pygame.font.Font(FONT_BOLD if os.path.exists(FONT_BOLD) else FONT_REGULAR, 72)
                print(f"✓ Using custom font: Mochibop")
            else:
                # Fallback to system fonts
                cute_fonts = ['Comic Sans MS', 'Chalkboard', 'Marker Felt', 'Bradley Hand', 'Arial Rounded MT Bold']
                self.font = None
                self.big_font = None
                
                for font_name in cute_fonts:
                    try:
                        self.font = pygame.font.SysFont(font_name, 36)
                        self.big_font = pygame.font.SysFont(font_name, 72)
                        if self.font and self.big_font:
                            print(f"✓ Using system font: {font_name}")
                            break
                    except:
                        continue
                
                # If no cute fonts found, use default
                if not self.font:
                    self.font = pygame.font.SysFont(None, 36)
                    self.big_font = pygame.font.SysFont(None, 72)
                    print("✓ Using default system font")
            
            self.font_available = True
        except (NotImplementedError, ImportError) as e:
            # Font module not available
            self.font_available = False
            print(f"Warning: pygame.font not available ({e}), using basic text rendering")
        
        # Try to load custom background
        self.backgrounds = asset_manager.get_background_images()
        self.custom_ground = asset_manager.get_ground_sprite()
        
        # Background cycling with random repetition
        self.current_bg_index = 0
        self.bg_repeat_count = 0
        self.bg_repeats_remaining = 0
        if self.backgrounds:
            self.bg_repeat_count = random.randint(1, 4)
            self.bg_repeats_remaining = self.bg_repeat_count
        
        # Parallax scrolling for backgrounds
        self.bg_scroll_offset = 0
        self.bg_scroll_speed = PLAYER_SPEED * BACKGROUND_SCROLL_SPEED_MULTIPLIER
        
        # Cloud animation offset
        self.cloud_offset = 0
    
    def _choose_next_background(self):
        """Choose the next background with random repetition."""
        if not self.backgrounds:
            return
        
        # If we still have repeats left, don't change background
        if self.bg_repeats_remaining > 0:
            self.bg_repeats_remaining -= 1
            return
        
        # Move to next background
        self.current_bg_index = (self.current_bg_index + 1) % len(self.backgrounds)
        
        # Decide how many times to repeat this background (1-4 times)
        self.bg_repeat_count = random.randint(1, 4)
        self.bg_repeats_remaining = self.bg_repeat_count - 1
    
    def update(self):
        """Update scrolling animations."""
        # Update background scroll offset for parallax effect
        self.bg_scroll_offset += self.bg_scroll_speed
        # Wrap around when we've scrolled a full screen width
        if self.bg_scroll_offset >= SCREEN_WIDTH:
            self.bg_scroll_offset -= SCREEN_WIDTH
    
    def draw_background(self, score=0):
        """Draw background (custom or procedural) with parallax scrolling."""
        if self.backgrounds:
            # Change background every 5 points
            if score > 0 and score % 5 == 0:
                bg_change_threshold = (score // 5) - 1
                if bg_change_threshold != getattr(self, '_last_bg_change', -1):
                    self._last_bg_change = bg_change_threshold
                    self._choose_next_background()
            
            # Calculate scroll position (negative to scroll left)
            scroll_x = -int(self.bg_scroll_offset)
            
            # Draw current background with seamless looping
            current_bg = self.backgrounds[self.current_bg_index]
            self.screen.blit(current_bg, (scroll_x, 0))
            self.screen.blit(current_bg, (scroll_x + SCREEN_WIDTH, 0))
        else:
            self._draw_procedural_background()
    
    def _draw_procedural_background(self):
        """Draw procedural gradient sky with clouds."""
        # Gradient sky
        for i in range(SCREEN_HEIGHT):
            color_intensity = 173 + (i * 50 // SCREEN_HEIGHT)
            color = (173, 216 - (i * 20 // SCREEN_HEIGHT), 230)
            pygame.draw.line(self.screen, color, (0, i), (SCREEN_WIDTH, i))
        
        # Animated clouds
        self.cloud_offset = (pygame.time.get_ticks() // 50) % SCREEN_WIDTH
        cloud_y_positions = [50, 100, 150, 80, 130]
        for i, y in enumerate(cloud_y_positions):
            x = (self.cloud_offset + i * 200) % (SCREEN_WIDTH + 100) - 50
            self._draw_cloud(x, y)
    
    def _draw_cloud(self, x, y):
        """Draw a cute cloud."""
        pygame.draw.circle(self.screen, WHITE, (x, y), 20)
        pygame.draw.circle(self.screen, WHITE, (x + 25, y), 25)
        pygame.draw.circle(self.screen, WHITE, (x + 50, y), 20)
        pygame.draw.circle(self.screen, WHITE, (x + 25, y - 15), 20)
    
    def draw_ground(self):
        """Draw ground (custom or procedural)."""
        if self.custom_ground:
            # Tile the ground sprite
            sprite_width = self.custom_ground.get_width()
            sprite_height = self.custom_ground.get_height()
            y_pos = GROUND_Y + PLAYER_SIZE
            
            for x in range(0, SCREEN_WIDTH, sprite_width):
                self.screen.blit(self.custom_ground, (x, y_pos))
        else:
            self._draw_procedural_ground()
    
    def _draw_procedural_ground(self):
        """Draw procedural ground with grass."""
        # Main ground
        pygame.draw.rect(self.screen, GROUND_GREEN, 
                        (0, GROUND_Y + PLAYER_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Grass detail
        for x in range(0, SCREEN_WIDTH, 20):
            grass_height = random.randint(5, 10)
            pygame.draw.line(self.screen, GROUND_DARK, 
                           (x, GROUND_Y + PLAYER_SIZE), 
                           (x, GROUND_Y + PLAYER_SIZE - grass_height), 2)
    
    def draw_ui(self, score, high_score, show_instructions=False, current_pattern=None, player_name=None, pattern_stats=None):
        """Draw score and UI elements.
        pattern_stats: tuple of (attempts, completions, success_rate) for current pattern
        """
        if not self.font_available:
            # Draw simple text blocks when font is not available
            if player_name:
                self._draw_simple_text(f"Speler: {player_name}", 20, 10)
                self._draw_simple_text(f"Score: {score}", 20, 35)
                self._draw_simple_text(f"Beste: {high_score}", 20, 60)
            else:
                self._draw_simple_text(f"Score: {score}", 20, 10)
                self._draw_simple_text(f"Beste: {high_score}", 20, 50)
            if show_instructions:
                self._draw_simple_text("Druk SPATIE om te springen!", SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2)
            # Pattern debug info
            if SHOW_PATTERN_DEBUG and current_pattern:
                pattern_text = f"Patroon: {current_pattern}"
                if pattern_stats:
                    attempts, completions, success_rate = pattern_stats
                    # Add medal emoji based on completions
                    medal = self._get_medal_emoji(completions)
                    pattern_text += f" {medal} ({completions}/{attempts} = {success_rate:.0f}%)"
                self._draw_simple_text(pattern_text, 20, 90, color=BLACK)
        else:
            # Player name (if provided) - compact layout on one line with score
            y_offset = 15
            x_offset = 300  # Move UI more to the right to avoid being cut off
            
            if player_name:
                player_text = self.font.render(f"🎮 {player_name}", True, HEART_RED)
                self.screen.blit(player_text, (x_offset, y_offset))
                
                # Score on same line, to the right of player name
                score_text = self.font.render(f"Score: {score}", True, BLACK)
                score_x = x_offset + player_text.get_width() + 30  # 30px spacing
                self.screen.blit(score_text, (score_x, y_offset))
                
                # High score on same line, to the right of score
                high_score_text = self.font.render(f"Beste: {high_score}", True, BLACK)
                high_score_x = score_x + score_text.get_width() + 30
                self.screen.blit(high_score_text, (high_score_x, y_offset))
            else:
                # No player name - just score and high score
                score_text = self.font.render(f"Score: {score}", True, BLACK)
                self.screen.blit(score_text, (x_offset, y_offset))
                
                high_score_text = self.font.render(f"Beste: {high_score}", True, BLACK)
                high_score_x = x_offset + score_text.get_width() + 30
                self.screen.blit(high_score_text, (high_score_x, y_offset))
            
            # Instructions - centered vertically in middle of screen
            if show_instructions:
                instruction_text = self.font.render("Druk SPATIE om te springen!", True, BLACK)
                text_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                # Draw background box for better visibility
                bg_rect = pygame.Rect(text_rect.x - 20, text_rect.y - 10, text_rect.width + 40, text_rect.height + 20)
                pygame.draw.rect(self.screen, (255, 255, 255, 200), bg_rect, border_radius=10)
                pygame.draw.rect(self.screen, BLACK, bg_rect, 3, border_radius=10)
                self.screen.blit(instruction_text, text_rect)
            
            # Pattern debug info (below main UI) - now includes stats with medals
            if SHOW_PATTERN_DEBUG and current_pattern:
                pattern_text = f"Patroon: {current_pattern}"
                if pattern_stats:
                    attempts, completions, success_rate = pattern_stats
                    # Add medal based on completions
                    medal = self._get_medal_emoji(completions)
                    # Color code based on success rate
                    if success_rate >= 80:
                        color = (0, 200, 0)  # Green - easy
                    elif success_rate >= 50:
                        color = (255, 165, 0)  # Orange - medium
                    else:
                        color = (255, 0, 0)  # Red - hard
                    
                    pattern_text += f" {medal} [{completions}/{attempts} = {success_rate:.0f}%]"
                    pattern_render = self.font.render(pattern_text, True, color)
                else:
                    pattern_render = self.font.render(pattern_text, True, BLACK)
                
                self.screen.blit(pattern_render, (x_offset, 55))
    
    def _get_medal_emoji(self, completions):
        """Get medal emoji based on number of completions."""
        if completions == 0:
            return ""  # No medal
        elif completions == 1:
            return "🥉"  # Bronze
        elif completions == 2:
            return "🥈"  # Silver
        else:
            return "🥇"  # Gold for 3+
    
    def _draw_simple_text(self, text, x, y, color=BLACK, size=16):
        """Draw simple pixel text when pygame.font is not available."""
        # Simple 5x7 pixel font patterns for readable text
        # Each character is a 5-bit pattern per row (7 rows)
        font_data = {
            'A': [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
            'B': [0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
            'C': [0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110],
            'D': [0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
            'E': [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
            'F': [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000],
            'G': [0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01110],
            'H': [0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
            'I': [0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
            'J': [0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100],
            'L': [0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
            'M': [0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001],
            'N': [0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001],
            'O': [0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
            'P': [0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000],
            'R': [0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
            'S': [0b01110, 0b10001, 0b10000, 0b01110, 0b00001, 0b10001, 0b01110],
            'T': [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
            'U': [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
            'V': [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
            'W': [0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001],
            'Y': [0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100],
            '0': [0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110],
            '1': [0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
            '2': [0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111],
            '3': [0b01110, 0b10001, 0b00001, 0b00110, 0b00001, 0b10001, 0b01110],
            '4': [0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
            '5': [0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110],
            '6': [0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
            '7': [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000],
            '8': [0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
            '9': [0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100],
            ':': [0b00000, 0b00100, 0b00000, 0b00000, 0b00000, 0b00100, 0b00000],
            '!': [0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100],
            ' ': [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
        }
        
        # Calculate character size based on size parameter
        pixel_size = max(1, size // 8)
        char_width = 6 * pixel_size
        char_height = 7 * pixel_size
        
        # Draw each character
        for i, char in enumerate(text.upper()):
            if char in font_data:
                pattern = font_data[char]
                char_x = x + i * char_width
                
                # Draw the character pixel by pixel
                for row in range(7):
                    for col in range(5):
                        if pattern[row] & (1 << (4 - col)):
                            pygame.draw.rect(self.screen, color, 
                                           (char_x + col * pixel_size, 
                                            y + row * pixel_size, 
                                            pixel_size, pixel_size))
    
    def draw_game_over(self, score, selected_option=0):
        """Draw game over screen with menu options."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        menu_options = ["Opnieuw", "Wissel Speler", "Speler Profiel"]
        
        if not self.font_available:
            # Simple fallback rendering
            self._draw_simple_text("Spel Over!", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100, HEART_RED, 24)
            self._draw_simple_text(f"Eindstand: {score}", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40, WHITE, 18)
            
            for i, option in enumerate(menu_options):
                y = SCREEN_HEIGHT // 2 + 20 + i * 50
                color = YELLOW if i == selected_option else WHITE
                prefix = "> " if i == selected_option else "  "
                self._draw_simple_text(f"{prefix}{option}", SCREEN_WIDTH // 2 - 80, y, color, 18)
            
            self._draw_simple_text("Gebruik Pijltjestoetsen + SPATIE", SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 150, SKY_LIGHT, 14)
        else:
            # Game Over text
            game_over_text = self.big_font.render("Spel Over! 💫", True, HEART_RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(game_over_text, text_rect)
            
            # Final score
            score_text = self.font.render(f"Eindstand: {score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(score_text, score_rect)
            
            # Menu options
            for i, option in enumerate(menu_options):
                y = SCREEN_HEIGHT // 2 + 20 + i * 60
                
                # Highlight selected option
                if i == selected_option:
                    color = YELLOW
                    # Draw selection background
                    bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, y - 10, 240, 50)
                    pygame.draw.rect(self.screen, (255, 255, 100, 100), bg_rect, border_radius=10)
                    pygame.draw.rect(self.screen, YELLOW, bg_rect, 3, border_radius=10)
                    option_text = self.font.render(f"▸ {option}", True, color)
                else:
                    color = WHITE
                    option_text = self.font.render(option, True, color)
                
                option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y + 10))
                self.screen.blit(option_text, option_rect)
            
            # Instructions
            hint_text = self.font.render("↑/↓ om te selecteren, SPATIE om te bevestigen", True, SKY_LIGHT)
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200))
            self.screen.blit(hint_text, hint_rect)
    
    def draw_pause_menu(self, selected_option):
        """Draw pause menu with options: Resume, Restart, Switch Player, Select Difficulty, Player Profile."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        menu_options = ["Hervatten", "Opnieuw", "Wissel Speler", "Kies Moeilijkheid", "Speler Profiel"]
        
        if not self.font_available:
            # Simple fallback rendering
            self._draw_simple_text("GEPAUZEERD", SCREEN_WIDTH // 2 - 80, 150, YELLOW, 24)
            
            for i, option in enumerate(menu_options):
                y = 250 + i * 60
                color = HEART_RED if i == selected_option else WHITE
                prefix = "> " if i == selected_option else "  "
                self._draw_simple_text(f"{prefix}{option}", SCREEN_WIDTH // 2 - 120, y, color, 18)
            
            self._draw_simple_text("Gebruik Pijltjestoetsen + SPATIE", SCREEN_WIDTH // 2 - 140, 500, SKY_LIGHT, 14)
        else:
            # Pause title
            pause_text = self.big_font.render("⏸ GEPAUZEERD", True, YELLOW)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
            self.screen.blit(pause_text, pause_rect)
            
            # Menu options
            for i, option in enumerate(menu_options):
                y = 250 + i * 60
                
                # Highlight selected option
                if i == selected_option:
                    color = HEART_RED
                    # Draw selection background
                    bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, y - 10, 300, 50)
                    pygame.draw.rect(self.screen, (255, 200, 200, 100), bg_rect, border_radius=10)
                    pygame.draw.rect(self.screen, HEART_RED, bg_rect, 3, border_radius=10)
                    option_text = self.font.render(f"▸ {option}", True, color)
                else:
                    color = WHITE
                    option_text = self.font.render(option, True, color)
                
                option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y + 10))
                self.screen.blit(option_text, option_rect)
            
            # Controls hint
            hint_text = self.font.render("Gebruik ↑↓ Pijltjestoetsen + SPATIE of ESC om te hervatten", True, SKY_LIGHT)
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
            self.screen.blit(hint_text, hint_rect)
    
    def draw_player_profile(self, player_name, high_score, pattern_stats):
        """Draw player profile page showing achievements and pattern statistics.
        pattern_stats: dict of {pattern_name: {'attempts': X, 'completions': Y}}
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 40))
        self.screen.blit(overlay, (0, 0))
        
        if not self.font_available:
            self._draw_simple_text(f"Profiel: {player_name}", SCREEN_WIDTH // 2 - 150, 50, WHITE, 24)
            self._draw_simple_text(f"Hoogste Score: {high_score}", SCREEN_WIDTH // 2 - 150, 100, YELLOW, 18)
            self._draw_simple_text("Druk SPATIE om terug te gaan", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 50, SKY_LIGHT, 14)
        else:
            # Profile header
            title_text = self.big_font.render(f"🎮 Profiel: {player_name}", True, HEART_RED)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
            self.screen.blit(title_text, title_rect)
            
            # High score
            score_text = self.font.render(f"Hoogste Score: {high_score}", True, YELLOW)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
            self.screen.blit(score_text, score_rect)
            
            # Achievements section
            achievements_text = self.font.render("Prestaties:", True, WHITE)
            self.screen.blit(achievements_text, (100, 200))
            
            # Pattern statistics
            if pattern_stats:
                y = 250
                sorted_patterns = sorted(pattern_stats.items(), key=lambda x: x[1].get('completions', 0), reverse=True)
                
                # Show top 10 patterns
                for i, (pattern_name, stats) in enumerate(sorted_patterns[:10]):
                    if y > SCREEN_HEIGHT - 100:
                        break
                    
                    attempts = stats.get('attempts', 0)
                    completions = stats.get('completions', 0)
                    success_rate = (completions / attempts * 100) if attempts > 0 else 0
                    
                    # Get medal
                    medal = self._get_medal_emoji(completions)
                    
                    # Color based on success rate
                    if success_rate >= 80:
                        color = (0, 200, 0)
                    elif success_rate >= 50:
                        color = (255, 165, 0)
                    else:
                        color = (200, 200, 200)
                    
                    # Draw pattern stats
                    pattern_text = self.font.render(
                        f"{medal} {pattern_name}: {completions}/{attempts} ({success_rate:.0f}%)",
                        True, color
                    )
                    self.screen.blit(pattern_text, (120, y))
                    y += 40
            else:
                no_stats_text = self.font.render("Nog geen patronen voltooid!", True, WHITE)
                self.screen.blit(no_stats_text, (120, 250))
            
            # Instructions
            hint_text = self.font.render("Druk SPATIE of ESC om terug te gaan", True, SKY_LIGHT)
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(hint_text, hint_rect)
