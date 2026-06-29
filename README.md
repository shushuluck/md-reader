# MD Reader

轻量、快速的 Markdown 阅读器，基于 Tauri 2.0 构建。支持 Windows / macOS / Linux / Android。

## 功能

- 📑 **多标签页** — 同时打开多个文件，拖拽排序
- 🎨 **三套主题** — 暗黑玻璃 / 简约扁平 / 暖色纸张
- 📝 **Markdown 渲染** — 代码高亮 + Mermaid 流程图
- 📋 **目录大纲** — 标题层级导航，点击跳转
- 🔍 **正则搜索** — 高亮匹配 + 计数
- 📂 **文件浏览器** — 侧边栏目录树
- 🕐 **最近文件** — 快速打开历史文件
- 👁 **文件变更监听** — 外部修改自动提示
- 📋 **代码复制** — 代码块一键复制按钮
- 🖼 **图片预览** — 点击放大查看
- 📱 **Android 支持** — 触摸手势、响应式布局
- ⌨️ **完整快捷键** — Ctrl+O/S/E/F/B

## 下载

| 平台 | 格式 | 大小 |
|:-----|:-----|:-----|
| Windows x64 | `.exe` / `.msi` | ~5MB |
| macOS (Intel + Apple Silicon) | `.app` | ~8MB |
| Linux x64 | `.deb` / `.AppImage` | ~6MB |
| Android (arm64) | `.apk` | ~8MB |

👉 [下载最新版本](https://github.com/shushuluck/md-reader/releases)

## 截图

| 🌙 暗黑玻璃 | ☀️ 简约扁平 | 📜 暖色纸张 |
|:-----------|:-----------|:-----------|
| 深色毛玻璃风格 | 纯净白色扁平 | 温暖纸张质感 |

## 技术栈

| 组件 | 技术 |
|:-----|:-----|
| 框架 | Tauri 2.0 (Rust) |
| 前端 | Vite + 原生 JS |
| Markdown | markdown-it |
| 代码高亮 | highlight.js |
| 流程图 | Mermaid |
| 文件监听 | notify |

## 快捷键

| 快捷键 | 功能 |
|:-------|:-----|
| Ctrl+O | 打开文件 |
| Ctrl+S | 保存 |
| Ctrl+E | 编辑/预览切换 |
| Ctrl+F | 搜索 |
| Ctrl+B | 文件浏览器 |
| Ctrl+Shift+O | 目录大纲 |
| Ctrl+W | 关闭标签页 |
| F5 | 刷新 |

## 开发

```bash
# 安装依赖
npm install

# 桌面开发
npm run tauri dev

# Android 开发
npm run tauri android dev

# 构建桌面版
npm run tauri build

# 构建 Android
npm run tauri android build
```

## 分支说明

| 分支 | 说明 |
|:-----|:-----|
| `main` | Tauri 2.0 当前版本 |
| `pyqt5` | 旧版 PyQt5 存档 |
