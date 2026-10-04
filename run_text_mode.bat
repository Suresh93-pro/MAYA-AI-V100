@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (echo Please run INSTALL_MAYA.bat first.&pause&exit /b 1)
.venv\Scripts\python.exe -c "from core.config import load_config; from core.launcher import WindowsLauncher; from core.commands import CommandEngine; c=load_config(); e=CommandEngine(c,WindowsLauncher(c)); print('MAYA text mode. Type commands; Ctrl+C to exit.');\nimport sys; [e.handle(x) for x in sys.stdin]"
pause
