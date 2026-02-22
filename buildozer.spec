[app]

# 应用基本信息
title = 马年元宵祝福
package.name = blessapp
package.domain = com.sjinyu.horsebless

# 版本号（会被 GitHub Actions 中的提取逻辑覆盖，但保留默认值）
version.regex = APP_VERSION = ["']v(.*?)["']
version.filename = %(source.dir)s/main.py

# 源代码目录
source.dir = .
source.include_exts = py,png,jpg,ttf,txt

# 需要包含的额外文件/目录
source.include_patterns = images/*.png, images/*.jpg, chinese.ttf

# 应用图标（可选，若没有请注释）
# icon.filename = %(source.dir)s/icon.png

# 依赖库（必须包含 pyjnius，因为代码中使用了 jnius）
requirements = python3,kivy,pyjnius

# 针对安卓的配置
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 34

# 权限（读写存储用于崩溃日志写入）
android.permissions = WRITE_EXTERNAL_STORAGE

# 全屏设置（与代码中 Window.fullscreen 配合）
fullscreen = 1

# 开屏图（启动画面）
presplash.filename = %(source.dir)s/images/splash1.png

# 如果需要签名发布版（将在 release 构建时通过环境变量传入）
android.keystore = $(KEYSTORE_FILE)
android.keystore.alias = $(KEYSTORE_ALIAS)
android.keystore.password = $(KEYSTORE_PASS)
android.keystore.alias.password = $(KEYALIAS_PASS)

# 是否启用 android 私有存储
android.private_storage = True

# 其他选项（保持默认）
osx.python_version = 3
osx.kivy_version = 2.2.1

[buildozer]
log_level = 2
warn_on_root = 1
