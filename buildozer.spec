[app]
title = 马年元宵祝福
package.name = blessapp
package.domain = com.sjinyu

# 版本号从 main.py 提取
version.regex = APP_VERSION = ["']v(.*?)["']
version.filename = %(source.dir)s/main.py

source.dir = .
source.include_exts = py,png,jpg,ttf,txt
source.include_patterns = images/*.png, images/*.jpg, chinese.ttf

# 固定依赖版本，避免兼容性问题
requirements = python3,kivy==2.2.1,pyjnius==1.4.0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 34

# 仅构建 arm64-v8a 架构，减少编译时间
android.archs = arm64-v8a

# 强制 pyjnius 重新生成 C 文件
android.extra_env = PYJNIUS_CYTHONIZE=1

# 权限
android.permissions = WRITE_EXTERNAL_STORAGE
android.accept_sdk_license = True

# 全屏与启动图
fullscreen = 1
presplash.filename = %(source.dir)s/images/splash1.png

# 自动接受 SDK 许可证
android.accept_sdk_license = True

# 签名配置（release 时通过环境变量传入）
android.keystore = $(KEYSTORE_FILE)
android.keystore.alias = $(KEYSTORE_ALIAS)
android.keystore.password = $(KEYSTORE_PASS)
android.keystore.alias.password = $(KEYALIAS_PASS)

[buildozer]
log_level = 2
