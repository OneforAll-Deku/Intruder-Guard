@echo off
title IntruderGuard Setup
setlocal

cd /d "%~dp0"

:: ──────────────────────────────────────────────
:: Step 1: Check Python is installed
:: ──────────────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Download and install from: https://python.org
    pause
    exit /b 1
)

:: ──────────────────────────────────────────────
:: Step 2: Check if required packages are present
:: If not, install from requirements.txt
:: ──────────────────────────────────────────────
python -c "import customtkinter, cv2, PIL" >nul 2>&1
if %errorlevel% equ 0 goto :sync_and_launch

echo [INFO] Installing required dependencies...
python -m pip install -r requirements.txt --quiet --no-warn-script-location
if %errorlevel% neq 0 (
    echo [ERROR] Dependency install failed. Check your internet connection.
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully.

:: ──────────────────────────────────────────────
:: Step 3: Sync latest intruder_guard.py to the
:: install directory (C:\ProgramData\IntruderGuard)
:: so the Task Scheduler background worker always
:: runs the most up-to-date version of the script.
:: ──────────────────────────────────────────────
:sync_and_launch
set INSTALL_DIR=C:\ProgramData\IntruderGuard
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo [INFO] Syncing latest script and assets to %INSTALL_DIR%...
copy /y "%~dp0intruder_guard.py" "%INSTALL_DIR%\intruder_guard.py" >nul
copy /y "%~dp0Intruder Guard icon.ico" "%INSTALL_DIR%\Intruder Guard icon.ico" >nul
if %errorlevel% equ 0 (
    echo [OK] Script and assets synced — background worker will use the latest version.
) else (
    echo [WARN] Could not sync assets to %INSTALL_DIR%. Run as Administrator if needed.
)

:: ──────────────────────────────────────────────
:: Step 4: Launch the main GUI app
:: (Python will request UAC elevation internally
::  via ShellExecuteW if not already admin)
:: ──────────────────────────────────────────────
echo [INFO] Launching IntruderGuard...
python "%~dp0intruder_guard.py"
