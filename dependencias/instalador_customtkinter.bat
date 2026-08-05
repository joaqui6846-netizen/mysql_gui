@echo off
title Instalador de CustomTkinter

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta agregado al PATH.
    echo Asegurate de instalar Python marcando la casilla 'Add Python to PATH'.
    pause
    exit /b
)

echo Instalando CustomTkinter y actualizando pip...
python -m pip install --upgrade pip
python -m pip install customtkinter

echo.
echo ¡CustomTkinter se ha instalado correctamente!
pause