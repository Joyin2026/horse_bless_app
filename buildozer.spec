[app]
title = 马年送祝福
package.name = blessapp
package.domain = com.sjinyu.bless

version.regex = APP_VERSION = ["']v(.*?)["']
version.filename = %(source.dir)s/main.py

source.dir = .
source.include_exts = py,png,jpg,txt,json
source.include_patterns = images/*.png, images/*.jpg, data/bless.json

requirements = python3==3.9.9,kivy==2.1.0
android.api = 33               # 与 NDK 25b 更匹配
android.minapi = 21
android.ndk = 25b               # 保持 NDK 25b
android.sdk = 33
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
android.archs = arm64-v8a
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE

# 确保 C++ 共享库被打包
android.add_src_patterns = lib/arm64-v8a/libc++_shared.so

fullscreen = 1
orientation = portrait
icon.filename = %(source.dir)s/images/icon.png
presplash.filename = %(source.dir)s/images/presplash.png

android.release_artifact = apk
android.accept_sdk_license = True
android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1
