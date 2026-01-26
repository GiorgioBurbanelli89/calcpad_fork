# Verificar si la imagen Base64 es válida
$base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

try {
    # Decodificar Base64
    $bytes = [Convert]::FromBase64String($base64)
    Write-Host "Base64 decodificado: $($bytes.Length) bytes" -ForegroundColor Green

    # Verificar firma PNG (89 50 4E 47 = PNG)
    if ($bytes[0] -eq 0x89 -and $bytes[1] -eq 0x50 -and $bytes[2] -eq 0x4E -and $bytes[3] -eq 0x47) {
        Write-Host "Firma PNG válida: 89 50 4E 47" -ForegroundColor Green
    } else {
        Write-Host "ERROR: No es un PNG válido" -ForegroundColor Red
        Write-Host "Primeros bytes: $([BitConverter]::ToString($bytes[0..3]))" -ForegroundColor Yellow
    }

    # Guardar como archivo para verificar
    $tempPng = "$env:TEMP\test_imagen.png"
    [IO.File]::WriteAllBytes($tempPng, $bytes)
    Write-Host "`nImagen guardada en: $tempPng" -ForegroundColor Cyan
    Write-Host "Tamaño archivo: $((Get-Item $tempPng).Length) bytes" -ForegroundColor Cyan

    # Abrir la imagen
    Write-Host "`nAbriendo imagen en visor predeterminado..." -ForegroundColor Yellow
    Start-Process $tempPng

} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
}

# También verificar el HTML generado
Write-Host "`n=== VERIFICANDO HTML GENERADO ===" -ForegroundColor Cyan
$html = Get-Content "test_salida_cli.html" -Raw

if ($html -match '<img src=''data:image/png;base64,([^'']+)''') {
    $htmlBase64 = $matches[1]
    Write-Host "Base64 encontrado en HTML: $($htmlBase64.Length) caracteres" -ForegroundColor Green

    if ($htmlBase64 -eq $base64) {
        Write-Host "Base64 coincide con el esperado" -ForegroundColor Green
    } else {
        Write-Host "Base64 NO coincide" -ForegroundColor Red
        Write-Host "Esperado: $base64" -ForegroundColor Yellow
        Write-Host "En HTML:  $htmlBase64" -ForegroundColor Yellow
    }
} else {
    Write-Host "NO se encontró tag <img> con data:image en el HTML" -ForegroundColor Red
}
