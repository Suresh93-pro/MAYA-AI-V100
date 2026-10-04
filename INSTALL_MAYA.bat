@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title MAYA AI V100 - FINAL INSTALLER
color 0B
cls
echo ============================================================
echo                 MAYA AI V100 - FINAL
echo ============================================================
echo.
set "PY="
for %%P in (py python python3) do if not defined PY (where %%P >nul 2>&1 && set "PY=%%P")
if not defined PY goto NOPY
for /f "tokens=2" %%V in ('"%PY%" --version 2^>^&1') do set "VER=%%V"
echo Python detected: %VER%
echo.
if not exist ".venv\Scripts\python.exe" (
  echo Creating private environment...
  "%PY%" -m venv .venv
  if errorlevel 1 goto FAIL
)
echo Upgrading pip...
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto FAIL
echo.
echo Installing MAYA components...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto FAIL
echo.
echo Checking Python files...
.venv\Scripts\python.exe -m py_compile main.py
if errorlevel 1 goto FAIL
for %%F in (core\*.py) do (
  .venv\Scripts\python.exe -m py_compile "%%~fF"
  if errorlevel 1 goto FAIL
)
if not exist "logs" mkdir logs
>".installed" echo MAYA V100 installed %DATE% %TIME%
echo.
echo ============================================================
echo              MAYA V100 INSTALL COMPLETE
 echo ============================================================
echo.
echo Double-click START_MAYA.bat to launch MAYA.
echo.
pause
exit /b 0
:NOPY
echo Python was not found on PATH.
echo Install Python from https://www.python.org/downloads/
echo Then reopen this installer.
pause
exit /b 1
:FAIL
echo.
echo ============================================================
echo INSTALLATION FAILED
 echo ============================================================
echo Read the error above and send me a screenshot.
pause
exit /b 1
