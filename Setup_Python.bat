@echo off
title IntruderGuard (Python) Setup

echo ===========================================
echo      IntruderGuard - Python Setup
echo ===========================================
echo.

:: Check for python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not added to your PATH!
    echo Please install Python 3 from python.org and try again.
    pause
    exit /b
)

:: Check if requirements are already installed to avoid unnecessary pings
python -c "import customtkinter, cv2, PIL" >nul 2>&1
if %errorlevel% equ 0 (
    echo Dependencies already verified. Starting IntruderGuard...
    goto :start_app
)

echo Required libraries are missing. Checking for updates...
echo (If this hangs, please check your internet connection)

echo Upgrading pip...
python -m pip install --upgrade pip --quiet --no-warn-script-location >nul 2>&1

echo Installing required Python packages...
python -m pip install -r requirements.txt --quiet --no-warn-script-location
if %errorlevel% neq 0 (
    echo.
    echo Failed to install dependencies! Please check your internet connection 
    echo or run this script in an administrative command prompt.
    pause
    exit /b
)

:start_app
echo.
echo Starting IntruderGuard Manager...
echo.
python intruder_guard.py
