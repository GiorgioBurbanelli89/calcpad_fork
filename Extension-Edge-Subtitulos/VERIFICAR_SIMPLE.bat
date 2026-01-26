@echo off
chcp 65001 >nul
cls
echo.
echo ========================================
echo   VERIFICACION RAPIDA DE LA EXTENSION
echo ========================================
echo.

cd /d "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Extension-Edge-Subtitulos"

echo [1/5] Verificando archivos principales...
echo.

if exist "manifest.json" (
    echo   [OK] manifest.json existe
) else (
    echo   [ERROR] manifest.json NO ENCONTRADO
    goto error
)

if exist "background.js" (
    echo   [OK] background.js existe
) else (
    echo   [ERROR] background.js NO ENCONTRADO
    goto error
)

if exist "content.js" (
    echo   [OK] content.js existe
) else (
    echo   [ERROR] content.js NO ENCONTRADO
    goto error
)

if exist "content_youtube.js" (
    echo   [OK] content_youtube.js existe
) else (
    echo   [ERROR] content_youtube.js NO ENCONTRADO
    goto error
)

if exist "popup.html" (
    echo   [OK] popup.html existe
) else (
    echo   [ERROR] popup.html NO ENCONTRADO
    goto error
)

if exist "popup.js" (
    echo   [OK] popup.js existe
) else (
    echo   [ERROR] popup.js NO ENCONTRADO
    goto error
)

if exist "styles.css" (
    echo   [OK] styles.css existe
) else (
    echo   [ERROR] styles.css NO ENCONTRADO
    goto error
)

echo.
echo [2/5] Verificando carpeta de iconos...
echo.

if exist "icons\icon16.png" (
    echo   [OK] icon16.png existe
) else (
    echo   [ERROR] icon16.png NO ENCONTRADO
    goto error
)

if exist "icons\icon48.png" (
    echo   [OK] icon48.png existe
) else (
    echo   [ERROR] icon48.png NO ENCONTRADO
    goto error
)

if exist "icons\icon128.png" (
    echo   [OK] icon128.png existe
) else (
    echo   [ERROR] icon128.png NO ENCONTRADO
    goto error
)

echo.
echo [3/5] Mostrando contenido de manifest.json...
echo.

type manifest.json

echo.
echo [4/5] Verificando tamanos de archivos...
echo.

for %%F in (manifest.json background.js content.js content_youtube.js popup.html popup.js styles.css) do (
    echo   %%F: %%~zF bytes
)

echo.
echo [5/5] RESUMEN
echo.
echo ========================================
echo   TODOS LOS ARCHIVOS CORRECTOS!
echo ========================================
echo.
echo SIGUIENTE PASO:
echo.
echo 1. Abre Microsoft Edge
echo 2. Escribe: edge://extensions/
echo 3. Activa "Modo de desarrollador" (arriba derecha)
echo 4. Busca: "Subtitulos ES + Descargador de Videos HD"
echo 5. Haz clic en el boton RECARGAR (icono circular)
echo 6. Espera 2 segundos
echo 7. Abre YouTube y reproduce un video
echo 8. Haz clic en el icono de la extension
echo.
echo ========================================
echo.
goto end

:error
echo.
echo ========================================
echo   ERROR: FALTAN ARCHIVOS
echo ========================================
echo.
echo Hay archivos faltantes en la extension.
echo Verifica que todos los archivos esten en:
echo C:\Users\j-b-j\Documents\Calcpad-7.5.7\Extension-Edge-Subtitulos
echo.

:end
echo Presiona cualquier tecla para salir...
pause >nul
