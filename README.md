# 📝 MDReader - Markdown Reader for Windows

A lightweight Markdown viewer for Windows, built with PyQt5 and QWebEngineView.

## ✨ Features

- **Full Markdown Rendering** - Tables, fenced code blocks, blockquotes, lists, images
- **Syntax Highlighting** - Python, C, JavaScript, SCL and 100+ languages
- **File Tree Browser** - Browse and open files from sidebar
- **Dark/Light Theme** - One-click theme switching
- **In-page Search** - Ctrl+F to find text instantly
- **Export HTML** - Save rendered document as HTML
- **Recent Files** - Quick access to last 20 opened files
- **Drag & Drop** - Drag .md files to open
- **File Association** - Associate .md files to open with MDReader
- **Multi-encoding** - Auto-detect UTF-8, GBK, GB2312

## 📸 Screenshots

> TODO: Add screenshots here

## 🚀 Quick Start

### Option 1: Run from Source

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/md-reader.git
cd md-reader

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Option 2: Build Executable

```bash
# Install dependencies and PyInstaller
pip install -r requirements.txt pyinstaller

# Build
build.bat

# Run
dist\MDReader\MDReader.exe
```

### Option 3: Create Installer

1. Install [Inno Setup 6](https://jrsoftware.org/isinfo.php)
2. Run `build_installer.bat`
3. Find installer at `installer_output\MDReader_Setup_1.0.0.exe`

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|:---------|:-------|
| `Ctrl+O` | Open file |
| `Ctrl+Shift+O` | Open folder |
| `Ctrl+W` | Close document |
| `Ctrl+F` | Search in page |
| `Ctrl+T` | Toggle theme |
| `Ctrl+B` | Toggle sidebar |
| `F5` | Reload file |
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |
| `Ctrl+0` | Reset zoom |
| `Esc` | Clear search |

## 📦 Dependencies

| Package | Version | Purpose |
|:--------|:--------|:--------|
| PyQt5 | 5.15+ | GUI Framework |
| PyQtWebEngine | 5.15+ | Web Rendering Engine |
| markdown | 3.7+ | Markdown Parser |
| Pygments | 2.18+ | Syntax Highlighting |

## 🛠️ Build from Source

### Requirements

- Python 3.9+
- Windows 10/11

### Build Steps

```bash
# 1. Install dependencies
pip install PyQt5 PyQtWebEngine markdown Pygments pyinstaller

# 2. Build executable
python -m PyInstaller --noconfirm --onedir --windowed --name "MDReader" --icon "icon.ico" main.py

# 3. (Optional) Create installer with Inno Setup
# Open setup.iss in Inno Setup 6 and compile
```

## 📁 Project Structure

```
md-reader/
├── main.py              # Main application
├── requirements.txt     # Python dependencies
├── build.bat            # Build executable script
├── build_installer.bat  # Build installer script
├── setup.iss            # Inno Setup configuration
├── .gitignore           # Git ignore rules
├── LICENSE              # MIT License
└── README.md            # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- [Python-Markdown](https://python-markdown.github.io/)
- [Pygments](https://pygments.org/)

---

**Made with ❤️ for Markdown lovers**
