# Capturar todos los errores de Calcpad
Write-Host "=== CAPTURA DE ERRORES CALCPAD ===" -ForegroundColor Cyan

# 1. Verificar archivos de log
$tempPath = [System.IO.Path]::GetTempPath()
$debugFile = Join-Path $tempPath "calcpad-calculate-debug.txt"
$generalDebugFile = Join-Path $tempPath "calcpad-debug.txt"

Write-Host "`n=== LOGS DE DEBUG ===" -ForegroundColor Yellow

if (Test-Path $debugFile) {
    Write-Host "`n--- calcpad-calculate-debug.txt (ultimas 50 lineas) ---" -ForegroundColor Green
    Get-Content $debugFile -Tail 50
} else {
    Write-Host "No existe: $debugFile" -ForegroundColor Gray
}

if (Test-Path $generalDebugFile) {
    Write-Host "`n--- calcpad-debug.txt (ultimas 50 lineas) ---" -ForegroundColor Green
    Get-Content $generalDebugFile -Tail 50
} else {
    Write-Host "No existe: $generalDebugFile" -ForegroundColor Gray
}

# 2. Capturar output de WebView2
Write-Host "`n=== ARCHIVOS HTML GENERADOS ===" -ForegroundColor Yellow

$outputFiles = @(
    "calcpad-output-initial.html",
    "calcpad-output-final.html",
    "calcpad-output-partial.html"
)

foreach ($file in $outputFiles) {
    $fullPath = Join-Path $tempPath $file
    if (Test-Path $fullPath) {
        Write-Host "`n--- $file (primeros 500 caracteres) ---" -ForegroundColor Green
        $content = Get-Content $fullPath -Raw
        $preview = $content.Substring(0, [Math]::Min(500, $content.Length))
        Write-Host $preview -ForegroundColor White
    } else {
        Write-Host "No existe: $file" -ForegroundColor Gray
    }
}

# 3. Verificar estado del proceso
Write-Host "`n=== ESTADO DEL PROCESO ===" -ForegroundColor Yellow

$process = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue

if ($null -ne $process) {
    Write-Host "Proceso activo: PID=$($process.Id)" -ForegroundColor Green
    Write-Host "Memoria: $([Math]::Round($process.WorkingSet64 / 1MB, 2)) MB" -ForegroundColor White
    Write-Host "Threads: $($process.Threads.Count)" -ForegroundColor White

    # Ver si hay errores en Event Viewer
    Write-Host "`n--- Errores de aplicacion (ultimos 5) ---" -ForegroundColor Yellow
    try {
        Get-EventLog -LogName Application -Source "Application Error" -Newest 5 -ErrorAction SilentlyContinue |
            Where-Object { $_.Message -match "Calcpad" } |
            ForEach-Object {
                Write-Host "[$($_.TimeGenerated)] $($_.Message)" -ForegroundColor Red
            }
    } catch {
        Write-Host "No se puede acceder al Event Log" -ForegroundColor Gray
    }
} else {
    Write-Host "Proceso NO activo" -ForegroundColor Red
}

# 4. Verificar archivos CPD recientes
Write-Host "`n=== ARCHIVO CPD ACTUAL ===" -ForegroundColor Yellow

$currentFile = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Examples\html\00-indice.cpd"
if (Test-Path $currentFile) {
    Write-Host "Archivo: $currentFile" -ForegroundColor Green
    $content = Get-Content $currentFile -Raw
    Write-Host "Tamanio: $($content.Length) caracteres" -ForegroundColor White
    Write-Host "`nPrimeras 20 lineas:" -ForegroundColor Yellow
    Get-Content $currentFile -Head 20 | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
}

Write-Host "`n=== FIN CAPTURA ===" -ForegroundColor Cyan
