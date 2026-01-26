# Script para probar conversión de Word usando DocxReader
$docxPath = "C:\Users\j-b-j\Downloads\calculo_estructural_escalera_metalica.docx"
$outputHtml = "word_test_output.html"

Write-Host "======================================"
Write-Host "Conversión Word → HTML con DocxReader"
Write-Host "======================================"
Write-Host "Documento: $docxPath"
Write-Host ""

# Cargar el assembly
Add-Type -Path "Calcpad.Wpf\bin\Debug\net10.0-windows\net10.0\Calcpad.OpenXml.dll"

try {
    Write-Host "Creando DocxReader..."
    $reader = New-Object Calcpad.OpenXml.DocxReader

    Write-Host "Leyendo documento..."
    $html = $reader.ReadToHtml($docxPath)

    Write-Host "Guardando HTML..."
    $html | Out-File -FilePath $outputHtml -Encoding UTF8

    Write-Host ""
    Write-Host "======================================"
    Write-Host "Información del documento:"
    Write-Host "======================================"
    Write-Host "Título: $($reader.Title)"
    Write-Host "Versión Word: $($reader.WordVersion)"
    Write-Host "Imágenes: $($reader.Images.Count)"
    Write-Host "Advertencias: $($reader.Warnings.Count)"

    if ($reader.Warnings.Count -gt 0) {
        Write-Host ""
        Write-Host "Advertencias:"
        foreach ($warning in $reader.Warnings) {
            Write-Host "  - $warning"
        }
    }

    Write-Host ""
    Write-Host "======================================"
    Write-Host "Análisis del HTML generado:"
    Write-Host "======================================"

    $htmlContent = Get-Content $outputHtml -Raw

    $h1Count = ([regex]::Matches($htmlContent, '<h1')).Count
    $h2Count = ([regex]::Matches($htmlContent, '<h2')).Count
    $h3Count = ([regex]::Matches($htmlContent, '<h3')).Count
    $tableCount = ([regex]::Matches($htmlContent, '<table')).Count
    $trCount = ([regex]::Matches($htmlContent, '<tr>')).Count
    $tdCount = ([regex]::Matches($htmlContent, '<td')).Count
    $boldCount = ([regex]::Matches($htmlContent, '<strong>|font-weight:bold')).Count
    $colorCount = ([regex]::Matches($htmlContent, 'color:#')).Count
    $bgColorCount = ([regex]::Matches($htmlContent, 'background-color:')).Count
    $imgCount = ([regex]::Matches($htmlContent, '<img')).Count

    Write-Host "H1: $h1Count"
    Write-Host "H2: $h2Count"
    Write-Host "H3: $h3Count"
    Write-Host "Tablas: $tableCount"
    Write-Host "Filas: $trCount"
    Write-Host "Celdas: $tdCount"
    Write-Host "Textos en negrita: $boldCount"
    Write-Host "Textos con color: $colorCount"
    Write-Host "Fondos con color: $bgColorCount"
    Write-Host "Imágenes: $imgCount"

    Write-Host ""
    Write-Host "======================================"
    Write-Host "Muestra del HTML (primeras 50 líneas):"
    Write-Host "======================================"

    $lines = $htmlContent -split "`n"
    for ($i = 0; $i -lt [Math]::Min(50, $lines.Count); $i++) {
        Write-Host $lines[$i]
    }

    Write-Host ""
    Write-Host "Abriendo en navegador..."
    Start-Process $outputHtml

    Write-Host "Archivo generado: $outputHtml" -ForegroundColor Green

} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.Exception.StackTrace
}
