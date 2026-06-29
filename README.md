# 📝 MDReader - Windows Markdown 阅读器

轻量级 Markdown 文件阅读器，基于 PyQt5 + QWebEngineView 构建。

## ✨ 功能特性

- **完整 Markdown 渲染** - 表格、代码块、引用、列表、图片
- **代码语法高亮** - 支持 Python、C、JavaScript、SCL 等 100+ 种语言
- **编辑模式** - 直接编辑 Markdown 文件并保存（Ctrl+E 切换）
- **浮动文件浏览器** - 可拖拽的独立窗口，快速浏览文件夹（Ctrl+B 切换）
- **亮色/暗色主题** - 一键切换，护眼阅读
- **页面内搜索** - Ctrl+F 快速查找文本
- **导出 HTML** - 将渲染后的文档导出为网页
- **最近打开文件** - 快速访问最近 20 个文件
- **拖拽打开** - 直接拖放 .md 文件到窗口
- **文件关联** - 双击 .md 文件直接打开
- **多编码支持** - 自动检测 UTF-8、GBK、GB2312
- **撤销/重做** - 编辑模式下支持完整的撤销重做

## 📸 截图

> TODO: 添加截图

## 🚀 快速开始

### 方式一：源码运行

```bash
# 克隆仓库
git clone https://github.com/shushuluck/md-reader.git
cd md-reader

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

### 方式二：打包为可执行文件

```bash
# 安装依赖和 PyInstaller
pip install -r requirements.txt pyinstaller

# 打包
build.bat

# 运行
dist\MDReader\MDReader.exe
```

### 方式三：制作安装包

1. 安装 [Inno Setup 6](https://jrsoftware.org/isinfo.php)
2. 运行 `build_installer.bat`
3. 安装包位于 `installer_output\MDReader_Setup_1.0.0.exe`

## ⌨️ 快捷键

| 快捷键 | 功能 |
|:-------|:-----|
| `Ctrl+O` | 打开文件 |
| `Ctrl+Shift+O` | 打开文件夹 |
| `Ctrl+S` | 保存文件 |
| `Ctrl+Shift+S` | 另存为 |
| `Ctrl+E` | 切换编辑/阅读模式 |
| `Ctrl+W` | 关闭文档 |
| `Ctrl+F` | 搜索 |
| `Ctrl+T` | 切换主题 |
| `Ctrl+B` | 显示/隐藏文件浏览器 |
| `F5` | 重新加载 |
| `Ctrl+Z` | 撤销（编辑模式） |
| `Ctrl+Y` | 重做（编辑模式） |
| `Ctrl++` | 放大 |
| `Ctrl+-` | 缩小 |
| `Ctrl+0` | 重置缩放 |
| `Esc` | 清除搜索 |

## 📦 依赖库

| 库 | 版本 | 用途 |
|:---|:-----|:-----|
| PyQt5 | 5.15+ | GUI 框架 |
| PyQtWebEngine | 5.15+ | Web 渲染引擎 |
| markdown | 3.7+ | Markdown 解析器 |
| Pygments | 2.18+ | 代码语法高亮 |

## 🛠️ 从源码构建

### 环境要求

- Python 3.9+
- Windows 10/11

### 构建步骤

```bash
# 1. 安装依赖
pip install PyQt5 PyQtWebEngine markdown Pygments pyinstaller

# 2. 打包为可执行文件
python -m PyInstaller --noconfirm --onedir --windowed --name "MDReader" --icon "icon.ico" main.py

# 3. （可选）使用 Inno Setup 制作安装包
# 在 Inno Setup 6 中打开 setup.iss 并编译
```

## 📁 项目结构

```
md-reader/
├── main.py              # 主程序
├── requirements.txt     # Python 依赖
├── build.bat            # 打包脚本
├── build_installer.bat  # 安装包制作脚本
├── setup.iss            # Inno Setup 配置文件
├── .gitignore           # Git 忽略规则
├── LICENSE              # MIT 开源许可证
└── README.md            # 说明文档
```

## 🆕 更新日志

### v2.0 (2026-06-30)
- 移除左侧固定侧边栏，改为浮动文件浏览器面板
- 新增编辑模式，支持直接编辑和保存 Markdown 文件
- 工具栏增加保存按钮和编辑模式切换按钮
- 文件菜单增加保存/另存为功能
- 编辑菜单增加撤销/重做/剪切/复制/粘贴
- 关闭时自动检查未保存更改

### v1.0 (2026-06-29)
- 初始版本发布
- Markdown 渲染、代码高亮、目录树、主题切换

## 🤝 参与贡献

欢迎提交 Pull Request！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/新功能`)
3. 提交更改 (`git commit -m '添加新功能'`)
4. 推送分支 (`git push origin feature/新功能`)
5. 提交 Pull Request

## 📄 开源许可证

本项目基于 MIT 许可证开源 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI 框架
- [Python-Markdown](https://python-markdown.github.io/) - Markdown 解析
- [Pygments](https://pygments.org/) - 代码高亮

---

**用 ❤️ 为 Markdown 爱好者打造**
