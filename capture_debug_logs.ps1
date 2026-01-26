# Script para capturar logs de Debug de Calcpad
# Requiere DebugView de Sysinternals o puedes ver la salida en Visual Studio

Write-Host "=== Captura de Logs de Debug ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para ver los logs de Debug, tienes estas opciones:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. DebugView (Sysinternals):" -ForegroundColor Green
Write-Host "   - Descarga: https://docs.microsoft.com/en-us/sysinternals/downloads/debugview"
Write-Host "   - Ejecuta como administrador"
Write-Host "   - Activa 'Capture Global Win32'"
Write-Host "   - Filtra por 'ApplyPreviewEdit' o 'TextChanged'"
Write-Host ""
Write-Host "2. Visual Studio:" -ForegroundColor Green
Write-Host "   - Abre la solucion en Visual Studio"
Write-Host "   - F5 para ejecutar en modo Debug"
Write-Host "   - Los logs aparecen en la ventana 'Output'"
Write-Host ""
Write-Host "3. Output Console (si ejecutas desde VS):" -ForegroundColor Green
Write-Host "   - Debug > Windows > Output"
Write-Host ""

# Intentar descargar DebugView si no existe
$debugViewPath = "$env:TEMP\DebugView"
$debugViewExe = "$debugViewPath\Dbgview.exe"

if (-not (Test-Path $debugViewExe)) {
    Write-Host "Descargando DebugView..." -ForegroundColor Yellow

    $url = "https://download.sysinternals.com/files/DebugView.zip"
    $zipPath = "$env:TEMP\DebugView.zip"

    try {
        Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing
        Expand-Archive -Path $zipPath -DestinationPath $debugViewPath -Force
        Remove-Item $zipPath
        Write-Host "DebugView descargado en: $debugViewPath" -ForegroundColor Green
    }
    catch {
        Write-Host "No se pudo descargar DebugView: $_" -ForegroundColor Red
    }
}

if (Test-Path $debugViewExe) {
    Write-Host ""
    Write-Host "Iniciando DebugView..." -ForegroundColor Cyan
    Start-Process $debugViewExe -Verb RunAs
    Write-Host "DebugView iniciado. Asegurate de activar 'Capture > Capture Global Win32'" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Ahora prueba escribir en el TextBox de preview en Calcpad" -ForegroundColor Cyan
Write-Host "Los logs mostraran:" -ForegroundColor DarkGray
Write-Host "  [TextChanged] - cuando escribes algo"
Write-Host "  [ApplyPreviewEdit] - cuando se aplican los cambios"
