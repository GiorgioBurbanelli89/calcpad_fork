# Crear una imagen PNG de prueba con texto visible
Add-Type -AssemblyName System.Drawing

# Crear bitmap de 200x100 pixels
$bitmap = New-Object System.Drawing.Bitmap(200, 100)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)

# Fondo azul claro
$graphics.Clear([System.Drawing.Color]::LightBlue)

# Dibujar rectángulo rojo
$redBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Red)
$graphics.FillRectangle($redBrush, 10, 10, 80, 80)

# Dibujar texto
$font = New-Object System.Drawing.Font("Arial", 16, [System.Drawing.FontStyle]::Bold)
$blackBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Black)
$graphics.DrawString("CALCPAD", $font, $blackBrush, 100, 35)

# Guardar como PNG
$tempPng = "$env:TEMP\calcpad_test.png"
$bitmap.Save($tempPng, [System.Drawing.Imaging.ImageFormat]::Png)

Write-Host "Imagen guardada: $tempPng" -ForegroundColor Green

# Convertir a Base64
$bytes = [IO.File]::ReadAllBytes($tempPng)
$base64 = [Convert]::ToBase64String($bytes)

Write-Host "Tamaño PNG: $($bytes.Length) bytes" -ForegroundColor Cyan
Write-Host "Tamaño Base64: $($base64.Length) caracteres" -ForegroundColor Cyan
Write-Host "`nBase64 (primeros 100 chars):" -ForegroundColor Yellow
Write-Host $base64.Substring(0, [Math]::Min(100, $base64.Length))

# Guardar Base64 en archivo de texto
$base64File = "imagen_test_base64.txt"
$base64 | Out-File -FilePath $base64File -Encoding UTF8
Write-Host "`nBase64 completo guardado en: $base64File" -ForegroundColor Green

# Limpiar
$graphics.Dispose()
$bitmap.Dispose()
$redBrush.Dispose()
$font.Dispose()
$blackBrush.Dispose()

Write-Host "`nAbriendo imagen para verificar..." -ForegroundColor Cyan
Start-Process $tempPng
