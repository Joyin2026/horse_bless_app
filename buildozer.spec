[app]
title = 马年送祝福
package.name = blessapp
package.domain = com.sjinyu.bless

version.regex = APP_VERSION = ["']v(.*?)["']
version.filename = %(source.dir)s/main.py

source.dir = .
source.include_exts = py,png,jpg,txt,json,ttf
source.include_patterns = images/*.png, images/*.jpg, data/bless.json

requirements = python3, kivy==2.1.0, pyjnius==1.6.0, urllib3

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b

android.archs = arm64-v8a

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE

android.debug = True
fullscreen = 1
orientation = portrait

icon.filename = %(source.dir)s/images/icon.png
presplash.filename = %(source.dir)s/images/presplash.png

android.accept_sdk_license = True
android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1
