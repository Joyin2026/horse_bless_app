[app]
title = 马年元宵祝福
package.name = blessapp
package.domain = com.sjinyu

version.regex = APP_VERSION = ["']v(.*?)["']
version.filename = %(source.dir)s/main.py

source.dir = .
source.include_exts = py,png,jpg,ttf,txt
source.include_patterns = images/*.png, images/*.jpg, chinese.ttf

requirements = python3,kivy,pyjnius==1.4.0   # 指定版本

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 34
android.permissions = WRITE_EXTERNAL_STORAGE
fullscreen = 1
presplash.filename = %(source.dir)s/images/splash1.png

# 添加环境变量强制 pyjnius 重新生成 C 文件
android.extra_env = PYJNIUS_CYTHONIZE=1

# 可选，指定 Java 路径
android.java_home = /usr/lib/jvm/temurin-17-jdk-amd64

android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1
