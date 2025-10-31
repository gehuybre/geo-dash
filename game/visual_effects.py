"""
Visual effects system for game feedback - popups, streaks, combos.
"""

import pygame
import math
import random
from .config import *


class ScorePopup:
    """Floating score text that appears when landing on platforms."""
    
    def __init__(self, x, y, points, combo_streak=0):
        self.x = x
        self.y = y
        self.points = points
        self.combo_streak = combo_streak
        self.lifetime = 60  # Frames to live
        self.age = 0
        self.velocity_y = -2  # Float upward
        self.velocity_x = 0
    
    def update(self):
        """Update popup position and age."""
        self.age += 1
        self.y += self.velocity_y
        self.x += self.velocity_x
        self.velocity_y += 0.05  # Slight gravity
        return self.age < self.lifetime
    
    def draw(self, screen):
        """Draw the floating score text."""
        # Fade out over time
        alpha = int(255 * (1 - self.age / self.lifetime))
        
        # Create text based on combo streak
        if self.combo_streak > 0:
            text = f"+{self.combo_streak}"
            color = self._get_combo_color(self.combo_streak)
        else:
            text = f"+{self.points}"
            color = YELLOW
        
        font_size = 36 if self.points > 5 else 24
        
        # Try to use pygame font
        try:
            font = pygame.font.SysFont('Comic Sans MS', font_size, bold=True)
            text_surface = font.render(text, True, color)
            text_surface.set_alpha(alpha)
            
            # Draw shadow
            shadow = font.render(text, True, BLACK)
            shadow.set_alpha(alpha // 2)
            screen.blit(shadow, (self.x + 2, self.y + 2))
            
            # Draw main text
            screen.blit(text_surface, (self.x, self.y))
        except:
            # Fallback to simple rendering
            pass
    
    def _get_combo_color(self, streak):
        """Get color based on combo streak."""
        if streak >= 10:
            return (255, 0, 255)  # Magenta for 10+
        elif streak >= 5:
            return (255, 100, 0)  # Orange for 5+
        elif streak >= 3:
            return (255, 200, 0)  # Gold for 3+
        else:
            return YELLOW  # Yellow for 1-2


class StreakIndicator:
    """Flashy streak counter that shows current combo."""
    
    def __init__(self, x, y, streak_count):
        self.x = x
        self.y = y
        self.streak_count = streak_count
        self.lifetime = 90  # Longer lifetime for streak messages
        self.age = 0
        self.scale = 1.0
        self.pulse_speed = 0.1
    
    def update(self):
        """Update streak indicator animation."""
        self.age += 1
        # Pulse effect
        self.scale = 1.0 + 0.2 * math.sin(self.age * self.pulse_speed)
        return self.age < self.lifetime
    
    def draw(self, screen):
        """Draw flashy streak indicator."""
        # Fade out near end
        if self.age > self.lifetime - 20:
            alpha = int(255 * ((self.lifetime - self.age) / 20))
        else:
            alpha = 255
        
        try:
            # Main streak text
            base_size = 48
            font_size = int(base_size * self.scale)
            font = pygame.font.SysFont('Comic Sans MS', font_size, bold=True)
            
            # Different messages based on streak level
            if self.streak_count >= 10:
                text = f"🔥 UNSTOPPABLE x{self.streak_count}! 🔥"
                color = (255, 0, 255)  # Magenta
                glow_color = (255, 100, 255)
            elif self.streak_count >= 5:
                text = f"⚡ ON FIRE x{self.streak_count}! ⚡"
                color = (255, 100, 0)  # Orange
                glow_color = (255, 150, 50)
            elif self.streak_count >= 3:
                text = f"✨ STREAK x{self.streak_count}! ✨"
                color = (255, 200, 0)  # Gold
                glow_color = (255, 230, 100)
            else:
                text = f"COMBO x{self.streak_count}!"
                color = YELLOW
                glow_color = (255, 255, 150)
            
            # Draw glow effect
            for offset in range(3, 0, -1):
                glow_alpha = alpha // (offset + 1)
                glow_font = pygame.font.SysFont('Comic Sans MS', font_size + offset * 2, bold=True)
                glow_surface = glow_font.render(text, True, glow_color)
                glow_surface.set_alpha(glow_alpha)
                glow_rect = glow_surface.get_rect(center=(self.x, self.y))
                screen.blit(glow_surface, glow_rect)
            
            # Draw main text
            text_surface = font.render(text, True, color)
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(center=(self.x, self.y))
            screen.blit(text_surface, text_rect)
            
            # Draw outline
            outline_font = pygame.font.SysFont('Comic Sans MS', font_size, bold=True)
            outline_surface = outline_font.render(text, True, BLACK)
            outline_surface.set_alpha(alpha)
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                outline_rect = outline_surface.get_rect(center=(self.x + dx, self.y + dy))
                screen.blit(outline_surface, outline_rect)
            
        except:
            # Fallback rendering
            pass


class StreakBrokenIndicator:
    """Visual indicator when a streak is broken."""
    
    def __init__(self, x, y, broken_streak):
        self.x = x
        self.y = y
        self.broken_streak = broken_streak
        self.lifetime = 60
        self.age = 0
        self.velocity_y = 1  # Fall down slightly
    
    def update(self):
        """Update broken streak animation."""
        self.age += 1
        self.y += self.velocity_y
        self.velocity_y += 0.05
        return self.age < self.lifetime
    
    def draw(self, screen):
        """Draw streak broken message."""
        alpha = int(255 * (1 - self.age / self.lifetime))
        
        try:
            font_size = 36
            font = pygame.font.SysFont('Comic Sans MS', font_size, bold=True)
            
            # Show the streak that was lost
            if self.broken_streak >= 5:
                text = f"💔 STREAK LOST x{self.broken_streak}!"
                color = (255, 50, 50)  # Red
            elif self.broken_streak >= 3:
                text = f"Streak Lost x{self.broken_streak}"
                color = (200, 100, 100)  # Light red
            else:
                # Don't show for small streaks
                return
            
            # Draw shadow
            shadow = font.render(text, True, BLACK)
            shadow.set_alpha(alpha // 2)
            shadow_rect = shadow.get_rect(center=(self.x + 2, self.y + 2))
            screen.blit(shadow, shadow_rect)
            
            # Draw main text
            text_surface = font.render(text, True, color)
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(center=(self.x, self.y))
            screen.blit(text_surface, text_rect)
            
        except:
            # Fallback rendering
            pass


class ComboParticle:
    """Small particle effects that spawn during combos."""
    
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = 30
        self.age = 0
        # Random velocity
        angle = math.radians(random.randint(0, 360))
        speed = random.uniform(1, 3)
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed - 2  # Bias upward
        self.size = random.randint(3, 6)
    
    def update(self):
        """Update particle position."""
        self.age += 1
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.2  # Gravity
        return self.age < self.lifetime
    
    def draw(self, screen):
        """Draw particle."""
        alpha = int(255 * (1 - self.age / self.lifetime))
        size = int(self.size * (1 - self.age / self.lifetime))
        
        if size > 0:
            surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(surface, color_with_alpha, (size, size), size)
            screen.blit(surface, (self.x - size, self.y - size))


class VisualEffectsManager:
    """Manages all visual effects in the game."""
    
    def __init__(self):
        self.score_popups = []
        self.streak_indicators = []
        self.streak_broken_indicators = []
        self.particles = []
    
    def add_score_popup(self, x, y, points, combo_streak=0):
        """Add a floating score popup."""
        popup = ScorePopup(x, y, points, combo_streak)
        self.score_popups.append(popup)
    
    def add_streak_indicator(self, streak_count):
        """Add a flashy streak indicator."""
        x = SCREEN_WIDTH // 2
        y = 150
        indicator = StreakIndicator(x, y, streak_count)
        self.streak_indicators.append(indicator)
        
        # Add particles for big streaks
        if streak_count >= 3:
            self._add_combo_particles(x, y, streak_count)
    
    def add_streak_broken(self, x, y, broken_streak):
        """Add streak broken indicator."""
        if broken_streak >= 3:  # Only show for streaks of 3+
            indicator = StreakBrokenIndicator(x, y, broken_streak)
            self.streak_broken_indicators.append(indicator)
    
    def _add_combo_particles(self, x, y, streak_count):
        """Add particles for combo effects."""
        # Determine color based on streak
        if streak_count >= 10:
            color = (255, 0, 255)
        elif streak_count >= 5:
            color = (255, 100, 0)
        else:
            color = (255, 200, 0)
        
        # Spawn particles
        particle_count = min(streak_count * 2, 20)
        for _ in range(particle_count):
            particle = ComboParticle(x, y, color)
            self.particles.append(particle)
    
    def update(self):
        """Update all visual effects."""
        self.score_popups = [p for p in self.score_popups if p.update()]
        self.streak_indicators = [s for s in self.streak_indicators if s.update()]
        self.streak_broken_indicators = [s for s in self.streak_broken_indicators if s.update()]
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, screen):
        """Draw all visual effects."""
        # Draw particles first (background layer)
        for particle in self.particles:
            particle.draw(screen)
        
        # Draw score popups
        for popup in self.score_popups:
            popup.draw(screen)
        
        # Draw streak indicators (foreground layer)
        for indicator in self.streak_indicators:
            indicator.draw(screen)
        
        # Draw streak broken indicators
        for indicator in self.streak_broken_indicators:
            indicator.draw(screen)
    
    def clear(self):
        """Clear all effects."""
        self.score_popups.clear()
        self.streak_indicators.clear()
        self.streak_broken_indicators.clear()
        self.particles.clear()
