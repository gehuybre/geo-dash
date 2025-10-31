# Pattern Generator

Modular pattern generation system for Geo Dash obstacle patterns.

## Structure

```
generators/
├── __init__.py           # Package exports
├── physics_engine.py     # Physics calculations and validation
├── obstacle_builders.py  # Pattern building blocks
├── pattern_library.py    # Pre-designed pattern generators
└── main.py               # Main entry point
```

## Usage

Generate all patterns with difficulty variants:

```bash
python -m generators.main
```

Or from the root directory:

```bash
python generators/main.py
```

## Architecture

### Physics Engine (`physics_engine.py`)

- **Physics Constants**: Matches game engine exactly (GRAVITY, JUMP_POWER, etc.)
- **Trajectory Calculation**: Simulates player jump arcs
- **Validation**: Ensures all obstacles are reachable via physics

### Obstacle Builders (`obstacle_builders.py`)

- **Gap Patterns**: Pre-defined gap rhythms (SHORT, MEDIUM, LONG, VARIED)
- **Height Patterns**: Functions for generating height sequences (wave, stepped, alternating, etc.)
- **Width Patterns**: Varied and rhythmic width generators
- **Obstacle Creators**: `create_platform()`, `create_floating_platform()`

### Pattern Library (`pattern_library.py`)

Contains 10 pattern generator functions:

1. **steady_rhythm_v4**: Consistent platform hops
2. **wave_rider_v4**: Undulating heights
3. **quick_hops_v4**: Fast thin platforms
4. **rest_and_run_v4**: Bursts with rest areas
5. **stepped_ascent_v4**: Gradual climbs
6. **zigzag_chaos_v4**: Unpredictable heights
7. **long_jumper_v4**: Maximum distance jumps
8. **mixed_madness_v4**: Ultimate variety
9. **kitchen_sink_v4**: 30% platforms, 30% bars, hazards
10. **obstacle_course_v4**: Strategic sequences

Each pattern generates 3 difficulty variants (easy, medium, hard) via `generate_difficulty_variants()`.

## Difficulty Scaling

- **Hard**: Original pattern (1.0x width)
- **Medium**: +15% platform width (1.15x)
- **Easy**: +25% platform width (1.25x)

## Output

Patterns are saved to `obstacle_patterns/` as JSON files with physics validation.
