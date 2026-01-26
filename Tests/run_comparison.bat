@echo off
REM ============================================================================
REM Script de Comparación FEM: Calcpad vs Mathcad
REM ============================================================================

echo.
echo ========================================================================
echo Sistema de Comparacion FEM: Calcpad vs Mathcad
echo ========================================================================
echo.

set CLI_PATH=..\Calcpad.Cli\bin\Release\net10.0\Cli.exe
set TEST_FILE=mathcad_fem_comparison.cpd
set OUTPUT_FILE=mathcad_fem_comparison.html

REM Verificar que existe el CLI
if not exist "%CLI_PATH%" (
    echo ERROR: No se encontro el CLI de Calcpad
    echo.
    echo Compilando CLI...
    cd ..\Calcpad.Cli
    dotnet build -c Release
    cd ..\Tests
    echo.
)

echo [1/2] Generando resultados de Calcpad...
echo.
"%CLI_PATH%" "%TEST_FILE%" "%OUTPUT_FILE%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Fallo la generacion del HTML
    pause
    exit /b 1
)

echo.
echo [2/2] HTML generado exitosamente: %OUTPUT_FILE%
echo (El CLI abrira automaticamente el HTML en el navegador)

echo.
echo ========================================================================
echo PROXIMO PASO:
echo ========================================================================
echo.
echo 1. Revisa el HTML con los resultados de Calcpad
echo 2. Abre Mathcad Prime 10
echo 3. Copia el codigo de: INSTRUCCIONES_MATHCAD.md
echo 4. Ejecuta en Mathcad y anota los resultados en: COMPARACION_RESULTADOS.md
echo.
echo Archivos generados:
echo   - %OUTPUT_FILE%
echo   - RESULTADOS_CALCPAD.md
echo   - INSTRUCCIONES_MATHCAD.md
echo   - COMPARACION_RESULTADOS.md
echo.
echo ========================================================================

pause
