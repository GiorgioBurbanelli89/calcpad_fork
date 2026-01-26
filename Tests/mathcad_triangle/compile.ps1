# Script PowerShell para compilar mathcad_triangle.dll

$vsPath = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
$srcDir = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Tests\mathcad_triangle"
$mathcadDir = "C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions"

Write-Host "==========================================="
Write-Host " Compilando mathcad_triangle.dll"
Write-Host "==========================================="
Write-Host ""

$compileScript = @"
@echo off
call "$vsPath" >nul 2>&1
cd /d "$srcDir"
cl /I"$mathcadDir" mathcad_triangle.c /LD /link /out:mathcad_triangle.dll /entry:DllEntryPoint "$mathcadDir\mcaduser.lib"
"@

$tempBat = "$env:TEMP\compile_mathcad_triangle.bat"
$compileScript | Out-File -FilePath $tempBat -Encoding ASCII

$process = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$tempBat`"" -NoNewWindow -Wait -PassThru -RedirectStandardOutput "$env:TEMP\compile_tri_output.txt" -RedirectStandardError "$env:TEMP\compile_tri_error.txt"

Get-Content "$env:TEMP\compile_tri_output.txt"
Get-Content "$env:TEMP\compile_tri_error.txt"

Write-Host ""
Write-Host "Exit code: $($process.ExitCode)"

if (Test-Path "$srcDir\mathcad_triangle.dll") {
    Write-Host ""
    Write-Host "DLL creada exitosamente!"
    Write-Host "Ubicacion: $srcDir\mathcad_triangle.dll"

    $dllSize = (Get-Item "$srcDir\mathcad_triangle.dll").Length
    Write-Host "Tamano: $dllSize bytes"
}
