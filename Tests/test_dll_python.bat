@echo off
REM ============================================================================
REM Prueba REAL: Cargar DLLs de Mathcad usando Python desde Calcpad
REM ============================================================================

echo.
echo ========================================================================
echo PRUEBA REAL: DLLs de Mathcad mediante Python en Calcpad
echo ========================================================================
echo.

set CLI_PATH=..\Calcpad.Cli\bin\Release\net10.0\Cli.exe
set TEST_FILE=mathcad_dll_python_test.cpd
set OUTPUT_FILE=mathcad_dll_python_test.html

REM Verificar que existe Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python no esta instalado o no esta en PATH
    echo.
    echo Instala Python desde: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [INFO] Python encontrado:
python --version
echo.

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

REM Verificar que existen las DLLs
if not exist "mathcad_fem.dll" (
    echo ADVERTENCIA: mathcad_fem.dll no encontrada en Tests/
    echo Por favor compila las DLLs primero.
    echo.
)

if not exist "mathcad_triangle\mathcad_triangle.dll" (
    echo ADVERTENCIA: mathcad_triangle.dll no encontrada
    echo.
)

echo [INFO] Este metodo usa Python + ctypes para cargar las DLLs
echo [INFO] Python se ejecuta desde Calcpad mediante MultLangCode @{python}
echo.

echo [1/2] Ejecutando Calcpad con Python + DLLs...
echo.
"%CLI_PATH%" "%TEST_FILE%" "%OUTPUT_FILE%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Fallo la ejecucion
    echo.
    echo Posibles causas:
    echo   1. Las DLLs no se encontraron
    echo   2. Python no pudo cargar las DLLs (verifica arquitectura: 32-bit vs 64-bit)
    echo   3. Error en el codigo Python
    echo.
    pause
    exit /b 1
)

echo.
echo [2/2] HTML generado exitosamente: %OUTPUT_FILE%
echo (El navegador deberia abrirse automaticamente)

echo.
echo ========================================================================
echo RESULTADO:
echo ========================================================================
echo.
echo El HTML muestra:
echo   1. Calculos analiticos (Calcpad)
echo   2. Resultados de DLLs (Python + ctypes)
echo   3. Comparacion y diferencias
echo   4. Estado PASS/FAIL para cada test
echo.
echo Si todas las pruebas muestran "✓ PASS", las DLLs funcionan correctamente!
echo.
echo ========================================================================

pause
