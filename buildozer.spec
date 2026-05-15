[app]
title = Graviton
package.name = graviton
package.domain = com.graviton
source.dir =.
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,json
source.include_dirs =.
version = 0.1
requirements = python3,kivy==2.3.0,sdl2,ffmpeg,pyjnius,android
orientation = portrait
fullscreen = 1
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk_path =
android.arch = arm64-v8a
android.permissions = INTERNET
android.allow_backup = False
android.arch_abi = arm64-v8a
android.meta_data = android.app.lib_name=main
android.logcat_filters = *:S python:I

[buildozer]
log_level = 2
warn_on_root = 1
