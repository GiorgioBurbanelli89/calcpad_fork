@echo off
REM =====================================================
REM Script para compilar DLL FEM para Mathcad Prime 10
REM Ejecutar desde "x64 Native Tools Command Prompt for VS 2022"
REM =====================================================

echo.
echo =====================================================
echo  Compilando mathcad_fem.dll para Mathcad Prime 10
echo =====================================================
echo.

REM Configurar rutas
set EIGEN_PATH=C:\Users\j-b-j\eigen
set MATHCAD_PATH=C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions
set SRC_PATH=C:\Users\j-b-j\Documents\Calcpad-7.5.7\Tests

REM Cambiar al directorio de codigo fuente
cd /d "%SRC_PATH%"

echo Compilando...
echo.

cl /I"%EIGEN_PATH%" /I"%MATHCAD_PATH%" mathcad_fem.cpp /LD /EHsc /O2 /MD /link /out:mathcad_fem.dll /entry:DllEntryPoint "%MATHCAD_PATH%\mcaduser.lib"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: La compilacion fallo!
    pause
    exit /b 1
)

echo.
echo =====================================================
echo  Compilacion exitosa!
echo =====================================================
echo.

REM Copiar DLL a Mathcad
echo Copiando DLL a Mathcad Prime...
copy /Y mathcad_fem.dll "%MATHCAD_PATH%\"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: No se pudo copiar la DLL. Ejecuta como Administrador.
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
echo   fem_beam_K(E,A,I,L)         - Matriz rigidez viga 2D (6x6)
echo   fem_frame3d_K(E,G,A,Iy,Iz,J,L) - Matriz rigidez frame 3D (12x12)
echo   fem_solve(K,F,supports)     - Resuelve K*U=F
echo   cantilever_defl(P,L,E,I)    - Deflexion analitica cantilever
echo.
echo Reinicia Mathcad Prime para cargar las nuevas funciones.
echo.

pause
