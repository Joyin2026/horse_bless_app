[app]
title = 马年送祝福
package.name = blessapp
package.domain = com.sjinyu.bless

version.regex = APP_VERSION = ["']v(.*?)["']
version.filename = %(source.dir)s/main.py

source.dir = .
source.include_exts = py,png,jpg,txt,json
source.include_patterns = images/*.png, images/*.jpg, data/*.json

requirements = python3,kivy==2.2.1,pyjnius==1.4.0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

android.extra_env = PYJNIUS_CYTHONIZE=1
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
android.archs = arm64-v8a
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE

fullscreen = 1
orientation = portrait
icon.filename = %(source.dir)s/images/icon.png
presplash.filename = %(source.dir)s/images/presplash.png

# 强制 release 构建生成 APK 文件（而非 AAB）
android.release_artifact = apk

# 签名配置（release 时通过环境变量传入）
android.keystore = $(KEYSTORE_FILE)
android.keystore.alias = $(KEYSTORE_ALIAS)
android.keystore.password = $(KEYSTORE_PASS)
android.keystore.alias.password = $(KEYALIAS_PASS)

android.accept_sdk_license = True
android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1
