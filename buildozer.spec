[app]
title = 马年送祝福
package.name = blessapp
package.domain = com.sjinyu.bless

version.regex = APP_VERSION = ["']v(.*?)["']
version.filename = %(source.dir)s/main.py

source.dir = .
source.include_exts = py,png,jpg,txt,json,ttf
source.include_patterns = images/*.png, images/*.jpg, data/bless.json

requirements = python3, kivy==2.1.0, pyjnius, urllib3

android.api = 30
android.minapi = 21
android.ndk = 25b
android.sdk = 30
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b  # 确保路径正确

android.archs = arm64-v8a

# 添加必要的 Gradle 依赖
android.gradle_dependencies = 'com.android.support:support-annotations:28.0.0'

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE


fullscreen = 1
orientation = portrait

icon.filename = %(source.dir)s/images/icon.png
presplash.filename = %(source.dir)s/images/presplash.png

# 暂时禁用签名，构建 debug 版本以便获取更多信息
# android.release_artifact = apk  # 注释掉
android.accept_sdk_license = True
android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1
