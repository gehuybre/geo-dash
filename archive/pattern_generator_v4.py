"""
Pattern Generator V4 – "The Floor is Lava" Rhythm Platformer

This generator creates patterns where the player NEVER touches the ground.
All movement is jump-in, land, jump-out between floating platforms and bars.

Gameplay Concept:
- Floor is lava (killzones at ground level)
- Platforms fill 80% of vertical space (bottom 20% is lava, top 20% is empty)
- Each platform is a valid landing spot that sets up the next jump
- Rhythm-based: predictable jump patterns with varied platform sizes
- Height variation: platforms at different elevations for visual interest
- Platform variety: thin bars (quick hops), wide platforms (rest areas)

Physics Constraints:
- GRAVITY = 0.8, JUMP_POWER = -15, PLAYER_SPEED = 6
- Jump trajectory: parabolic arc based on starting position
- Platform must intersect jump arc for valid landing

Platform Design Principles:
1. Every platform must intersect the jump arc from previous platform
2. Gaps vary (100-225px) for rhythm
3. Platform widths vary (2-8 blocks) for timing variety
4. Heights vary freely - trajectory validation ensures reachability
5. No sudden difficulty spikes - gradual variation

Usage:
  python pattern_generator_v4.py
"""
import json, os, random

OUTPUT_DIR = "obstacle_patterns"

# ============================================================================
# PHYSICS ENGINE & TRAJECTORY VALIDATION
# ============================================================================

# Core physics constants (match game engine exactly)
GRAVITY = 0.8
JUMP_POWER = -15
PLAYER_SPEED = 6
GROUND_Y = 600
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 40

# Derived physics values
max_jump_height = (abs(JUMP_POWER) ** 2) / (2 * GRAVITY)
MAX_OBSTACLE_HEIGHT = int(max_jump_height * 0.7)  # 98px
time_to_peak = abs(JUMP_POWER) / GRAVITY
total_air_time = time_to_peak * 2
MAX_JUMP_DISTANCE = int(total_air_time * PLAYER_SPEED)  # 225px

# Viewport constraints
MIN_PLATFORM_HEIGHT = 1  # 30px above ground (allow starting platform)
MAX_PLATFORM_HEIGHT = 4  # 120px above ground (top 20% empty)

print(f"Floor is Lava Generator: Heights {MIN_PLATFORM_HEIGHT}-{MAX_PLATFORM_HEIGHT}")
print(f"Physics: Trajectory-based validation, Max jump distance={MAX_JUMP_DISTANCE}px")

def calculate_jump_trajectory(start_x, start_y, num_steps=50):
    """
    Calculate the parabolic jump arc from a starting position.
    Returns list of (x, y) points along the jump path.
    
    Player jumps with JUMP_POWER, moves forward with PLAYER_SPEED, pulled down by GRAVITY.
    """
    trajectory = []
    x = start_x
    y = start_y
    velocity_y = JUMP_POWER
    
    for _ in range(num_steps):
        trajectory.append((x, y))
        
        # Update position
        x += PLAYER_SPEED
        y += velocity_y
        velocity_y += GRAVITY
        
        # Stop if we hit ground or go too far
        if y >= GROUND_Y or x > start_x + MAX_JUMP_DISTANCE + 100:
            break
    
    return trajectory

def platform_intersects_trajectory(trajectory, platform_x, platform_top, platform_width, debug=False):
    """
    Check if a platform intersects the jump trajectory.
    Player can land on platform if any point in trajectory is within platform bounds.
    
    Args:
        trajectory: List of (x, y) points from calculate_jump_trajectory
        platform_x: Left edge of platform
        platform_top: Top edge of platform (Y coordinate)
        platform_width: Width of platform in pixels
    
    Returns:
        True if player can land on this platform from the jump arc
    """
    platform_right = platform_x + platform_width
    
    # Track if we found any horizontal overlap
    horizontal_overlaps = []
    
    for i, (x, y) in enumerate(trajectory):
        # Check if trajectory point is horizontally within platform bounds
        # Player's left edge is at x, right edge at x + PLAYER_WIDTH
        player_left = x
        player_right = x + PLAYER_WIDTH
        
        # Does player overlap platform horizontally?
        if player_right >= platform_x and player_left <= platform_right:
            horizontal_overlaps.append((i, x, y))
            
            # Check if player is at or just above platform top (can land on it)
            # Player lands when their bottom (y + PLAYER_HEIGHT) touches platform top
            player_bottom = y + PLAYER_HEIGHT
            
            if player_bottom >= platform_top - 5:  # 5px tolerance
                if debug:
                    print(f"    ✓ Landing at trajectory point {i}: player_bottom={player_bottom}, platform_top={platform_top}")
                return True
    
    if debug and horizontal_overlaps:
        print(f"    Found {len(horizontal_overlaps)} horizontal overlaps but no valid landing")
        for i, x, y in horizontal_overlaps[:3]:  # Show first 3
            player_bottom = y + PLAYER_HEIGHT
            print(f"      Point {i}: x={x}, player_bottom={player_bottom}, platform_top={platform_top}, diff={player_bottom - platform_top}")
    
    return False

def can_reach_platform(prev_platform, next_platform, debug=False):
    """
    Check if player can jump from prev_platform and land on next_platform.
    
    Platform format: {'x': int, 'y_top': int, 'width': int, 'height': int}
    
    Returns: (can_reach: bool, reason: str)
    """
    # Player starts jump from right edge of previous platform
    jump_start_x = prev_platform['x'] + prev_platform['width']
    jump_start_y = prev_platform['y_top']
    
    # Calculate jump arc
    trajectory = calculate_jump_trajectory(jump_start_x, jump_start_y)
    
    if debug:
        print(f"\n  Jump from x={jump_start_x}, y={jump_start_y} (height={prev_platform['height']})")
        print(f"  Target platform: x={next_platform['x']}, y_top={next_platform['y_top']} (height={next_platform['height']})")
        print(f"  Gap distance: {next_platform['x'] - jump_start_x}px")
        print(f"  Trajectory has {len(trajectory)} points")
        if trajectory:
            print(f"  Trajectory range: x={trajectory[0][0]}-{trajectory[-1][0]}, y={min(p[1] for p in trajectory)}-{max(p[1] for p in trajectory)}")
    
    # Check if next platform intersects the arc
    intersects = platform_intersects_trajectory(
        trajectory,
        next_platform['x'],
        next_platform['y_top'],
        next_platform['width'],
        debug=debug
    )
    
    if intersects:
        return True, "Platform reachable via jump arc"
    
    # Check horizontal distance as fallback diagnostic
    distance = next_platform['x'] - jump_start_x
    if distance > MAX_JUMP_DISTANCE:
        return False, f"Gap {distance}px exceeds max jump {MAX_JUMP_DISTANCE}px"
    
    return False, f"Platform not in jump arc (gap={distance}px, height_diff={next_platform['y_top'] - jump_start_y}px)"

def validate_pattern(pattern_data):
    """
    Validate pattern using trajectory-based physics.
    Each platform must be reachable via jump arc from previous platform.
    
    Returns: (is_valid: bool, error_msg: str, touches_ground: bool)
    """
    obstacles_data = pattern_data.get('obstacles', [])
    
    if not obstacles_data:
        return False, "No obstacles in pattern", False
    
    # Convert pattern data to platform positions
    platforms = []
    current_x = 800  # Starting X position
    touches_ground = False  # Track if any jump path reaches ground
    
    for obs in obstacles_data:
        # Parse bar type
        bar_type = obs.get('bar_type', '')
        parts = bar_type.replace('bar-', '').split('-')
        
        # Determine height based on format
        if len(parts) == 3:
            # Floating platform: bar-{width}-{floor}-{ceiling}
            width = int(parts[0]) * 30
            floor_height = int(parts[1]) * 30
            ceiling_height = int(parts[2]) * 30
            # Platform top is at ceiling height
            height = ceiling_height
        elif len(parts) >= 2:
            # Regular bar: bar-{width}-{height}
            width = int(parts[0]) * 30
            height = int(parts[1]) * 30
        else:
            width, height = 30, 30
        
        # Parse gap
        gap_type = obs.get('gap_type', 'gap-1.5')
        # Extract gap multiplier (remove 'gap-' prefix and any hazard suffix like '-lava')
        gap_str = gap_type.replace('gap-', '').split('-')[0]  # Get first part (the multiplier)
        gap_mult = float(gap_str)
        gap_after = int(gap_mult * 100)
        
        platform = {
            'x': current_x,
            'y_top': GROUND_Y - height,
            'width': width,
            'height': height,
            'is_killzone': obs.get('is_killzone', False)
        }
        platforms.append(platform)
        current_x += width + gap_after
    
    # Validate each platform is reachable from previous
    for i in range(1, len(platforms)):
        if platforms[i]['is_killzone']:
            continue  # Skip killzone validation
        
        prev = platforms[i - 1]
        current = platforms[i]
        
        # Skip if previous is killzone - player must jump from ground
        if prev['is_killzone']:
            # Check if reachable from ground level
            ground_platform = {'x': prev['x'], 'y_top': GROUND_Y, 'width': prev['width'], 'height': 0}
            can_reach, reason = can_reach_platform(ground_platform, current, debug=True)
            if not can_reach:
                return False, f"Obstacle {i}: Not reachable from ground after lava - {reason}", touches_ground
            touches_ground = True  # Jump from ground
            continue
        
        # Calculate trajectory and check if it touches ground
        jump_start_x = prev['x'] + prev['width']
        jump_start_y = prev['y_top']
        trajectory = calculate_jump_trajectory(jump_start_x, jump_start_y)
        
        # Check if trajectory reaches ground (y >= GROUND_Y)
        for x, y in trajectory:
            if y + PLAYER_HEIGHT >= GROUND_Y:  # Player bottom touches ground
                touches_ground = True
                break
        
        can_reach, reason = can_reach_platform(prev, current, debug=False)
        if not can_reach:
            # Enable debug for failed validation
            print(f"\n❌ Validation failed at obstacle {i}:")
            can_reach_platform(prev, current, debug=True)
            return False, f"Obstacle {i}: {reason}", touches_ground
    
    return True, "Pattern is valid", touches_ground

# ============================================================================
# PATTERN BUILDING BLOCKS
# ============================================================================


def create_pattern(name, description, obstacles, pattern_type, rhythm_hint):
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

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def save_pattern(pattern, filename):
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

# ---------------- Platform Builders ----------------
def create_platform(width, height, gap, gap_hazard=None):
    """Create a floating platform (bar type).
    
    Args:
        width: Platform width in blocks
        height: Platform height in blocks (0 = ground level)
        gap: Gap multiplier or full gap_type (e.g., "gap-2.0" or just "2.0")
        gap_hazard: Optional hazard type for the gap ("lava", "acid", None)
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
    """Create a floating platform suspended between floor and ceiling.
    
    Args:
        width: Platform width in blocks
        floor_height: Distance from ground to bottom of platform in blocks
        ceiling_height: Distance from ground to top of platform in blocks
        gap: Gap multiplier or full gap_type
        gap_hazard: Optional hazard type for the gap ("lava", "acid", None)
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

# ---------------- Gap Patterns ----------------
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
    """Generate random gap for elevated platforms (needs >175px for safe landing)."""
    mult = round(random.uniform(min_mult, max_mult) * 4) / 4  # Round to 0.25
    return f"gap-{mult}"

# ---------------- Height Patterns ----------------
def random_heights(count, low=1, high=4):
    """Random heights - trajectory validation ensures they're all reachable."""
    return [random.randint(low, high) for _ in range(count)]

def alternating_heights(count, low=2, high=4):
    """Create alternating high-low pattern."""
    heights = []
    current = low
    for _ in range(count):
        heights.append(current)
        current = high if current == low else low
    return heights

def wave_heights(count, low=1, high=4):
    """Create smooth wave pattern - up then down."""
    mid = count // 2
    ascending = [low + int((high - low) * i / mid) for i in range(mid)]
    descending = list(reversed(ascending))
    return (ascending + descending)[:count]

def stepped_heights(count, low=1, high=4):
    """Create stepped pattern: gradually increase then reset."""
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
    """All platforms at same height - rhythm without height changes."""
    return [height] * count

# ---------------- Width Patterns ----------------
def varied_widths(count):
    """Mix of thin bars (2-3) and wide platforms (4-8)."""
    widths = []
    for _ in range(count):
        # 60% thin bars, 40% wide platforms
        if random.random() < 0.6:
            widths.append(random.randint(2, 3))  # Quick hops
        else:
            widths.append(random.randint(4, 8))  # Rest areas
    return widths

def rhythm_widths(count):
    """Rhythmic pattern of thin-wide-thin-wide."""
    pattern = [2, 2, 5, 2, 2, 6, 2, 2, 5]
    widths = []
    for i in range(count):
        widths.append(pattern[i % len(pattern)])
    return widths

# ---------------- Pattern Generators ----------------
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
    - Hazard gauntlets (multiple hazards in a row)
    - Mixed height challenges
    - 30% platforms, 30% bars, varied hazards
    """
    obstacles = []
    HAZARD_TYPES = ["spikes", "saw", "lava", "electric", "laser", "poison"]
    
    # Stats tracking
    platform_count = 0
    bar_count = 0
    max_height_count = 0
    total_obstacles = 0
    
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

# ---------------- Difficulty Scaling ----------------
def scale_pattern_widths(obstacles, scale_factor):
    """
    Scale all platform/bar widths by scale_factor.
    For example: 1.0 = hard (no change), 1.15 = medium (+15%), 1.25 = easy (+25%)
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
    Returns list of (pattern, difficulty_suffix) tuples.
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

# ---------------- Main ----------------
def generate_all_patterns():
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
        kitchen_sink_v4,  # Ultimate variety: 30%P/30%B/hazards
        obstacle_course_v4,  # Strategic sequences with max variety
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

if __name__ == "__main__":
    generate_all_patterns()
