"""
Physics Engine & Trajectory Validation

Provides physics calculations and pattern validation for the Geometry Dash clone.
Uses exact game physics constants to validate that obstacle patterns are playable.
"""

# Core physics constants (must match config.py exactly)
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


def calculate_jump_trajectory(start_x, start_y, num_steps=50):
    """
    Calculate the parabolic jump arc from a starting position.
    Returns list of (x, y) points along the jump path.
    
    Player jumps with JUMP_POWER, moves forward with PLAYER_SPEED, pulled down by GRAVITY.
    
    Args:
        start_x: Starting X position
        start_y: Starting Y position (top of platform)
        num_steps: Number of simulation steps
        
    Returns:
        List of (x, y) tuples representing the jump trajectory
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
        debug: Print debug info if True
    
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
    
    Args:
        prev_platform: Dictionary with platform properties (x, y_top, width, height)
        next_platform: Dictionary with platform properties (x, y_top, width, height)
        debug: Print debug info if True
        
    Returns:
        Tuple (can_reach: bool, reason: str)
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
    
    Args:
        pattern_data: Dictionary containing pattern obstacles and metadata
        
    Returns:
        Tuple (is_valid: bool, error_msg: str, touches_ground: bool)
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
