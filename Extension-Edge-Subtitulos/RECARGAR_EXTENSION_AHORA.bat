@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   RECARGAR EXTENSIÓN - PASOS
echo ========================================
echo.
echo 1. Abre Microsoft Edge
echo.
echo 2. Escribe en la barra de direcciones:
echo    edge://extensions/
echo.
echo 3. Activa "Modo de desarrollador"
echo    (Interruptor arriba a la derecha)
echo.
echo 4. Busca: "Subtítulos ES + Descargador de Videos HD"
echo.
echo 5. Haz clic en el botón RECARGAR (icono circular ↻)
echo.
echo 6. Espera 2 segundos
echo.
echo 7. Cierra TODAS las pestañas abiertas
echo.
echo 8. Abre YouTube: https://www.youtube.com/watch?v=dQw4w9WgXcQ
echo.
echo 9. Reproduce el video
echo.
echo 10. Espera 5 segundos
echo.
echo 11. Haz clic en el icono de la extensión
echo.
echo 12. Deberías ver varios videos detectados
echo     (diferentes calidades: 360p, 720p, 1080p)
echo.
echo ========================================
echo   VENTAJAS DE NUESTRA EXTENSIÓN
echo ========================================
echo.
echo ✓ SIN LÍMITE de descargas
echo ✓ SIN tiempo de espera
echo ✓ SIN restricciones por hora
echo ✓ SIN anuncios
echo ✓ SIN necesidad de pagar
echo ✓ Funciona en TODOS los sitios
echo ✓ Detecta TODOS los formatos
echo ✓ Código simple y legible
echo.
echo ========================================
echo   VIDEO DOWNLOADHELPER vs NUESTRA
echo ========================================
echo.
echo Video DownloadHelper:
echo   ✗ 2 videos cada 1 hora (versión gratis)
echo   ✗ Hay que pagar para más
echo   ✗ Código ofuscado
echo.
echo Nuestra extensión:
echo   ✓ Descargas ILIMITADAS
echo   ✓ 100%% gratis
echo   ✓ Código abierto
echo.
echo ========================================
echo.
echo Presiona ENTER para continuar...
pause >nul
echo.
echo ¿Quieres abrir Edge en la página de extensiones?
echo.
echo (S = Sí, N = No)
set /p respuesta="Tu respuesta: "

if /i "%respuesta%"=="S" (
    echo.
    echo Abriendo Edge...
    start msedge.exe edge://extensions/
    echo.
    echo Ahora:
    echo 1. Busca la extensión
    echo 2. Haz clic en RECARGAR
    echo 3. ¡Listo!
) else (
    echo.
    echo Abre manualmente: edge://extensions/
)

echo.
pause
