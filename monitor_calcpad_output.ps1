# Monitor de Calcpad WPF - Solo monitorea ventana ya abierta
# Asume que Calcpad ya está ejecutándose con un archivo abierto

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MONITOR DE CALCPAD WPF" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Buscar proceso de Calcpad
Write-Host "[1/4] Buscando Calcpad en ejecución..." -ForegroundColor Yellow

$calcpadProcess = Get-Process | Where-Object { $_.ProcessName -eq "Calcpad" -or $_.MainWindowTitle -like "*Calcpad*" }

if (-not $calcpadProcess) {
    Write-Host "✗ No se encontró Calcpad ejecutándose" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor:" -ForegroundColor Yellow
    Write-Host "1. Abre Calcpad.Wpf manualmente" -ForegroundColor Gray
    Write-Host "2. Abre test_css_linking.cpd o Test_TypeScript_@ts.cpd" -ForegroundColor Gray
    Write-Host "3. Ejecuta este script de nuevo" -ForegroundColor Gray
    exit 1
}

Write-Host "✓ Calcpad encontrado (PID: $($calcpadProcess.Id))" -ForegroundColor Green
Write-Host "  Ventana: $($calcpadProcess.MainWindowTitle)" -ForegroundColor Gray
Write-Host ""

# Información de la ventana
Write-Host "[2/4] Información de la ventana:" -ForegroundColor Yellow
$automation = [System.Windows.Automation.AutomationElement]::RootElement
$condition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    $calcpadProcess.Id
)

$window = $automation.FindFirst([System.Windows.Automation.TreeScope]::Children, $condition)

if ($window) {
    Write-Host "✓ Título: $($window.Current.Name)" -ForegroundColor Green
    Write-Host "  Clase: $($window.Current.ClassName)" -ForegroundColor Gray
    Write-Host "  Estado: $($window.Current.IsOffscreen ? 'Oculta' : 'Visible')" -ForegroundColor Gray
} else {
    Write-Host "⚠ No se pudo obtener información de UI Automation" -ForegroundColor Yellow
}
Write-Host ""

# Verificar archivos generados
Write-Host "[3/4] Verificando archivos generados..." -ForegroundColor Yellow
Write-Host "Esperando 2 segundos para permitir generación de archivos..." -ForegroundColor Gray
Start-Sleep -Seconds 2

$tempDir = "temp_multilang"
$cssFile = Join-Path $tempDir "styles.css"
$htmlFile = Join-Path $tempDir "index.html"
$tsConfigFile = Join-Path $tempDir "tsconfig.json"

Write-Host ""
Write-Host "Carpeta temp: $PWD\$tempDir" -ForegroundColor Gray
Write-Host ""

# Verificar existencia y contenido
$results = @{
    CSS = @{
        Exists = Test-Path $cssFile
        Size = 0
        HasContent = $false
    }
    HTML = @{
        Exists = Test-Path $htmlFile
        Size = 0
        HasContent = $false
        HasLink = $false
    }
    TSConfig = @{
        Exists = Test-Path $tsConfigFile
        Size = 0
    }
}

if ($results.CSS.Exists) {
    $cssContent = Get-Content $cssFile -Raw
    $results.CSS.Size = (Get-Item $cssFile).Length
    $results.CSS.HasContent = $cssContent.Length -gt 0

    Write-Host "✓ styles.css encontrado" -ForegroundColor Green
    Write-Host "  Tamaño: $($results.CSS.Size) bytes" -ForegroundColor Gray
    Write-Host "  Líneas: $((Get-Content $cssFile).Count)" -ForegroundColor Gray

    # Mostrar primeras líneas
    $firstLines = (Get-Content $cssFile | Select-Object -First 3) -join "`n"
    Write-Host "  Preview:" -ForegroundColor Gray
    Write-Host "  $($firstLines -replace "`n", "`n  ")" -ForegroundColor DarkGray
} else {
    Write-Host "✗ styles.css NO encontrado" -ForegroundColor Red
}
Write-Host ""

if ($results.HTML.Exists) {
    $htmlContent = Get-Content $htmlFile -Raw
    $results.HTML.Size = (Get-Item $htmlFile).Length
    $results.HTML.HasContent = $htmlContent.Length -gt 0

    # Verificar si contiene <link> a styles.css
    $results.HTML.HasLink = $htmlContent -match '<link[^>]*href=["'']styles\.css["'']'

    Write-Host "✓ index.html encontrado" -ForegroundColor Green
    Write-Host "  Tamaño: $($results.HTML.Size) bytes" -ForegroundColor Gray
    Write-Host "  Líneas: $((Get-Content $htmlFile).Count)" -ForegroundColor Gray

    if ($results.HTML.HasLink) {
        Write-Host "  ✓ Contiene <link> a styles.css" -ForegroundColor Green

        # Extraer la línea del link
        $linkLine = ($htmlContent -split "`n" | Where-Object { $_ -match '<link.*styles\.css' }) -join ""
        if ($linkLine) {
            Write-Host "  Link encontrado:" -ForegroundColor Gray
            Write-Host "  $($linkLine.Trim())" -ForegroundColor DarkGray
        }
    } else {
        Write-Host "  ✗ NO contiene <link> a styles.css" -ForegroundColor Red
    }

    # Verificar si se abrió en navegador
    $htmlFileFullPath = Resolve-Path $htmlFile
    $browserProcess = Get-Process | Where-Object {
        $_.MainWindowTitle -like "*index.html*" -or
        $_.MainWindowTitle -like "*$htmlFileFullPath*"
    }

    if ($browserProcess) {
        Write-Host "  ✓ Abierto en navegador: $($browserProcess.ProcessName)" -ForegroundColor Green
    }
} else {
    Write-Host "✗ index.html NO encontrado" -ForegroundColor Red
}
Write-Host ""

if ($results.TSConfig.Exists) {
    Write-Host "✓ tsconfig.json encontrado (ya configurado)" -ForegroundColor Green
} else {
    Write-Host "⚠ tsconfig.json no encontrado (solo necesario para TypeScript)" -ForegroundColor Yellow
}
Write-Host ""

# Listar todos los archivos en temp_multilang
if (Test-Path $tempDir) {
    $allFiles = Get-ChildItem $tempDir -File
    if ($allFiles) {
        Write-Host "Archivos en $tempDir/:" -ForegroundColor Gray
        foreach ($file in $allFiles) {
            Write-Host "  - $($file.Name) ($($file.Length) bytes)" -ForegroundColor DarkGray
        }
    }
}
Write-Host ""

# Resumen final
Write-Host "[4/4] RESUMEN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$cssWorking = $results.CSS.Exists -and $results.CSS.HasContent
$htmlWorking = $results.HTML.Exists -and $results.HTML.HasContent
$linkingWorking = $results.HTML.HasLink

if ($cssWorking -and $htmlWorking -and $linkingWorking) {
    Write-Host "✅ CSS LINKING FUNCIONA PERFECTAMENTE" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verificado:" -ForegroundColor Green
    Write-Host "  ✓ Bloque @{css} → styles.css generado" -ForegroundColor Green
    Write-Host "  ✓ Bloque @{html} → index.html generado" -ForegroundColor Green
    Write-Host "  ✓ <link> automático inyectado" -ForegroundColor Green
    Write-Host "  ✓ Archivos vinculados correctamente" -ForegroundColor Green

} elseif ($cssWorking -and $htmlWorking) {
    Write-Host "⚠️ PARCIALMENTE FUNCIONAL" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Archivos generados pero:" -ForegroundColor Yellow
    Write-Host "  ✓ styles.css existe" -ForegroundColor Green
    Write-Host "  ✓ index.html existe" -ForegroundColor Green
    Write-Host "  ✗ <link> NO fue inyectado automáticamente" -ForegroundColor Red

} else {
    Write-Host "❌ CSS LINKING NO FUNCIONÓ" -ForegroundColor Red
    Write-Host ""
    Write-Host "Problemas detectados:" -ForegroundColor Red
    if (-not $cssWorking) {
        Write-Host "  ✗ styles.css no generado correctamente" -ForegroundColor Red
    }
    if (-not $htmlWorking) {
        Write-Host "  ✗ index.html no generado correctamente" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Para verificar manualmente:" -ForegroundColor Gray
Write-Host "1. Abre index.html en un editor de texto" -ForegroundColor Gray
Write-Host "2. Busca la línea: <link rel=\"stylesheet\" href=\"styles.css\">" -ForegroundColor Gray
Write-Host "3. Abre index.html en navegador y verifica estilos aplicados" -ForegroundColor Gray
Write-Host ""
Write-Host "Carpeta: $PWD\$tempDir" -ForegroundColor Cyan
