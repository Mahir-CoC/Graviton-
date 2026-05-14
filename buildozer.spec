[app]
title = Graviton
package.name = graviton
package.domain = org.graviton.game
source.dir = .
source.include_exts = py,png,jpg,mp3,wav,json,atlas,ttf
version = 1.0
requirements = python3,kivy==2.2.1
orientation = portrait
fullscreen = 1
icon.filename = %(source.dir)s/icône.png
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.theme = @android:style/Theme.NoTitleBar
android.entrypoint = org.kivy.android.PythonActivity
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1
