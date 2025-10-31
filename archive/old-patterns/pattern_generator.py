"""
Pattern generator script for creating obstacle patterns programmatically.
Run this script to generate pattern variations automatically.
"""

import json
import os


def create_pattern(name, description, obstacles):
    """Helper to create pattern JSON"""
    return {
        "name": name,
        "description": description,
        "obstacles": obstacles
    }


def save_pattern(pattern, filename, archive=False):
    """Save pattern to file"""
    folder = "archive/old-patterns" if archive else "obstacle_patterns"
    path = f"{folder}/{filename}.json"
    with open(path, 'w') as f:
        json.dump(pattern, f, indent=2)
    print(f"Created: {path}")


# Example: Generate spike wall variations for different heights
def generate_spike_walls():
    """Generate spike wall patterns at different heights"""
    for height in range(3, 9):
        pattern = create_pattern(
            f"Spike Wall {height}",
            f"Dense wall of spikes at height {height}",
            [{"bar_type": f"bar-1-{height}", "gap_type": "gap-0"} for _ in range(8)]
        )
        save_pattern(pattern, f"spike_wall_{height}")


# Example: Generate staircase variations
def generate_staircases():
    """Generate ascending/descending staircases"""
    for max_height in range(4, 8):
        obstacles = []
        # Ascending
        for h in range(1, max_height + 1):
            obstacles.append({"bar_type": f"bar-2-{h}", "gap_type": "gap-0"})
        # Descending
        for h in range(max_height - 1, 0, -1):
            obstacles.append({"bar_type": f"bar-2-{h}", "gap_type": "gap-0"})
        obstacles[-1]["gap_type"] = "gap-2.5"  # Final gap
        
        pattern = create_pattern(
            f"Staircase {max_height}",
            f"Symmetrical staircase reaching height {max_height}",
            obstacles
        )
        save_pattern(pattern, f"staircase_{max_height}")


# Example: Generate platform bridges with varying widths
def generate_bridges():
    """Generate bridge patterns with different platform widths"""
    for width in range(4, 9):
        obstacles = [
            {"bar_type": f"bar-{width}-1", "gap_type": "gap-2"}
            for _ in range(6)
        ]
        obstacles[-1]["gap_type"] = "gap-2.5"
        
        pattern = create_pattern(
            f"Bridge Width {width}",
            f"Platform bridge with width-{width} platforms",
            obstacles
        )
        save_pattern(pattern, f"bridge_w{width}")


# Example: Generate floating sky bridges at different heights
def generate_sky_bridges():
    """Generate floating platform patterns at various heights"""
    for floor_height in range(2, 6):
        obstacles = [
            {"bar_type": f"bar-4-{floor_height}-1", "gap_type": "gap-2"}
            for _ in range(5)
        ]
        obstacles[-1]["gap_type"] = "gap-2.5"
        
        pattern = create_pattern(
            f"Sky Bridge {floor_height}",
            f"Floating platforms at height {floor_height}",
            obstacles
        )
        save_pattern(pattern, f"sky_bridge_h{floor_height}")


# Example: Generate ceiling obstacles
def generate_ceiling_obstacles():
    """Generate hanging obstacles from above"""
    for ceiling_drop in range(1, 4):
        obstacles = [
            {"bar_type": f"bar-2-{5+ceiling_drop}-{ceiling_drop}", "gap_type": "gap-1.5"}
            for _ in range(4)
        ]
        obstacles[-1]["gap_type"] = "gap-2"
        
        pattern = create_pattern(
            f"Ceiling Drop {ceiling_drop}",
            f"Hanging obstacles dropping {ceiling_drop} units from ceiling",
            obstacles
        )
        save_pattern(pattern, f"ceiling_drop_{ceiling_drop}")


def generate_mixed_marathons():
    """Generate long patterns (20-40 blocks) mixing ground obstacles and floating platforms"""
    import random
    
    # Pattern 1: Ground Run → Platform Climb → Ground Sprint
    obstacles = []
    # Ground run (8 blocks)
    for _ in range(8):
        obstacles.append({"bar_type": f"bar-{random.randint(2,4)}-{random.randint(1,2)}", "gap_type": "gap-1.5"})
    
    # Transition: staircase up (5 blocks)
    for h in range(1, 4):
        obstacles.append({"bar_type": f"bar-2-{h}", "gap_type": "gap-0"})
    
    # Floating platforms (10 blocks at height 3)
    for _ in range(10):
        obstacles.append({"bar_type": f"bar-{random.randint(3,5)}-3-1", "gap_type": "gap-1.5"})
    
    # Transition: staircase down (3 blocks)
    for h in range(2, 0, -1):
        obstacles.append({"bar_type": f"bar-2-{h}", "gap_type": "gap-0"})
    
    # Ground sprint (6 blocks)
    for _ in range(6):
        obstacles.append({"bar_type": f"bar-{random.randint(2,3)}-1", "gap_type": "gap-2"})
    
    obstacles[-1]["gap_type"] = "gap-3"  # Resting space
    
    pattern = create_pattern(
        "Marathon Mix Alpha",
        "Long pattern: ground run → platform climb → ground sprint (32 blocks)",
        obstacles
    )
    save_pattern(pattern, "marathon_mix_alpha")
    
    
    # Pattern 2: Low Platforms → High Platforms → Ground Finish
    obstacles = []
    # Low floating platforms (12 blocks at height 2)
    for _ in range(12):
        obstacles.append({"bar_type": f"bar-{random.randint(3,6)}-2-1", "gap_type": "gap-1.5"})
    
    # Climb to high platforms (4 blocks)
    obstacles.append({"bar_type": "bar-3-2-1", "gap_type": "gap-1"})
    obstacles.append({"bar_type": "bar-3-3-1", "gap_type": "gap-1"})
    obstacles.append({"bar_type": "bar-3-3-1", "gap_type": "gap-1.5"})
    
    # High floating platforms (8 blocks at height 3)
    for _ in range(8):
        obstacles.append({"bar_type": f"bar-{random.randint(4,6)}-3-1", "gap_type": "gap-1.5"})
    
    # Drop to ground (3 blocks descending)
    obstacles.append({"bar_type": "bar-2-2", "gap_type": "gap-0"})
    obstacles.append({"bar_type": "bar-2-1", "gap_type": "gap-0"})
    
    # Ground finish (6 blocks)
    for _ in range(6):
        obstacles.append({"bar_type": f"bar-{random.randint(2,4)}-1", "gap_type": "gap-2"})
    
    obstacles[-1]["gap_type"] = "gap-3"
    
    pattern = create_pattern(
        "Marathon Mix Beta",
        "Long pattern: low platforms → high platforms → ground finish (35 blocks)",
        obstacles
    )
    save_pattern(pattern, "marathon_mix_beta")
    
    
    # Pattern 3: Ground Zigzag → Platform Run → Ground Obstacles
    obstacles = []
    # Ground zigzag (10 blocks - varying heights)
    heights = [1, 2, 1, 2, 3, 2, 1, 2, 1, 2]
    for h in heights:
        obstacles.append({"bar_type": f"bar-{random.randint(2,3)}-{h}", "gap_type": "gap-1.5"})
    
    # Climb up (4 blocks)
    for h in range(2, 4):
        obstacles.append({"bar_type": f"bar-2-{h}", "gap_type": "gap-0"})
    
    # Platform run (14 blocks at height 3)
    for _ in range(14):
        obstacles.append({"bar_type": f"bar-{random.randint(4,7)}-3-1", "gap_type": "gap-1.5"})
    
    # Drop to ground
    obstacles.append({"bar_type": "bar-2-2", "gap_type": "gap-1"})
    obstacles.append({"bar_type": "bar-2-1", "gap_type": "gap-1"})
    
    # Ground obstacles (8 blocks)
    for _ in range(8):
        obstacles.append({"bar_type": f"bar-{random.randint(2,4)}-{random.randint(1,2)}", "gap_type": "gap-2"})
    
    obstacles[-1]["gap_type"] = "gap-3"
    
    pattern = create_pattern(
        "Marathon Mix Gamma",
        "Long pattern: ground zigzag → platform run → ground obstacles (38 blocks)",
        obstacles
    )
    save_pattern(pattern, "marathon_mix_gamma")
    
    
    # Pattern 4: Ground Stairs → Extended Platforms → Ground Run
    obstacles = []
    # Ground ascending stairs (6 blocks)
    for h in range(1, 4):
        obstacles.append({"bar_type": f"bar-3-{h}", "gap_type": "gap-0"})
        if h < 3:  # Don't add gap after last stair
            obstacles.append({"bar_type": f"bar-2-{h}", "gap_type": "gap-1"})
    
    # Transition platform at height 3 (player is on top of height-3 stair)
    obstacles.append({"bar_type": "bar-4-3-1", "gap_type": "gap-1.5"})
    
    # Extended platform section (15 blocks at height 3)
    for _ in range(15):
        obstacles.append({"bar_type": f"bar-{random.randint(3,6)}-3-1", "gap_type": "gap-1.5"})
    
    # Descending stairs (4 blocks)
    for h in range(3, 0, -1):
        obstacles.append({"bar_type": f"bar-2-{h}", "gap_type": "gap-0"})
    
    # Ground run (10 blocks)
    for _ in range(10):
        obstacles.append({"bar_type": f"bar-{random.randint(2,4)}-1", "gap_type": "gap-1.5"})
    
    obstacles[-1]["gap_type"] = "gap-3"
    
    pattern = create_pattern(
        "Marathon Mix Delta",
        "Long pattern: ground stairs → extended platforms → ground run (35 blocks)",
        obstacles
    )
    save_pattern(pattern, "marathon_mix_delta")
    
    
    # Pattern 5: Alternating Ground/Platform Sections
    obstacles = []
    # Ground section 1 (7 blocks)
    for _ in range(7):
        obstacles.append({"bar_type": f"bar-{random.randint(2,4)}-{random.randint(1,2)}", "gap_type": "gap-1.5"})
    
    # Climb to platforms (3 blocks)
    for h in range(1, 3):
        obstacles.append({"bar_type": f"bar-2-{h}", "gap_type": "gap-0"})
    
    # Platform section 1 (8 blocks at height 2)
    for _ in range(8):
        obstacles.append({"bar_type": f"bar-{random.randint(4,6)}-2-1", "gap_type": "gap-1.5"})
    
    # Drop to ground
    obstacles.append({"bar_type": "bar-2-1", "gap_type": "gap-1"})
    
    # Ground section 2 (6 blocks)
    for _ in range(6):
        obstacles.append({"bar_type": f"bar-{random.randint(2,3)}-1", "gap_type": "gap-2"})
    
    # Climb higher (4 blocks)
    for h in range(1, 4):
        obstacles.append({"bar_type": f"bar-2-{h}", "gap_type": "gap-0"})
    
    # Platform section 2 (6 blocks at height 3)
    for _ in range(6):
        obstacles.append({"bar_type": f"bar-{random.randint(4,5)}-3-1", "gap_type": "gap-1.5"})
    
    # Final drop
    obstacles.append({"bar_type": "bar-2-2", "gap_type": "gap-1"})
    obstacles.append({"bar_type": "bar-2-1", "gap_type": "gap-2"})
    
    obstacles[-1]["gap_type"] = "gap-3"
    
    pattern = create_pattern(
        "Marathon Mix Epsilon",
        "Long pattern: alternating ground/platform sections (37 blocks)",
        obstacles
    )
    save_pattern(pattern, "marathon_mix_epsilon")


if __name__ == "__main__":
    print("Pattern Generator")
    print("=" * 50)
    
    # Uncomment the generators you want to run:
    
    # generate_spike_walls()
    # generate_staircases()
    # generate_bridges()
    # generate_sky_bridges()        # NEW: Floating platforms!
    # generate_ceiling_obstacles()   # NEW: Ceiling hazards!
    generate_mixed_marathons()     # NEW: Long mixed patterns (20-40 blocks)!
    
    print("\nDone! Run the game to test new patterns.")
