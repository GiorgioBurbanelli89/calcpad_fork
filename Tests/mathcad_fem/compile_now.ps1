# Script PowerShell para compilar DLL de Mathcad Prime

$vsPath = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
$srcDir = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Tests\mathcad_fem"
$mathcadDir = "C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions"

Write-Host "==========================================="
Write-Host " Compilando mathcad_fem.dll"
Write-Host "==========================================="
Write-Host ""

$compileScript = @"
@echo off
call "$vsPath" >nul 2>&1
cd /d "$srcDir"
cl /I"$mathcadDir" mathcad_fem.C /LD /link /out:..\mathcad_fem.dll /entry:DllEntryPoint "$mathcadDir\mcaduser.lib"
"@

$tempBat = "$env:TEMP\compile_mathcad_fem.bat"
$compileScript | Out-File -FilePath $tempBat -Encoding ASCII

$process = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$tempBat`"" -NoNewWindow -Wait -PassThru -RedirectStandardOutput "$env:TEMP\compile_output.txt" -RedirectStandardError "$env:TEMP\compile_error.txt"

Get-Content "$env:TEMP\compile_output.txt"
Get-Content "$env:TEMP\compile_error.txt"

Write-Host ""
Write-Host "Exit code: $($process.ExitCode)"

if (Test-Path "$srcDir\..\mathcad_fem.dll") {
    Write-Host ""
    Write-Host "DLL creada exitosamente!"
    Write-Host "Ubicacion: $srcDir\..\mathcad_fem.dll"

    $dllSize = (Get-Item "$srcDir\..\mathcad_fem.dll").Length
    Write-Host "Tamano: $dllSize bytes"
}
