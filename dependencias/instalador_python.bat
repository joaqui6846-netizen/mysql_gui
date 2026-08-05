@echo off
setlocal enableextensions enabledelayedexpansion

echo ============================================
echo   Iniciando descarga e instalacion de Python
echo ============================================
echo.

:: Configuración de variables
set "PYTHON_VER=3.12.2"
set "URL=https://www.python.org/ftp/python/%PYTHON_VER%/python-%PYTHON_VER%-amd64.exe"
set "INSTALLER=%TEMP%\python_installer.exe"

:: 1. Descargar el instalador mediante PowerShell
echo Descargando Python %PYTHON_VER%...
powershell -Command "Invoke-WebRequest -Uri '%URL%' -OutFile '%INSTALLER%'"

if not exist "%INSTALLER%" (
    echo Error: No se pudo descargar el archivo de instalacion.
    pause
    exit /b 1
)

:: 2. Ejecutar la instalacion en modo silencioso
echo Instalando Python... Por favor espera unos momentos...
"%INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

:: 3. Limpieza y comprobacion
del "%INSTALLER%"

echo.
echo ============================================
echo   Instalacion completada con exito.
echo ============================================
echo.
echo Nota: Reinicia el Símbolo del sistema para comprobar que 'python' funciona.
pause