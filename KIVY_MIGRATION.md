# Kivy iOS Migration Plan

## Overview
Migrating Geo Dash from Pygame to Kivy for iOS deployment via TestFlight and App Store.

## Branch Structure
- `main` - Pygame version (desktop)
- `kivy-ios` - Kivy version (mobile/iOS)

## Migration Strategy

### Phase 1: Core Kivy Setup ✓
- [x] Create kivy-ios branch
- [ ] Add Kivy dependencies
- [ ] Create buildozer.spec for iOS
- [ ] Set up basic Kivy app structure

### Phase 2: Game Logic Port
Since the game logic is modular, most can be reused:
- [ ] Port config.py to work with Kivy coordinates
- [ ] Port physics.py (no changes needed)
- [ ] Port player.py to use Kivy widgets/canvas
- [ ] Port obstacles.py to use Kivy graphics
- [ ] Port managers/ (minimal changes)

### Phase 3: Rendering Engine
- [ ] Replace renderer.py with Kivy canvas drawing
- [ ] Port visual effects to Kivy animations
- [ ] Convert font rendering to Kivy labels
- [ ] Adapt asset loading for Kivy

### Phase 4: Input Handling
- [ ] Replace keyboard input with touch controls
- [ ] Add virtual buttons for mobile
- [ ] Implement swipe/tap gestures
- [ ] Add pause/menu touch areas

### Phase 5: iOS-Specific Features
- [ ] Configure buildozer.spec for iOS
- [ ] Set up app icons and splash screens
- [ ] Configure permissions (if needed)
- [ ] Test on iOS simulator
- [ ] Build .ipa for TestFlight

## Key Differences: Pygame vs Kivy

### Coordinate System
- **Pygame**: Origin (0,0) at top-left, Y increases downward
- **Kivy**: Origin (0,0) at bottom-left, Y increases upward
- **Solution**: Invert Y calculations or use Kivy's coordinate system

### Rendering
- **Pygame**: Direct screen.blit() calls
- **Kivy**: Canvas instructions (Rectangle, Ellipse, etc.)
- **Solution**: Create Kivy widgets for player/obstacles

### Game Loop
- **Pygame**: Manual `while running` loop with clock.tick()
- **Kivy**: Built-in Clock.schedule_interval() for updates
- **Solution**: Use Clock.schedule_interval(self.update, 1/60)

### Input
- **Pygame**: pygame.event.get() for keyboard
- **Kivy**: on_touch_down/on_touch_up for touch
- **Solution**: Virtual jump button + swipe detection

### Assets
- **Pygame**: pygame.image.load()
- **Kivy**: Image, AsyncImage, or Atlas
- **Solution**: Use Kivy's Image widget or CoreImage

## File Structure (Kivy Version)

```
geo-dash/
├── main.py                 # Kivy app entry point
├── buildozer.spec          # iOS build configuration
├── kivy_game/
│   ├── __init__.py
│   ├── game.py            # Main game widget
│   ├── player.py          # Player widget
│   ├── obstacle.py        # Obstacle widget
│   ├── renderer.py        # Kivy canvas renderer
│   └── controls.py        # Touch input handler
├── core/                   # Reuse from Pygame version
│   └── physics.py         # No changes needed
├── managers/               # Reuse from Pygame version
│   ├── pattern_manager.py # No changes needed
│   ├── bar_type_manager.py
│   └── score_manager.py   # No changes needed
├── data/
│   ├── bar_types.json
│   └── save_data.json
├── obstacle_patterns/      # Reuse from Pygame version
└── assets/
    ├── backgrounds/
    ├── fonts/
    ├── hazards/
    └── icon.png           # App icon for iOS
```

## Buildozer Configuration Highlights

```ini
[app]
title = Geo Dash
package.name = geodash
package.domain = com.yourname

# iOS specific
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0

# Permissions
# ios.plist.NSPhotoLibraryUsageDescription = Save screenshots

# Orientation
orientation = landscape

# Requirements
requirements = python3,kivy,pillow
```

## Development Workflow

1. **Local Development**: Test on desktop with `python main.py`
2. **iOS Simulator**: Build with `buildozer ios debug`
3. **TestFlight**: Build release with `buildozer ios release`
4. **App Store**: Submit via Xcode with .ipa

## Testing Checklist

- [ ] Game starts and shows player selection
- [ ] Player can jump with touch
- [ ] Obstacles generate and scroll
- [ ] Collision detection works
- [ ] Score tracking works
- [ ] Visual effects display
- [ ] Pattern loading works
- [ ] Save/load high scores
- [ ] Performance is smooth (60 FPS)
- [ ] Touch controls are responsive
- [ ] Menus work on touch
- [ ] Game over/pause menus functional

## Resources

- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Buildozer iOS](https://buildozer.readthedocs.io/en/latest/ios.html)
- [Kivy-iOS Toolchain](https://github.com/kivy/kivy-ios)
- [TestFlight Beta Testing](https://developer.apple.com/testflight/)

## Notes

- Keep Pygame version on `main` branch for desktop releases
- Kivy version on `kivy-ios` branch for mobile releases
- Core game logic (physics, patterns, managers) is shared via git merge
- Only UI/rendering/input layers differ between branches
