@echo off
setlocal
cd /d "%~dp0"
title MAYA AI V100
if not exist ".venv\Scripts\python.exe" (
 echo Please run INSTALL_MAYA.bat first.
 pause
 exit /b 1
)
.venv\Scripts\python.exe main.py
if errorlevel 1 (
 echo.
 echo MAYA stopped with an error. Send a screenshot of this window.
 pause
)
