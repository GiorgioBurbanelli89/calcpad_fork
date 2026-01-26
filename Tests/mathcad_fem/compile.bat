@echo off
REM =====================================================
REM Compilar DLL FEM para Mathcad Prime 10
REM EJECUTAR DESDE: x64 Native Tools Command Prompt for VS 2022
REM =====================================================

echo.
echo =====================================================
echo  Compilando mathcad_fem.dll para Mathcad Prime 10
echo =====================================================
echo.

cd /d "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Tests\mathcad_fem"

REM Compilar usando el formato oficial de PTC
cl /I"..\..\..\..\..\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions" mathcad_fem.C /LD /link /out:..\mathcad_fem.dll /entry:"DllEntryPoint" "C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions\mcaduser.lib"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Compilacion fallida!
    pause
    exit /b 1
)

echo.
echo =====================================================
echo  Compilacion exitosa!
echo =====================================================
echo.

echo Copiando DLL a Mathcad Prime...
copy /Y "..\mathcad_fem.dll" "C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions\"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: No se pudo copiar. Ejecuta como Administrador.
    echo.
    echo Copia manualmente:
    echo   FROM: C:\Users\j-b-j\Documents\Calcpad-7.5.7\Tests\mathcad_fem.dll
    echo   TO:   C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions\
    pause
    exit /b 1
)

echo.
echo =====================================================
echo  INSTALACION COMPLETADA!
echo =====================================================
echo.
echo Funciones disponibles en Mathcad Prime:
echo.
echo   fem_beam_K(E,A,I,L)              - Matriz rigidez viga 2D (6x6)
echo   fem_frame3d_K(E,G,A,Iy,Iz,J,L)  - Matriz rigidez frame 3D (12x12)
echo   cantilever_defl(P,L,E,I)         - Deflexion cantilever
echo   cantilever_rot(P,L,E,I)          - Rotacion cantilever
echo.
echo Reinicia Mathcad Prime para cargar las funciones.
echo.

pause
