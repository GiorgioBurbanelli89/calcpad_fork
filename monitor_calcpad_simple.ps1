# Monitor simple de Calcpad WPF
# Solo verifica archivos generados

$ErrorActionPreference = "Continue"

Write-Host "========================================"
Write-Host "MONITOR DE CALCPAD WPF"
Write-Host "========================================"
Write-Host ""

# Buscar proceso de Calcpad
Write-Host "[1/3] Buscando Calcpad en ejecucion..."

$calcpadProcess = Get-Process | Where-Object { $_.ProcessName -eq "Calcpad" }

if (-not $calcpadProcess) {
    Write-Host "X No se encontro Calcpad ejecutandose"
    Write-Host ""
    Write-Host "Por favor:"
    Write-Host "1. Abre Calcpad.Wpf manualmente"
    Write-Host "2. Abre test_css_linking.cpd"
    Write-Host "3. Presiona F5 para calcular"
    Write-Host "4. Ejecuta este script de nuevo"
    exit 1
}

Write-Host "OK Calcpad encontrado (PID: $($calcpadProcess.Id))"
Write-Host "   Ventana: $($calcpadProcess.MainWindowTitle)"
Write-Host ""

# Verificar archivos generados
Write-Host "[2/3] Verificando archivos generados..."
Write-Host "Carpeta: $PWD\temp_multilang"
Write-Host ""

$tempDir = "temp_multilang"
$cssFile = Join-Path $tempDir "styles.css"
$htmlFile = Join-Path $tempDir "index.html"

$cssExists = Test-Path $cssFile
$htmlExists = Test-Path $htmlFile

if ($cssExists) {
    $cssSize = (Get-Item $cssFile).Length
    $cssLines = (Get-Content $cssFile).Count
    Write-Host "OK styles.css encontrado"
    Write-Host "   Tamano: $cssSize bytes"
    Write-Host "   Lineas: $cssLines"
    Write-Host ""

    # Mostrar primeras 3 lineas
    Write-Host "   Preview:"
    Get-Content $cssFile | Select-Object -First 3 | ForEach-Object {
        Write-Host "   $_"
    }
} else {
    Write-Host "X styles.css NO encontrado"
}
Write-Host ""

if ($htmlExists) {
    $htmlSize = (Get-Item $htmlFile).Length
    $htmlLines = (Get-Content $htmlFile).Count
    $htmlContent = Get-Content $htmlFile -Raw

    Write-Host "OK index.html encontrado"
    Write-Host "   Tamano: $htmlSize bytes"
    Write-Host "   Lineas: $htmlLines"

    # Verificar si contiene link a styles.css
    $hasLink = $htmlContent -match '<link[^>]*href=["'']styles\.css["'']'

    if ($hasLink) {
        Write-Host "   OK Contiene link a styles.css"

        # Buscar y mostrar la linea del link
        $linkLines = Get-Content $htmlFile | Where-Object { $_ -match 'link.*styles\.css' }
        if ($linkLines) {
            Write-Host "   Link encontrado:"
            foreach ($line in $linkLines) {
                Write-Host "   $($line.Trim())"
            }
        }
    } else {
        Write-Host "   X NO contiene link a styles.css"
    }
} else {
    Write-Host "X index.html NO encontrado"
}
Write-Host ""

# Listar todos los archivos
if (Test-Path $tempDir) {
    $allFiles = Get-ChildItem $tempDir -File
    if ($allFiles) {
        Write-Host "Todos los archivos en temp_multilang:"
        foreach ($file in $allFiles) {
            Write-Host "  - $($file.Name) ($($file.Length) bytes)"
        }
    }
}
Write-Host ""

# Resumen
Write-Host "[3/3] RESUMEN"
Write-Host "========================================"

$cssOK = $cssExists -and ((Get-Item $cssFile).Length -gt 0)
$htmlOK = $htmlExists -and ((Get-Item $htmlFile).Length -gt 0)

if (-not $htmlExists) {
    $linkOK = $false
} else {
    $htmlContent = Get-Content $htmlFile -Raw
    $linkOK = $htmlContent -match '<link[^>]*href=["'']styles\.css["'']'
}

if ($cssOK -and $htmlOK -and $linkOK) {
    Write-Host "EXITO: CSS LINKING FUNCIONA"
    Write-Host ""
    Write-Host "Verificado:"
    Write-Host "  OK Bloque css -> styles.css generado"
    Write-Host "  OK Bloque html -> index.html generado"
    Write-Host "  OK link automatico inyectado"

} elseif ($cssOK -and $htmlOK) {
    Write-Host "PARCIAL: Archivos generados pero sin link"
    Write-Host ""
    Write-Host "  OK styles.css existe"
    Write-Host "  OK index.html existe"
    Write-Host "  X link NO inyectado"

} else {
    Write-Host "ERROR: CSS LINKING NO FUNCIONO"
    Write-Host ""
    if (-not $cssOK) {
        Write-Host "  X styles.css problema"
    }
    if (-not $htmlOK) {
        Write-Host "  X index.html problema"
    }
}

Write-Host ""
Write-Host "Para probar manualmente:"
Write-Host "1. Abre: $PWD\$tempDir\index.html"
Write-Host "2. Verifica que los estilos se apliquen"
Write-Host ""
