"""
Pattern Library - Pre-designed obstacle pattern generators

Contains all pattern generator functions for creating varied gameplay experiences.
Each pattern is physics-validated to ensure playability.
"""

import random
from .obstacle_builders import (
    create_pattern,
    create_platform,
    create_floating_platform,
    random_gap,
    random_heights,
    alternating_heights,
    wave_heights,
    stepped_heights,
    constant_height,
    varied_widths,
    rhythm_widths,
    GAP_RHYTHM_SHORT,
    GAP_RHYTHM_MEDIUM,
    GAP_RHYTHM_LONG,
    GAP_RHYTHM_VARIED
)


# ============================================================================
# PATTERN GENERATORS
# ============================================================================

def steady_rhythm_v4():
    """Simple steady rhythm - great for getting comfortable with the mechanic."""
    obstacles = []
    count = random.randint(25, 30)
    
    # First platform at ground level for accessibility
    obstacles.append(create_platform(random.randint(4, 6), 0, "gap-2.0"))  # height=0 means ground level
    
    # Steady platforms at medium height
    gaps = GAP_RHYTHM_MEDIUM
    widths = [random.randint(3, 5) for _ in range(count)]
    heights = constant_height(count, height=2)  # Constant at height 2 (60px)
    
    for i, (h, w) in enumerate(zip(heights, widths)):
        gap = gaps[i % len(gaps)]
        obstacles.append(create_platform(w, h, gap))
    
    return create_pattern(
        "Steady Rhythm",
        "Consistent platform hops at steady height",
        obstacles,
        "platform",
        "4/4 steady"
    )


def wave_rider_v4():
    """Wave pattern - heights go up and down smoothly."""
    obstacles = []
    count = random.randint(28, 35)
    
    # First platform at ground level
    obstacles.append(create_platform(random.randint(4, 6), 0, "gap-2.0"))
    
    # Wave heights with varied gaps
    heights = wave_heights(count, low=1, high=4)
    widths = varied_widths(count)
    
    for i, (h, w) in enumerate(zip(heights, widths)):
        gap = random_gap(1.75, 2.25)
        obstacles.append(create_platform(w, h, gap))
    
    return create_pattern(
        "Wave Rider",
        "Ride the wave - platforms rise and fall",
        obstacles,
        "platform",
        "Flowing waves"
    )


def quick_hops_v4():
    """Fast-paced quick hops on thin platforms."""
    obstacles = []
    count = random.randint(30, 40)
    
    # First platform at ground level
    obstacles.append(create_platform(random.randint(4, 6), 0, "gap-2.0"))
    
    # Quick hops - thin platforms, short gaps
    gaps = GAP_RHYTHM_SHORT
    heights = alternating_heights(count, low=1, high=3)
    
    for i, h in enumerate(heights):
        gap = gaps[i % len(gaps)]
        width = random.randint(2, 3)  # Thin platforms only
        # Add lava to some gaps (20% chance)
        gap_hazard = "lava" if random.random() < 0.2 else None
        obstacles.append(create_platform(width, h, gap, gap_hazard))
    
    return create_pattern(
        "Quick Hops",
        "Fast-paced hopping on thin platforms - don't miss!",
        obstacles,
        "platform",
        "Fast 8th notes"
    )


def rest_and_run_v4():
    """Mix of rest platforms and running sections."""
    obstacles = []
    
    # First platform at ground level
    obstacles.append(create_platform(random.randint(4, 6), 0, "gap-2.0"))
    
    # Pattern: 3 quick hops -> 1 rest -> repeat
    for section in range(random.randint(5, 7)):
        # Quick section: 3 thin platforms with adequate gaps
        for hop in range(3):
            # Add lava to gaps occasionally (15% chance)
            gap_hazard = "lava" if section > 0 and hop > 0 and random.random() < 0.15 else None
            obstacles.append(create_platform(
                width=random.randint(2, 3),
                height=random.randint(1, 3),
                gap=random_gap(1.75, 2.25),
                gap_hazard=gap_hazard
            ))
        
        # Rest platform: wide and stable
        obstacles.append(create_platform(
            width=random.randint(6, 8),
            height=random.randint(2, 3),
            gap=random_gap(2.0, 2.25)
        ))
    
    return create_pattern(
        "Rest and Run",
        "Bursts of quick hops with rest platforms - catch your breath!",
        obstacles,
        "platform",
        "Burst then rest"
    )


def stepped_ascent_v4():
    """Gradual climb up then drop down."""
    obstacles = []
    count = random.randint(25, 32)
    
    # First platform at ground level
    obstacles.append(create_platform(random.randint(4, 6), 0, "gap-2.0"))
    
    # Stepped ascent
    heights = stepped_heights(count, low=1, high=4)
    widths = rhythm_widths(count)
    gaps = GAP_RHYTHM_VARIED
    
    for i, (h, w) in enumerate(zip(heights, widths)):
        gap = gaps[i % len(gaps)]
        # Add lava on descents (30% chance when dropping)
        gap_hazard = "lava" if i > 0 and heights[i] < heights[i-1] and random.random() < 0.3 else None
        obstacles.append(create_platform(w, h, gap, gap_hazard))
    
    return create_pattern(
        "Stepped Ascent",
        "Climb the steps, then drop!",
        obstacles,
        "platform",
        "Ascending steps"
    )


def zigzag_chaos_v4():
    """Chaotic height changes - safe transitions."""
    obstacles = []
    count = random.randint(28, 35)
    
    # First platform at ground level
    obstacles.append(create_platform(random.randint(4, 6), 0, "gap-2.0"))
    
    # Random heights with safe transitions (no big drops)
    heights = []
    prev_height = 2
    for _ in range(count):
        # Avoid big drops - max drop of 1 level
        max_down = max(1, prev_height - 1)
        max_up = min(4, prev_height + 2)
        height = random.randint(max_down, max_up)
        heights.append(height)
        prev_height = height
    
    widths = varied_widths(count)
    
    for i, (h, w) in enumerate(zip(heights, widths)):
        gap = random_gap(1.75, 2.25)
        # Add lava in gaps (25% chance)
        gap_hazard = "lava" if random.random() < 0.25 else None
        obstacles.append(create_platform(w, h, gap, gap_hazard))
    
    return create_pattern(
        "Zigzag Chaos",
        "Unpredictable heights - stay focused!",
        obstacles,
        "platform",
        "Chaotic variation"
    )


def long_jumper_v4():
    """Extended jumps - use the full jump distance."""
    obstacles = []
    count = random.randint(20, 25)
    
    # First platform at ground level
    obstacles.append(create_platform(random.randint(5, 7), 0, "gap-2.0"))
    
    # Long jumps with wide landing platforms
    gaps = GAP_RHYTHM_LONG
    heights = alternating_heights(count, low=1, high=4)
    
    for i, h in enumerate(heights):
        gap = gaps[i % len(gaps)]
        width = random.randint(5, 8)  # Wide platforms for safe landing
        # Add lava in longer gaps (35% chance)
        gap_hazard = "lava" if random.random() < 0.35 else None
        obstacles.append(create_platform(width, h, gap, gap_hazard))
    
    return create_pattern(
        "Long Jumper",
        "Maximum distance jumps - commit to the leap!",
        obstacles,
        "platform",
        "Extended jumps"
    )


def mixed_madness_v4():
    """Everything mixed - ultimate variety with safe height transitions."""
    obstacles = []
    count = random.randint(30, 40)
    
    # First platform at ground level
    obstacles.append(create_platform(random.randint(4, 6), 0, "gap-2.0"))
    
    # Complete chaos - all patterns mixed but avoid big drops
    heights = []
    prev_height = 2  # Start at reasonable height
    for _ in range(count):
        # Don't drop more than 1 level at a time
        max_drop = max(1, prev_height - 1)
        max_up = min(4, prev_height + 2)
        height = random.randint(max_drop, max_up)
        heights.append(height)
        prev_height = height
    
    widths = varied_widths(count)
    all_gaps = GAP_RHYTHM_SHORT + GAP_RHYTHM_MEDIUM + GAP_RHYTHM_LONG
    
    for i, (h, w) in enumerate(zip(heights, widths)):
        gap = random.choice(all_gaps)
        # More lava for chaos (30% chance)!
        gap_hazard = "lava" if random.random() < 0.3 else None
        obstacles.append(create_platform(w, h, gap, gap_hazard))
    
    return create_pattern(
        "Mixed Madness",
        "Everything at once - ultimate variety!",
        obstacles,
        "platform",
        "Total chaos"
    )


def kitchen_sink_v4():
    """
    ULTIMATE VARIETY: Combines everything!
    - 30% floating platforms (bar-{width}-{floor}-{ceiling})
    - 30% regular bars (bar-{width}-{height})
    - Hazards in gaps (lava, spikes, etc.)
    - Varied widths (2-8 blocks)
    - 10%+ at max height (120px)
    """
    obstacles = []
    count = random.randint(40, 50)
    
    # First platform at ground level
    obstacles.append(create_platform(random.randint(5, 7), 0, "gap-2.0"))
    
    # Available hazard types for gaps
    HAZARD_TYPES = ["spikes", "saw", "lava", "electric", "laser", "poison"]
    
    # Track what we've created for proper distribution
    platform_count = 0
    bar_count = 0
    max_height_count = 0
    prev_height = 2  # Start at moderate height
    
    for i in range(count):
        # Decide obstacle type based on current distribution
        total = platform_count + bar_count
        platform_ratio = platform_count / total if total > 0 else 0
        bar_ratio = bar_count / total if total > 0 else 0
        
        # Width variation (2-8 blocks)
        width = random.choice([2, 2, 3, 3, 3, 4, 4, 5, 6, 7, 8])
        
        # Height selection with safe transitions (no big drops)
        max_down = max(1, prev_height - 1)
        max_up = min(4, prev_height + 2)
        
        # Ensure 10%+ at max height 4
        if max_height_count / (i + 1) < 0.10 and random.random() < 0.3:
            height = 4  # Max height 120px
            max_height_count += 1
        else:
            height = random.randint(max_down, max_up)
            if height == 4:
                max_height_count += 1
        
        prev_height = height  # Track for next iteration
        
        # Gap selection
        gap = random.choice(GAP_RHYTHM_SHORT + GAP_RHYTHM_MEDIUM + GAP_RHYTHM_LONG)
        
        # Hazard in gap occasionally (15% chance)
        gap_hazard = random.choice(HAZARD_TYPES) if random.random() < 0.15 else None
        
        # Choose obstacle type to maintain 30/30 distribution
        if platform_ratio < 0.30 or (platform_ratio < 0.35 and bar_ratio >= 0.30):
            # Create floating platform (suspended in air)
            floor_height = height
            ceiling_height = height + random.randint(2, 3)  # Platform thickness
            obstacles.append(create_floating_platform(width, floor_height, ceiling_height, gap, gap_hazard))
            platform_count += 1
            
        elif bar_ratio < 0.30 or (bar_ratio < 0.35 and platform_ratio >= 0.30):
            # Create regular bar (on ground, various heights)
            obstacles.append(create_platform(width, height, gap, gap_hazard))
            bar_count += 1
            
        else:
            # Random choice between platform and bar
            if random.random() < 0.5:
                floor_height = height
                ceiling_height = height + random.randint(2, 3)
                obstacles.append(create_floating_platform(width, floor_height, ceiling_height, gap, gap_hazard))
                platform_count += 1
            else:
                obstacles.append(create_platform(width, height, gap, gap_hazard))
                bar_count += 1
    
    return create_pattern(
        "Kitchen Sink",
        f"Everything! Platforms, bars, hazards - {platform_count}P/{bar_count}B, {max_height_count} at max height",
        obstacles,
        "mixed",
        "Ultimate variety"
    )


def obstacle_course_v4():
    """
    MAXIMUM VARIETY with strategic sequences:
    - Thin platform sequences (precision jumps)
    - Wide bar rest areas (catch your breath)
    - Hazard-filled gaps
    - Mixed height challenges
    - 30% platforms, 30% bars, varied hazards
    """
    obstacles = []
    HAZARD_TYPES = ["spikes", "saw", "lava", "electric", "laser", "poison"]
    
    # First platform at ground level
    obstacles.append(create_platform(random.randint(5, 7), 0, "gap-2.0"))
    
    # Stats tracking
    platform_count = 0
    bar_count = 0
    max_height_count = 0
    total_obstacles = 1  # Count the starting platform
    
    # Sequence 2: Thin platform precision section (5-7 platforms)
    prev_height = 2  # Start at moderate height
    for i in range(random.randint(5, 7)):
        # Safe height transitions - no big drops
        max_down = max(1, prev_height - 1)
        max_up = min(4, prev_height + 1)
        height = random.randint(max_down, max_up)
        if height == 4:
            max_height_count += 1
        floor = height
        ceiling = height + 2
        # Add hazard to some gaps
        gap_hazard = random.choice(HAZARD_TYPES) if i > 0 and random.random() < 0.2 else None
        obstacles.append(create_floating_platform(2, floor, ceiling, random.choice(GAP_RHYTHM_SHORT), gap_hazard))
        platform_count += 1
        total_obstacles += 1
        prev_height = height
    
    # Sequence 3: Wide bar rest area
    obstacles.append(create_platform(random.randint(6, 8), random.randint(1, 2), "gap-2.0"))
    bar_count += 1
    total_obstacles += 1
    
    # Sequence 4: Mixed height bars (6-8 bars)
    for _ in range(random.randint(6, 8)):
        height = random.choice([1, 2, 3, 4, 4])  # Favor height 4
        if height == 4:
            max_height_count += 1
        width = random.choice([3, 4, 5])
        # Add hazards to some gaps
        gap_hazard = random.choice(HAZARD_TYPES) if random.random() < 0.25 else None
        obstacles.append(create_platform(width, height, random.choice(GAP_RHYTHM_MEDIUM), gap_hazard))
        bar_count += 1
        total_obstacles += 1
    
    # Sequence 5: Platform bridge (wide platforms at max height)
    for _ in range(random.randint(4, 6)):
        floor = 4
        ceiling = random.randint(6, 7)
        obstacles.append(create_floating_platform(random.randint(5, 7), floor, ceiling, random.choice(GAP_RHYTHM_MEDIUM)))
        platform_count += 1
        max_height_count += 1
        total_obstacles += 1
    
    # Sequence 6: Gradual descent (no big drops!)
    for h in [4, 3, 3, 2, 2, 1]:
        obstacles.append(create_platform(random.randint(3, 5), h, "gap-2.0"))
        bar_count += 1
        if h == 4:
            max_height_count += 1
        total_obstacles += 1
    
    # Sequence 7: Final mixed chaos (balance to 30/30 distribution)
    remaining = random.randint(8, 12)
    for _ in range(remaining):
        total = platform_count + bar_count
        platform_ratio = platform_count / total if total > 0 else 0
        bar_ratio = bar_count / total if total > 0 else 0
        
        height = random.randint(1, 4)
        if height == 4:
            max_height_count += 1
        
        if platform_ratio < 0.30:
            # Add platform
            floor = height
            ceiling = height + random.randint(2, 3)
            width = random.choice([2, 3, 4, 5, 6])
            obstacles.append(create_floating_platform(width, floor, ceiling, random.choice(GAP_RHYTHM_MEDIUM + GAP_RHYTHM_LONG)))
            platform_count += 1
        elif bar_ratio < 0.30:
            # Add bar
            width = random.choice([2, 3, 4, 5, 6, 7, 8])
            obstacles.append(create_platform(width, height, random.choice(GAP_RHYTHM_MEDIUM + GAP_RHYTHM_LONG)))
            bar_count += 1
        else:
            # Random choice
            if random.random() < 0.5:
                floor = height
                ceiling = height + 2
                obstacles.append(create_floating_platform(random.randint(2, 6), floor, ceiling, random.choice(GAP_RHYTHM_MEDIUM)))
                platform_count += 1
            else:
                obstacles.append(create_platform(random.randint(2, 7), height, random.choice(GAP_RHYTHM_MEDIUM)))
                bar_count += 1
        total_obstacles += 1
    
    max_height_pct = int(100 * max_height_count / total_obstacles)
    platform_pct = int(100 * platform_count / total_obstacles)
    bar_pct = int(100 * bar_count / total_obstacles)
    
    return create_pattern(
        "Obstacle Course",
        f"Strategic sequences: {platform_count}P({platform_pct}%)/{bar_count}B({bar_pct}%), {max_height_count}({max_height_pct}%) max height",
        obstacles,
        "mixed",
        "Varied sequences"
    )


# ============================================================================
# DIFFICULTY SCALING
# ============================================================================

def scale_pattern_widths(obstacles, scale_factor):
    """
    Scale all platform/bar widths by scale_factor.
    For example: 1.0 = hard (no change), 1.15 = medium (+15%), 1.25 = easy (+25%)
    
    Args:
        obstacles: List of obstacle dictionaries
        scale_factor: Width multiplier (e.g., 1.15 for +15%)
        
    Returns:
        New list of scaled obstacles
    """
    scaled_obstacles = []
    for obs in obstacles:
        scaled_obs = obs.copy()
        bar_type = obs.get('bar_type', '')
        
        if bar_type.startswith('bar-'):
            parts = bar_type.replace('bar-', '').split('-')
            if len(parts) >= 2:
                # Scale the width (first number)
                original_width = int(parts[0])
                new_width = max(2, int(original_width * scale_factor))  # Min width of 2
                
                # Reconstruct bar_type with new width
                if len(parts) == 3:
                    # Floating platform: bar-{width}-{floor}-{ceiling}
                    scaled_obs['bar_type'] = f"bar-{new_width}-{parts[1]}-{parts[2]}"
                else:
                    # Regular bar: bar-{width}-{height}
                    scaled_obs['bar_type'] = f"bar-{new_width}-{parts[1]}"
        
        scaled_obstacles.append(scaled_obs)
    
    return scaled_obstacles


def generate_difficulty_variants(pattern_func):
    """
    Generate easy, medium, and hard variants of a pattern.
    
    Args:
        pattern_func: Pattern generator function
        
    Returns:
        List of (pattern, difficulty_suffix) tuples
    """
    # Generate base pattern
    base_pattern = pattern_func()
    base_obstacles = base_pattern['obstacles']
    
    variants = []
    
    # Hard (original, no scaling)
    hard_pattern = create_pattern(
        base_pattern['name'] + " (Hard)",
        base_pattern['description'],
        base_obstacles,
        base_pattern['metadata']['type'],
        base_pattern['metadata']['rhythm']
    )
    variants.append((hard_pattern, "_hard"))
    
    # Medium (+15% width)
    medium_obstacles = scale_pattern_widths(base_obstacles, 1.15)
    medium_pattern = create_pattern(
        base_pattern['name'] + " (Medium)",
        base_pattern['description'],
        medium_obstacles,
        base_pattern['metadata']['type'],
        base_pattern['metadata']['rhythm']
    )
    variants.append((medium_pattern, "_medium"))
    
    # Easy (+25% width)
    easy_obstacles = scale_pattern_widths(base_obstacles, 1.25)
    easy_pattern = create_pattern(
        base_pattern['name'] + " (Easy)",
        base_pattern['description'],
        easy_obstacles,
        base_pattern['metadata']['type'],
        base_pattern['metadata']['rhythm']
    )
    variants.append((easy_pattern, "_easy"))
    
    return variants
