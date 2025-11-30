@echo off
echo Deploying Billabong Plugin to QGIS...

REM Define Source and Destination
SET "SOURCE_DIR=%~dp0"
SET "DEST_DIR=%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\Billabong"

REM Create destination directory if it doesn't exist
if not exist "%DEST_DIR%" mkdir "%DEST_DIR%"

REM Robocopy options:
REM /E - Copy subdirectories, including empty ones.
REM /PURGE - Delete destination files/directories that no longer exist in source.
REM /XD - Exclude directories (git, venv, etc)
REM /XF - Exclude files (git files, python cache)
robocopy "%SOURCE_DIR%." "%DEST_DIR%" /E /PURGE /IS /XD .git .idea __pycache__ .vscode venv /XF .gitignore deploy.bat *.pyc

echo.
echo Deployment Complete! 
echo Please restart QGIS or use 'Plugin Reloader' to see changes.
pause
