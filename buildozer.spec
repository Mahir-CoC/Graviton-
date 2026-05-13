[app]

; (str) Title of your application
title = Graviton

; (str) Package name
package.name = graviton

; (str) Package domain - crée un nom unique
package.domain = org.j178.graviton

; (str) Source code where the main.py live
source.dir =.

; (list) Source files to include
source.include_exts = py,png,jpg,mp3,wav,json,atlas,ttf

; (str) Entry point file
main.py = main.py

; (str) Application version
version = 0.1

; (list) Application requirements
requirements = python3,kivy==2.3.0

; (str) Presplash of the application
; presplash.filename = %(source.dir)s/presplash.png

; (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

; (str) Supported orientation
orientation = portrait

; (list) Permissions
android.permissions = INTERNET

; (int) Target Android API
android.api = 31

; (int) Minimum Android API
android.minapi = 21

; (int) Android NDK version
android.ndk = 25b

; (bool) Use --private data storage
android.private_storage = False

; (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

; (str) Android app theme
android.theme = @android:style/Theme.NoTitleBar

; (bool) Indicates if the application supports multiple screens
android.manifest.multi_screen = True

; (str) Android logcat filters
android.logcat_filters = *:S python:D

[buildozer]

; (int) Log level
log_level = 2

; (str) Path to build artifact storage
warn_on_root = 1