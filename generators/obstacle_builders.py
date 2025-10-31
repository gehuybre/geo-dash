"""
Obstacle Builders - Pattern creation utilities

Provides builder functions for creating obstacles, platforms, and patterns
with varied gaps, heights, and widths.
"""

import random


# ============================================================================
# GAP PATTERNS
# ============================================================================

# Jump peaks at 112.5px horizontal distance
# For elevated platforms, you need to be descending when you arrive
# Higher platforms = need even more distance because jump goes higher
# Safe formula: gap should be > (112px + height_boost)
# For heights 60-120px, minimum gap should be ~180-200px to ensure landing
GAP_RHYTHM_SHORT = ["gap-1.75", "gap-2.0", "gap-1.75", "gap-2.0"]  # 175-200px - safe minimum
GAP_RHYTHM_MEDIUM = ["gap-2.0", "gap-2.25", "gap-2.0", "gap-2.25"]  # 200-225px - comfortable
GAP_RHYTHM_LONG = ["gap-2.0", "gap-2.25", "gap-2.0", "gap-2.25"]  # 200-225px - max distance
GAP_RHYTHM_VARIED = ["gap-1.75", "gap-2.0", "gap-2.25", "gap-2.0"]  # Mixed rhythm


def random_gap(min_mult=1.75, max_mult=2.25):
    """
    Generate random gap for elevated platforms (needs >175px for safe landing).
    
    Args:
        min_mult: Minimum gap multiplier
        max_mult: Maximum gap multiplier
        
    Returns:
        Gap string in format "gap-{multiplier}"
    """
    mult = round(random.uniform(min_mult, max_mult) * 4) / 4  # Round to 0.25
    return f"gap-{mult}"


# ============================================================================
# HEIGHT PATTERNS
# ============================================================================

def random_heights(count, low=1, high=4):
    """
    Random heights - trajectory validation ensures they're all reachable.
    
    Args:
        count: Number of heights to generate
        low: Minimum height
        high: Maximum height
        
    Returns:
        List of random heights
    """
    return [random.randint(low, high) for _ in range(count)]


def alternating_heights(count, low=2, high=4):
    """
    Create alternating high-low pattern.
    
    Args:
        count: Number of heights to generate
        low: Low height value
        high: High height value
        
    Returns:
        List of alternating heights
    """
    heights = []
    current = low
    for _ in range(count):
        heights.append(current)
        current = high if current == low else low
    return heights


def wave_heights(count, low=1, high=4):
    """
    Create smooth wave pattern - up then down.
    
    Args:
        count: Number of heights to generate
        low: Minimum height
        high: Maximum height
        
    Returns:
        List of heights forming a wave pattern
    """
    mid = count // 2
    ascending = [low + int((high - low) * i / mid) for i in range(mid)]
    descending = list(reversed(ascending))
    return (ascending + descending)[:count]


def stepped_heights(count, low=1, high=4):
    """
    Create stepped pattern: gradually increase then reset.
    
    Args:
        count: Number of heights to generate
        low: Minimum height
        high: Maximum height
        
    Returns:
        List of heights in stepped pattern
    """
    step_size = 6
    heights = []
    for i in range(count):
        if i % step_size == 0 and i > 0:
            heights.append(low)  # Reset to low
        else:
            h = low + min(i % step_size, high - low)
            heights.append(h)
    return heights


def constant_height(count, height=3):
    """
    All platforms at same height - rhythm without height changes.
    
    Args:
        count: Number of heights to generate
        height: Constant height value
        
    Returns:
        List of identical heights
    """
    return [height] * count


# ============================================================================
# WIDTH PATTERNS
# ============================================================================

def varied_widths(count):
    """
    Mix of thin bars (2-3) and wide platforms (4-8).
    
    Args:
        count: Number of widths to generate
        
    Returns:
        List of varied widths
    """
    widths = []
    for _ in range(count):
        # 60% thin bars, 40% wide platforms
        if random.random() < 0.6:
            widths.append(random.randint(2, 3))  # Quick hops
        else:
            widths.append(random.randint(4, 8))  # Rest areas
    return widths


def rhythm_widths(count):
    """
    Rhythmic pattern of thin-wide-thin-wide.
    
    Args:
        count: Number of widths to generate
        
    Returns:
        List of widths in rhythmic pattern
    """
    pattern = [2, 2, 5, 2, 2, 6, 2, 2, 5]
    widths = []
    for i in range(count):
        widths.append(pattern[i % len(pattern)])
    return widths


# ============================================================================
# OBSTACLE BUILDERS
# ============================================================================

def create_pattern(name, description, obstacles, pattern_type, rhythm_hint):
    """
    Create pattern dictionary with metadata.
    
    Args:
        name: Pattern name
        description: Pattern description
        obstacles: List of obstacle dictionaries
        pattern_type: Type ("bar", "platform", "mixed")
        rhythm_hint: Rhythm description
        
    Returns:
        Pattern dictionary
    """
    return {
        "name": name,
        "description": description,
        "obstacles": obstacles,
        "metadata": {
            "type": pattern_type,
            "length": len(obstacles),
            "rhythm": rhythm_hint,
        },
    }


def create_platform(width, height, gap, gap_hazard=None):
    """
    Create a floating platform (bar type).
    
    Args:
        width: Platform width in blocks
        height: Platform height in blocks (0 = ground level)
        gap: Gap multiplier or full gap_type (e.g., "gap-2.0" or just "2.0")
        gap_hazard: Optional hazard type for the gap ("lava", "acid", None)
        
    Returns:
        Obstacle dictionary
    """
    # If gap is just a number or gap-{number}, add hazard suffix if specified
    if gap_hazard:
        # Ensure gap starts with "gap-"
        if not gap.startswith("gap-"):
            gap_str = f"gap-{gap}"
        else:
            gap_str = gap
        # Add hazard suffix
        gap_type = f"{gap_str}-{gap_hazard}"
    else:
        # No hazard, use gap as-is (ensure it starts with "gap-")
        if not gap.startswith("gap-"):
            gap_type = f"gap-{gap}"
        else:
            gap_type = gap
    
    return {"bar_type": f"bar-{width}-{height}", "gap_type": gap_type}


def create_floating_platform(width, floor_height, ceiling_height, gap, gap_hazard=None):
    """
    Create a floating platform suspended between floor and ceiling.
    
    Args:
        width: Platform width in blocks
        floor_height: Distance from ground to bottom of platform in blocks
        ceiling_height: Distance from ground to top of platform in blocks
        gap: Gap multiplier or full gap_type
        gap_hazard: Optional hazard type for the gap ("lava", "acid", None)
        
    Returns:
        Obstacle dictionary
    """
    # If gap is just a number or gap-{number}, add hazard suffix if specified
    if gap_hazard:
        # Ensure gap starts with "gap-"
        if not gap.startswith("gap-"):
            gap_str = f"gap-{gap}"
        else:
            gap_str = gap
        # Add hazard suffix
        gap_type = f"{gap_str}-{gap_hazard}"
    else:
        # No hazard, use gap as-is (ensure it starts with "gap-")
        if not gap.startswith("gap-"):
            gap_type = f"gap-{gap}"
        else:
            gap_type = gap
    
    return {"bar_type": f"bar-{width}-{floor_height}-{ceiling_height}", "gap_type": gap_type}
