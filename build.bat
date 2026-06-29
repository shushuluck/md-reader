@echo off
chcp 65001 >nul
echo ========================================
echo   Markdown 阅读器 - Windows 打包脚本
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

:: 安装依赖
echo [1/3] 安装依赖...
pip install -r requirements.txt pyinstaller -q
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

:: 打包
echo [2/3] 正在打包为 exe...
pyinstaller ^
    --noconfirm ^
    --onedir ^
    --windowed ^
    --name "MDReader" ^
    --icon NUL ^
    --add-data "README.md;." ^
    --hidden-import PyQt5.QtWebEngineWidgets ^
    --hidden-import PyQt5.QtWebChannel ^
    --hidden-import PyQt5.QtWebEngineCore ^
    --hidden-import markdown ^
    --hidden-import pygments ^
    --collect-all PyQt5.QtWebEngineWidgets ^
    --collect-all PyQt5.QtWebEngine ^
    main.py

if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo [3/3] 打包完成！
echo 输出目录: dist\MDReader\
echo 可执行文件: dist\MDReader\MDReader.exe
echo.

:: 创建快捷方式说明
echo 使用方法:
echo   1. 将 dist\MDReader 文件夹复制到任意位置
echo   2. 双击 MDReader.exe 启动
echo   3. 可将 .md 文件拖拽到窗口打开
echo   4. 可右键 .md 文件 → 打开方式 → 选择 MDReader.exe
echo.
pause
