@echo off
REM ============================================================================
REM Script para ejecutar la calculadora
REM ============================================================================

echo.
echo ========================================
echo   EJECUTANDO CALCULADORA
echo ========================================
echo.

REM Verificar que exista el EXE
if not exist "calculadora.exe" (
    echo ERROR: calculadora.exe no encontrado
    echo.
    echo Compila primero con: compilar.bat
    echo.
    pause
    exit /b 1
)

REM Verificar que exista la DLL
if not exist "matematicas.dll" (
    echo ERROR: matematicas.dll no encontrada
    echo.
    echo Compila primero con: compilar.bat
    echo.
    pause
    exit /b 1
)

echo Archivos encontrados:
echo   ✓ calculadora.exe
echo   ✓ matematicas.dll
echo.
echo Ejecutando...
echo.

REM Ejecutar el programa
calculadora.exe
