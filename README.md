# MD Reader

轻量、快速的 Markdown 阅读器，基于 Tauri 2.0 构建。

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
- ⌨️ **完整快捷键** — Ctrl+O/S/E/F/B

## 技术栈

| 组件 | 技术 |
|:-----|:-----|
| 框架 | Tauri 2.0 (Rust) |
| 前端 | Vite + 原生 JS |
| Markdown | markdown-it |
| 代码高亮 | highlight.js |
| 流程图 | Mermaid |
| 文件监听 | notify |

## 安装

下载对应平台的安装包：

- Windows: `MD Reader_x.x.x_x64-setup.exe` 或 `.msi`
- macOS: `MD Reader.app`
- Linux: `.deb` / `.AppImage`

## 开发

```bash
# 安装依赖
npm install

# 开发模式
npm run tauri dev

# 构建
npm run tauri build
```

## 快捷键

| 快捷键 | 功能 |
|:-------|:-----|
| Ctrl+O | 打开文件 |
| Ctrl+Shift+O | 打开文件夹 |
| Ctrl+S | 保存 |
| Ctrl+E | 编辑/预览切换 |
| Ctrl+F | 搜索 |
| Ctrl+B | 文件浏览器 |
| Ctrl+Shift+O | 目录大纲 |
| Ctrl+W | 关闭标签页 |
| F5 | 刷新 |

## 构建产物

| 平台 | 大小 |
|:-----|:-----|
| Windows | ~5MB |
| macOS | ~8MB |
| Linux | ~6MB |
