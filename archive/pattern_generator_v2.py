"""
Enhanced Pattern Generator for Geometry Dash Clone
Follows gameplay design principles: rhythm, flow, and progressive challenge.

Design Rules:
- Patterns: 20-40 blocks with resting spaces
- No consecutive same-height obstacles (ascending/descending only)
- Valleys must be extra wide
- Killzones under platform sections to encourage platform use
- Smooth transitions between patterns
- Distinct pattern identities
"""

import json
import os
import random


# ============================================================================
# CORE HELPERS
# ============================================================================

def create_pattern(name, description, obstacles, pattern_type, rhythm_hint):
    """Create pattern JSON with metadata"""
    return {
        "name": name,
        "description": description,
        "obstacles": obstacles,
        "metadata": {
            "type": pattern_type,  # "bar" or "platform" or "mixed"
            "length": len(obstacles),
            "rhythm": rhythm_hint
        }
    }


def save_pattern(pattern, filename):
    """Save pattern to obstacle_patterns folder"""
    path = f"obstacle_patterns/{filename}.json"
    with open(path, 'w') as f:
        json.dump(pattern, f, indent=2)
    print(f"✓ Created: {filename} ({pattern['metadata']['length']} blocks, {pattern['metadata']['type']})")


def add_resting_gap(obstacles, gap_size="gap-3"):
    """Add resting space to last obstacle"""
    if obstacles:
        obstacles[-1]["gap_type"] = gap_size


# ============================================================================
# RHYTHM & HEIGHT HELPERS
# ============================================================================

def ascending_heights(start, end, count):
    """Generate ascending height sequence (no repeats)"""
    if count == 1:
        return [start]
    step = max(1, (end - start) // (count - 1))
    heights = []
    current = start
    for _ in range(count):
        heights.append(current)
        current = min(current + step, end)
    return heights


def descending_heights(start, end, count):
    """Generate descending height sequence (no repeats)"""
    return list(reversed(ascending_heights(end, start, count)))


def wave_heights(min_h, max_h, count):
    """Generate wave pattern (ascending then descending, no repeats)"""
    half = count // 2
    ascending = ascending_heights(min_h, max_h, half)
    descending = descending_heights(max_h, min_h, count - half)
    return ascending + descending


def zigzag_heights(min_h, max_h, count):
    """Generate zigzag pattern (alternating up/down trends, no consecutive repeats)"""
    heights = []
    current = min_h
    going_up = True
    
    for i in range(count):
        heights.append(current)
        
        if going_up:
            current += 1
            if current >= max_h:
                going_up = False
        else:
            current -= 1
            if current <= min_h:
                going_up = True
    
    return heights


# ============================================================================
# OBSTACLE BUILDERS
# ============================================================================

def create_bar_obstacle(height, width=None, gap="gap-1.5"):
    """Create ground-based bar obstacle"""
    if width is None:
        width = random.randint(2, 4)
    return {
        "bar_type": f"bar-{width}-{height}",
        "gap_type": gap
    }


def create_platform_obstacle(floor_height, width=None, ceiling_height=1, gap="gap-1.5"):
    """Create floating platform obstacle"""
    if width is None:
        width = random.randint(3, 6)
    return {
        "bar_type": f"bar-{width}-{floor_height}-{ceiling_height}",
        "gap_type": gap
    }


def create_killzone(width=1, gap="gap-0"):
    """Create killzone marker (height 0 = floor hazard)"""
    return {
        "bar_type": f"bar-{width}-0",
        "gap_type": gap,
        "is_killzone": True  # Visual marker for renderer
    }


# ============================================================================
# PATTERN GENERATORS - BAR SECTIONS
# ============================================================================

def generate_rising_stairs_pattern():
    """Bar pattern: Gradual ascending staircase with rhythm"""
    obstacles = []
    
    # Ascending stairs (12-16 blocks)
    count = random.randint(12, 16)
    heights = ascending_heights(1, 3, count)
    
    for h in heights:
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    # Brief rest section (3 blocks)
    for _ in range(3):
        obstacles.append(create_bar_obstacle(1, width=3, gap="gap-1.5"))
    
    add_resting_gap(obstacles, "gap-3")
    
    return create_pattern(
        "Rising Stairs Flow",
        "Gradual ascending staircase with rhythmic rest section",
        obstacles,
        "bar",
        "Steady climb - sync to building beat"
    )


def generate_valley_run_pattern():
    """Bar pattern: Down into wide valley, then up (valley is extra wide)"""
    obstacles = []
    
    # Descend (6 blocks)
    descend_heights = descending_heights(3, 1, 6)
    for h in descend_heights:
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    # WIDE VALLEY (8 blocks - extra wide as per rules)
    for _ in range(8):
        obstacles.append(create_bar_obstacle(1, width=random.randint(3, 5), gap="gap-2"))
    
    # Ascend (6 blocks)
    ascend_heights = ascending_heights(1, 3, 6)
    for h in ascend_heights:
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    # Finish (4 blocks)
    for _ in range(4):
        obstacles.append(create_bar_obstacle(3, width=3, gap="gap-1.5"))
    
    add_resting_gap(obstacles, "gap-3")
    
    return create_pattern(
        "Valley Runner",
        "Descend into wide valley, then climb back up",
        obstacles,
        "bar",
        "Medium tempo - wide valley for momentum"
    )


def generate_zigzag_rhythm_pattern():
    """Bar pattern: Zigzag heights with consistent rhythm"""
    obstacles = []
    
    # Zigzag section (18-22 blocks)
    count = random.randint(18, 22)
    heights = zigzag_heights(1, 3, count)
    
    for h in heights:
        obstacles.append(create_bar_obstacle(h, width=random.randint(2, 3), gap="gap-1.5"))
    
    # Smooth landing (3 blocks)
    for _ in range(3):
        obstacles.append(create_bar_obstacle(1, width=4, gap="gap-2"))
    
    add_resting_gap(obstacles, "gap-3")
    
    return create_pattern(
        "Zigzag Rhythm Run",
        "Alternating height pattern with steady beat",
        obstacles,
        "bar",
        "Fast tempo - continuous flow"
    )


# ============================================================================
# PATTERN GENERATORS - PLATFORM SECTIONS
# ============================================================================

def generate_ascending_platforms_pattern():
    """Platform pattern: Rising platforms with killzones below"""
    obstacles = []
    
    # Ground start (3 blocks)
    for _ in range(3):
        obstacles.append(create_bar_obstacle(1, width=3, gap="gap-1.5"))
    
    # Transition up (3 blocks)
    for h in range(1, 4):
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    # Ascending platforms (12-15 blocks) with KILLZONES below
    platform_count = random.randint(12, 15)
    floor_heights = ascending_heights(3, 3, platform_count)  # Stay at height 3 mostly
    
    # Add killzones before platform section
    for _ in range(2):
        obstacles.append(create_killzone(width=2, gap="gap-0"))
    
    for floor_h in floor_heights:
        obstacles.append(create_platform_obstacle(floor_h, width=random.randint(4, 6), gap="gap-1.5"))
    
    # Descent (3 blocks)
    for h in range(3, 0, -1):
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    # Ground finish (2 blocks)
    for _ in range(2):
        obstacles.append(create_bar_obstacle(1, width=3, gap="gap-2"))
    
    add_resting_gap(obstacles, "gap-3")
    
    return create_pattern(
        "Sky Climber",
        "Rising platform section with floor killzones",
        obstacles,
        "platform",
        "Flowing jumps - stay high or die"
    )


def generate_wave_platforms_pattern():
    """Platform pattern: Wave-like platform heights"""
    obstacles = []
    
    # Ground intro (4 blocks)
    for _ in range(4):
        obstacles.append(create_bar_obstacle(1, width=3, gap="gap-1.5"))
    
    # Climb to platforms (2 blocks)
    for h in [2, 3]:
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    # Wave platforms (16-20 blocks) with KILLZONES
    platform_count = random.randint(16, 20)
    heights = wave_heights(2, 3, platform_count)  # Wave between heights 2-3
    
    # Killzones under platforms
    for _ in range(3):
        obstacles.append(create_killzone(width=2, gap="gap-0"))
    
    for floor_h in heights:
        obstacles.append(create_platform_obstacle(floor_h, width=random.randint(4, 5), gap="gap-1.5"))
    
    # Return to ground (2 blocks)
    for h in range(2, 0, -1):
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    add_resting_gap(obstacles, "gap-3")
    
    return create_pattern(
        "Wave Rider",
        "Undulating platform heights - rhythmic wave pattern",
        obstacles,
        "platform",
        "Medium flow - ride the wave"
    )


# ============================================================================
# PATTERN GENERATORS - MIXED SECTIONS
# ============================================================================

def generate_mixed_challenge_pattern():
    """Mixed pattern: Bars → Platforms → Bars with varying intensity"""
    obstacles = []
    
    # Bar section 1: Rising (8 blocks)
    bar_heights_1 = ascending_heights(1, 3, 8)
    for h in bar_heights_1:
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-1.5"))
    
    # Transition to platforms (2 blocks)
    for h in [3, 3]:
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    # Platform section (10 blocks) with KILLZONES
    for _ in range(2):
        obstacles.append(create_killzone(width=2, gap="gap-0"))
    
    for _ in range(10):
        obstacles.append(create_platform_obstacle(3, width=random.randint(4, 6), gap="gap-1.5"))
    
    # Drop to bars (3 blocks)
    for h in range(3, 0, -1):
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    # Bar section 2: Descending rhythm (6 blocks)
    bar_heights_2 = descending_heights(2, 1, 6)
    for h in bar_heights_2:
        obstacles.append(create_bar_obstacle(h, width=3, gap="gap-2"))
    
    add_resting_gap(obstacles, "gap-3")
    
    return create_pattern(
        "Challenge Medley",
        "Mixed bars and platforms - tests versatility",
        obstacles,
        "mixed",
        "Variable tempo - adapt to sections"
    )


def generate_progressive_ascent_pattern():
    """Mixed pattern: Progressive difficulty increase"""
    obstacles = []
    
    # Easy start: Low bars (6 blocks)
    for _ in range(6):
        obstacles.append(create_bar_obstacle(1, width=random.randint(3, 5), gap="gap-2"))
    
    # Medium: Ascending bars (6 blocks)
    medium_heights = ascending_heights(1, 2, 6)
    for h in medium_heights:
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-1.5"))
    
    # Hard: High platforms (12 blocks) with KILLZONES
    obstacles.append(create_bar_obstacle(3, width=2, gap="gap-0"))
    
    for _ in range(2):
        obstacles.append(create_killzone(width=2, gap="gap-0"))
    
    for _ in range(12):
        obstacles.append(create_platform_obstacle(3, width=random.randint(4, 5), gap="gap-1.5"))
    
    # Cool down: Descent (4 blocks)
    for h in range(3, 0, -1):
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    # Rest (2 blocks)
    for _ in range(2):
        obstacles.append(create_bar_obstacle(1, width=4, gap="gap-2"))
    
    add_resting_gap(obstacles, "gap-3")
    
    return create_pattern(
        "Progressive Climb",
        "Gradual difficulty increase: easy → medium → hard → rest",
        obstacles,
        "mixed",
        "Building intensity - progressive challenge"
    )


# ============================================================================
# MAIN GENERATOR
# ============================================================================

def generate_all_patterns():
    """Generate complete pattern set"""
    print("\n" + "=" * 60)
    print("🎮 GEOMETRY DASH PATTERN GENERATOR V2")
    print("=" * 60)
    print("\nDesign Principles:")
    print("  ✓ Patterns: 20-40 blocks with resting spaces")
    print("  ✓ No consecutive same heights (ascending/descending)")
    print("  ✓ Extra-wide valleys")
    print("  ✓ Killzones under platform sections")
    print("  ✓ Rhythmic flow and distinct identities")
    print("\n" + "-" * 60)
    
    patterns_created = 0
    
    # Bar Patterns
    print("\n📊 Generating BAR patterns...")
    save_pattern(generate_rising_stairs_pattern(), "rising_stairs_flow")
    patterns_created += 1
    
    save_pattern(generate_valley_run_pattern(), "valley_runner")
    patterns_created += 1
    
    save_pattern(generate_zigzag_rhythm_pattern(), "zigzag_rhythm_run")
    patterns_created += 1
    
    # Platform Patterns
    print("\n🌟 Generating PLATFORM patterns...")
    save_pattern(generate_ascending_platforms_pattern(), "sky_climber")
    patterns_created += 1
    
    save_pattern(generate_wave_platforms_pattern(), "wave_rider")
    patterns_created += 1
    
    # Mixed Patterns
    print("\n🎯 Generating MIXED patterns...")
    save_pattern(generate_mixed_challenge_pattern(), "challenge_medley")
    patterns_created += 1
    
    save_pattern(generate_progressive_ascent_pattern(), "progressive_climb")
    patterns_created += 1
    
    print("\n" + "-" * 60)
    print(f"\n✅ Generated {patterns_created} patterns successfully!")
    print("\n💡 Next steps:")
    print("  1. Run the game to test patterns")
    print("  2. Check killzone rendering (height 0 obstacles)")
    print("  3. Verify no consecutive same-height obstacles")
    print("  4. Test rhythm and flow")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    generate_all_patterns()
