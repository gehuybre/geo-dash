"""
Pattern Generator Package - Modular obstacle pattern generation system.

This package provides tools for generating physics-validated obstacle patterns
for the Geometry Dash clone game.
"""

from .physics_engine import (
    GRAVITY,
    JUMP_POWER,
    PLAYER_SPEED,
    GROUND_Y,
    MAX_JUMP_DISTANCE,
    MAX_OBSTACLE_HEIGHT,
    MIN_PLATFORM_HEIGHT,
    MAX_PLATFORM_HEIGHT,
    calculate_jump_trajectory,
    platform_intersects_trajectory,
    can_reach_platform,
    validate_pattern
)

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
    scale_pattern_widths,
    generate_difficulty_variants
)

__all__ = [
    # Physics
    'GRAVITY', 'JUMP_POWER', 'PLAYER_SPEED', 'GROUND_Y',
    'MAX_JUMP_DISTANCE', 'MAX_OBSTACLE_HEIGHT',
    'MIN_PLATFORM_HEIGHT', 'MAX_PLATFORM_HEIGHT',
    'calculate_jump_trajectory', 'platform_intersects_trajectory',
    'can_reach_platform', 'validate_pattern',
    
    # Builders
    'create_pattern', 'create_platform', 'create_floating_platform',
    'random_gap', 'random_heights', 'alternating_heights',
    'wave_heights', 'stepped_heights', 'constant_height',
    'varied_widths', 'rhythm_widths',
    'GAP_RHYTHM_SHORT', 'GAP_RHYTHM_MEDIUM', 'GAP_RHYTHM_LONG', 'GAP_RHYTHM_VARIED',
    
    # Pattern Library
    'steady_rhythm_v4', 'wave_rider_v4', 'quick_hops_v4',
    'rest_and_run_v4', 'stepped_ascent_v4', 'zigzag_chaos_v4',
    'long_jumper_v4', 'mixed_madness_v4', 'kitchen_sink_v4',
    'obstacle_course_v4', 'scale_pattern_widths', 'generate_difficulty_variants'
]
