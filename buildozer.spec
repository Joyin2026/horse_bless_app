# buildozer.spec - 马年祝福应用配置
[app]
title = 新春送祝福-v1.7.1
version.regex = APP_VERSION = ['"](.*)['"]
version.filename = %(source.dir)s/main.py
package.name = horsebless
package.domain = bless.sjinyu.com
source.dir = .
source.include_exts = py,png,jpg,kv,ttf
extra_files = chinese.ttf,images/
requirements = python3,kivy,pyjnius==1.5.0
android.permissions = INTERNET
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png
presplash.bg_color = #FFF5E6
fullscreen = 1
orientation = portrait
android.api = 31
android.minapi = 21
android.ndk = 25b
android.enable_androidx = True
android.archs = arm64-v8a
android.sdk_url = https://mirrors.aliyun.com/android-sdk/
android.ndk_url = https://mirrors.aliyun.com/android-ndk/
# 签名配置
android.keystore = $(KEYSTORE_FILE)
android.keystore_alias = $(KEYSTORE_ALIAS)
android.keystore_password = $(KEYSTORE_PASS)
android.keyalias_password = $(KEYALIAS_PASS)

# 其他选项
osx.python_version = 3
osx.kivy_version = 2.2.1
