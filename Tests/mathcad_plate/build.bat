@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cd /d "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Tests\mathcad_plate"
cl /I"C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions" mathcad_plate.c /LD /link /out:mathcad_plate.dll /entry:DllEntryPoint "C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions\mcaduser.lib" kernel32.lib
echo.
echo Exit code: %ERRORLEVEL%
if exist mathcad_plate.dll (
    echo DLL creada exitosamente!
    dir mathcad_plate.dll
)
