# Test directo usando la API de Calcpad
$ErrorActionPreference = "Stop"

Write-Host "=== PRUEBA DIRECTA DEL SISTEMA BASE64 ===" -ForegroundColor Cyan

# Cargar las DLLs de Calcpad
$dllPath = ".\Calcpad.Wpf\bin\Release\net10.0-windows"
Add-Type -Path "$dllPath\Calcpad.Core.dll"
Add-Type -Path "$dllPath\Calcpad.Common.dll"

# Leer el archivo de prueba
$testFile = ".\test_imagen_pequeña.cpd"
$code = Get-Content $testFile -Raw -Encoding UTF8

Write-Host "Archivo cargado: $testFile" -ForegroundColor Green
Write-Host "Tamaño: $($code.Length) caracteres`n" -ForegroundColor Green

# Limpiar log de debug
$debugLog = "$env:TEMP\calcpad-debug.txt"
if (Test-Path $debugLog) { Remove-Item $debugLog }

# Crear instancia del parser
$parser = New-Object Calcpad.Core.ExpressionParser

# Procesar el código
Write-Host "Procesando código con ExpressionParser..." -ForegroundColor Cyan
try {
    $parser.Parse($code, $true, $false)
    $html = $parser.HtmlResult

    Write-Host "HTML generado: $($html.Length) caracteres" -ForegroundColor Green

    # Guardar resultado
    $outputFile = ".\test_salida_directo.html"
    $html | Out-File -FilePath $outputFile -Encoding UTF8

    Write-Host "`nArchivo guardado: $outputFile" -ForegroundColor Green

    # Analizar resultado
    Write-Host "`n=== ANÁLISIS DEL RESULTADO ===" -ForegroundColor Yellow

    if ($html -match "<!--MULTILANG_OUTPUT:") {
        Write-Host "ERROR: Todavía hay marcadores MULTILANG_OUTPUT sin decodificar" -ForegroundColor Red
        $matches = [regex]::Matches($html, '<!--MULTILANG_OUTPUT:([^-]{0,50})')
        Write-Host "Encontrados: $($matches.Count) marcadores" -ForegroundColor Red
    }

    if ($html -match "data:image/") {
        Write-Host "ÉXITO: Imagen Base64 embebida correctamente" -ForegroundColor Green
        $imgMatches = [regex]::Matches($html, 'src="data:image/(\w+);base64,([^"]{0,30})')
        foreach ($match in $imgMatches) {
            Write-Host "  - Formato: $($match.Groups[1].Value)" -ForegroundColor Cyan
            Write-Host "    Base64: $($match.Groups[2].Value)..." -ForegroundColor Gray
        }
    } else {
        Write-Host "NO se encontraron imágenes Base64" -ForegroundColor Red
    }

    if ($html -match "Error.*MULTILANG") {
        Write-Host "`nERROR: Problemas al procesar marcadores MULTILANG" -ForegroundColor Red
        $errorMatches = [regex]::Matches($html, 'Error[^<]*MULTILANG[^<]*')
        foreach ($err in $errorMatches) {
            Write-Host "  $($err.Value)" -ForegroundColor Yellow
        }
    }

} catch {
    Write-Host "ERROR al procesar: $_" -ForegroundColor Red
    Write-Host $_.Exception.StackTrace -ForegroundColor Gray
}

# Verificar log de debug
Write-Host "`n=== LOG DE DEBUG ===" -ForegroundColor Yellow
if (Test-Path $debugLog) {
    Get-Content $debugLog | ForEach-Object {
        if ($_ -match "ExpressionParser") {
            Write-Host $_ -ForegroundColor Cyan
        } elseif ($_ -match "MULTILANG") {
            Write-Host $_ -ForegroundColor Yellow
        } else {
            Write-Host $_ -ForegroundColor Gray
        }
    }
} else {
    Write-Host "No se generó log de debug" -ForegroundColor Yellow
}

Write-Host "`n=== PRUEBA COMPLETADA ===" -ForegroundColor Green
