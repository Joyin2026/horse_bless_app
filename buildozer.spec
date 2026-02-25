[app]

# (str) 应用名称
title = 马年送祝福

# (str) 包名（唯一标识）
package.name = blessapp

# (str) 包域名（反向域名，用于生成完整包名）
package.domain = com.sjinyu.bless

# (str) 从 main.py 中自动提取版本号
version.regex = APP_VERSION = ["']v(.*?)["']
version.filename = %(source.dir)s/main.py

# (int) 版本代码（Android 内部使用，每次更新需递增）
version.code = 260111

# (str) 应用源代码目录
source.dir = .

# (list) 需要包含的源码文件扩展名（自动复制到 APK）
source.include_exts = py,png,jpg,jpeg,txt,json

# (list) 需要精确包含的文件模式（可选，与 include_exts 互补）
source.include_patterns = images/*.png, images/*.jpg, data/bless.json

# (list) 项目依赖的 Python 模块（指定版本以确保稳定）
requirements = python3, kivy==2.3.1, pyjnius==1.5.0

# (str) 应用入口文件
source.main = main.py

# (list) Android 权限
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE
android.native_graphics = False

# (int) Android SDK API 级别
android.api = 33

# (int) 最低支持的 Android API 级别
android.minapi = 21

# (str) Android NDK 版本
android.ndk = 25b

# (int) Android SDK 版本（与 api 保持一致）
android.sdk = 33

# (str) 指定 NDK 路径（Buildozer 会自动下载，此路径为最终存放位置）
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b

# (list) 目标 CPU 架构（仅 arm64-v8a 可减小 APK 体积）
android.archs = arm64-v8a

# (bool) 是否全屏（隐藏状态栏和导航栏）
fullscreen = 1

# (str) 屏幕方向
orientation = portrait

# (str) 应用图标路径
icon.filename = %(source.dir)s/images/icon.png

# (str) 启动画面图片路径
presplash.filename = %(source.dir)s/images/presplash.png

# (bool) 自动接受 SDK 许可证
android.accept_sdk_license = True

# (bool) 启用私有存储（避免外部存储权限警告）
android.private_storage = True

# (str) 构建产物类型（apk 或 aab）
android.release_artifact = apk

# (str) 额外的编译环境变量（用于 pyjnius 的 Cython 编译）
android.extra_env = PYJNIUS_CYTHONIZE=1, JNIUS_PLATFORM=android

# ---------- 以下为 Buildozer 通用配置 ----------
[buildozer]
# (int) 日志级别（0=安静, 1=标准, 2=详细）
log_level = 2

# (bool) 当以 root 身份运行时发出警告（CI 环境可忽略）
warn_on_root = 1

# (str) 目标平台（android / ios）
target = android

# (str) 构建输出目录
bin.dir = ./bin

# (str) 构建缓存目录
build.dir = ./.buildozer

# ---------- 签名配置（由环境变量传入，无需在文件中硬编码） ----------
# 以下配置留空，GitHub Actions 通过 P4A_RELEASE_KEYSTORE 等变量动态设置
# android.keystore =
# android.keystore_pass =
# android.keyalias =
# android.keyalias_pass =
