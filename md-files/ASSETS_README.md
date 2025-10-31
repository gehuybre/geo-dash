# Assets Folder

This folder is where you can place custom images to customize the game's appearance.

## Supported Asset Types

### backgrounds/ folder
- **Multiple backgrounds** that cycle during gameplay!
- Place any number of PNG/JPG images (800x600px recommended)
- Backgrounds change every 5 points
- Each background repeats randomly 1-4 times
- See `backgrounds/README.md` for details

### player.png
- Size: 40x40 pixels (or will be scaled to fit)
- Format: PNG with transparency recommended
- This will replace the cute pink cube character

### obstacle.png
- Format: PNG with transparency recommended
- Will be scaled to fit different obstacle sizes
- This will replace the purple gradient blocks

### background.png
- Size: 800x600 pixels
- Format: PNG or JPG
- This will replace the gradient sky with clouds

### ground.png
- Format: PNG with transparency recommended
- Will be tiled horizontally across the ground
- This will replace the green grass ground

## How to Use

1. Create or download your custom sprites
2. Name them exactly as shown above (case-sensitive)
3. Place them in this `assets` folder
4. Run the game - it will automatically load your custom assets!

## Fallback

If any asset file is not found, the game will automatically use the built-in procedural graphics (the cute default style). This means you can mix and match - use a custom background but keep the default player, for example!

## Tips

- Keep file sizes reasonable (under 1MB each)
- PNG format is recommended for sprites with transparency
- Test your assets in the game to ensure they look good
- The obstacle sprite will be stretched to different sizes, so simple designs work best
