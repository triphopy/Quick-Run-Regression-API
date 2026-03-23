@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_CMD="

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=py"
)

if not defined PYTHON_CMD (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    echo Could not find Python launcher. Please install Python or add it to PATH.
    exit /b 1
)

echo Using %PYTHON_CMD%
echo Installing or updating PyInstaller...
call %PYTHON_CMD% -m pip install pyinstaller
if errorlevel 1 (
    echo Failed to install PyInstaller.
    exit /b 1
)

echo Building SONIC launcher...
call %PYTHON_CMD% -m PyInstaller launcher.py ^
  --name SONIC ^
  --onedir ^
  --clean ^
  --noconfirm ^
  --add-data "app.py;." ^
  --add-data "assets;assets" ^
  --add-data "docs;docs" ^
  --add-data "robot;robot" ^
  --add-data "src;src" ^
  --hidden-import streamlit.web.cli ^
  --hidden-import robot ^
  --collect-all streamlit ^
  --collect-all robot

if errorlevel 1 (
    echo Build failed.
    exit /b 1
)

if not exist "dist\\SONIC" (
    echo Build output folder was not created.
    exit /b 1
)

if exist "packaging\\README-for-user.txt" (
    copy /Y "packaging\\README-for-user.txt" "dist\\SONIC\\README-for-user.txt" >nul
)

echo.
echo Build completed successfully.
echo Output folder: %CD%\dist\SONIC
echo Executable: %CD%\dist\SONIC\SONIC.exe

endlocal
