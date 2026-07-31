@echo off
REM Script para iniciar HoraControl - Backend + Frontend Chrome

title HoraControl - Sistema de Horas
color 0A

echo.
echo ========================================
echo     INICIANDO HORACONTROL
echo ========================================
echo.

REM Cambiar a la carpeta del proyecto
cd /d "%~dp0"

echo [1/2] Iniciando Backend Flask...
echo.

REM Iniciar el backend en una nueva ventana de PowerShell
start powershell -NoExit -Command "python app.py"

REM Esperar a que el servidor se inicie (3 segundos)
timeout /t 3 /nobreak

echo [2/2] Abriendo Chrome...
echo.

REM Abrir Chrome en la URL local
start chrome http://localhost:5000

echo.
echo ========================================
echo     HORACONTROL INICIADO
echo ========================================
echo.
echo Backend: http://localhost:5000
echo.
echo Presiona ENTER para cerrar esta ventana...
pause
