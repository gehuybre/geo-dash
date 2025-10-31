# Hazard Graphics Reference

## Overview

Six distinct SVG hazard types for visual variety in the game. Each hazard is 60×60px and designed to be visually distinctive.

## Hazard Types

### 1. Spikes (`hazard_spikes.svg`)
**Color Scheme**: Red gradient (#FF3030 → #CC0000)  
**Style**: Sharp upward triangular spikes on a dark base  
**Visual Features**:
- 5 pointed spikes with varying heights
- Gradient fill for depth
- Highlight accents on spike tips
- Dark gray base platform
**Best Use**: Ground hazards, static obstacles

---

### 2. Saw Blade (`hazard_saw.svg`)
**Color Scheme**: Orange/Red gradient (#FF9900 → #CC3300)  
**Style**: Circular rotating saw with teeth  
**Visual Features**:
- 8 triangular teeth around circumference
- Radial gradient for 3D effect
- Central hub with mechanical details
- Warning yellow stripes
**Best Use**: Rotating obstacles, moving hazards

---

### 3. Lava Pool (`hazard_lava.svg`)
**Color Scheme**: Yellow/Orange/Red (#FFCC00 → #CC0000)  
**Style**: Bubbling molten lava  
**Visual Features**:
- Wavy surface animation
- Bubbles with glow effects
- Hot spots (bright yellow areas)
- Steam/smoke particles
- Dark crust at surface
**Best Use**: Floor hazards, pit obstacles

---

### 4. Electric Field (`hazard_electric.svg`)
**Color Scheme**: Cyan/Blue (#00FFFF → #0033FF)  
**Style**: Electrical energy field with lightning bolts  
**Visual Features**:
- 2 main lightning bolt paths
- Electric arcs and sparks
- Bright core highlights
- Energy particles
- Glowing aura effect
**Best Use**: Energy barriers, wall hazards

---

### 5. Laser Beam (`hazard_laser.svg`)
**Color Scheme**: Magenta/Pink (#FF0066)  
**Style**: Vertical laser beam from emitter  
**Visual Features**:
- Top circular emitter
- Vertical beam with glow
- Bright white core line
- Particle effects along beam
- Energy ripples
- Bottom impact glow
**Best Use**: Vertical barriers, timed obstacles

---

### 6. Poison Gas (`hazard_poison.svg`)
**Color Scheme**: Lime/Green (#CCFF00 → #339900)  
**Style**: Toxic cloud with skull warning  
**Visual Features**:
- Billowing cloud shapes
- Skull symbol in center
- Rising toxic bubbles (animated)
- Dripping effect at bottom
- Semi-transparent layers
**Best Use**: Area denial, atmospheric hazards

---

## Technical Specifications

### File Format
- **Type**: SVG (Scalable Vector Graphics)
- **Size**: 60×60 pixels viewBox
- **Location**: `/assets/`

### Features
- **Gradients**: Linear and radial for depth
- **Opacity**: Layered transparency for effects
- **Animations**: Poison gas includes CSS animations (bubbles)
- **Scalable**: Vector format scales to any size

### Color Coding System
- **Red/Orange**: Physical damage (spikes, saw, lava)
- **Blue/Cyan**: Energy damage (electric, laser)
- **Green/Yellow**: Chemical damage (poison)

---

## Integration Guide

### Loading SVGs in Pygame

```python
import pygame
from pygame import gfxdraw
import xml.etree.ElementTree as ET

# Option 1: Convert to PNG first
# Use external tool or library like cairosvg

# Option 2: Use pygame-svg library
import pygame_svg

hazard = pygame_svg.load("assets/hazard_spikes.svg")
screen.blit(hazard, (x, y))
```

### Recommended Usage

| Hazard Type | Use Case | Animation Suggestion |
|-------------|----------|---------------------|
| Spikes | Static floor hazards | None |
| Saw | Moving/rotating obstacles | Rotate 360° continuously |
| Lava | Pit/pool hazards | Vertical bob animation |
| Electric | Energy barriers | Flicker/pulse opacity |
| Laser | Vertical barriers | Beam intensity pulse |
| Poison | Area hazards | Fade in/out, drift left/right |

### Size Scaling

Original: 60×60px
- **Small hazard**: 30×30px (0.5× scale)
- **Medium hazard**: 60×60px (1× scale - default)
- **Large hazard**: 90×90px (1.5× scale)

---

## Customization Tips

### Changing Colors

Edit the gradient definitions in each SVG:

```xml
<linearGradient id="spikeGrad">
  <stop offset="0%" style="stop-color:#FF3030"/>
  <stop offset="100%" style="stop-color:#CC0000"/>
</linearGradient>
```

### Adding Animation (Web/HTML5)

The poison gas SVG includes animation examples:

```xml
<animate attributeName="cy" from="50" to="10" dur="3s" repeatCount="indefinite"/>
```

For Pygame, animate programmatically:
- Rotate saw blade: `pygame.transform.rotate()`
- Pulse effects: Vary alpha/opacity over time
- Movement: Update position each frame

---

## Performance Notes

- **SVGs are small**: 1.4KB - 2.8KB each
- **Memory efficient**: Vector graphics scale without quality loss
- **Consider pre-rendering**: Convert to PNG sprites for better Pygame performance
- **Batch rendering**: Group similar hazards for efficiency

---

## Future Enhancements

Potential additions:
- **Fire hazard**: Animated flames
- **Ice hazard**: Frozen spikes/crystals
- **Shadow hazard**: Dark void effect
- **Gravity well**: Swirling vortex
- **Explosion hazard**: Burst animation
- **Acid hazard**: Dripping corrosive liquid

---

**Created**: October 31, 2025  
**Format**: SVG 1.1  
**License**: Part of Geo Dash project  
**Total Hazards**: 6 types
