[app]
title = Graviton
package.name = graviton
package.domain = org.graviton.game
source.dir = .
source.include_exts = py,png,jpg,mp3,wav,json,atlas,ttf
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 1
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = True
android.theme = @android:style/Theme.NoTitleBar
android.entrypoint = org.kivy.android.PythonActivity

[buildozer]
log_level = 2
warn_on_root = 1
