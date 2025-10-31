"""
Score tracking and persistence management.
"""

import json
import os


class ScoreManager:
    """Manages game scoring and high score persistence per player."""
    
    def __init__(self, player_name="Guest", save_file="data/save_data.json"):
        self.save_file = save_file
        self.player_name = player_name
        self.distance = 0  # Distance traveled in pixels
        self.score = 0  # Score based on distance
        self.landing_bonus = 0  # Bonus points from successful landings
        self.high_score = self.load_high_score()
    
    def load_high_score(self):
        """Load high score for current player from JSON file."""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    # Support new per-player format
                    if 'players' in data:
                        return data['players'].get(self.player_name, {}).get('high_score', 0)
                    # Legacy format compatibility
                    elif 'high_score' in data:
                        return data.get('high_score', 0)
            except (json.JSONDecodeError, IOError):
                return 0
        return 0
    
    def save_high_score(self):
        """Save high score for current player to JSON file."""
        try:
            # Ensure data directory exists
            import os
            os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
            
            # Load existing data
            data = {'players': {}}
            if os.path.exists(self.save_file):
                try:
                    with open(self.save_file, 'r') as f:
                        existing_data = json.load(f)
                        # Migrate old format if needed
                        if 'players' in existing_data:
                            data = existing_data
                        elif 'high_score' in existing_data:
                            # Migrate old single high score to Guest player
                            data['players']['Guest'] = {'high_score': existing_data['high_score']}
                except (json.JSONDecodeError, IOError):
                    pass
            
            # Update current player's high score
            if self.player_name not in data['players']:
                data['players'][self.player_name] = {}
            data['players'][self.player_name]['high_score'] = self.high_score
            
            # Save
            with open(self.save_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Saved high score for {self.player_name}: {self.high_score}")
        except IOError as e:
            print(f"Failed to save high score: {e}")
    
    def get_all_players(self):
        """Get list of all player names with scores."""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    if 'players' in data:
                        return [(name, info.get('high_score', 0)) 
                                for name, info in data['players'].items()]
                    elif 'high_score' in data:
                        return [('Guest', data['high_score'])]
            except (json.JSONDecodeError, IOError):
                pass
        return []
    
    def update_distance(self, pixels):
        """Update distance traveled and calculate score."""
        self.distance += pixels
        self.score = (self.distance // 100) + self.landing_bonus  # 1 point per 100 pixels + landing bonuses
    
    def add_landing_bonus(self, combo_streak=0):
        """Add bonus points for successful landing with combo multiplier.
        Base bonus is 5 points, plus 1 point for each consecutive platform landing.
        """
        bonus = 5 + combo_streak  # 5 base + streak bonus
        self.landing_bonus += bonus
        self.score = (self.distance // 100) + self.landing_bonus
        return bonus  # Return actual bonus awarded for UI display
    
    def check_and_save_high_score(self):
        """Check if current score is a high score and save if it is.
        Always saves the player to ensure they appear in the player list."""
        is_new_high_score = False
        if self.score > self.high_score:
            self.high_score = self.score
            is_new_high_score = True
        
        # Always save to ensure player is in the list, even with score 0
        self.save_high_score()
        return is_new_high_score
    
    def reset(self):
        """Reset current game scores (keeps high score)."""
        self.distance = 0
        self.score = 0
        self.landing_bonus = 0
    
    def get_score(self):
        """Get current score."""
        return self.score
    
    def get_high_score(self):
        """Get high score."""
        return self.high_score
    
    def get_distance(self):
        """Get current distance."""
        return self.distance
