"""
Markdown 阅读器 - PyQt5 版本
功能：渲染 .md 文件，支持代码高亮、搜索、主题切换、编辑模式
"""

import sys
import os
import json
import markdown
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTreeView,
    QFileSystemModel, QStatusBar, QMenuBar,
    QAction, QToolBar, QLineEdit, QLabel, QWidget,
    QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox,
    QShortcut, QFrame, QDialog, QPlainTextEdit, QSplitter,
    QActionGroup
)
from PyQt5.QtCore import (
    Qt, QUrl, QDir, QSize, QSettings, QTimer,
    QFileInfo, pyqtSignal, QPoint
)
from PyQt5.QtGui import (
    QIcon, QKeySequence, QFont, QColor, QPalette, QTextCursor
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView, QWebEngineSettings, QWebEnginePage
)
from PyQt5.QtWebChannel import QWebChannel


# ============================================================
# 主题配置
# ============================================================

THEMES = {
    'light': {
        'name': '☀️ 亮色',
        'css_vars': {
            '--bg': '#ffffff',
            '--text': '#1a1a2e',
            '--text-secondary': '#555',
            '--heading': '#16213e',
            '--link': '#0f3460',
            '--link-hover': '#e94560',
            '--code-bg': '#f5f5f5',
            '--code-text': '#d63384',
            '--pre-bg': '#282c34',
            '--pre-text': '#abb2bf',
            '--border': '#e0e0e0',
            '--table-header': '#f0f0f0',
            '--table-stripe': '#fafafa',
            '--blockquote-border': '#e94560',
            '--blockquote-bg': '#fef6f8',
            '--highlight-bg': '#fff3cd',
            '--shadow': 'rgba(0,0,0,0.08)',
        }
    },
    'dark': {
        'name': '🌙 深色',
        'css_vars': {
            '--bg': '#1a1a2e',
            '--text': '#e0e0e0',
            '--text-secondary': '#aaa',
            '--heading': '#eee',
            '--link': '#64b5f6',
            '--link-hover': '#e94560',
            '--code-bg': '#2d2d44',
            '--code-text': '#f08d49',
            '--pre-bg': '#16161e',
            '--pre-text': '#abb2bf',
            '--border': '#333',
            '--table-header': '#252540',
            '--table-stripe': '#1e1e35',
            '--blockquote-border': '#e94560',
            '--blockquote-bg': '#2a1a20',
            '--highlight-bg': '#3a3000',
            '--shadow': 'rgba(0,0,0,0.3)',
        }
    },
    'green': {
        'name': '🌿 护眼绿',
        'css_vars': {
            '--bg': '#CCE8CF',
            '--text': '#1a1a2e',
            '--text-secondary': '#4a5568',
            '--heading': '#2d3748',
            '--link': '#2b6cb0',
            '--link-hover': '#e53e3e',
            '--code-bg': '#b8d8ba',
            '--code-text': '#c53030',
            '--pre-bg': '#2d3748',
            '--pre-text': '#e2e8f0',
            '--border': '#a0c8a4',
            '--table-header': '#b8d8ba',
            '--table-stripe': '#c2dcc4',
            '--blockquote-border': '#48bb78',
            '--blockquote-bg': '#c2e0c5',
            '--highlight-bg': '#fefce8',
            '--shadow': 'rgba(0,0,0,0.06)',
        }
    },
    'sepia': {
        'name': '📜 羊皮纸',
        'css_vars': {
            '--bg': '#f4ecd8',
            '--text': '#5b4636',
            '--text-secondary': '#8b7355',
            '--heading': '#3e2723',
            '--link': '#8b4513',
            '--link-hover': '#d32f2f',
            '--code-bg': '#e8dcc8',
            '--code-text': '#c0392b',
            '--pre-bg': '#3e2723',
            '--pre-text': '#d7ccc8',
            '--border': '#d4c5a9',
            '--table-header': '#e8dcc8',
            '--table-stripe': '#f0e6d0',
            '--blockquote-border': '#d4a574',
            '--blockquote-bg': '#efe5d0',
            '--highlight-bg': '#fff8e1',
            '--shadow': 'rgba(0,0,0,0.08)',
        }
    },
    'blue': {
        'name': '🌊 海洋蓝',
        'css_vars': {
            '--bg': '#e8f4fd',
            '--text': '#1e3a5f',
            '--text-secondary': '#4a6fa5',
            '--heading': '#0d47a1',
            '--link': '#1565c0',
            '--link-hover': '#d32f2f',
            '--code-bg': '#bbdefb',
            '--code-text': '#c62828',
            '--pre-bg': '#0d47a1',
            '--pre-text': '#e3f2fd',
            '--border': '#90caf9',
            '--table-header': '#bbdefb',
            '--table-stripe': '#e3f2fd',
            '--blockquote-border': '#42a5f5',
            '--blockquote-bg': '#e1f5fe',
            '--highlight-bg': '#fff9c4',
            '--shadow': 'rgba(0,0,0,0.06)',
        }
    },
    'gray': {
        'name': '🌫️ 柔灰',
        'css_vars': {
            '--bg': '#2a2a2a',
            '--text': '#d4d4d4',
            '--text-secondary': '#9ca3af',
            '--heading': '#f3f4f6',
            '--link': '#60a5fa',
            '--link-hover': '#f87171',
            '--code-bg': '#3f3f3f',
            '--code-text': '#fb923c',
            '--pre-bg': '#1f1f1f',
            '--pre-text': '#d4d4d4',
            '--border': '#4b5563',
            '--table-header': '#374151',
            '--table-stripe': '#2d2d2d',
            '--blockquote-border': '#6b7280',
            '--blockquote-bg': '#333333',
            '--highlight-bg': '#423d00',
            '--shadow': 'rgba(0,0,0,0.3)',
        }
    },
    'lavender': {
        'name': '💜 薰衣草',
        'css_vars': {
            '--bg': '#f3e8ff',
            '--text': '#3b1f6e',
            '--text-secondary': '#7c3aed',
            '--heading': '#5b21b6',
            '--link': '#7c3aed',
            '--link-hover': '#dc2626',
            '--code-bg': '#e9d5ff',
            '--code-text': '#be185d',
            '--pre-bg': '#4c1d95',
            '--pre-text': '#e9d5ff',
            '--border': '#c4b5fd',
            '--table-header': '#e9d5ff',
            '--table-stripe': '#f5f0ff',
            '--blockquote-border': '#a78bfa',
            '--blockquote-bg': '#ede9fe',
            '--highlight-bg': '#fef9c3',
            '--shadow': 'rgba(0,0,0,0.06)',
        }
    },
}

# 界面样式模板
UI_STYLE_TEMPLATE = """
    QMainWindow, QWidget {{ background: {ui_bg}; color: {ui_text}; }}
    QToolBar {{
        background: {ui_bg}; border-bottom: 1px solid {ui_border};
        padding: 4px; spacing: 6px;
    }}
    QToolBar QToolButton {{
        background: transparent; border: 1px solid transparent;
        border-radius: 4px; padding: 6px 12px; font-size: 13px;
        color: {ui_text};
    }}
    QToolBar QToolButton:hover {{ background: {ui_hover}; border-color: {ui_border}; }}
    QToolBar QToolButton:checked {{ background: {ui_checked}; color: white; }}
    QLineEdit {{
        background: {ui_input_bg}; border: 1px solid {ui_border}; border-radius: 4px;
        padding: 6px 10px; font-size: 13px; color: {ui_text};
    }}
    QLineEdit:focus {{ border-color: {ui_focus}; }}
    QStatusBar {{ background: {ui_bg}; border-top: 1px solid {ui_border}; font-size: 12px; }}
    QMenuBar {{ background: {ui_bg}; border-bottom: 1px solid {ui_border}; color: {ui_text}; }}
    QMenuBar::item:selected {{ background: {ui_hover}; }}
    QMenu {{ background: {ui_bg}; border: 1px solid {ui_border}; color: {ui_text}; }}
    QMenu::item:selected {{ background: {ui_hover}; }}
    QPlainTextEdit {{
        background: {editor_bg}; color: {editor_text};
        border: 1px solid {ui_border}; font-family: 'Consolas', 'Microsoft YaHei', monospace;
        font-size: 14px; line-height: 1.6;
    }}
    QTreeView {{
        background: {ui_bg}; color: {ui_text};
        border: 1px solid {ui_border}; border-radius: 4px;
        font-size: 13px;
    }}
    QTreeView::item {{ padding: 4px 8px; }}
    QTreeView::item:selected {{ background: {ui_checked}; color: white; }}
    QTreeView::item:hover {{ background: {ui_hover}; }}
"""

# 各主题的界面样式
UI_STYLES = {
    'light': UI_STYLE_TEMPLATE.format(
        ui_bg='#ffffff', ui_text='#1a1a2e', ui_border='#e0e0e0',
        ui_hover='#e8f0fe', ui_checked='#0f3460', ui_input_bg='white',
        ui_focus='#0f3460', editor_bg='#ffffff', editor_text='#1a1a2e'
    ),
    'dark': UI_STYLE_TEMPLATE.format(
        ui_bg='#1a1a2e', ui_text='#e0e0e0', ui_border='#333',
        ui_hover='#252540', ui_checked='#e94560', ui_input_bg='#252540',
        ui_focus='#e94560', editor_bg='#1a1a2e', editor_text='#e0e0e0'
    ),
    'green': UI_STYLE_TEMPLATE.format(
        ui_bg='#CCE8CF', ui_text='#1a1a2e', ui_border='#a0c8a4',
        ui_hover='#b8d8ba', ui_checked='#2d7a32', ui_input_bg='#d8eeda',
        ui_focus='#2d7a32', editor_bg='#d8eeda', editor_text='#1a1a2e'
    ),
    'sepia': UI_STYLE_TEMPLATE.format(
        ui_bg='#f4ecd8', ui_text='#5b4636', ui_border='#d4c5a9',
        ui_hover='#e8dcc8', ui_checked='#8b4513', ui_input_bg='#f8f2e4',
        ui_focus='#8b4513', editor_bg='#f8f2e4', editor_text='#5b4636'
    ),
    'blue': UI_STYLE_TEMPLATE.format(
        ui_bg='#e8f4fd', ui_text='#1e3a5f', ui_border='#90caf9',
        ui_hover='#bbdefb', ui_checked='#1565c0', ui_input_bg='#f0f8ff',
        ui_focus='#1565c0', editor_bg='#f0f8ff', editor_text='#1e3a5f'
    ),
    'gray': UI_STYLE_TEMPLATE.format(
        ui_bg='#2a2a2a', ui_text='#d4d4d4', ui_border='#4b5563',
        ui_hover='#374151', ui_checked='#3b82f6', ui_input_bg='#333333',
        ui_focus='#3b82f6', editor_bg='#2a2a2a', editor_text='#d4d4d4'
    ),
    'lavender': UI_STYLE_TEMPLATE.format(
        ui_bg='#f3e8ff', ui_text='#3b1f6e', ui_border='#c4b5fd',
        ui_hover='#e9d5ff', ui_checked='#7c3aed', ui_input_bg='#f8f0ff',
        ui_focus='#7c3aed', editor_bg='#f8f0ff', editor_text='#3b1f6e'
    ),
}


# ============================================================
# Markdown 渲染器
# ============================================================

class MarkdownRenderer:
    """将 Markdown 文本转换为带样式的 HTML"""

    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                'tables',
                'fenced_code',
                'codehilite',
                'toc',
                'attr_list',
                'md_in_html',
                'nl2br',
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'linenums': False,
                    'guess_lang': True,
                }
            }
        )

    def render(self, md_text: str, file_path: str = '', theme: str = 'light') -> str:
        """将 Markdown 转换为完整 HTML 页面"""
        self.md.reset()
        body = self.md.convert(md_text)

        # 获取主题 CSS 变量
        theme_config = THEMES.get(theme, THEMES['light'])
        css_vars = theme_config['css_vars']
        css_vars_str = '\n            '.join([f'{k}: {v};' for k, v in css_vars.items()])

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {{
            {css_vars_str}
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                         'Microsoft YaHei', '微软雅黑', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.8;
            padding: 30px 50px;
            max-width: 960px;
            margin: 0 auto;
            transition: background 0.3s, color 0.3s;
        }}

        /* 标题 */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--heading);
            margin: 1.5em 0 0.5em;
            line-height: 1.3;
            font-weight: 600;
        }}
        h1 {{ font-size: 2em; border-bottom: 3px solid var(--link); padding-bottom: 0.3em; }}
        h2 {{ font-size: 1.6em; border-bottom: 1px solid var(--border); padding-bottom: 0.2em; }}
        h3 {{ font-size: 1.3em; }}
        h4 {{ font-size: 1.1em; }}

        /* 段落 */
        p {{ margin: 0.8em 0; }}

        /* 链接 */
        a {{
            color: var(--link);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: all 0.2s;
        }}
        a:hover {{
            color: var(--link-hover);
            border-bottom-color: var(--link-hover);
        }}

        /* 列表 */
        ul, ol {{
            margin: 0.8em 0;
            padding-left: 2em;
        }}
        li {{ margin: 0.3em 0; }}
        li > ul, li > ol {{ margin: 0.2em 0; }}

        /* 代码 */
        code {{
            font-family: 'Cascadia Code', 'JetBrains Mono', 'Fira Code',
                         'Consolas', 'Source Code Pro', monospace;
            background: var(--code-bg);
            color: var(--code-text);
            padding: 0.15em 0.4em;
            border-radius: 4px;
            font-size: 0.9em;
        }}

        pre {{
            background: var(--pre-bg);
            color: var(--pre-text);
            padding: 1em 1.2em;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1em 0;
            box-shadow: 0 2px 8px var(--shadow);
            line-height: 1.5;
        }}
        pre code {{
            background: none;
            color: inherit;
            padding: 0;
            font-size: 0.88em;
        }}

        /* 代码高亮 (Pygments) */
        .highlight {{ background: var(--pre-bg); border-radius: 8px; padding: 1em; overflow-x: auto; }}
        .highlight pre {{ margin: 0; padding: 0; box-shadow: none; }}
        .hll {{ background-color: #444; }}
        .c, .cm, .c1, .cs {{ color: #5c6370; font-style: italic; }}
        .k, .kn, .kp, .kr, .kt {{ color: #c678dd; }}
        .kd {{ color: #c678dd; }}
        .n, .nb, .nc, .nd, .ne, .nf, .ni, .nl, .nn, .nt {{ color: #e06c75; }}
        .o, .ow {{ color: #56b6c2; }}
        .p {{ color: #abb2bf; }}
        .s, .s1, .s2, .sb, .sc, .sd, .se, .sh, .si, .sx, .sr, .ss {{ color: #98c379; }}
        .m, .mf, .mh, .mi, .mo {{ color: #d19a66; }}
        .na {{ color: #d19a66; }}
        .nv, .vc, .vg, .vi {{ color: #e06c75; }}

        /* 表格 */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
            box-shadow: 0 1px 4px var(--shadow);
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            border: 1px solid var(--border);
            padding: 0.6em 1em;
            text-align: left;
        }}
        th {{
            background: var(--table-header);
            font-weight: 600;
        }}
        tr:nth-child(even) {{ background: var(--table-stripe); }}
        tr:hover {{ background: var(--highlight-bg); }}

        /* 引用块 */
        blockquote {{
            border-left: 4px solid var(--blockquote-border);
            background: var(--blockquote-bg);
            margin: 1em 0;
            padding: 0.8em 1.2em;
            border-radius: 0 8px 8px 0;
            color: var(--text-secondary);
        }}
        blockquote p {{ margin: 0.3em 0; }}

        /* 分割线 */
        hr {{
            border: none;
            height: 2px;
            background: linear-gradient(to right, transparent, var(--border), transparent);
            margin: 2em 0;
        }}

        /* 图片 */
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 12px var(--shadow);
            margin: 1em 0;
        }}

        /* 折叠块 */
        details {{
            border: 1px solid var(--border);
            border-radius: 8px;
            margin: 1em 0;
            overflow: hidden;
        }}
        summary {{
            background: var(--table-header);
            padding: 0.8em 1.2em;
            cursor: pointer;
            font-weight: 600;
            user-select: none;
            transition: background 0.2s;
        }}
        summary:hover {{ background: var(--highlight-bg); }}
        details[open] summary {{ border-bottom: 1px solid var(--border); }}
        details > *:not(summary) {{ padding: 0 1.2em; }}
        details > *:last-child {{ padding-bottom: 1em; }}

        /* 复选框任务列表 */
        input[type="checkbox"] {{
            margin-right: 0.5em;
            transform: scale(1.2);
        }}

        /* 滚动条 */
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{
            background: var(--border);
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--text-secondary); }}

        /* 搜索高亮 */
        .search-highlight {{
            background: #ffeb3b;
            color: #000;
            padding: 1px 2px;
            border-radius: 2px;
        }}
        .search-highlight.active {{
            background: #ff9800;
        }}
    </style>
</head>
<body>
    {body}
    <script>
        // 支持外部链接在默认浏览器打开
        document.addEventListener('click', function(e) {{
            const link = e.target.closest('a');
            if (link && link.href.startsWith('http')) {{
                e.preventDefault();
                window.open(link.href, '_blank');
            }}
        }});

        // 平滑滚动
        document.documentElement.style.scrollBehavior = 'smooth';
    </script>
</body>
</html>"""
        return html


# ============================================================
# 自定义 WebEnginePage（处理链接点击）
# ============================================================

class MarkdownWebPage(QWebEnginePage):
    """自定义页面，处理外部链接"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._main_window = parent

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        """拦截链接点击"""
        if nav_type == QWebEnginePage.NavigationTypeLinkClicked:
            if url.scheme() in ('http', 'https'):
                import webbrowser
                webbrowser.open(url.toString())
                return False
            elif url.scheme() == 'file':
                file_path = url.toLocalFile()
                if file_path.endswith('.md') and self._main_window:
                    self._main_window.open_file(file_path)
                    return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


# ============================================================
# 文件浏览器浮动面板
# ============================================================

class FileBrowserPanel(QWidget):
    """文件浏览器浮动面板"""

    file_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window | Qt.WindowStaysOnTopHint)
        self.setWindowTitle('文件浏览器')
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.resize(300, 500)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.fs_model = QFileSystemModel()
        self.fs_model.setReadOnly(True)
        self.fs_model.setNameFilterDisables(False)
        self.fs_model.setNameFilters(['*.md', '*.markdown', '*.txt'])

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.fs_model)
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.clicked.connect(self._on_tree_clicked)
        self.tree_view.setAnimated(True)

        layout.addWidget(self.tree_view)

    def set_root_path(self, folder: str):
        index = self.fs_model.setRootPath(folder)
        self.tree_view.setRootIndex(index)
        self.tree_view.scrollToTop()

    def _on_tree_clicked(self, index):
        file_path = self.fs_model.filePath(index)
        if os.path.isfile(file_path) and file_path.endswith(('.md', '.markdown', '.txt')):
            self.file_selected.emit(file_path)

    def select_file(self, file_path: str):
        index = self.fs_model.index(file_path)
        if index.isValid():
            self.tree_view.setCurrentIndex(index)
            self.tree_view.scrollTo(index)


# ============================================================
# 主窗口
# ============================================================

class MarkdownReader(QMainWindow):
    """Markdown 阅读器主窗口"""

    def __init__(self):
        super().__init__()

        # 状态
        self.current_file = None
        self.renderer = MarkdownRenderer()
        self.settings = QSettings('MDReader', 'MarkdownReader')
        self.recent_files = []
        self.current_theme = 'light'
        self.is_edit_mode = False
        self.file_browser = None

        # 初始化
        self._init_window()
        self._init_menu()
        self._init_toolbar()
        self._init_ui()
        self._init_shortcuts()
        self._load_settings()

    def _init_window(self):
        self.setWindowTitle('Markdown 阅读器')
        self.setMinimumSize(900, 600)
        self.resize(1200, 800)
        self.setWindowIcon(self.style().standardIcon(
            self.style().SP_FileDialogDetailedView
        ))

    def _init_menu(self):
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')

        open_action = QAction('打开文件(&O)...', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        open_folder_action = QAction('打开文件夹(&D)...', self)
        open_folder_action.setShortcut(QKeySequence('Ctrl+Shift+O'))
        open_folder_action.triggered.connect(self.open_folder_dialog)
        file_menu.addAction(open_folder_action)

        file_menu.addSeparator()

        self.recent_menu = file_menu.addMenu('最近打开(&R)')
        self._update_recent_menu()

        file_menu.addSeparator()

        save_action = QAction('保存(&S)', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction('另存为(&A)...', self)
        save_as_action.setShortcut(QKeySequence('Ctrl+Shift+S'))
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        reload_action = QAction('重新加载(&R)', self)
        reload_action.setShortcut(QKeySequence.Refresh)
        reload_action.triggered.connect(self.reload_file)
        file_menu.addAction(reload_action)

        file_menu.addSeparator()

        close_action = QAction('关闭文档(&C)', self)
        close_action.setShortcut(QKeySequence('Ctrl+W'))
        close_action.triggered.connect(self.close_document)
        file_menu.addAction(close_action)

        file_menu.addSeparator()

        export_html_action = QAction('导出为 HTML(&H)...', self)
        export_html_action.triggered.connect(self.export_html)
        file_menu.addAction(export_html_action)

        file_menu.addSeparator()

        quit_action = QAction('退出(&Q)', self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu('编辑(&E)')

        self.toggle_edit_action = QAction('编辑模式(&E)', self)
        self.toggle_edit_action.setShortcut(QKeySequence('Ctrl+E'))
        self.toggle_edit_action.setCheckable(True)
        self.toggle_edit_action.triggered.connect(self.toggle_edit_mode)
        edit_menu.addAction(self.toggle_edit_action)

        edit_menu.addSeparator()

        undo_action = QAction('撤销(&U)', self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction('重做(&R)', self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction('剪切(&T)', self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self._cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction('复制(&C)', self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self._copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction('粘贴(&P)', self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self._paste)
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()

        select_all_action = QAction('全选(&A)', self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(self._select_all)
        edit_menu.addAction(select_all_action)

        # 视图菜单
        view_menu = menubar.addMenu('视图(&V)')

        # 主题子菜单
        theme_menu = view_menu.addMenu('主题(&T)')
        self.theme_group = QActionGroup(self)
        self.theme_group.setExclusive(True)

        for theme_id, theme_info in THEMES.items():
            action = QAction(theme_info['name'], self)
            action.setCheckable(True)
            action.setData(theme_id)
            action.triggered.connect(lambda checked, t=theme_id: self.set_theme(t))
            self.theme_group.addAction(action)
            theme_menu.addAction(action)
            if theme_id == self.current_theme:
                action.setChecked(True)

        view_menu.addSeparator()

        toggle_browser_action = QAction('文件浏览器(&B)', self)
        toggle_browser_action.setShortcut(QKeySequence('Ctrl+B'))
        toggle_browser_action.triggered.connect(self.toggle_file_browser)
        view_menu.addAction(toggle_browser_action)

        view_menu.addSeparator()

        zoom_in_action = QAction('放大(&I)', self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(lambda: self.web_view.setZoomFactor(
            min(3.0, self.web_view.zoomFactor() + 0.1)
        ))
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction('缩小(&O)', self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(lambda: self.web_view.setZoomFactor(
            max(0.5, self.web_view.zoomFactor() - 0.1)
        ))
        view_menu.addAction(zoom_out_action)

        reset_zoom_action = QAction('重置缩放', self)
        reset_zoom_action.setShortcut(QKeySequence('Ctrl+0'))
        reset_zoom_action.triggered.connect(lambda: self.web_view.setZoomFactor(1.0))
        view_menu.addAction(reset_zoom_action)

        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')

        about_action = QAction('关于(&A)', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _init_toolbar(self):
        toolbar = QToolBar('工具栏')
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        open_btn = QAction('📂 打开', self)
        open_btn.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_btn)

        save_btn = QAction('💾 保存', self)
        save_btn.triggered.connect(self.save_file)
        toolbar.addAction(save_btn)

        reload_btn = QAction('🔄 刷新', self)
        reload_btn.triggered.connect(self.reload_file)
        toolbar.addAction(reload_btn)

        close_btn = QAction('✖ 关闭', self)
        close_btn.triggered.connect(self.close_document)
        toolbar.addAction(close_btn)

        toolbar.addSeparator()

        self.edit_btn = QAction('✏️ 编辑', self)
        self.edit_btn.setCheckable(True)
        self.edit_btn.triggered.connect(self.toggle_edit_mode)
        toolbar.addAction(self.edit_btn)

        toolbar.addSeparator()

        search_label = QLabel(' 🔍 ')
        toolbar.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('搜索...')
        self.search_input.setFixedWidth(200)
        self.search_input.returnPressed.connect(self.search_in_page)
        toolbar.addWidget(self.search_input)

        search_btn = QAction('查找', self)
        search_btn.triggered.connect(self.search_in_page)
        toolbar.addAction(search_btn)

        toolbar.addSeparator()

        # 主题下拉选择
        theme_label = QLabel(' 🎨 ')
        toolbar.addWidget(theme_label)

        self.theme_combo = QComboBox()
        for theme_id, theme_info in THEMES.items():
            self.theme_combo.addItem(theme_info['name'], theme_id)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_combo_changed)
        toolbar.addWidget(self.theme_combo)

        # 文件浏览器按钮
        browser_btn = QAction('📁 浏览器', self)
        browser_btn.triggered.connect(self.toggle_file_browser)
        toolbar.addAction(browser_btn)

        spacer = QWidget()
        spacer.setSizePolicy(
            spacer.sizePolicy().horizontalPolicy(),
            spacer.sizePolicy().verticalPolicy()
        )
        toolbar.addWidget(spacer)

        self.file_label = QLabel('未打开文件')
        self.file_label.setStyleSheet('font-size: 12px; color: #888; padding: 0 10px;')
        toolbar.addWidget(self.file_label)

    def _init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.web_view = QWebEngineView()
        self.web_page = MarkdownWebPage(self)
        self.web_view.setPage(self.web_page)

        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, False)
        settings.setFontSize(QWebEngineSettings.DefaultFontSize, 16)

        self.text_editor = QPlainTextEdit()
        self.text_editor.setTabStopDistance(40)
        self.text_editor.textChanged.connect(self._on_text_changed)
        self.text_editor.hide()

        layout.addWidget(self.web_view)
        layout.addWidget(self.text_editor)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel('就绪')
        self.status_bar.addWidget(self.status_label)

        self.edit_status_label = QLabel('')
        self.edit_status_label.setStyleSheet('color: #e94560; font-weight: bold;')
        self.status_bar.addPermanentWidget(self.edit_status_label)

        self._show_welcome()

    def _init_shortcuts(self):
        QShortcut(QKeySequence.Find, self, lambda: self.search_input.setFocus())
        QShortcut(QKeySequence('Ctrl+W'), self, self.close_document)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self._clear_search)

    def _load_settings(self):
        geom = self.settings.value('geometry')
        if geom:
            self.restoreGeometry(geom)

        state = self.settings.value('windowState')
        if state:
            self.restoreState(state)

        self.current_theme = self.settings.value('theme', 'light')
        self._apply_theme()

        self.recent_files = self.settings.value('recent_files', [])

        last_folder = self.settings.value('last_folder', '')
        if last_folder and os.path.isdir(last_folder):
            self._init_file_browser(last_folder)

        last_file = self.settings.value('last_file', '')
        if last_file and os.path.isfile(last_file):
            QTimer.singleShot(100, lambda: self.open_file(last_file))

    def _save_settings(self):
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('windowState', self.saveState())
        self.settings.setValue('theme', self.current_theme)
        self.settings.setValue('recent_files', self.recent_files)
        if self.current_file:
            self.settings.setValue('last_file', self.current_file)
            self.settings.setValue('last_folder', str(Path(self.current_file).parent))

    # ----------------------------------------------------------
    # 主题切换
    # ----------------------------------------------------------

    def set_theme(self, theme_id: str):
        """设置指定主题"""
        if theme_id in THEMES:
            self.current_theme = theme_id
            self._apply_theme()

            # 更新菜单选中状态
            for action in self.theme_group.actions():
                if action.data() == theme_id:
                    action.setChecked(True)
                    break

            # 更新下拉框
            index = self.theme_combo.findData(theme_id)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)

            # 重新渲染
            if self.current_file and not self.is_edit_mode:
                self._render_current_file()

    def _on_theme_combo_changed(self, index: int):
        """下拉框主题切换"""
        theme_id = self.theme_combo.itemData(index)
        if theme_id and theme_id != self.current_theme:
            self.set_theme(theme_id)

    def _apply_theme(self):
        style = UI_STYLES.get(self.current_theme, UI_STYLES['light'])
        self.setStyleSheet(style)

        bg_color = THEMES[self.current_theme]['css_vars']['--bg']
        self.web_view.setStyleSheet(f'background: {bg_color};')

    def _render_current_file(self):
        """用当前主题重新渲染文件"""
        if not self.current_file:
            return
        try:
            content = self.text_editor.toPlainText() if self.is_edit_mode else self._raw_content
            html = self.renderer.render(content, self.current_file, self.current_theme)
            self.web_view.setHtml(html, QUrl.fromLocalFile(self.current_file))
        except Exception as e:
            self.status_label.setText(f'❌ 渲染失败: {str(e)}')

    # ----------------------------------------------------------
    # 文件操作
    # ----------------------------------------------------------

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '打开 Markdown 文件', '',
            'Markdown 文件 (*.md *.markdown *.txt);;所有文件 (*)'
        )
        if file_path:
            self.open_file(file_path)

    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, '选择文件夹')
        if folder:
            self._init_file_browser(folder)

    def open_file(self, file_path: str):
        if self.is_edit_mode and self.text_editor.document().isModified():
            reply = QMessageBox.question(
                self, '保存更改',
                '当前文件已修改，是否保存？',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return

        file_path = os.path.abspath(file_path)
        if not os.path.isfile(file_path):
            self.status_label.setText(f'❌ 文件不存在: {file_path}')
            return

        try:
            content = None
            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                self.status_label.setText('❌ 无法解码文件')
                return

            self._raw_content = content

            html = self.renderer.render(content, file_path, self.current_theme)
            self.web_view.setHtml(html, QUrl.fromLocalFile(file_path))

            self.text_editor.setPlainText(content)
            self.text_editor.document().setModified(False)

            self.current_file = file_path
            file_name = Path(file_path).name
            self.setWindowTitle(f'{file_name} - Markdown 阅读器')
            self.file_label.setText(f'📄 {file_name}')

            self._add_recent_file(file_path)

            file_size = os.path.getsize(file_path)
            lines = content.count('\n') + 1
            self.status_label.setText(
                f'✅ {file_name} | {lines} 行 | {file_size/1024:.1f} KB'
            )

            if self.file_browser:
                self.file_browser.select_file(file_path)

        except Exception as e:
            self.status_label.setText(f'❌ 打开失败: {str(e)}')

    def save_file(self):
        if not self.current_file:
            return

        if not self.is_edit_mode:
            self.status_label.setText('ℹ️ 请先切换到编辑模式')
            return

        try:
            content = self.text_editor.toPlainText()
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)

            self.text_editor.document().setModified(False)
            self._raw_content = content

            html = self.renderer.render(content, self.current_file, self.current_theme)
            self.web_view.setHtml(html, QUrl.fromLocalFile(self.current_file))

            self.status_label.setText(f'✅ 已保存: {Path(self.current_file).name}')
        except Exception as e:
            self.status_label.setText(f'❌ 保存失败: {str(e)}')

    def save_file_as(self):
        if not self.current_file and not self.is_edit_mode:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, '另存为', '',
            'Markdown 文件 (*.md);;文本文件 (*.txt);;所有文件 (*)'
        )
        if not file_path:
            return

        try:
            content = self.text_editor.toPlainText() if self.is_edit_mode else self._raw_content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.current_file = file_path
            self.text_editor.document().setModified(False)
            self._raw_content = content

            file_name = Path(file_path).name
            self.setWindowTitle(f'{file_name} - Markdown 阅读器')
            self.file_label.setText(f'📄 {file_name}')
            self.status_label.setText(f'✅ 已保存: {file_name}')
        except Exception as e:
            self.status_label.setText(f'❌ 保存失败: {str(e)}')

    def reload_file(self):
        if self.current_file:
            self.open_file(self.current_file)

    def close_document(self):
        if self.is_edit_mode and self.text_editor.document().isModified():
            reply = QMessageBox.question(
                self, '保存更改',
                '当前文件已修改，是否保存？',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return

        if self.current_file:
            self.current_file = None
            self._raw_content = ''
            self.setWindowTitle('Markdown 阅读器')
            self.file_label.setText('未打开文件')
            self.status_label.setText('就绪')
            self.edit_status_label.setText('')

            if self.is_edit_mode:
                self.toggle_edit_mode(False)

            self._show_welcome()

    def export_html(self):
        if not self.current_file:
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, '导出 HTML', '',
            'HTML 文件 (*.html);;所有文件 (*)'
        )
        if not save_path:
            return

        try:
            content = self.text_editor.toPlainText() if self.is_edit_mode else self._raw_content
            html = self.renderer.render(content, self.current_file, self.current_theme)

            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html)

            self.status_label.setText(f'✅ 已导出: {save_path}')
        except Exception as e:
            self.status_label.setText(f'❌ 导出失败: {str(e)}')

    # ----------------------------------------------------------
    # 编辑模式
    # ----------------------------------------------------------

    def toggle_edit_mode(self, checked=None):
        if not self.current_file:
            self.status_label.setText('ℹ️ 请先打开文件')
            return

        if checked is None:
            checked = not self.is_edit_mode

        self.is_edit_mode = checked
        self.edit_btn.setChecked(checked)
        self.toggle_edit_action.setChecked(checked)

        if checked:
            self.web_view.hide()
            self.text_editor.show()
            self.text_editor.setPlainText(self._raw_content)
            self.text_editor.document().setModified(False)
            self.edit_status_label.setText('✏️ 编辑模式')
            self.status_label.setText('📝 已切换到编辑模式')
        else:
            if self.text_editor.document().isModified():
                reply = QMessageBox.question(
                    self, '保存更改',
                    '文件已修改，是否保存并刷新预览？',
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
                if reply == QMessageBox.Save:
                    self.save_file()
                elif reply == QMessageBox.Cancel:
                    self.is_edit_mode = True
                    self.edit_btn.setChecked(True)
                    self.toggle_edit_action.setChecked(True)
                    return

            self.text_editor.hide()
            self.web_view.show()
            self.edit_status_label.setText('')

            content = self.text_editor.toPlainText()
            html = self.renderer.render(content, self.current_file, self.current_theme)
            self.web_view.setHtml(html, QUrl.fromLocalFile(self.current_file))
            self.status_label.setText('👁️ 已切换到阅读模式')

    def _on_text_changed(self):
        if self.is_edit_mode:
            if self.text_editor.document().isModified():
                self.edit_status_label.setText('✏️ 编辑模式 *')
            else:
                self.edit_status_label.setText('✏️ 编辑模式')

    def _undo(self):
        if self.is_edit_mode:
            self.text_editor.undo()

    def _redo(self):
        if self.is_edit_mode:
            self.text_editor.redo()

    def _cut(self):
        if self.is_edit_mode:
            self.text_editor.cut()

    def _copy(self):
        if self.is_edit_mode:
            self.text_editor.copy()

    def _paste(self):
        if self.is_edit_mode:
            self.text_editor.paste()

    def _select_all(self):
        if self.is_edit_mode:
            self.text_editor.selectAll()

    # ----------------------------------------------------------
    # 文件浏览器
    # ----------------------------------------------------------

    def _init_file_browser(self, folder: str):
        if not self.file_browser:
            self.file_browser = FileBrowserPanel(self)
            self.file_browser.file_selected.connect(self.open_file)

        self.file_browser.set_root_path(folder)
        self.file_browser.show()
        self.file_browser.raise_()

    def toggle_file_browser(self):
        if not self.file_browser:
            self.open_folder_dialog()
            return

        if self.file_browser.isVisible():
            self.file_browser.hide()
        else:
            self.file_browser.show()
            self.file_browser.raise_()

    # ----------------------------------------------------------
    # 搜索
    # ----------------------------------------------------------

    def search_in_page(self):
        text = self.search_input.text().strip()
        if text:
            if self.is_edit_mode:
                cursor = self.text_editor.textCursor()
                cursor.movePosition(QTextCursor.Start)
                self.text_editor.setTextCursor(cursor)

                found = self.text_editor.find(text)
                if found:
                    self.status_label.setText(f'🔍 搜索: {text}')
                else:
                    self.status_label.setText(f'❌ 未找到: {text}')
            else:
                self.web_view.findText(text)
                self.status_label.setText(f'🔍 搜索: {text}')

    def _clear_search(self):
        self.search_input.clear()
        if not self.is_edit_mode:
            self.web_view.findText('')
        if self.current_file:
            self.status_label.setText(f'📄 {Path(self.current_file).name}')

    # ----------------------------------------------------------
    # 最近文件
    # ----------------------------------------------------------

    def _add_recent_file(self, file_path: str):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:20]
        self._update_recent_menu()

    def _update_recent_menu(self):
        self.recent_menu.clear()
        if not self.recent_files:
            action = QAction('（无）', self)
            action.setEnabled(False)
            self.recent_menu.addAction(action)
            return

        for i, path in enumerate(self.recent_files[:10]):
            if os.path.isfile(path):
                name = Path(path).name
                action = QAction(f'{i+1}. {name}', self)
                action.setToolTip(path)
                action.triggered.connect(lambda checked, p=path: self.open_file(p))
                self.recent_menu.addAction(action)

        self.recent_menu.addSeparator()
        clear_action = QAction('清除记录', self)
        clear_action.triggered.connect(self._clear_recent)
        self.recent_menu.addAction(clear_action)

    def _clear_recent(self):
        self.recent_files.clear()
        self._update_recent_menu()

    # ----------------------------------------------------------
    # 欢迎页面
    # ----------------------------------------------------------

    def _show_welcome(self):
        theme_css = THEMES[self.current_theme]['css_vars']
        bg = theme_css['--bg']
        text = theme_css['--text']
        heading = theme_css['--heading']
        link = theme_css['--link']

        welcome_html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>
    body {{
        font-family: -apple-system, 'Microsoft YaHei', sans-serif;
        display: flex; justify-content: center; align-items: center;
        min-height: 100vh; margin: 0;
        background: linear-gradient(135deg, {link} 0%, {heading} 100%);
        color: white;
    }}
    .container {{
        text-align: center; max-width: 600px; padding: 40px;
    }}
    h1 {{ font-size: 3em; margin-bottom: 0.3em; }}
    .emoji {{ font-size: 4em; }}
    p {{ font-size: 1.2em; opacity: 0.9; line-height: 1.6; }}
    .shortcuts {{
        background: rgba(255,255,255,0.15); border-radius: 12px;
        padding: 20px 30px; margin-top: 30px; text-align: left;
    }}
    .shortcuts h3 {{ margin-bottom: 15px; }}
    .row {{ display: flex; justify-content: space-between; padding: 6px 0; }}
    .key {{
        background: rgba(255,255,255,0.2); padding: 2px 10px;
        border-radius: 4px; font-family: monospace;
    }}
</style>
</head>
<body>
<div class="container">
    <div class="emoji">📝</div>
    <h1>Markdown 阅读器</h1>
    <p>支持代码高亮、表格、编辑模式、多主题配色</p>
    <div class="shortcuts">
        <h3>⌨️ 快捷键</h3>
        <div class="row"><span>打开文件</span><span class="key">Ctrl+O</span></div>
        <div class="row"><span>编辑模式</span><span class="key">Ctrl+E</span></div>
        <div class="row"><span>保存</span><span class="key">Ctrl+S</span></div>
        <div class="row"><span>搜索</span><span class="key">Ctrl+F</span></div>
        <div class="row"><span>文件浏览器</span><span class="key">Ctrl+B</span></div>
    </div>
</div>
</body></html>"""
        self.web_view.setHtml(welcome_html)

    # ----------------------------------------------------------
    # 关于
    # ----------------------------------------------------------

    def show_about(self):
        theme_list = '\n'.join([f'<li>{info["name"]}</li>' for info in THEMES.values()])
        QMessageBox.about(
            self, '关于 Markdown 阅读器',
            '<h2>📝 Markdown 阅读器</h2>'
            '<p>版本 2.1</p>'
            '<p>基于 PyQt5 + QWebEngineView 构建</p>'
            '<hr>'
            '<p><b>功能特性：</b></p>'
            '<ul>'
            '<li>Markdown 完整渲染（表格、代码高亮、折叠块）</li>'
            '<li>文件浏览器浮动面板</li>'
            '<li>编辑模式（支持保存）</li>'
            f'<li>多种舒适配色主题：{theme_list}</li>'
            '<li>页面内搜索</li>'
            '<li>导出 HTML</li>'
            '<li>最近打开文件记录</li>'
            '</ul>'
        )

    # ----------------------------------------------------------
    # 窗口事件
    # ----------------------------------------------------------

    def closeEvent(self, event):
        if self.is_edit_mode and self.text_editor.document().isModified():
            reply = QMessageBox.question(
                self, '保存更改',
                '当前文件已修改，是否保存？',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return

        self._save_settings()

        if self.file_browser:
            self.file_browser.close()

        super().closeEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith(('.md', '.markdown', '.txt')):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(('.md', '.markdown', '.txt')):
                self.open_file(file_path)
                break


# ============================================================
# 入口
# ============================================================

def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName('MarkdownReader')
    app.setOrganizationName('MDReader')

    font = QFont()
    font.setFamily('Microsoft YaHei')
    font.setPointSize(10)
    app.setFont(font)

    reader = MarkdownReader()
    reader.show()

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.isfile(file_path):
            reader.open_file(file_path)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
