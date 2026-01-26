# Script para comparar visualmente Excel original vs HTML generado
Write-Host "======================================"
Write-Host "Comparación Excel → Calcpad HTML"
Write-Host "======================================"

# Abrir Excel original y HTML generado lado a lado
$excelPath = "C:\Users\j-b-j\Downloads\HOJA DE CALCULO 23-01-2026.xlsx"
$htmlPath = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\excel_NEW.html"

Write-Host "`n1. Abriendo Excel original..."
Start-Process $excelPath

Write-Host "2. Abriendo HTML generado..."
Start-Process $htmlPath

Write-Host "`n======================================"
Write-Host "Verificación de tablas en HTML:"
Write-Host "======================================"

$htmlContent = Get-Content $htmlPath -Raw

# Contar elementos
$tableCount = ([regex]::Matches($htmlContent, '<table')).Count
$trCount = ([regex]::Matches($htmlContent, '<tr>')).Count
$tdCount = ([regex]::Matches($htmlContent, '<td')).Count
$h2Count = ([regex]::Matches($htmlContent, '<h2')).Count

Write-Host "Tablas encontradas: $tableCount"
Write-Host "Filas (<tr>): $trCount"
Write-Host "Celdas (<td>): $tdCount"
Write-Host "Hojas (H2): $h2Count"

# Buscar problemas comunes
Write-Host "`n======================================"
Write-Host "Verificando formato:"
Write-Host "======================================"

# Verificar colores
$greenHeaders = ([regex]::Matches($htmlContent, 'color:#217346')).Count
Write-Host "Encabezados verdes: $greenHeaders"

# Verificar celdas con fondo de color
$coloredBg = ([regex]::Matches($htmlContent, 'background-color:')).Count
Write-Host "Celdas con color de fondo: $coloredBg"

# Verificar negrita
$boldCells = ([regex]::Matches($htmlContent, 'font-weight:bold')).Count
Write-Host "Celdas en negrita: $boldCells"

# Buscar las primeras líneas de una tabla
Write-Host "`n======================================"
Write-Host "Muestra de la primera tabla (LOSA):"
Write-Host "======================================"

if ($htmlContent -match '(?s)<h2[^>]*>LOSA</h2>.*?<table[^>]*>(.*?)</table>') {
    $tableContent = $matches[1]
    $rows = [regex]::Matches($tableContent, '<tr>(.*?)</tr>')

    Write-Host "Total filas en tabla LOSA: $($rows.Count)"

    # Mostrar primeras 5 filas
    Write-Host "`nPrimeras 5 filas:"
    for ($i = 0; $i -lt [Math]::Min(5, $rows.Count); $i++) {
        $rowHtml = $rows[$i].Groups[1].Value
        $cells = [regex]::Matches($rowHtml, '<td[^>]*>(.*?)</td>')

        $cellValues = @()
        foreach ($cell in $cells) {
            $val = $cell.Groups[1].Value
            if ($val.Length -gt 20) { $val = $val.Substring(0, 20) + "..." }
            $cellValues += $val
        }

        Write-Host "  Fila $($i+1): $($cellValues -join ' | ')"
    }
}

Write-Host "`n======================================"
Write-Host "Comparación lista. Revisa ambas ventanas."
Write-Host "======================================"
