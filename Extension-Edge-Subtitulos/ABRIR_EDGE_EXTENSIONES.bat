@echo off
chcp 65001 >nul
cls
echo.
echo ========================================
echo   BOTONES ARREGLADOS
echo ========================================
echo.
echo El problema estaba en popup.js
echo Las funciones no estaban en scope global
echo.
echo SOLUCION APLICADA:
echo   [OK] downloadVideo() - ARREGLADO
echo   [OK] copyUrl() - ARREGLADO
echo   [OK] Todas las funciones ahora son window.functionName
echo.
echo ========================================
echo   ABRIENDO EDGE
echo ========================================
echo.
echo En 3 segundos se abrira Edge en la pagina de extensiones...
timeout /t 3 /nobreak >nul

start msedge.exe edge://extensions/

echo.
echo ========================================
echo   INSTRUCCIONES
echo ========================================
echo.
echo 1. Busca: "Subtitulos ES + Descargador de Videos HD"
echo.
echo 2. Haz clic en el boton RECARGAR (icono circular)
echo.
echo 3. Cierra TODAS las pestanas abiertas
echo.
echo 4. Abre YouTube y reproduce un video
echo.
echo 5. Haz clic en el icono de la extension
echo.
echo 6. AHORA los botones SI funcionaran:
echo    - Descargar
echo    - Copiar URL
echo.
echo ========================================
echo.
pause
