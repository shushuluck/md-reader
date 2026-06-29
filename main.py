"""
Markdown 阅读器 - PyQt5 版本
功能：渲染 .md 文件，支持代码高亮、目录树、搜索、主题切换
"""

import sys
import os
import json
import markdown
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTreeView,
    QFileSystemModel, QSplitter, QStatusBar, QMenuBar,
    QAction, QToolBar, QLineEdit, QLabel, QWidget,
    QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox,
    QShortcut, QFrame
)
from PyQt5.QtCore import (
    Qt, QUrl, QDir, QSize, QSettings, QTimer,
    QFileInfo, pyqtSignal
)
from PyQt5.QtGui import (
    QIcon, QKeySequence, QFont, QColor, QPalette
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView, QWebEngineSettings, QWebEnginePage
)
from PyQt5.QtWebChannel import QWebChannel


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

    def render(self, md_text: str, file_path: str = '') -> str:
        """将 Markdown 转换为完整 HTML 页面"""
        self.md.reset()
        body = self.md.convert(md_text)

        # 检测是否包含折叠详情块
        has_details = '<details>' in body

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {{
            --bg: #ffffff;
            --text: #1a1a2e;
            --text-secondary: #555;
            --heading: #16213e;
            --link: #0f3460;
            --link-hover: #e94560;
            --code-bg: #f5f5f5;
            --code-text: #d63384;
            --pre-bg: #282c34;
            --pre-text: #abb2bf;
            --border: #e0e0e0;
            --table-header: #f0f0f0;
            --table-stripe: #fafafa;
            --blockquote-border: #e94560;
            --blockquote-bg: #fef6f8;
            --highlight-bg: #fff3cd;
            --shadow: rgba(0,0,0,0.08);
        }}

        [data-theme="dark"] {{
            --bg: #1a1a2e;
            --text: #e0e0e0;
            --text-secondary: #aaa;
            --heading: #eee;
            --link: #64b5f6;
            --link-hover: #e94560;
            --code-bg: #2d2d44;
            --code-text: #f08d49;
            --pre-bg: #16161e;
            --pre-text: #abb2bf;
            --border: #333;
            --table-header: #252540;
            --table-stripe: #1e1e35;
            --blockquote-border: #e94560;
            --blockquote-bg: #2a1a20;
            --highlight-bg: #3a3000;
            --shadow: rgba(0,0,0,0.3);
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
                // 通过 pywebchannel 调用 Python 方法（如果启用）
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
                # 外部链接用系统浏览器打开
                import webbrowser
                webbrowser.open(url.toString())
                return False
            elif url.scheme() == 'file':
                # 本地 md 文件在阅读器中打开
                file_path = url.toLocalFile()
                if file_path.endswith('.md') and self._main_window:
                    self._main_window.open_file(file_path)
                    return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


# ============================================================
# 主窗口
# ============================================================

class MarkdownReader(QMainWindow):
    """Markdown 阅读器主窗口"""

    # 主题样式表
    THEME_STYLES = {
        'light': """
            QMainWindow, QWidget { background: #f8f9fa; color: #1a1a2e; }
            QTreeView {
                background: #ffffff; color: #1a1a2e;
                border: 1px solid #e0e0e0; border-radius: 4px;
                font-size: 13px;
            }
            QTreeView::item { padding: 4px 8px; }
            QTreeView::item:selected { background: #0f3460; color: white; }
            QTreeView::item:hover { background: #e8f0fe; }
            QToolBar {
                background: #ffffff; border-bottom: 1px solid #e0e0e0;
                padding: 4px; spacing: 6px;
            }
            QToolBar QToolButton {
                background: transparent; border: 1px solid transparent;
                border-radius: 4px; padding: 6px 12px; font-size: 13px;
            }
            QToolBar QToolButton:hover { background: #e8f0fe; border-color: #ccc; }
            QLineEdit {
                background: white; border: 1px solid #ddd; border-radius: 4px;
                padding: 6px 10px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #0f3460; }
            QStatusBar { background: #ffffff; border-top: 1px solid #e0e0e0; font-size: 12px; }
            QMenuBar { background: #ffffff; border-bottom: 1px solid #e0e0e0; }
            QMenuBar::item:selected { background: #e8f0fe; }
            QMenu { background: white; border: 1px solid #ddd; }
            QMenu::item:selected { background: #e8f0fe; }
            QSplitter::handle { background: #e0e0e0; width: 3px; }
        """,
        'dark': """
            QMainWindow, QWidget { background: #16161e; color: #e0e0e0; }
            QTreeView {
                background: #1a1a2e; color: #e0e0e0;
                border: 1px solid #333; border-radius: 4px;
                font-size: 13px;
            }
            QTreeView::item { padding: 4px 8px; }
            QTreeView::item:selected { background: #e94560; color: white; }
            QTreeView::item:hover { background: #252540; }
            QToolBar {
                background: #1a1a2e; border-bottom: 1px solid #333;
                padding: 4px; spacing: 6px;
            }
            QToolBar QToolButton {
                background: transparent; border: 1px solid transparent;
                border-radius: 4px; padding: 6px 12px; font-size: 13px;
                color: #e0e0e0;
            }
            QToolBar QToolButton:hover { background: #252540; border-color: #444; }
            QLineEdit {
                background: #252540; border: 1px solid #444; border-radius: 4px;
                padding: 6px 10px; font-size: 13px; color: #e0e0e0;
            }
            QLineEdit:focus { border-color: #e94560; }
            QStatusBar { background: #1a1a2e; border-top: 1px solid #333; font-size: 12px; }
            QMenuBar { background: #1a1a2e; border-bottom: 1px solid #333; color: #e0e0e0; }
            QMenuBar::item:selected { background: #252540; }
            QMenu { background: #1a1a2e; border: 1px solid #444; color: #e0e0e0; }
            QMenu::item:selected { background: #252540; }
            QSplitter::handle { background: #333; width: 3px; }
        """
    }

    def __init__(self):
        super().__init__()

        # 状态
        self.current_file = None
        self.renderer = MarkdownRenderer()
        self.settings = QSettings('MDReader', 'MarkdownReader')
        self.recent_files = []
        self.current_theme = 'light'

        # 初始化
        self._init_window()
        self._init_menu()
        self._init_toolbar()
        self._init_ui()
        self._init_shortcuts()
        self._load_settings()

    def _init_window(self):
        """初始化窗口属性"""
        self.setWindowTitle('Markdown 阅读器')
        self.setMinimumSize(900, 600)
        self.resize(1200, 800)

        # 窗口图标（使用文字图标）
        self.setWindowIcon(self.style().standardIcon(
            self.style().SP_FileDialogDetailedView
        ))

    def _init_menu(self):
        """初始化菜单栏"""
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

        # 最近文件子菜单
        self.recent_menu = file_menu.addMenu('最近打开(&R)')
        self._update_recent_menu()

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

        # 视图菜单
        view_menu = menubar.addMenu('视图(&V)')

        theme_action = QAction('切换主题(&T)', self)
        theme_action.setShortcut(QKeySequence('Ctrl+T'))
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)

        view_menu.addSeparator()

        toggle_tree_action = QAction('显示/隐藏目录树(&S)', self)
        toggle_tree_action.setShortcut(QKeySequence('Ctrl+B'))
        toggle_tree_action.triggered.connect(self.toggle_tree)
        view_menu.addAction(toggle_tree_action)

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
        """初始化工具栏"""
        toolbar = QToolBar('工具栏')
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # 打开按钮
        open_btn = QAction('📂 打开', self)
        open_btn.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_btn)

        # 刷新按钮
        reload_btn = QAction('🔄 刷新', self)
        reload_btn.triggered.connect(self.reload_file)
        toolbar.addAction(reload_btn)

        # 关闭按钮
        close_btn = QAction('✖ 关闭', self)
        close_btn.triggered.connect(self.close_document)
        toolbar.addAction(close_btn)

        toolbar.addSeparator()

        # 搜索框
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

        # 主题切换
        theme_btn = QAction('🌓 主题', self)
        theme_btn.triggered.connect(self.toggle_theme)
        toolbar.addAction(theme_btn)

        # 弹簧
        spacer = QWidget()
        spacer.setSizePolicy(
            spacer.sizePolicy().horizontalPolicy(),
            spacer.sizePolicy().verticalPolicy()
        )
        toolbar.addWidget(spacer)

        # 文件名标签
        self.file_label = QLabel('未打开文件')
        self.file_label.setStyleSheet('font-size: 12px; color: #888; padding: 0 10px;')
        toolbar.addWidget(self.file_label)

    def _init_ui(self):
        """初始化主界面"""
        # 主分割器（左右布局）
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(3)

        # 左侧：文件树
        self.tree_frame = QFrame()
        tree_layout = QVBoxLayout(self.tree_frame)
        tree_layout.setContentsMargins(0, 0, 0, 0)

        # 文件系统模型
        self.fs_model = QFileSystemModel()
        self.fs_model.setReadOnly(True)
        self.fs_model.setNameFilterDisables(False)
        self.fs_model.setNameFilters(['*.md', '*.markdown', '*.txt'])

        # 文件树视图
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.fs_model)
        self.tree_view.setColumnHidden(1, True)  # 隐藏大小列
        self.tree_view.setColumnHidden(2, True)  # 隐藏类型列
        self.tree_view.setColumnHidden(3, True)  # 隐藏修改日期列
        self.tree_view.setHeaderHidden(True)
        self.tree_view.clicked.connect(self._on_tree_clicked)
        self.tree_view.setAnimated(True)

        tree_layout.addWidget(self.tree_view)
        self.splitter.addWidget(self.tree_frame)

        # 右侧：WebView
        self.web_view = QWebEngineView()
        self.web_page = MarkdownWebPage(self)
        self.web_view.setPage(self.web_page)

        # WebView 设置
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, False)
        settings.setFontSize(QWebEngineSettings.DefaultFontSize, 16)

        self.splitter.addWidget(self.web_view)

        # 分割器比例
        self.splitter.setSizes([250, 950])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.setCentralWidget(self.splitter)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel('就绪')
        self.status_bar.addWidget(self.status_label)

        # 显示欢迎页面
        self._show_welcome()

    def _init_shortcuts(self):
        """初始化快捷键"""
        # Ctrl+F 聚焦搜索框
        QShortcut(QKeySequence.Find, self, lambda: self.search_input.setFocus())

        # Ctrl+W 关闭文档
        QShortcut(QKeySequence('Ctrl+W'), self, self.close_document)

        # Escape 清除搜索
        QShortcut(QKeySequence(Qt.Key_Escape), self, self._clear_search)

    def _load_settings(self):
        """加载设置"""
        # 窗口几何
        geom = self.settings.value('geometry')
        if geom:
            self.restoreGeometry(geom)

        # 窗口状态
        state = self.settings.value('windowState')
        if state:
            self.restoreState(state)

        # 分割器状态
        splitter = self.settings.value('splitter')
        if splitter:
            self.splitter.restoreState(splitter)

        # 主题
        self.current_theme = self.settings.value('theme', 'light')
        self._apply_theme()

        # 最近文件
        self.recent_files = self.settings.value('recent_files', [])

        # 上次打开的文件夹
        last_folder = self.settings.value('last_folder', '')
        if last_folder and os.path.isdir(last_folder):
            self._set_tree_root(last_folder)

        # 上次打开的文件
        last_file = self.settings.value('last_file', '')
        if last_file and os.path.isfile(last_file):
            QTimer.singleShot(100, lambda: self.open_file(last_file))

    def _save_settings(self):
        """保存设置"""
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('windowState', self.saveState())
        self.settings.setValue('splitter', self.splitter.saveState())
        self.settings.setValue('theme', self.current_theme)
        self.settings.setValue('recent_files', self.recent_files)
        if self.current_file:
            self.settings.setValue('last_file', self.current_file)
            self.settings.setValue('last_folder', str(Path(self.current_file).parent))

    # ----------------------------------------------------------
    # 文件操作
    # ----------------------------------------------------------

    def open_file_dialog(self):
        """打开文件对话框"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '打开 Markdown 文件', '',
            'Markdown 文件 (*.md *.markdown *.txt);;所有文件 (*)'
        )
        if file_path:
            self.open_file(file_path)

    def open_folder_dialog(self):
        """打开文件夹对话框"""
        folder = QFileDialog.getExistingDirectory(self, '选择文件夹')
        if folder:
            self._set_tree_root(folder)

    def open_file(self, file_path: str):
        """打开并渲染 Markdown 文件"""
        file_path = os.path.abspath(file_path)
        if not os.path.isfile(file_path):
            self.status_label.setText(f'❌ 文件不存在: {file_path}')
            return

        try:
            # 尝试多种编码读取
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

            # 渲染 HTML
            html = self.renderer.render(content, file_path)

            # 设置到 WebView
            self.web_view.setHtml(html, QUrl.fromLocalFile(file_path))

            # 更新状态
            self.current_file = file_path
            file_name = Path(file_path).name
            self.setWindowTitle(f'{file_name} - Markdown 阅读器')
            self.file_label.setText(f'📄 {file_name}')

            # 更新最近文件
            self._add_recent_file(file_path)

            # 文件信息
            file_size = os.path.getsize(file_path)
            lines = content.count('\n') + 1
            self.status_label.setText(
                f'✅ {file_name} | {lines} 行 | {file_size/1024:.1f} KB'
            )

            # 更新文件树选中状态
            self._select_in_tree(file_path)

        except Exception as e:
            self.status_label.setText(f'❌ 打开失败: {str(e)}')

    def reload_file(self):
        """重新加载当前文件"""
        if self.current_file:
            self.open_file(self.current_file)

    def close_document(self):
        """关闭当前文档，回到欢迎页面"""
        if self.current_file:
            self.current_file = None
            self.setWindowTitle('Markdown 阅读器')
            self.file_label.setText('未打开文件')
            self.status_label.setText('就绪')
            self._show_welcome()

    def export_html(self):
        """导出为 HTML 文件"""
        if not self.current_file:
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, '导出 HTML', '',
            'HTML 文件 (*.html);;所有文件 (*)'
        )
        if not save_path:
            return

        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                content = f.read()
            html = self.renderer.render(content, self.current_file)

            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html)

            self.status_label.setText(f'✅ 已导出: {save_path}')
        except Exception as e:
            self.status_label.setText(f'❌ 导出失败: {str(e)}')

    # ----------------------------------------------------------
    # 文件树
    # ----------------------------------------------------------

    def _set_tree_root(self, folder: str):
        """设置文件树根目录"""
        index = self.fs_model.setRootPath(folder)
        self.tree_view.setRootIndex(index)
        self.tree_view.scrollToTop()

    def _on_tree_clicked(self, index):
        """文件树点击事件"""
        file_path = self.fs_model.filePath(index)
        if os.path.isfile(file_path) and file_path.endswith(('.md', '.markdown', '.txt')):
            self.open_file(file_path)

    def _select_in_tree(self, file_path: str):
        """在文件树中选中指定文件"""
        index = self.fs_model.index(file_path)
        if index.isValid():
            self.tree_view.setCurrentIndex(index)
            self.tree_view.scrollTo(index)

    # ----------------------------------------------------------
    # 搜索
    # ----------------------------------------------------------

    def search_in_page(self):
        """在页面中搜索文本"""
        text = self.search_input.text().strip()
        if text:
            self.web_view.findText(text)
            self.status_label.setText(f'🔍 搜索: {text}')

    def _clear_search(self):
        """清除搜索"""
        self.search_input.clear()
        self.web_view.findText('')
        if self.current_file:
            self.status_label.setText(f'📄 {Path(self.current_file).name}')

    # ----------------------------------------------------------
    # 主题
    # ----------------------------------------------------------

    def toggle_theme(self):
        """切换主题"""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self._apply_theme()
        # 重新渲染当前文件以应用 WebView 内部主题
        if self.current_file:
            self.reload_file()

    def _apply_theme(self):
        """应用主题样式"""
        style = self.THEME_STYLES.get(self.current_theme, '')
        self.setStyleSheet(style)

        # 更新 WebView 背景
        bg_color = '#1a1a2e' if self.current_theme == 'dark' else '#ffffff'
        self.web_view.setStyleSheet(f'background: {bg_color};')

    # ----------------------------------------------------------
    # 显示/隐藏
    # ----------------------------------------------------------

    def toggle_tree(self):
        """显示/隐藏文件树"""
        self.tree_frame.setVisible(not self.tree_frame.isVisible())

    # ----------------------------------------------------------
    # 最近文件
    # ----------------------------------------------------------

    def _add_recent_file(self, file_path: str):
        """添加到最近文件列表"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:20]  # 最多保留 20 个
        self._update_recent_menu()

    def _update_recent_menu(self):
        """更新最近文件菜单"""
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
        """清除最近文件记录"""
        self.recent_files.clear()
        self._update_recent_menu()

    # ----------------------------------------------------------
    # 欢迎页面
    # ----------------------------------------------------------

    def _show_welcome(self):
        """显示欢迎页面"""
        welcome_html = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>
    body {
        font-family: -apple-system, 'Microsoft YaHei', sans-serif;
        display: flex; justify-content: center; align-items: center;
        min-height: 100vh; margin: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .container {
        text-align: center; max-width: 600px; padding: 40px;
    }
    h1 { font-size: 3em; margin-bottom: 0.3em; }
    .emoji { font-size: 4em; }
    p { font-size: 1.2em; opacity: 0.9; line-height: 1.6; }
    .shortcuts {
        background: rgba(255,255,255,0.15); border-radius: 12px;
        padding: 20px 30px; margin-top: 30px; text-align: left;
    }
    .shortcuts h3 { margin-bottom: 15px; }
    .row { display: flex; justify-content: space-between; padding: 6px 0; }
    .key {
        background: rgba(255,255,255,0.2); padding: 2px 10px;
        border-radius: 4px; font-family: monospace;
    }
</style>
</head>
<body>
<div class="container">
    <div class="emoji">📝</div>
    <h1>Markdown 阅读器</h1>
    <p>支持代码高亮、表格、目录树、暗色主题</p>
    <div class="shortcuts">
        <h3>⌨️ 快捷键</h3>
        <div class="row"><span>打开文件</span><span class="key">Ctrl+O</span></div>
        <div class="row"><span>打开文件夹</span><span class="key">Ctrl+Shift+O</span></div>
        <div class="row"><span>搜索</span><span class="key">Ctrl+F</span></div>
        <div class="row"><span>切换主题</span><span class="key">Ctrl+T</span></div>
        <div class="row"><span>目录树</span><span class="key">Ctrl+B</span></div>
        <div class="row"><span>重新加载</span><span class="key">F5</span></div>
        <div class="row"><span>放大/缩小</span><span class="key">Ctrl +/-</span></div>
    </div>
</div>
</body></html>"""
        self.web_view.setHtml(welcome_html)

    # ----------------------------------------------------------
    # 关于
    # ----------------------------------------------------------

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, '关于 Markdown 阅读器',
            '<h2>📝 Markdown 阅读器</h2>'
            '<p>版本 1.0</p>'
            '<p>基于 PyQt5 + QWebEngineView 构建</p>'
            '<hr>'
            '<p><b>功能特性：</b></p>'
            '<ul>'
            '<li>Markdown 完整渲染（表格、代码高亮、折叠块）</li>'
            '<li>文件目录树浏览</li>'
            '<li>亮色/暗色主题切换</li>'
            '<li>页面内搜索</li>'
            '<li>导出 HTML</li>'
            '<li>最近打开文件记录</li>'
            '</ul>'
        )

    # ----------------------------------------------------------
    # 窗口事件
    # ----------------------------------------------------------

    def closeEvent(self, event):
        """关闭窗口时保存设置"""
        self._save_settings()
        super().closeEvent(event)

    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith(('.md', '.markdown', '.txt')):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event):
        """拖放事件"""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(('.md', '.markdown', '.txt')):
                self.open_file(file_path)
                break


# ============================================================
# 入口
# ============================================================

def main():
    # 高 DPI 支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName('MarkdownReader')
    app.setOrganizationName('MDReader')

    # 全局字体
    font = QFont()
    font.setFamily('Microsoft YaHei')
    font.setPointSize(10)
    app.setFont(font)

    # 创建并显示主窗口
    reader = MarkdownReader()
    reader.show()

    # 如果命令行传入了文件，直接打开
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.isfile(file_path):
            reader.open_file(file_path)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
