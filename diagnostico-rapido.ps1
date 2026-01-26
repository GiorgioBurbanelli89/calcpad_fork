# Diagnóstico rápido - ver últimas 30 líneas de telemetría
$file = Get-ChildItem "C:\Users\j-b-j\AppData\Local\Temp\Calcpad\calcpad_telemetry_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName

Write-Host "`n=== ÚLTIMAS 30 LÍNEAS DE TELEMETRÍA ===" -ForegroundColor Cyan
Write-Host "Archivo: $file`n" -ForegroundColor Gray

$content = Get-Content $file -Tail 30
foreach ($line in $content) {
    if ($line -match "\[ERROR\]") {
        Write-Host $line -ForegroundColor Red
    }
    elseif ($line -match "Success: False|MultilangProcessed: False") {
        Write-Host $line -ForegroundColor Yellow
    }
    elseif ($line -match "\[OUTPUT\]|\[WEBVIEW\]") {
        Write-Host $line -ForegroundColor White
    }
    else {
        Write-Host $line -ForegroundColor Gray
    }
}

Write-Host "`n=== BUSCAR ERRORES ===" -ForegroundColor Cyan
$errors = Get-Content $file | Select-String "\[ERROR\]"
if ($errors) {
    Write-Host "ERRORES ENCONTRADOS:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host $_ -ForegroundColor Red }
} else {
    Write-Host "✅ No hay errores en el log" -ForegroundColor Green
}

Write-Host "`n=== ESTADO ACTUAL ===" -ForegroundColor Cyan
$lastOperation = Get-Content $file | Select-String "OPERATION_END" | Select-Object -Last 1
Write-Host $lastOperation -ForegroundColor Green
