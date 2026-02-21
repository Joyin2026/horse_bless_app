# buildozer.spec - 马年送祝福应用配置
[app]
# 应用标识
title = 新春送祝福-v1.7.4
# 版本
version.regex = APP_VERSION = ['"](.*)['"]
version.filename = %(source.dir)s/main.py
package.name = horsebless
package.domain = bless.sjinyu.com
# 强制应用竖屏
orientation = portrait
android.manifest.orientation = portrait
# 源码目录
source.dir = .
source.include_exts = py,png,jpg,kv,ttf
#extra_files = chinese.ttf,images/

# 需求
requirements = python3==3.8.10,kivy==2.2.1,jnius

# 权限
android.permissions = INTERNET

# 图标
icon.filename = %(source.dir)s/icon.png

# 启动画面
presplash.filename = %(source.dir)s/presplash.png
presplash.bg_color = #FFF5E6

# 全屏
fullscreen = 1

# Android 特定配置
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 34

# 启用 AndroidX
android.enable_androidx = True
android.release_artifact = apk
# 架构
android.archs = arm64-v8a

# 国内镜像（可选）
android.sdk_url = https://mirrors.aliyun.com/android-sdk/
android.ndk_url = https://mirrors.aliyun.com/android-ndk/

# 签名配置（通过环境变量注入）
android.keystore = $(KEYSTORE_FILE)
android.keystore_alias = $(KEYSTORE_ALIAS)
android.keystore_password = $(KEYSTORE_PASS)
android.keyalias_password = $(KEYALIAS_PASS)

# 其他选项
osx.python_version = 3
osx.kivy_version = 2.2.1
