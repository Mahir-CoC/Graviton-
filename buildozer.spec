[app]
title = Graviton
package.name = graviton
package.domain = com.graviton
source.dir =.
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,json
version = 0.1
requirements = python3,kivy==2.3.0,sdl2,ffmpeg,pyjnius,android
orientation = portrait
fullscreen = 1
android.api = 33
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 33.0.2
android.arch = arm64-v8a
android.permissions = INTERNET

[buildozer]
log_level = 2
