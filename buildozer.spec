[app]
title = Graviton
package.name = graviton
package.domain = org.graviton.game
source.dir = .
source.include_exts = py,png,jpg,mp3,wav,json,atlas,ttf
version = 1.0
requirements = python3,kivy==2.3.0,sdl2,sdl2_image,sdl2_mixer,sdl2_ttf
orientation = portrait
fullscreen = 1
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk = 23b
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = True
android.skip_update = False
android.theme = @android:style/Theme.NoTitleBar
android.entrypoint = org.kivy.android.PythonActivity
android.logcat_filters = *:S python:D
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
