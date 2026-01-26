@echo off
echo Compilando SAP2000_Runner.cs...

set SAP_PATH=C:\Program Files\Computers and Structures\SAP2000 24
set CSC_PATH=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe

"%CSC_PATH%" /reference:"%SAP_PATH%\CSiAPIv1.dll" /reference:"%SAP_PATH%\SAP2000v1.dll" SAP2000_Runner.cs

if %errorlevel% == 0 (
    echo.
    echo Compilacion exitosa!
    echo Ejecutable generado: SAP2000_Runner.exe
    echo.
    echo Para ejecutar: SAP2000_Runner.exe
) else (
    echo.
    echo Error en la compilacion
)

pause
