[app]

# 应用标题（显示在图标下方）
title = 马年送祝福

# 包名（必须唯一）
package.name = blessapp

# 域名（反向域名风格）
package.domain = com.sjinyu.bless

# 从 main.py 中提取版本号
version.regex = APP_VERSION = ["']v(.*?)["']
version.filename = %(source.dir)s/main.py
version.code = 260111

# 源代码目录
source.dir = .

# 需要包含的文件类型
source.include_exts = py,png,jpg,jpeg,txt,json

# 需要包含的特定路径（支持通配符）
source.include_patterns = images/*.png, images/*.jpg, data/*.json

# Python 依赖（按需添加）
requirements = python3, kivy==2.2.1, pyjnius==1.4.0, pillow, certifi

# 主入口文件
source.main = main.py

# 所需 Android 权限
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE

# Android SDK 和目标 API
android.api = 33
android.minapi = 21

# NDK 版本
android.ndk = 25b

# SDK 版本
android.sdk = 33

# 额外环境变量（确保 pyjnius 正确编译）
android.extra_env = PYJNIUS_CYTHONIZE=1, JNIUS_PLATFORM=android

# NDK 路径（使用 buildozer 自动下载的路径，通常无需修改）
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b

# 支持的架构（仅 arm64-v8a 可加快构建）
android.archs = arm64-v8a

# 全屏模式
fullscreen = 1

# 屏幕方向
orientation = portrait

# 图标和启动画面（请确保文件存在）
icon.filename = %(source.dir)s/images/icon.png
presplash.filename = %(source.dir)s/images/presplash.png

# 接受 SDK 许可（自动同意）
android.accept_sdk_license = True

# 启用私有存储（用于访问应用专属目录）
android.private_storage = True

# 构建产物格式（APK 或 AAB）
android.release_artifact = apk

[buildozer]

# 日志级别
log_level = 2

# 如果以 root 运行则警告（在 CI 中无影响）
warn_on_root = 1

# 目标平台
target = android

# 输出目录
bin.dir = ./bin

# 构建缓存目录
build.dir = ./.buildozer
