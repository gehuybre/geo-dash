# Geo Dash - Kivy iOS Branch

This branch contains the Kivy/KivyMD port of Geo Dash for iOS deployment.

## 🎮 About

Geo Dash is a Geometry Dash clone with physics-validated obstacle generation, custom assets, and modular architecture. This branch is specifically configured for iOS release via TestFlight and the App Store.

## 📱 iOS Development

### Prerequisites

1. **macOS** with Xcode installed
2. **Python 3.9+**
3. **Buildozer** for iOS packaging
4. **Apple Developer Account** for TestFlight/App Store

### Setup

```bash
# Install buildozer
pip install buildozer

# Install Cython (required for iOS)
pip install cython

# Clone and checkout kivy-ios branch
git clone https://github.com/gehuybre/geo-dash.git
cd geo-dash
git checkout kivy-ios

# Install dependencies
pip install -r requirements-kivy.txt
```

### Building for iOS

```bash
# Debug build (for testing on simulator/device)
buildozer ios debug

# Release build (for TestFlight/App Store)
buildozer ios release

# Deploy to connected device
buildozer ios debug deploy run
```

### Testing

```bash
# Test on desktop (Kivy runs on desktop too)
python main.py
```

## 🎯 Key Differences from Pygame Version

- **Touch Controls**: Tap to jump instead of spacebar
- **Kivy Graphics**: Canvas-based rendering instead of Pygame blitting
- **Mobile-Optimized**: Larger touch targets, simplified UI
- **iOS Integration**: TestFlight/App Store ready with buildozer

## 📂 Branch Strategy

- `main` - Pygame version (desktop/PC)
- `kivy-ios` - Kivy version (mobile/iOS)

Core game logic is shared via selective merges.

## 🚀 Deployment Workflow

1. **Development**: Test on macOS with `python main.py`
2. **Testing**: Build debug .ipa and test on iOS device
3. **TestFlight**: Build release .ipa and upload via Xcode
4. **App Store**: Submit for review through App Store Connect

## 📖 Documentation

See [KIVY_MIGRATION.md](./KIVY_MIGRATION.md) for detailed migration plan and architecture notes.

## 🎨 Assets

All assets from the Pygame version are compatible:
- Custom backgrounds
- Player sprites  
- Obstacle graphics
- Mochibop fonts
- Hazard SVGs (converted to PNG for mobile)

## ⚙️ Configuration

Edit `buildozer.spec` to customize:
- App name and version
- Package identifiers
- iOS deployment targets
- Permissions and capabilities
- App icons and splash screens

## 📝 License

Same as main branch - see original repository.

## 🐛 Issues

For iOS-specific issues, open an issue tagged with `kivy-ios` label.
