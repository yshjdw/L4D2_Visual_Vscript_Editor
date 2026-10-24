@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -3 -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo First run: installing PySide6 dependencies...
    py -3 -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Installation failed. Check Python version and internet connectivity.
        pause
        exit /b 1
    )
)
py -3 app.py
if errorlevel 1 (
    echo Startup failed. See README.md.
    pause
    exit /b 1
)
exit /b 0
