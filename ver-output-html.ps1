# Ver el HTML más reciente del Output de Calcpad WPF

$outputDir = "C:\Users\j-b-j\AppData\Local\Temp\Calcpad"

# Encontrar el archivo HTML más reciente
$htmlFiles = Get-ChildItem "$outputDir\output_html_*.html" -ErrorAction SilentlyContinue |
             Sort-Object LastWriteTime -Descending

if (!$htmlFiles) {
    Write-Host "[ERROR] No se encontraron archivos HTML del Output" -ForegroundColor Red
    Write-Host "`nAsegúrate de:" -ForegroundColor Yellow
    Write-Host "  1. Calcpad WPF está ejecutándose" -ForegroundColor White
    Write-Host "  2. Has presionado F5 para ejecutar código" -ForegroundColor White
    Write-Host "`nUbicación esperada: $outputDir\output_html_*.html`n" -ForegroundColor Gray
    exit 1
}

Write-Host "`n=== ARCHIVOS HTML DEL OUTPUT ===" -ForegroundColor Cyan
Write-Host "Total: $($htmlFiles.Count) archivos`n" -ForegroundColor White

# Mostrar lista de archivos
$i = 1
foreach ($file in $htmlFiles | Select-Object -First 10) {
    $timestamp = $file.LastWriteTime.ToString("HH:mm:ss")
    $size = [math]::Round($file.Length / 1KB, 1)
    Write-Host "[$i] $($file.Name) - ${size}KB - $timestamp" -ForegroundColor Gray
    $i++
}

# Abrir el más reciente en navegador
$latest = $htmlFiles[0]
Write-Host "`n=== ABRIENDO MÁS RECIENTE ===" -ForegroundColor Green
Write-Host "Archivo: $($latest.Name)" -ForegroundColor White
Write-Host "Tamaño: $([math]::Round($latest.Length / 1KB, 1))KB" -ForegroundColor White
Write-Host "Hora: $($latest.LastWriteTime.ToString('HH:mm:ss'))`n" -ForegroundColor White

# Abrir en navegador predeterminado
Start-Process $latest.FullName

Write-Host "HTML abierto en tu navegador.`n" -ForegroundColor Green
