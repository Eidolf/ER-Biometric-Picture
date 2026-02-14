@echo off
REM run.bat - Helper script to launch PassPhotoCheck

cd /d "%~dp0"

IF EXIST ".venv\Scripts\activate.bat" (
    CALL .venv\Scripts\activate.bat
) ELSE (
    ECHO Error: Virtual environment not found in .venv
    ECHO Please run: python -m venv .venv
    ECHO Then activate and install requirements.
    PAUSE
    EXIT /B 1
)

SET PYTHONPATH=.
python app/main.py
PAUSE
