@echo off
chcp 65001 >nul

if not exist "venv\Scripts\pythonw.exe" (
    echo Rode "instalar.bat" primeiro!
    pause
    exit /b 1
)

start "" venv\Scripts\pythonw.exe app.py
