# buildozer.spec - 马年祝福应用配置（最终修复版）
[app]
title = 新春送祝福-v1.7.4
package.name = horsebless
package.domain = bless.sjinyu.com

version.regex = APP_VERSION = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

source.dir = .
source.include_exts = py,png,jpg,kv,ttf

# 关键修改：不指定 Python 具体版本，让 buildozer 生成带 m 后缀的库
requirements = python3==3.8.10, kivy==2.2.1, pyjnius

# 强制竖屏
orientation = portrait
android.manifest.orientation = portrait

# 架构
android.archs = arm64-v8a
android.api = 31
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# 资源显式包含
android.add_src = images chinese.ttf

# 权限
android.permissions = INTERNET

# 图标和启动画面
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png
presplash.bg_color = #FFF5E6

# 全屏
fullscreen = 1

# 启用 AndroidX
android.enable_androidx = True

# 签名（从环境变量读取）
android.keystore = $(KEYSTORE_FILE)
android.keystore_alias = $(KEYSTORE_ALIAS)
android.keystore_password = $(KEYSTORE_PASS)
android.keyalias_password = $(KEYALIAS_PASS)
