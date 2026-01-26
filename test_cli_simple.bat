@echo off
echo === Prueba Calcpad CLI con imagen Base64 ===

cd /d "%~dp0"

rem Limpiar archivos anteriores
del test_salida_cli.html 2>nul
del "%TEMP%\calcpad-debug.txt" 2>nul

echo.
echo Ejecutando Calcpad CLI...
echo.

rem Ejecutar Calcpad CLI
"Calcpad.Cli\bin\Release\net10.0\Cli.exe" "test_imagen_pequeña.cpd" "test_salida_cli.html"

echo.
echo === Resultados ===

if exist "test_salida_cli.html" (
    echo [OK] HTML generado: test_salida_cli.html

    rem Verificar marcadores MULTILANG
    findstr /C:"MULTILANG_OUTPUT" "test_salida_cli.html" >nul
    if %ERRORLEVEL%==0 (
        echo [ERROR] Todavia hay marcadores MULTILANG_OUTPUT sin decodificar
    ) else (
        echo [OK] No hay marcadores MULTILANG_OUTPUT sin procesar
    )

    rem Verificar imagenes Base64
    findstr /C:"data:image/" "test_salida_cli.html" >nul
    if %ERRORLEVEL%==0 (
        echo [EXITO] Imagen Base64 encontrada en el HTML
    ) else (
        echo [ERROR] NO se encontro imagen Base64
    )
) else (
    echo [ERROR] No se genero el archivo HTML
)

echo.
echo === Log de Debug ===
if exist "%TEMP%\calcpad-debug.txt" (
    type "%TEMP%\calcpad-debug.txt"
) else (
    echo No se genero log de debug
)

echo.
echo Prueba completada.
