@echo off
echo ============================================================
echo COMPILAR TEST SAP2000 API - C#
echo ============================================================
echo.

REM Buscar csc.exe (compilador C#)
set CSC_PATH=""

REM Intentar versiones comunes de .NET Framework
if exist "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" (
    set CSC_PATH="C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
    echo Encontrado csc.exe: %CSC_PATH%
) else if exist "C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" (
    set CSC_PATH="C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe"
    echo Encontrado csc.exe: %CSC_PATH%
) else (
    echo ERROR: No se encontro el compilador C# (csc.exe)
    echo.
    echo Instala .NET Framework 4.0 o superior
    echo O usa Visual Studio Developer Command Prompt
    pause
    exit /b 1
)

REM Verificar SAP2000v1.dll
set SAP_DLL="C:\Program Files\Computers and Structures\SAP2000 24\SAP2000v1.dll"
if not exist %SAP_DLL% (
    echo ERROR: No se encontro SAP2000v1.dll
    echo Ruta esperada: %SAP_DLL%
    echo.
    echo Verifica la instalacion de SAP2000
    pause
    exit /b 1
)

echo.
echo Compilando TestSAP2000API.cs...
echo.

%CSC_PATH% /reference:%SAP_DLL% /out:TestSAP2000API.exe TestSAP2000API.cs

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo COMPILACION EXITOSA
    echo ============================================================
    echo.
    echo Ejecutable creado: TestSAP2000API.exe
    echo.
    echo ¿Ejecutar ahora? (S/N)
    set /p EJECUTAR=
    if /i "%EJECUTAR%"=="S" (
        echo.
        echo Ejecutando...
        echo.
        TestSAP2000API.exe
    )
) else (
    echo.
    echo ============================================================
    echo ERROR EN LA COMPILACION
    echo ============================================================
    echo.
    echo Revisa los errores arriba
    pause
    exit /b 1
)

pause
