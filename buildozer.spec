[app]
title = 马年送祝福
package.name = blessapp
package.domain = com.sjinyu.bless

version.regex = APP_VERSION = ["']v(.*?)["']
version.filename = %(source.dir)s/main.py

source.dir = .
source.include_exts = py,png,jpg,txt,json,ttf
source.include_patterns = images/*.png, images/*.jpg, data/bless.json

# 依赖：python3 指定版本以提高稳定性，kivy 使用 2.1.0，pyjnius 用于 Android 原生调用，urllib3 用于网络请求（可选）
requirements = python3==3.9.9, kivy==2.1.0, pyjnius, urllib3

# Android 目标 API 和 NDK 版本（NDK 必须 >=25 以满足 python-for-android 要求）
android.api = 30
android.minapi = 21
android.ndk = 25b
android.sdk = 30

# 如果 NDK 已手动下载，可指定路径；否则让 buildozer 自动管理
# android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b

# 支持的架构（仅 arm64-v8a，匹配您的设备）
android.archs = arm64-v8a

# 权限
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE

# 强制包含 C++ 共享库（避免闪退）
android.add_src_patterns = lib/arm64-v8a/libc++_shared.so

# 全屏与方向
fullscreen = 1
orientation = portrait

# 图标和启动画面（请确保这些文件存在于 images/ 目录）
icon.filename = %(source.dir)s/images/icon.png
presplash.filename = %(source.dir)s/images/presplash.png

# 输出格式为 APK
android.release_artifact = apk

# 接受 SDK 许可证
android.accept_sdk_license = True

# 启用私有存储（可选）
android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1
