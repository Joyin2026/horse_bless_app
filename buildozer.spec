[app]
title = 马年送祝福
package.name = blessapp
package.domain = com.sjinyu.bless

version.regex = APP_VERSION = ["']v(.*?)["']
version.filename = %(source.dir)s/main.py

source.dir = .
source.include_exts = py,png,jpg,txt,json
source.include_patterns = images/*.png, images/*.jpg, data/bless.json

requirements = python3,kivy==2.2.1,pyjnius==1.4.0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

android.extra_env = PYJNIUS_CYTHONIZE=1
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
android.archs = arm64-v8a
android.permissions = WRITE_EXTERNAL_STORAGE
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE

fullscreen = 1
orientation = portrait
icon.filename = %(source.dir)s/images/icon.png
presplash.filename = %(source.dir)s/images/presplash.png

# 新增：强制 release 构建生成 APK 文件（而非 AAB）
android.release_artifact = apk

android.accept_sdk_license = True
android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1
