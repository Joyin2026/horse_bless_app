# 年年送祝福 · 节日祝福语大全

> 一款汇集全年各大节日祝福语的安卓应用，一键复制、一键分享，让祝福不再词穷。

![Platform](https://img.shields.io/badge/Platform-Android-green)
![Kivy](https://img.shields.io/badge/Framework-Kivy-4CAF50)
![Version](https://img.shields.io/badge/Version-v2.6.110-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ 产品特色

- **🎊 17 个节日全覆盖**：春节、元宵、劳动、端午、中秋、国庆等传统佳节，加女神节、护士节、母亲节、教师节等行业节日
- **📝 千条精选祝福语**：1150+ 条精选祝福，每个节日 5 种风格分类，深情走心、文艺唯美、事业搞钱、幽默搞怪、长辈安康等
- **🔄 双下拉菜单**：传统佳节 / 行业节日 双分类切换，节日标签加粗高亮
- **📅 智能节日提醒**：自动判断下一个临近节日，显示"还有 N 天"倒计时
- **📋 一键复制分享**：支持复制到剪贴板，也可直接分享到微信、QQ 等社交应用
- **✏️ 分享前可编辑**：祝福语可二次编辑，更有温度
- **🌙 沉浸式全屏**：手动下滑显示状态栏，3 秒后自动隐藏，内容全屏无黑边
- **🔔 版本在线更新**：静默检查新版本，有更新时提示下载
- **🎨 节日氛围配色**：暖米黄 + 红棕色调，浓浓的节日喜庆感

---

## 📱 功能截图

| 首页 | 节日选择 | 分享弹窗 |
|------|---------|---------|
| ![首页](images/splash1.png) | ![节日](images/splash2.png) | ![分享](images/splash3.png) |

---

## 🎯 节日列表

### 传统佳节
- 🏮 春节
- 🏮 开工大吉
- 🏮 元宵节
- 🏮 劳动节
- 🏮 青年节
- 🏮 端午节
- 🏮 中秋节
- 🏮 国庆节
- 🏮 建党节

### 行业节日
- 💐 女神节（3.8）
- 👶 儿童节（6.1）
- 👩‍⚕️ 护士节（5.12）
- 👩 母亲节（5月第二个周日）
- 👨 父亲节（6月第三个周日）
- 🎖️ 建军节（8.1）
- 📚 教师节（9.10）
- 📰 记者节（11.8）

> 每年节日日期自动同步最新配置，支持在线更新。

---

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 开发框架 | Python + Kivy |
| 打包工具 | Buildozer / python-for-android |
| 持续集成 | GitHub Actions（自动构建 APK） |
| 数据格式 | JSON（本地 + 在线更新） |
| UI 风格 | 自定义绘制 + 节日配色 |

---

## 🚀 本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/Joyin2026/horse_bless_app.git
cd horse_bless_app

# 2. 安装依赖
pip install kivy

# 3. 桌面端运行（开发调试）
python main.py
```

### 构建安卓 APK

```bash
# 使用 Buildozer 构建
buildozer android debug
# 输出路径：bin/bless-*.apk
```

或使用 GitHub Actions 自动构建，查看 `.github/workflows/build.yml`。

---

## 📁 项目结构

```
horse_bless_app/
├── main.py               # 主程序（UI + 逻辑）
├── config.json           # 应用配置（版本、节日日期、更新地址）
├── buildozer.spec        # Buildozer 打包配置
├── chinese.ttf           # 中文字体
├── data/
│   └── bless.json        # 祝福语数据（节日 + 分类 + 多条祝福）
├── images/
│   ├── icon.png          # 应用图标
│   ├── bless.png         # 主标题
│   ├── start.png         # 启动页
│   ├── presplash.png     # 预加载图
│   ├── splash*.png       # 轮播图 / 截图
│   └── icon_*.png        # 功能图标
└── .github/
    └── workflows/
        └── build.yml     # CI 自动构建
```

---

## 🔄 更新说明

### v2.6.110
- 优化节日日期配置，支持在线同步
- 新增开工大吉等节日
- 下拉菜单样式升级，节日氛围更浓
- 修复部分机型沉浸式状态栏适配问题

---

## 📧 反馈与支持

- 官网：[卓影工作室](https://www.sjinyu.com)
- 邮箱：jinyu@sjinyu.com
- QQ：1529981

欢迎提交 Issue 和 PR！

---

## 📄 许可证

MIT License
