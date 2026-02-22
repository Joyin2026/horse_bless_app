[app]

# 应用的基本信息
title = 马年元宵祝福
package.name = blessapp
package.domain = com.sjinyu

# 版本号从代码中提取（匹配 APP_VERSION = "v1.7.0"）
version.regex = APP_VERSION = ["']v(.*?)["']
version.filename = %(source.dir)s/main.py

# 源代码目录
source.dir = .
source.include_exts = py,png,jpg,ttf,txt

# 需要包含的额外文件/目录
source.include_patterns = images/*.png, images/*.jpg, chinese.ttf

# 应用图标（可选）
# icon.filename = %(source.dir)s/icon.png

# 依赖库
requirements = python3,kivy,pyjnius

# 针对安卓的配置
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 34

# 权限
android.permissions = WRITE_EXTERNAL_STORAGE

# 添加 Java 代码（不需要）
# android.add_src =

# 是否启用 android 私有存储
android.private_storage = True

# 如果使用 Gradle 依赖（一般不需要）
# android.gradle_dependencies =

# 应用入口
osx.python_version = 3
osx.kivy_version = 2.2.1

# 全屏设置
fullscreen = 1

# 编译选项
presplash.filename = %(source.dir)s/images/splash1.png
# 如果需要图标
# icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 1

# 在构建之前执行的命令
# pre_build_commands =

# 其他平台相关配置（可忽略）
[requirements.android]
# 如果遇到 pyjnius 问题，可以尝试添加 recipes
# recipes = pyjnius

[requirements.osx]
# 略
