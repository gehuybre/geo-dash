"""
Score tracking and persistence management.
"""

import json
import os


class ScoreManager:
    """Manages game scoring and high score persistence."""
    
    def __init__(self, save_file="data/save_data.json"):
        self.save_file = save_file
        self.distance = 0  # Distance traveled in pixels
        self.score = 0  # Score based on distance
        self.high_score = self.load_high_score()
    
    def load_high_score(self):
        """Load high score from JSON file."""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
            except (json.JSONDecodeError, IOError):
                return 0
        return 0
    
    def save_high_score(self):
        """Save high score to JSON file."""
        try:
            with open(self.save_file, 'w') as f:
                json.dump({'high_score': self.high_score}, f, indent=2)
        except IOError as e:
            print(f"Failed to save high score: {e}")
    
    def update_distance(self, pixels):
        """Update distance traveled and calculate score."""
        self.distance += pixels
        self.score = self.distance // 100  # 1 point per 100 pixels
    
    def check_and_save_high_score(self):
        """Check if current score is a high score and save if it is."""
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            return True
        return False
    
    def reset(self):
        """Reset current game scores (keeps high score)."""
        self.distance = 0
        self.score = 0
    
    def get_score(self):
        """Get current score."""
        return self.score
    
    def get_high_score(self):
        """Get high score."""
        return self.high_score
    
    def get_distance(self):
        """Get current distance."""
        return self.distance
