#!/usr/bin/env python3
"""Test script to verify player save/load functionality"""

from managers.score_manager import ScoreManager
import os

print("=== Testing Player Save/Load System ===\n")

# Test 1: Load existing players
print("Test 1: Loading existing players")
sm = ScoreManager()
players = sm.get_all_players()
print(f"  Existing players: {players}\n")

# Test 2: Create a new player and save a score
print("Test 2: Creating new player 'Alice' with score 50")
alice = ScoreManager(player_name="Alice")
alice.distance = 5000  # 5000 pixels = 50 points
alice.update_distance(0)  # Calculate score
print(f"  Alice's score: {alice.score}")
alice.check_and_save_high_score()
print()

# Test 3: Verify Alice was saved
print("Test 3: Verifying Alice was saved")
sm2 = ScoreManager()
players = sm2.get_all_players()
print(f"  All players now: {players}")
print()

# Test 4: Load Alice and beat her score
print("Test 4: Loading Alice and beating her score")
alice2 = ScoreManager(player_name="Alice")
print(f"  Alice's loaded high score: {alice2.high_score}")
alice2.distance = 10000  # 10000 pixels = 100 points
alice2.update_distance(0)
print(f"  Alice's new score: {alice2.score}")
result = alice2.check_and_save_high_score()
print(f"  New high score saved: {result}")
print()

# Test 5: Verify high score was updated
print("Test 5: Verifying high score was updated")
alice3 = ScoreManager(player_name="Alice")
print(f"  Alice's high score after update: {alice3.high_score}")
print()

# Test 6: Landing bonus test
print("Test 6: Testing landing bonus")
bob = ScoreManager(player_name="Bob")
bob.distance = 1000  # 10 points from distance
bob.update_distance(0)
print(f"  Bob's score (distance only): {bob.score}")
bonus = bob.add_landing_bonus(combo_streak=3)  # 5 base + 3 combo = 8 points
print(f"  Landing bonus awarded: {bonus}")
print(f"  Bob's total score: {bob.score}")
bob.check_and_save_high_score()
print()

# Test 7: Show final state
print("Test 7: Final player list")
sm_final = ScoreManager()
final_players = sm_final.get_all_players()
for name, score in final_players:
    print(f"  {name}: {score}")

print("\n=== All Tests Complete ===")
