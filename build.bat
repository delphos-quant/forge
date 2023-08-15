@echo off

REM Check if PyInstaller is installed
pip list | findstr /C:"pyinstaller" 1>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Create the executable using PyInstaller
echo Creating executable with PyInstaller...
pyinstaller --onefile --name=strategy_manager orchestrator\server.py

REM Check if the executable generation was successful
if not exist ".\dist\strategy_manager.exe" (
    echo Error: Failed to create the executable.
    exit /b 1
) else (
    echo Build process completed! You can run the application using .\dist\strategy_manager.exe.
)
