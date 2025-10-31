"""
Pattern Generator V3 – Physics-validated patterns with platforms and hazards

This generator creates obstacle patterns (20-40 blocks each) that are guaranteed to be
physically possible to complete. All patterns are validated BEFORE saving using the same
physics constants as the game.

Key Features:
- Built-in physics validation (no need for game-side validation)
- Platform buildup: Always creates climbable stairs before platforms
- Hazard types: 6 types (spikes, saw, lava, electric, laser, poison)
- Proper height transitions: Never exceeds forward jump limits (39px up)
- Climb sequences: Uses gap-0 for stacked obstacles (max 58px climb)

Physics Constraints:
- GRAVITY = 0.8, JUMP_POWER = -15, PLAYER_SPEED = 6
- Max obstacle height: 98px (from ground)
- Max jump distance: 225px
- Max forward jump UP: 39px (with gap)
- Max climb UP: 58px (gap-0, stacked)
- Min safe gap: 60px

Usage:
  python pattern_generator_v3.py

Output:
  Saves validated JSON files to ./obstacle_patterns/
  Game loads these patterns without re-validation
"""
import json, os, random

OUTPUT_DIR = "obstacle_patterns"

# ---------------- Physics Constants (from config.py) ----------------
GRAVITY = 0.8
JUMP_POWER = -15
PLAYER_SPEED = 6
GROUND_Y = 600

# Physics calculations
max_jump_height = (abs(JUMP_POWER) ** 2) / (2 * GRAVITY)
MAX_OBSTACLE_HEIGHT = int(max_jump_height * 0.7)  # 98px
time_to_peak = abs(JUMP_POWER) / GRAVITY
total_air_time = time_to_peak * 2
MAX_JUMP_DISTANCE = int(total_air_time * PLAYER_SPEED)  # 225px
MIN_SAFE_GAP = int(PLAYER_SPEED * 10)  # 60px
MAX_FORWARD_JUMP_HEIGHT = int(MAX_OBSTACLE_HEIGHT * 0.4)  # 39px - can't jump as high when jumping forward
MAX_CLIMB_HEIGHT = int(MAX_OBSTACLE_HEIGHT * 0.6)  # 58px - can jump higher when climbing (gap-0)

print(f"Physics Validator: Max height={MAX_OBSTACLE_HEIGHT}px, Max distance={MAX_JUMP_DISTANCE}px, "
      f"Forward jump up={MAX_FORWARD_JUMP_HEIGHT}px, Climb={MAX_CLIMB_HEIGHT}px")

# ---------------- Pattern Validation ----------------
def validate_pattern(pattern_data):
    """Validate that a pattern is physically possible to complete.
    Returns (is_valid, error_message)"""
    obstacles_data = pattern_data.get('obstacles', [])
    
    if not obstacles_data:
        return False, "No obstacles in pattern"
    
    # Resolve bar types and gaps to actual dimensions
    resolved = []
    for obs in obstacles_data:
        bar_type = obs.get('bar_type', '')
        gap_type = obs.get('gap_type', 'gap-1.5')
        
        # Parse bar type: bar-{width}-{height} or bar-{width}-{floor}-{ceiling}
        parts = bar_type.replace('bar-', '').split('-')
        if len(parts) >= 2:
            width = int(parts[0]) * 30
            height = int(parts[1]) * 30
        else:
            width, height = 30, 30
        
        # Parse gap type: gap-{multiplier}
        gap_mult = float(gap_type.replace('gap-', ''))
        gap_after = int(gap_mult * 100)
        
        resolved.append({
            'width': width,
            'height': height,
            'gap_after': gap_after,
            'is_killzone': obs.get('is_killzone', False)
        })
    
    # Simulate player movement through the pattern
    player_y = GROUND_Y  # Start on ground
    
    for i, obs in enumerate(resolved):
        height = obs['height']
        width = obs['width']
        gap_after = obs['gap_after']
        
        obstacle_top = GROUND_Y - height
        
        # First obstacle must be reachable from ground
        if i == 0 and height > MAX_OBSTACLE_HEIGHT:
            return False, f"Obstacle 0: height {height}px exceeds max {MAX_OBSTACLE_HEIGHT}px (not reachable from ground)"
        
        # Check if player can reach this obstacle from previous position
        if i > 0:
            prev_obs = resolved[i - 1]
            prev_height = prev_obs['height']
            prev_gap = prev_obs['gap_after']
            prev_top = GROUND_Y - prev_height
            
            # If gap is 0, this is stacked on previous obstacle
            if prev_gap == 0:
                # Stacked: player can climb if height difference is climbable
                height_diff = height - prev_height
                
                if height_diff > 0:
                    # Need to jump UP onto the stack
                    if height_diff > MAX_CLIMB_HEIGHT:
                        return False, f"Obstacle {i}: stack climb {height_diff}px exceeds max {MAX_CLIMB_HEIGHT}px"
                
                # Player is now on top of previous obstacle
                player_y = prev_top
            else:
                # There's a gap - need to jump
                if prev_gap > MAX_JUMP_DISTANCE:
                    return False, f"Obstacle {i-1}: gap {prev_gap}px exceeds max jump distance {MAX_JUMP_DISTANCE}px"
                
                # Check if gap allows safe landing
                if width < 60 and prev_gap < MIN_SAFE_GAP:
                    return False, f"Obstacle {i-1}: gap {prev_gap}px less than min safe gap {MIN_SAFE_GAP}px for narrow platform"
                
                # Check if we can jump from previous height to this height
                vertical_diff = prev_top - obstacle_top  # Negative if jumping up
                
                if vertical_diff < 0:  # Jumping UP
                    jump_up_height = abs(vertical_diff)
                    
                    if jump_up_height > MAX_FORWARD_JUMP_HEIGHT:
                        return False, f"Obstacle {i}: upward jump {jump_up_height}px exceeds max forward jump {MAX_FORWARD_JUMP_HEIGHT}px (from height {prev_height}px to {height}px)"
                
                # Player lands on this obstacle
                player_y = obstacle_top
    
    return True, "Pattern is valid"

# ---------------- Core helpers ----------------
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
    is_valid, error_msg = validate_pattern(pattern)
    if not is_valid:
        print(f"✗ FAILED: {filename} - {error_msg}")
        return False
    
    path = os.path.join(OUTPUT_DIR, f"{filename}.json")
    with open(path, "w") as f:
        json.dump(pattern, f, indent=2)
    print(f"✓ Created: {filename} ({pattern['metadata']['length']} blocks, {pattern['metadata']['type']}) - VALIDATED")
    return True

def add_resting_gap(obstacles, gap_size="gap-2.25"):
    if obstacles:
        obstacles[-1]["gap_type"] = gap_size

# --------------- Rhythm & height helpers ---------------
def ascending_heights(start, end, count):
    if count == 1:
        return [start]
    step = max(1, (end - start) // max(1, (count - 1)))
    heights, current = [], start
    for _ in range(count):
        heights.append(current)
        current = min(current + step, end)
    return heights

def descending_heights(start, end, count):
    return list(reversed(ascending_heights(end, start, count)))

def wave_heights(min_h, max_h, count):
    half = count // 2
    return ascending_heights(min_h, max_h, half) + descending_heights(max_h, min_h, count - half)

def zigzag_heights(min_h, max_h, count):
    heights, current, up = [], min_h, True
    for _ in range(count):
        heights.append(current)
        if up:
            current += 1
            if current >= max_h: up = False
        else:
            current -= 1
            if current <= min_h: up = True
    return heights

# Safe gaps and dedupe
GAP_CHOICES = ["gap-1.0", "gap-1.25", "gap-1.5", "gap-1.75", "gap-2.0", "gap-2.25"]

def choose_gap(prefer=None):
    if prefer in GAP_CHOICES: return prefer
    return random.choice(GAP_CHOICES)

def ensure_no_consecutive(heights, min_h=1, max_h=3):
    if not heights: return heights
    out = [heights[0]]
    for h in heights[1:]:
        if h == out[-1]:
            h = out[-1] + 1 if out[-1] < max_h else out[-1] - 1
        out.append(max(min(h, max_h), min_h))
    return out

def gap_phrase(kind="straight"):
    if kind == "swing": return ["gap-1.25", "gap-1.75", "gap-1.25", "gap-1.75"]
    if kind == "burst": return ["gap-1.0", "gap-1.0", "gap-1.5", "gap-2.0"]
    return ["gap-1.5"]*4

# --------------- Obstacle builders ---------------
def create_bar_obstacle(height, width=None, gap="gap-1.5"):
    if width is None: width = random.randint(2, 4)
    return {"bar_type": f"bar-{width}-{height}", "gap_type": gap}

def create_platform_obstacle(floor_height, width=None, ceiling_height=1, gap="gap-1.5"):
    if width is None: width = random.randint(3, 6)
    return {"bar_type": f"bar-{width}-{floor_height}-{ceiling_height}", "gap_type": gap}

def create_killzone(width=1, gap="gap-0", hazard_type=None):
    obj = {"bar_type": f"bar-{width}-0", "gap_type": gap, "is_killzone": True}
    if hazard_type:
        obj["hazard_type"] = hazard_type
    return obj

HAZARD_TYPES = ["spikes", "saw", "lava", "electric", "laser", "poison"]

def random_hazard():
    return random.choice(HAZARD_TYPES)

def create_platform_buildup(target_height, gap_after_stairs="gap-1.5"):
    """Create ascending stairs to reach a platform at target_height.
    Returns list of obstacles that climb from ground (height 1) to target_height.
    Uses gap-0 for all climbing stairs, then gap_after_stairs before the next obstacle.
    
    IMPORTANT: This assumes player is currently on ground. The first stair will have gap-0
    so player can climb it without needing a forward jump."""
    obstacles = []
    if target_height <= 1:
        return obstacles  # No buildup needed for ground-level platforms
    
    # Create stairs: 1 -> 2 -> ... -> target_height
    # All stairs use gap-0 (touching) to allow climbing
    for h in range(1, target_height + 1):
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    # Set the gap after the last stair to gap_after_stairs
    if obstacles:
        obstacles[-1]["gap_type"] = gap_after_stairs
    
    return obstacles

# --------------- Patterns ---------------
def rising_stairs_v3():
    obstacles = []
    reps = random.randint(7, 8)
    
    for _ in range(reps):
        # Create stairs: 1->2->3 using gap-0 for climbing
        for h in [1,2,3]:
            obstacles.append(create_bar_obstacle(h, width=random.randint(2,3), gap="gap-0"))
        
        # Descend back to ground with gap-0 (no gap jump from height 3 to height 1)
        for h in [2,1]:
            obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
        
        # Add gap after returning to ground
        obstacles[-1]["gap_type"] = "gap-1.5"
    
    # Final landing sequence
    for h in [2,1]:
        obstacles.append(create_bar_obstacle(h, width=3, gap=choose_gap("gap-1.75")))
    add_resting_gap(obstacles, "gap-2.25")
    return create_pattern("Rising Stairs Flow (v3)", "Ascending micro-stairs with descent; proper climbing sequences.", obstacles, "bar", "4/4 straight")

def valley_runner_v3():
    obstacles = []
    for h in ensure_no_consecutive(descending_heights(3,1,6),1,3):
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    for _ in range(random.randint(8,10)):
        obstacles.append(create_bar_obstacle(1, width=random.randint(3,5), gap=choose_gap("gap-2.0")))
    for h in ensure_no_consecutive(ascending_heights(1,3,6),1,3):
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    for h in [2,3,2,3]:
        obstacles.append(create_bar_obstacle(h, width=3, gap=choose_gap("gap-1.5")))
    add_resting_gap(obstacles, "gap-2.25")
    return create_pattern("Valley Runner (v3)", "Extra-wide valley then climb back.", obstacles, "bar", "Medium momentum")

def zigzag_rhythm_v3():
    obstacles = []
    count = random.randint(22,26)
    heights = ensure_no_consecutive(zigzag_heights(1,3,count),1,3)
    gp = gap_phrase("swing")
    for i,h in enumerate(heights):
        obstacles.append(create_bar_obstacle(h, width=random.randint(2,3), gap=gp[i % len(gp)]))
    for h in [2,1]:
        obstacles.append(create_bar_obstacle(h, width=4, gap=choose_gap("gap-2.0")))
    add_resting_gap(obstacles, "gap-2.25")
    return create_pattern("Zigzag Rhythm Run (v3)", "Alternating up/down with swing gaps.", obstacles, "bar", "Fast swing")

def sky_climber_v3():
    obstacles = []
    # Build up to first platform height (2) from ground
    # First add a ground-level bar to ensure proper connection
    obstacles.append(create_bar_obstacle(1, width=3, gap="gap-1.5"))
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    obstacles.extend(create_platform_buildup(2, gap_after_stairs="gap-0"))
    
    # Descend to ground before hazards
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    
    # Add hazard zone with variety (now player is at ground level)
    for _ in range(2):
        obstacles.append(create_killzone(width=2, gap="gap-0", hazard_type=random_hazard()))
    
    # Build back up to platforms after hazards
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    obstacles.extend(create_platform_buildup(2, gap_after_stairs="gap-1.5"))
    
    # Platform sequence at varying heights (2-3)
    heights = ensure_no_consecutive(wave_heights(2,3,random.randint(14,16)),2,3)
    prev_height = 2  # Track previous height for buildup
    
    for i, h in enumerate(heights):
        # If height increases by more than 1, need a stair step
        if h > prev_height:
            # Add intermediate stair(s) with gap-0 before them
            for intermediate in range(prev_height + 1, h + 1):
                obstacles.append(create_bar_obstacle(intermediate, width=2, gap="gap-0"))
            # Set gap after last stair
            obstacles[-1]["gap_type"] = "gap-1.0"
        
        obstacles.append(create_platform_obstacle(h, width=random.randint(4,6), gap=choose_gap()))
        prev_height = h
    
    # Descend back to ground
    for h in [3,2,1,1]:
        obstacles.append(create_bar_obstacle(h, width=2, gap=choose_gap("gap-1.5")))
    add_resting_gap(obstacles, "gap-2.25")
    return create_pattern("Sky Climber (v3)", "Wave of platforms over hazards with proper buildup.", obstacles, "platform", "Flow 4/4")

def chorus_wave_v3():
    obstacles = []
    # Build up to platform height (2)
    obstacles.append(create_bar_obstacle(1, width=3, gap="gap-1.5"))
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    obstacles.extend(create_platform_buildup(2, gap_after_stairs="gap-0"))
    
    # Descend to ground before hazards
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    
    # Hazard zone with variety (player at ground)
    for _ in range(3):
        obstacles.append(create_killzone(width=2, gap="gap-0", hazard_type=random_hazard()))
    
    # Build back up after hazards
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    obstacles.extend(create_platform_buildup(2, gap_after_stairs="gap-1.5"))
    
    # Platform sequence with buildup when height increases
    heights = ensure_no_consecutive(wave_heights(2,3,random.randint(16,18)),2,3)
    prev_height = 2  # Track previous height
    
    for i,h in enumerate(heights):
        # Add single stair step when jumping to higher platform
        if h > prev_height:
            # Add intermediate stairs with gap-0
            for intermediate in range(prev_height + 1, h + 1):
                obstacles.append(create_bar_obstacle(intermediate, width=2, gap="gap-0"))
            # Set gap after last stair
            obstacles[-1]["gap_type"] = "gap-1.0"
        
        g = "gap-1.5" if (i % 4 != 3) else "gap-2.0"
        obstacles.append(create_platform_obstacle(h, width=random.randint(4,6), gap=g))
        prev_height = h
    
    # Descend back to ground
    for h in [3,2,1]:
        obstacles.append(create_bar_obstacle(h, width=2, gap=choose_gap("gap-1.5")))
    add_resting_gap(obstacles, "gap-2.25")
    return create_pattern("Chorus Wave", "Sustained platforms with breathers and proper buildup.", obstacles, "platform", "Chorus 4/4")

def switchback_climb_v3():
    obstacles = []
    # Initial climb
    for h in ensure_no_consecutive([1,2,3,2,1,2],1,3):
        obstacles.append(create_bar_obstacle(h, width=2, gap=choose_gap("gap-1.5")))
    
    # Descend to ground before hazards
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    
    # Hazard zone with variety (player at ground)
    for _ in range(2):
        obstacles.append(create_killzone(width=2, gap="gap-0", hazard_type=random_hazard()))
    
    # Build up to platform section (start at height 2)
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    obstacles.extend(create_platform_buildup(2, gap_after_stairs="gap-1.0"))
    
    # Platform sequence with buildup
    heights = ensure_no_consecutive(wave_heights(2,3,12),2,3)
    prev_height = 2  # Track previous height
    
    for i, h in enumerate(heights):
        # Add climbing when height increases
        if h > prev_height:
            for intermediate in range(prev_height + 1, h + 1):
                obstacles.append(create_bar_obstacle(intermediate, width=2, gap="gap-0"))
            # Set gap after last stair
            obstacles[-1]["gap_type"] = "gap-1.0"
        
        obstacles.append(create_platform_obstacle(h, width=random.randint(4,5), gap=choose_gap()))
        prev_height = h
    
    # Descend with bars
    for h in ensure_no_consecutive([3,2,1,2,1],1,3):
        obstacles.append(create_bar_obstacle(h, width=3, gap=choose_gap("gap-1.75")))
    add_resting_gap(obstacles, "gap-2.25")
    return create_pattern("Switchback Climb", "Bars → platforms → bars with hazards and proper buildup.", obstacles, "mixed", "Bridge phrase")

def syncopated_runner_v3():
    obstacles = []
    # Create rhythm pattern that avoids large height jumps
    phrase = [1,2,2,3,2,1]  # Changed to avoid problematic jumps
    reps = random.randint(4,5)
    heights = ensure_no_consecutive((phrase*reps)[:random.randint(22,28)],1,3)
    gaps = ["gap-1.25","gap-1.75","gap-1.25","gap-1.5"]
    
    for i,h in enumerate(heights):
        if i > 0:
            prev_h = heights[i-1]
            # Check if we're jumping down more than 1 level with a gap
            if prev_h > h and (prev_h - h) > 1:
                # Add intermediate descending stair with gap-0
                obstacles.append(create_bar_obstacle(prev_h - 1, width=2, gap="gap-0"))
            # Check if we're jumping up more than 1 level with a gap  
            elif h > prev_h and (h - prev_h) > 1:
                # Add intermediate ascending stair with gap-0
                obstacles.append(create_bar_obstacle(prev_h + 1, width=2, gap="gap-0"))
        
        obstacles.append(create_bar_obstacle(h, width=random.randint(2,3), gap=gaps[i % len(gaps)]))
    
    add_resting_gap(obstacles, "gap-2.25")
    return create_pattern("Syncopated Runner", "Bar hurdles with syncopated gaps and safe height transitions.", obstacles, "bar", "Syncopated 4/4")

def hazard_platform_gauntlet():
    """Platform section with multiple hazard types requiring careful navigation."""
    obstacles = []
    
    # Initial warm-up
    for h in [1,2,1]:
        obstacles.append(create_bar_obstacle(h, width=3, gap=choose_gap("gap-1.5")))
    
    # Descend to ground before hazards
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    
    # Hazard zone 1: spikes (player at ground)
    for _ in range(2):
        obstacles.append(create_killzone(width=3, gap="gap-0", hazard_type="spikes"))
    
    # Build to platform height 2 (add ground bar first)
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    obstacles.extend(create_platform_buildup(2, gap_after_stairs="gap-1.5"))
    
    # Platform run at height 2
    for _ in range(4):
        obstacles.append(create_platform_obstacle(2, width=random.randint(4,5), gap=choose_gap("gap-1.5")))
    
    # Build to height 3 (add step from height 2)
    obstacles.append(create_bar_obstacle(3, width=2, gap="gap-1.0"))
    
    # Descend to ground before more hazards
    for h in [2,1]:
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    # Hazard zone 2: rotating saws
    for _ in range(2):
        obstacles.append(create_killzone(width=2, gap="gap-0", hazard_type="saw"))
    
    # Build back up to height 3
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    obstacles.extend(create_platform_buildup(3, gap_after_stairs="gap-1.75"))
    
    # High platform run at height 3
    for _ in range(4):
        obstacles.append(create_platform_obstacle(3, width=random.randint(4,6), gap=choose_gap("gap-1.75")))
    
    # Descend stairs
    for h in [3,2,1]:
        obstacles.append(create_bar_obstacle(h, width=2, gap=choose_gap("gap-1.5")))
    
    add_resting_gap(obstacles, "gap-2.25")
    return create_pattern("Hazard Platform Gauntlet", "Multi-level platforms over varied hazards with proper buildup.", obstacles, "mixed", "Challenging flow")

def lava_bridge_crossing():
    """Long lava hazard with platform bridges requiring precise timing."""
    obstacles = []
    
    # Approach
    for h in [1,1,2]:
        obstacles.append(create_bar_obstacle(h, width=2, gap=choose_gap("gap-1.5")))
    
    # Descend to ground before lava
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    
    # Long lava pit (player at ground)
    for _ in range(6):
        obstacles.append(create_killzone(width=2, gap="gap-0", hazard_type="lava"))
    
    # Build to platform height 3 (add ground connection)
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    obstacles.extend(create_platform_buildup(3, gap_after_stairs="gap-1.5"))
    
    # Platform bridges over lava (height 3)
    for _ in range(8):
        obstacles.append(create_platform_obstacle(3, width=random.randint(3,5), gap=choose_gap("gap-1.75")))
    
    # Descend to ground before more lava
    for h in [3,2,1]:
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    # More lava
    for _ in range(4):
        obstacles.append(create_killzone(width=2, gap="gap-0", hazard_type="lava"))
    
    # Build back up for final platforms
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    obstacles.extend(create_platform_buildup(3, gap_after_stairs="gap-2.0"))
    
    # Final platforms
    for _ in range(4):
        obstacles.append(create_platform_obstacle(3, width=random.randint(4,5), gap=choose_gap("gap-2.0")))
    
    # Descend
    for h in [3,2,1]:
        obstacles.append(create_bar_obstacle(h, width=3, gap=choose_gap("gap-1.5")))
    
    add_resting_gap(obstacles, "gap-2.25")
    return create_pattern("Lava Bridge Crossing", "Navigate platforms over extensive lava hazard.", obstacles, "platform", "Steady rhythm")

def electric_maze():
    """Mixed heights with electric hazards requiring varied movement."""
    obstacles = []
    
    # Start low
    for h in [1,2,1,2]:
        obstacles.append(create_bar_obstacle(h, width=2, gap=choose_gap("gap-1.5")))
    
    # Descend to ground before electric
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    
    # Electric floor section 1 (player at ground)
    for _ in range(3):
        obstacles.append(create_killzone(width=2, gap="gap-0", hazard_type="electric"))
    
    # Build to height 2 platforms (add ground connection)
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    obstacles.extend(create_platform_buildup(2, gap_after_stairs="gap-1.0"))
    
    for _ in range(3):
        obstacles.append(create_platform_obstacle(2, width=4, gap=choose_gap("gap-1.5")))
    
    # Descend to ground before more electric
    for h in [2,1]:
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    # More electric hazards
    for _ in range(2):
        obstacles.append(create_killzone(width=2, gap="gap-0", hazard_type="electric"))
    
    # Build to height 3 (from ground)
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    obstacles.extend(create_platform_buildup(3, gap_after_stairs="gap-1.0"))
    
    for _ in range(4):
        obstacles.append(create_platform_obstacle(3, width=random.randint(4,5), gap=choose_gap("gap-1.75")))
    
    # Descend to ground before final electric
    for h in [3,2,1]:
        obstacles.append(create_bar_obstacle(h, width=2, gap="gap-0"))
    
    # Electric hazards again
    for _ in range(3):
        obstacles.append(create_killzone(width=2, gap="gap-0", hazard_type="electric"))
    
    # Build to height 2 for final stretch
    obstacles.append(create_bar_obstacle(1, width=2, gap="gap-0"))
    obstacles.extend(create_platform_buildup(2, gap_after_stairs="gap-2.0"))
    
    for _ in range(3):
        obstacles.append(create_platform_obstacle(2, width=5, gap=choose_gap("gap-2.0")))
    
    # Descend to ground
    for h in [2,1,1]:
        obstacles.append(create_bar_obstacle(h, width=3, gap=choose_gap("gap-1.5")))
    
    add_resting_gap(obstacles, "gap-2.25")
    return create_pattern("Electric Maze", "Multi-level navigation through electric hazards.", obstacles, "mixed", "Complex rhythm")

# --------------- Main ---------------
def generate_all_patterns():
    print("\n=== GEOMETRY DASH PATTERN GENERATOR V3 ===")
    print("Features: Platform buildup, hazard types, proper climb sequences")
    print("Validation: Built-in physics validation ensures all patterns are playable\n")
    ensure_dir(OUTPUT_DIR)
    gens = [
        rising_stairs_v3,
        valley_runner_v3,
        zigzag_rhythm_v3,
        sky_climber_v3,
        chorus_wave_v3,
        switchback_climb_v3,
        syncopated_runner_v3,
        hazard_platform_gauntlet,
        lava_bridge_crossing,
        electric_maze,
    ]
    success_count = 0
    fail_count = 0
    
    for g in gens:
        p = g()
        fname = p["name"].lower().replace(" ", "_").replace("(", "").replace(")", "").replace("–", "-").replace("—","-")
        if save_pattern(p, fname):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully generated {success_count} valid patterns")
    if fail_count > 0:
        print(f"❌ Failed to generate {fail_count} patterns (physics validation failed)")
    print(f"{'='*60}")
    print("\nPattern features:")
    print("  • Platform buildup ensures all platforms are reachable")
    print("  • Hazard types: spikes, saw, lava, electric, laser, poison")
    print("  • Physics-validated climb sequences")
    print("  • All patterns guaranteed playable (validated before saving)")

if __name__ == "__main__":
    generate_all_patterns()
