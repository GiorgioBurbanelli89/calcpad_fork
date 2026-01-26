# Ver archivos HTML de output
$calcpadTempDir = "C:\Users\j-b-j\AppData\Local\Temp\Calcpad\"

Write-Host "=== ARCHIVOS HTML DE OUTPUT ===" -ForegroundColor Cyan

if (Test-Path $calcpadTempDir) {
    $htmlFiles = Get-ChildItem $calcpadTempDir -Filter "*.html" | Sort-Object LastWriteTime -Descending | Select-Object -First 5

    if ($htmlFiles.Count -eq 0) {
        Write-Host "NO HAY ARCHIVOS HTML en $calcpadTempDir" -ForegroundColor Red
    } else {
        Write-Host "Encontrados $($htmlFiles.Count) archivos HTML mas recientes:" -ForegroundColor Green

        foreach ($file in $htmlFiles) {
            Write-Host "`n========================================" -ForegroundColor Yellow
            Write-Host "Archivo: $($file.Name)" -ForegroundColor White
            Write-Host "Fecha: $($file.LastWriteTime)" -ForegroundColor Gray
            Write-Host "Tamanio: $($file.Length) bytes" -ForegroundColor Gray

            $content = Get-Content $file.FullName -Raw -Encoding UTF8
            $preview = $content.Substring(0, [Math]::Min(1000, $content.Length))

            Write-Host "`nContenido (primeros 1000 caracteres):" -ForegroundColor Cyan
            Write-Host $preview -ForegroundColor White
        }
    }
} else {
    Write-Host "ERROR: No existe directorio $calcpadTempDir" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
