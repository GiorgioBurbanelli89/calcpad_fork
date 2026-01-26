@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cd /d "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Tests\mathcad_fem"
cl /I"C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions" mathcad_fem.C /LD /link /out:..\mathcad_fem.dll /entry:DllEntryPoint "C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions\mcaduser.lib"
echo.
echo Exit code: %ERRORLEVEL%
