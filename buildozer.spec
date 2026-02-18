[app]

title = 马年新春祝福
package.name = horsebless
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,ttf

version = 1.0.9

requirements = python3,kivy,plyer,pyjnius

icon.filename = images/bless.png
presplash.filename = images/start.png

orientation = portrait
fullscreen = 1
android.enable_androidx = True

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE

android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# 签名配置
android.keystore = ./my-release-key.keystore
android.keystore_alias = zhuoying_horse_bless
android.keystore_password = 123456
android.keyalias_password = 123456

# 闪屏背景色（与图片背景一致）
presplash.bg_color = #FFF5E6

# 国内镜像（可选）
android.sdk_url = https://mirrors.aliyun.com/android-sdk/
android.ndk_url = https://mirrors.aliyun.com/android-ndk/

[buildozer]
log_level = 2
