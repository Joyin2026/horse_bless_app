[app]

title = 马年送祝福-v1.6.1
package.name = horsebless
package.domain = com.bless.sjinyu
source.dir = .
source.include_exts = py,png,jpg,ttf

version = 1.6.0

# release 模式
android.release = True

requirements = python3,kivy,plyer,pyjnius

icon.filename = images/bless.png
# presplash.filename = images/start.png

orientation = portrait
fullscreen = 1
android.enable_androidx = True

# 只保留 arm64-v8a（可根据需要添加 armeabi-v7a）
android.archs = arm64-v8a


# 最小权限（如果不需要网络，可以去掉 INTERNET）
android.permissions = INTERNET

android.api = 31
android.minapi = 21
android.ndk = 25b

# 签名配置
android.keystore = ${HOME}/work/horse_bless_app/horse_bless_app/my-release-key.keystore
android.keystore_alias = zhuoying_horse_bless
android.keystore_password = 123456
android.keyalias_password = 123456

# 闪屏背景色
presplash.bg_color = #FFF5E6

# 国内镜像（可选）
android.sdk_url = https://mirrors.aliyun.com/android-sdk/
android.ndk_url = https://mirrors.aliyun.com/android-ndk/

[buildozer]
log_level = 2
