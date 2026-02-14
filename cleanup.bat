@echo off
REM cleanup.bat - Removes dev environment, caches, and build artifacts
echo Cleaning up project...

REM Remove Virtual Environment
IF EXIST ".venv" (
    echo Removing .venv...
    rmdir /s /q .venv
)

REM Remove PyInstaller Artifacts
IF EXIST "build" (
    echo Removing build/...
    rmdir /s /q build
)
IF EXIST "dist" (
    echo Removing dist/...
    rmdir /s /q dist
)

REM Remove Pytest Cache
IF EXIST ".pytest_cache" (
    echo Removing .pytest_cache...
    rmdir /s /q .pytest_cache
)

REM Remove __pycache__ (Recursive)
echo Removing __pycache__ directories...
FOR /d /r . %%d IN (__pycache__) DO @IF EXIST "%%d" rd /s /q "%%d"

echo Cleanup complete.
PAUSE
