#!/usr/bin/env python3
"""
Pattern Generator Main Entry Point

Generates all obstacle patterns with difficulty variants and saves them
to the obstacle_patterns directory.

Usage:
    python -m generators.main
    or
    python generators/main.py
"""

import os
import json

from .physics_engine import validate_pattern
from .obstacle_builders import create_pattern
from .pattern_library import (
    steady_rhythm_v4,
    wave_rider_v4,
    quick_hops_v4,
    rest_and_run_v4,
    stepped_ascent_v4,
    zigzag_chaos_v4,
    long_jumper_v4,
    mixed_madness_v4,
    kitchen_sink_v4,
    obstacle_course_v4,
    generate_difficulty_variants
)


OUTPUT_DIR = "obstacle_patterns"


def ensure_dir(path):
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def save_pattern(pattern, filename):
    """
    Validate and save pattern to JSON file.
    
    Args:
        pattern: Pattern dictionary
        filename: Output filename (without .json extension)
        
    Returns:
        True if successful, False if validation failed
    """
    ensure_dir(OUTPUT_DIR)
    
    # Validate pattern before saving
    is_valid, error_msg, touches_ground = validate_pattern(pattern)
    if not is_valid:
        print(f"✗ FAILED: {filename} - {error_msg}")
        return False
    
    # Update lava zones based on ground touching
    obstacles = pattern['obstacles']
    for obs in obstacles:
        if obs.get('is_killzone', False):
            # If jump paths never touch ground, make lava continuous (full height)
            if not touches_ground:
                obs['continuous_lava'] = True  # Flag for rendering full-height lava
    
    path = os.path.join(OUTPUT_DIR, f"{filename}.json")
    with open(path, "w") as f:
        json.dump(pattern, f, indent=2)
    lava_type = "continuous" if not touches_ground else "15px bars"
    print(f"✓ Created: {filename} ({pattern['metadata']['length']} platforms, {pattern['metadata']['type']}, lava: {lava_type}) - VALIDATED")
    return True


def generate_all_patterns():
    """Generate all patterns with difficulty variants."""
    print("\n" + "="*70)
    print("=== GEOMETRY DASH PATTERN GENERATOR V4 ===")
    print("=== THE FLOOR IS LAVA - RHYTHM PLATFORMER ===")
    print("="*70)
    print("\nGameplay: Jump-in, land, jump-out rhythm")
    print("Heights: 2-4 (60-120px above lava)")
    print("Difficulties: Easy (+25% width), Medium (+15% width), Hard (original)")
    print("Validation: Built-in physics ensures all patterns are playable\n")
    
    ensure_dir(OUTPUT_DIR)
    
    generators = [
        steady_rhythm_v4,
        wave_rider_v4,
        quick_hops_v4,
        rest_and_run_v4,
        stepped_ascent_v4,
        zigzag_chaos_v4,
        long_jumper_v4,
        mixed_madness_v4,
        kitchen_sink_v4,
        obstacle_course_v4,
    ]
    
    success_count = 0
    fail_count = 0
    
    for gen in generators:
        # Generate difficulty variants
        variants = generate_difficulty_variants(gen)
        
        for pattern, difficulty_suffix in variants:
            # Get base name without difficulty tag (remove "(Hard)", "(Medium)", "(Easy)")
            base_name = pattern["name"].replace(" (Hard)", "").replace(" (Medium)", "").replace(" (Easy)", "")
            fname = base_name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_") + difficulty_suffix
            if save_pattern(pattern, fname):
                success_count += 1
            else:
                fail_count += 1
    
    print(f"\n{'='*70}")
    print(f"✅ Successfully generated {success_count} valid patterns")
    if fail_count > 0:
        print(f"❌ Failed to generate {fail_count} patterns (physics validation failed)")
    print(f"{'='*70}")
    print("\nPattern Features:")
    print("  • Floor is lava - never touch ground!")
    print("  • All platforms floating (60-120px elevation)")
    print("  • Rhythm-based gameplay - jump, land, repeat")
    print("  • Varied platform sizes (thin hops to wide rest areas)")
    print("  • Physics-validated - all patterns guaranteed playable")
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    generate_all_patterns()
