[app]
title = 马年元宵祝福
package.name = blessapp
package.domain = com.sjinyu

# 从 main.py 动态提取版本号
version.regex = APP_VERSION = ["']v(.*?)["']
version.filename = %(source.dir)s/main.py

source.dir = .
source.include_exts = py,png,jpg,ttf,txt
source.include_patterns = images/*.png, images/*.jpg, chinese.ttf

# 只保留必要依赖，移除注释，使用稳定版本
requirements = python3,kivy,pyjnius==1.4.0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 34

# 强制 pyjnius 重新生成 C 文件
android.extra_env = PYJNIUS_CYTHONIZE=1

# 显式指定 NDK 路径（避免环境变量冲突）
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b

# 只构建 arm64-v8a 架构（减少编译时间和内存）
android.archs = arm64-v8a

# 权限
android.permissions = WRITE_EXTERNAL_STORAGE

# 全屏设置
fullscreen = 1
presplash.filename = %(source.dir)s/images/splash1.png

# 自动接受 SDK 许可证
android.accept_sdk_license = True

# 签名配置（release 时通过环境变量传入）
android.keystore = $(KEYSTORE_FILE)
android.keystore.alias = $(KEYSTORE_ALIAS)
android.keystore.password = $(KEYSTORE_PASS)
android.keystore.alias.password = $(KEYALIAS_PASS)

android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1
