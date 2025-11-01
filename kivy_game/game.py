"""
Main Kivy Game Widget
Coordinates all game systems for iOS/mobile version.
"""

from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button

from .config import *
from .player import Player
from .obstacles import ObstacleGenerator
from managers.score_manager import ScoreManager


class GameWidget(Widget):
    """Main game widget coordinating all systems."""
    
    def __init__(self, **kwargs):
        super(GameWidget, self).__init__(**kwargs)
        
        # Game state
        self.game_over = False
        self.paused = False
        self.difficulty = "medium"
        self.player_name = "Guest"
        
        print(f"\n🎮 KIVY GAME INIT")
        print(f"   Window size: {Window.size}")
        print(f"   Difficulty: {self.difficulty}")
        
        # Initialize game systems
        self.player = Player(PLAYER_START_X, GROUND_Y)
        print(f"   Player position: ({self.player.x}, {self.player.y})")
        print(f"   Player size: {PLAYER_SIZE}x{PLAYER_SIZE}")
        print(f"   Ground Y: {GROUND_Y}")
        
        self.obstacle_generator = ObstacleGenerator(difficulty=self.difficulty)
        self.score_manager = ScoreManager(player_name=self.player_name)
        
        # Score tracking
        self.distance_traveled = 0
        self.last_score = 0
        
        print(f"   Obstacles: {len(self.obstacle_generator.obstacles)}")
        print(f"   Generating initial obstacles...")
        
        # Generate initial obstacles
        for _ in range(3):
            self.obstacle_generator.generate_obstacle()
        
        print(f"   Total obstacles after init: {len(self.obstacle_generator.obstacles)}")
        if self.obstacle_generator.obstacles:
            first_obs = self.obstacle_generator.obstacles[0]
            print(f"   First obstacle: x={first_obs.x}, y={first_obs.y}, w={first_obs.width}, h={first_obs.height}")
        print(f"🎮 INIT COMPLETE\n")
        
        # Setup background
        with self.canvas.before:
            # Sky gradient (simplified - just solid color for now)
            Color(*SKY_BLUE)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
            
            # Ground
            Color(*GROUND_GREEN)
            self.ground_rect = Rectangle(
                pos=(0, 0),
                size=(Window.size[0], GROUND_Y)
            )
        
        # Add player to canvas
        self.add_widget(self.player)
        
        # Create UI labels
        self.score_label = Label(
            text="Score: 0",
            font_size='20sp',
            pos=(10, Window.height - 40),
            size_hint=(None, None)
        )
        self.add_widget(self.score_label)
        
        self.high_score_label = Label(
            text=f"High Score: {self.score_manager.high_score}",
            font_size='16sp',
            pos=(10, Window.height - 70),
            size_hint=(None, None)
        )
        self.add_widget(self.high_score_label)
        
        # Create jump button for touch input
        self.jump_button = Button(
            text="JUMP",
            size_hint=(None, None),
            size=(150, 80),
            pos=(Window.width - 170, 20),
            font_size='24sp'
        )
        self.jump_button.bind(on_press=self.on_jump_button)
        self.add_widget(self.jump_button)
        
        # Schedule game update loop
        Clock.schedule_interval(self.update, 1/FPS)
    
    def on_jump_button(self, instance):
        """Handle jump button press."""
        if not self.game_over and not self.paused:
            self.player.jump()
    
    def on_touch_down(self, touch):
        """Handle touch input (tap anywhere to jump)."""
        if not self.game_over and not self.paused:
            # Allow jumping anywhere on screen, not just button
            self.player.jump()
        return super(GameWidget, self).on_touch_down(touch)
    
    def update(self, dt):
        """Main game update loop."""
        if self.game_over or self.paused:
            return
        
        # Update player
        self.player.update(dt)
        
        # Update obstacles
        self.obstacle_generator.update(dt)
        
        # Update distance and score
        self.distance_traveled += PLAYER_SPEED
        self.score_manager.update_distance(PLAYER_SPEED)
        current_score = self.score_manager.get_score()
        
        if current_score > self.last_score:
            self.last_score = current_score
            self.score_label.text = f"Score: {current_score}"
        
        # Check collisions
        if self.obstacle_generator.check_collision(self.player):
            self.handle_game_over()
        
        # Check if player fell off screen
        if self.player.y < -100:
            self.handle_game_over()
        
        # Render obstacles
        self.render_obstacles()
    
    def render_obstacles(self):
        """Render all obstacles on canvas."""
        # Remove old obstacle widgets
        for child in self.children[:]:
            if isinstance(child, type(self.obstacle_generator.obstacles[0] if self.obstacle_generator.obstacles else None)):
                self.remove_widget(child)
        
        # Add current obstacles
        for obstacle in self.obstacle_generator.obstacles:
            if obstacle not in self.children:
                self.add_widget(obstacle)
    
    def handle_game_over(self):
        """Handle game over state."""
        self.game_over = True
        self.score_manager.check_and_save_high_score()
        
        # Show game over screen
        game_over_label = Label(
            text=f"GAME OVER\\nScore: {self.last_score}\\nHigh Score: {self.score_manager.high_score}",
            font_size='32sp',
            pos=(Window.width/2 - 150, Window.height/2),
            size_hint=(None, None),
            halign='center'
        )
        self.add_widget(game_over_label)
        
        # Restart button
        restart_button = Button(
            text="Restart",
            size_hint=(None, None),
            size=(200, 60),
            pos=(Window.width/2 - 100, Window.height/2 - 100),
            font_size='24sp'
        )
        restart_button.bind(on_press=self.restart_game)
        self.add_widget(restart_button)
    
    def restart_game(self, instance):
        """Restart the game."""
        # Stop the current update loop
        Clock.unschedule(self.update)
        
        # Clear all widgets
        self.clear_widgets()
        self.canvas.clear()
        
        # Reset game state
        self.game_over = False
        self.paused = False
        self.distance_traveled = 0
        self.last_score = 0
        
        # Reinitialize game systems
        self.player = Player(PLAYER_START_X, GROUND_Y)
        self.obstacle_generator = ObstacleGenerator(difficulty=self.difficulty)
        self.score_manager.reset()
        
        # Regenerate initial obstacles
        for _ in range(3):
            self.obstacle_generator.generate_obstacle()
        
        # Setup background again
        with self.canvas.before:
            Color(*SKY_BLUE)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
            Color(*GROUND_GREEN)
            self.ground_rect = Rectangle(pos=(0, 0), size=(Window.size[0], GROUND_Y))
        
        # Add player to canvas
        self.add_widget(self.player)
        
        # Recreate UI labels
        self.score_label = Label(
            text="Score: 0",
            font_size='20sp',
            pos=(10, Window.height - 40),
            size_hint=(None, None)
        )
        self.add_widget(self.score_label)
        
        self.high_score_label = Label(
            text=f"High Score: {self.score_manager.high_score}",
            font_size='16sp',
            pos=(10, Window.height - 70),
            size_hint=(None, None)
        )
        self.add_widget(self.high_score_label)
        
        # Recreate jump button
        self.jump_button = Button(
            text="JUMP",
            size_hint=(None, None),
            size=(150, 80),
            pos=(Window.width - 170, 20),
            font_size='24sp'
        )
        self.jump_button.bind(on_press=self.on_jump_button)
        self.add_widget(self.jump_button)
        
        # Restart game update loop
        Clock.schedule_interval(self.update, 1/FPS)
