[app]

# Nom de l'application
title = Gravity Switch

# Nom du package (important : format reverse domain)
package.name = gravityswitch
package.domain = com.gravitylab

# Répertoire source (où se trouve ton main.py)
source.dir = .

# Fichier principal
source.include_exts = py,png,jpg,kv,atlas,mp3,ogg,wav,ttf,json

# Exclure les fichiers inutiles (accélère le build)
source.exclude_patterns = .buildozer,*.pyc,*.pyo,*.git*,__pycache__,*.spec,*.md,*.txt

# Icône (512x512 recommandé pour Android)
icon.filename = icon.png

# Version
version = 1.0

# Orientation
orientation = portrait

# Permissions (si besoin de stockage pour le score)
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# API Android
android.api = 34
android.minapi = 21

# NDK (versions stables récentes)
android.ndk = 25c
p4a.branch = master

# Requirements (très important)
requirements = python3==3.11.0,kivy==2.3.0,setuptools,hostpython3,Cython==0.29.36

# Optionnel : accélère un peu le build
android.release = false
android.debug = true

# Pour un meilleur support audio sur Android
android.audio = sdl2

# =============================================
# Sections avancées (ne pas toucher sauf besoin)
# =============================================

[buildozer]

# Version de Buildozer
buildozer.version = master

# Log level
log_level = 2

# Nettoyage avant build (recommandé la première fois)
clean = true

# Nombre de cœurs pour la compilation
osx.python_version = 3.11
osx.use_openssl = 1

# Pour GitHub Actions
p4a.bootstrap = sdl2
