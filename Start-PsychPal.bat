@echo off
title PsychPal Launcher
echo Starting PsychPal...
echo This window will remain open while the application is running.
echo Please do not close this window manually.
echo.

REM Navigate to app directory
cd %~dp0

REM Run the application
python desktop_app.py
    
if %errorlevel% neq 0 (
  echo.
  echo An error occurred while running PsychPal.
  echo Error code: %errorlevel%
  pause
)