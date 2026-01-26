# Analizar el archivo HTML final mas reciente
$file = Get-ChildItem "C:\Users\j-b-j\AppData\Local\Temp\Calcpad\" -Filter "output_html_final_*.html" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if ($null -eq $file) {
    Write-Host "NO SE ENCONTRO ningun archivo final" -ForegroundColor Red
    exit 1
}

Write-Host "=== ANALISIS DE OUTPUT FINAL ===" -ForegroundColor Cyan
Write-Host "Archivo: $($file.Name)" -ForegroundColor Yellow
Write-Host "Fecha: $($file.LastWriteTime)" -ForegroundColor Gray

$content = Get-Content $file.FullName -Raw -Encoding UTF8

Write-Host "Tamanio total: $($content.Length) caracteres" -ForegroundColor Green

# Buscar patrones clave
Write-Host "`n=== CONTENIDO ENCONTRADO ===" -ForegroundColor Cyan

if ($content -match 'NDICE COMPLETO') {
    Write-Host "[OK] Contiene 'INDICE COMPLETO'" -ForegroundColor Green
} else {
    Write-Host "[ERROR] NO contiene 'INDICE COMPLETO'" -ForegroundColor Red
}

if ($content -match 'EJEMPLOS COMPLETOS') {
    Write-Host "[OK] Contiene 'EJEMPLOS COMPLETOS'" -ForegroundColor Green
} else {
    Write-Host "[ERROR] NO contiene 'EJEMPLOS COMPLETOS'" -ForegroundColor Red
}

if ($content -match 'hola-mundo') {
    Write-Host "[OK] Contiene '01-hola-mundo'" -ForegroundColor Green
} else {
    Write-Host "[ERROR] NO contiene referencias a ejemplos" -ForegroundColor Red
}

# Mostrar ultimas 3000 caracteres
Write-Host "`n=== ULTIMOS 3000 CARACTERES ===" -ForegroundColor Cyan
$endPos = [Math]::Max(0, $content.Length - 3000)
$lastPart = $content.Substring($endPos)
Write-Host $lastPart -ForegroundColor White

Write-Host "`n=== FIN ANALISIS ===" -ForegroundColor Cyan
