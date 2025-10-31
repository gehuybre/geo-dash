# Multiple Backgrounds

Place multiple background images in this folder to have them cycle during gameplay!

## How It Works

- The game will automatically load all images from this folder
- Backgrounds cycle **every 5 points** you score
- Each background is **randomly repeated 1-4 times** before switching to the next
- Files are loaded in alphabetical order

## Supported Formats

- PNG (recommended)
- JPG/JPEG
- BMP

## Image Specifications

- **Size:** 800x600 pixels (will be scaled if different)
- **Name:** Any filename (e.g., `bg1.png`, `sky_blue.png`, `sunset.jpg`)

## Example Setup

```
assets/backgrounds/
├── 01_morning.png
├── 02_noon.png
├── 03_sunset.png
└── 04_night.png
```

The game will cycle through them as you play:
- Score 0-4: Morning (shown 1-4 times)
- Score 5-9: Noon (shown 1-4 times)
- Score 10-14: Sunset (shown 1-4 times)
- Score 15-19: Night (shown 1-4 times)
- Score 20+: Back to Morning, and repeat!

## Tips

- **Number your files** (01_, 02_, etc.) to control the order
- **Different themes** create variety (day/night cycle, seasons, weather)
- **Keep file sizes reasonable** (under 500KB each)
- **Test in-game** to see how they look!

## Fallback

If this folder is empty or doesn't exist, the game will:
1. Try to use `assets/background.png`
2. If that doesn't exist, use the default procedural gradient sky

Enjoy creating your custom background sequences! 🎨
