@echo off
echo ========================================
echo   MDReader - Build and Package
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.9+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Install dependencies
echo [1/4] Installing Python packages...
pip install PyQt5 PyQtWebEngine markdown Pygments pyinstaller -q
if errorlevel 1 (
    echo [INFO] Using mirror...
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple PyQt5 PyQtWebEngine markdown Pygments pyinstaller -q
)
echo      Done.
echo.

:: PyInstaller build
echo [2/4] Building exe (2-5 min)...
python -m PyInstaller --noconfirm --onedir --windowed --name "MDReader" --icon "icon.ico" --hidden-import PyQt5.QtWebEngineWidgets --hidden-import PyQt5.QtWebChannel --hidden-import PyQt5.QtWebEngineCore --collect-all PyQt5.QtWebEngineWidgets --collect-all PyQt5.QtWebEngine main.py
if errorlevel 1 (
    echo [ERROR] PyInstaller failed
    pause
    exit /b 1
)
echo      Build done.
echo.

:: Check Inno Setup
echo [3/4] Checking Inno Setup...
set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"

if "%ISCC%"=="" (
    echo.
    echo [INFO] Inno Setup 6 not found.
    echo        Install it from: https://jrsoftware.org/isinfo.php
    echo.
    echo        You can still use the exe directly:
    echo        dist\MDReader\MDReader.exe
    echo.
    pause
    exit /b 0
)
echo      Found: %ISCC%
echo.

:: Build installer
echo [4/4] Creating installer...
"%ISCC%" setup.iss
if errorlevel 1 (
    echo [ERROR] Installer build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo   All done!
echo ========================================
echo.
echo   Installer: installer_output\MDReader_Setup_1.0.0.exe
echo.
pause
