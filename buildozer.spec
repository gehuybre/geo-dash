[app]

# (str) Title of your application
title = Geo Dash

# (str) Package name
package.name = geodash

# (str) Package domain (needed for android/ios packaging)
package.domain = com.gehuybre

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,ttf,svg

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0,pillow

# (str) Supported orientation (landscape, portrait or all)
orientation = landscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

#
# iOS specific
#

[app:ios]

# (str) Name of the certificate to use for signing the debug version
# ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) Name of the certificate to use for signing the release version
# ios.codesign.release = %(ios.codesign.debug)s

# (str) URL of the git repository for kivy-ios
ios.kivy_ios_url = https://github.com/kivy/kivy-ios

# (str) Branch of kivy-ios to use
ios.kivy_ios_branch = master

# (str) URL of the git repository for ios-deploy
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy

# (str) Branch of ios-deploy to use
ios.ios_deploy_branch = 1.10.0

# (bool) Whether or not to sign the code
# ios.codesign.allowed = false

# (str) App plist customization
# Uncomment and customize as needed:
# ios.plist.UIBackgroundModes = ['audio']
# ios.plist.NSPhotoLibraryUsageDescription = This app needs access to photos
# ios.plist.NSCameraUsageDescription = This app needs access to the camera

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
# bin_dir = ./bin
