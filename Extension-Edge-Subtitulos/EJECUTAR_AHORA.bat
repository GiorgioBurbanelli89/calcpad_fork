@echo off
chcp 65001 >nul
cls
echo.
echo ========================================
echo   MONITOREAR EXTENSION EN TIEMPO REAL
echo ========================================
echo.
echo Iniciando monitoreo...
echo.
powershell -ExecutionPolicy Bypass -File "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Extension-Edge-Subtitulos\monitorear_extension.ps1"
echo.
echo ========================================
echo   SCRIPT TERMINADO
echo ========================================
echo.
pause
