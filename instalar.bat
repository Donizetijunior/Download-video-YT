@echo off
chcp 65001 >nul
title YouTube Downloader - Instalador

echo ============================================
echo    YouTube Downloader - Instalacao
echo ============================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Baixe em: https://www.python.org/downloads/
    echo IMPORTANTE: Marque "Add Python to PATH" na instalacao.
    pause
    exit /b 1
)
echo [OK] Python encontrado.

:: Verificar ffmpeg
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [AVISO] ffmpeg nao encontrado. Instalando via winget...
    winget install ffmpeg --accept-package-agreements --accept-source-agreements
    echo.
    echo ffmpeg instalado. Feche e abra este arquivo novamente para continuar.
    pause
    exit /b 0
)
echo [OK] ffmpeg encontrado.

:: Criar venv
if not exist "venv" (
    echo.
    echo Criando ambiente virtual...
    python -m venv venv
)
echo [OK] Ambiente virtual pronto.

:: Instalar dependencias
echo.
echo Instalando dependencias...
venv\Scripts\pip.exe install -r requirements.txt -q
echo [OK] Dependencias instaladas.

echo.
echo ============================================
echo    Instalacao concluida!
echo    Use "iniciar.bat" para abrir o app.
echo ============================================
pause
