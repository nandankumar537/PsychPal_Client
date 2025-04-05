@echo off
title PsychPal - Install Dependencies
echo PsychPal Dependency Installer
echo ============================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
  echo Python is not installed or not in your PATH.
  echo Please install Python 3.8 or later from https://www.python.org/downloads/
  echo Make sure to check "Add Python to PATH" during installation.
  echo.
  pause
  exit /b 1
)

REM Navigate to app directory
cd %~dp0\PsychPal

REM Install dependencies
echo Installing required packages...
pip install -r requirements.txt

if %errorlevel% neq 0 (
  echo.
  echo Error installing packages.
  echo Please check your internet connection and try again.
  pause
  exit /b 1
)

echo.
echo Dependencies successfully installed!
echo.
echo You can now run PsychPal by double-clicking on "Start-PsychPal.bat"
echo.
pause
