@echo off
REM ============================================================================
REM Script para compilar la DLL y el EXE
REM ============================================================================

echo.
echo ========================================
echo   COMPILANDO EJEMPLO DLL + EXE
echo ========================================
echo.

REM Verificar que g++ este instalado
where g++ >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: g++ no encontrado
    echo.
    echo Necesitas instalar MinGW o TDM-GCC
    echo.
    echo Descarga MinGW desde:
    echo   https://sourceforge.net/projects/mingw-w64/
    echo.
    echo O instala TDM-GCC desde:
    echo   https://jmeubank.github.io/tdm-gcc/
    echo.
    pause
    exit /b 1
)

echo [1/2] Compilando matematicas.dll...
echo.
echo Comando:
echo   g++ -shared -o matematicas.dll matematicas.cpp
echo.

g++ -shared -o matematicas.dll matematicas.cpp

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Fallo la compilacion de la DLL
    pause
    exit /b 1
)

echo ✓ matematicas.dll creada exitosamente
echo.

echo [2/2] Compilando calculadora.exe...
echo.
echo Comando:
echo   g++ -o calculadora.exe calculadora.cpp
echo.

g++ -o calculadora.exe calculadora.cpp

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Fallo la compilacion del EXE
    pause
    exit /b 1
)

echo ✓ calculadora.exe creado exitosamente
echo.

echo ========================================
echo   COMPILACION EXITOSA
echo ========================================
echo.
echo Archivos creados:
echo   - matematicas.dll  (biblioteca)
echo   - calculadora.exe  (ejecutable)
echo.
echo Ahora puedes:
echo   1. Ejecutar calculadora.exe
echo   2. O usar ejecutar.bat
echo.
echo Intenta hacer doble clic en matematicas.dll
echo (no pasara nada porque no es ejecutable)
echo.
echo Luego ejecuta calculadora.exe
echo (este SI se ejecuta y usa la DLL)
echo.

pause
