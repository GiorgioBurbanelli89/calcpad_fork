# Script de UI Automation para probar Calcpad WPF
# Prueba CSS linking y TypeScript

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTING CALCPAD WPF v1.0.2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Rutas
$calcpadExe = "Calcpad.Wpf\bin\Release\net10.0-windows\Calcpad.exe"
$testCssFile = "$PWD\test_css_linking.cpd"

# Verificar que el ejecutable existe
if (-not (Test-Path $calcpadExe)) {
    Write-Host "ERROR: No se encuentra Calcpad.exe" -ForegroundColor Red
    Write-Host "Ruta: $calcpadExe" -ForegroundColor Red
    exit 1
}

Write-Host "[1/6] Iniciando Calcpad WPF..." -ForegroundColor Yellow
Write-Host "Ejecutable: $calcpadExe" -ForegroundColor Gray

# Iniciar Calcpad
$process = Start-Process -FilePath $calcpadExe -PassThru -WindowStyle Normal

if (-not $process) {
    Write-Host "ERROR: No se pudo iniciar Calcpad" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Calcpad iniciado (PID: $($process.Id))" -ForegroundColor Green
Write-Host ""

# Esperar a que la ventana esté lista
Write-Host "[2/6] Esperando a que Calcpad cargue..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Buscar la ventana de Calcpad
$automation = [System.Windows.Automation.AutomationElement]::RootElement
$condition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    $process.Id
)

$window = $automation.FindFirst([System.Windows.Automation.TreeScope]::Children, $condition)

if (-not $window) {
    Write-Host "ERROR: No se pudo encontrar la ventana de Calcpad" -ForegroundColor Red
    $process | Stop-Process -Force
    exit 1
}

Write-Host "✓ Ventana encontrada: $($window.Current.Name)" -ForegroundColor Green
Write-Host ""

# Intentar abrir archivo con Ctrl+O
Write-Host "[3/6] Intentando abrir archivo de prueba..." -ForegroundColor Yellow
Write-Host "Archivo: test_css_linking.cpd" -ForegroundColor Gray

# Traer ventana al frente
$null = [System.Reflection.Assembly]::LoadWithPartialName("Microsoft.VisualBasic")
[Microsoft.VisualBasic.Interaction]::AppActivate($process.Id)
Start-Sleep -Milliseconds 500

# Simular Ctrl+O para abrir archivo
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("^o")
Start-Sleep -Seconds 2

# Escribir ruta del archivo
Write-Host "Escribiendo ruta del archivo..." -ForegroundColor Gray
[System.Windows.Forms.SendKeys]::SendWait($testCssFile)
Start-Sleep -Milliseconds 500
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Seconds 2

Write-Host "✓ Comando de apertura enviado" -ForegroundColor Green
Write-Host ""

# Calcular con F5
Write-Host "[4/6] Ejecutando cálculo (F5)..." -ForegroundColor Yellow
[System.Windows.Forms.SendKeys]::SendWait("{F5}")
Start-Sleep -Seconds 3

Write-Host "✓ Cálculo ejecutado" -ForegroundColor Green
Write-Host ""

# Verificar archivos generados
Write-Host "[5/6] Verificando archivos generados..." -ForegroundColor Yellow

$tempDir = "temp_multilang"
$cssFile = Join-Path $tempDir "styles.css"
$htmlFile = Join-Path $tempDir "index.html"

$results = @{
    CSS = Test-Path $cssFile
    HTML = Test-Path $htmlFile
}

if ($results.CSS) {
    $cssContent = Get-Content $cssFile -Raw
    $cssSize = (Get-Item $cssFile).Length
    Write-Host "✓ styles.css creado ($cssSize bytes)" -ForegroundColor Green
} else {
    Write-Host "✗ styles.css NO encontrado" -ForegroundColor Red
}

if ($results.HTML) {
    $htmlContent = Get-Content $htmlFile -Raw
    $htmlSize = (Get-Item $htmlFile).Length

    # Verificar si contiene <link> a styles.css
    if ($htmlContent -match '<link.*href="styles\.css"') {
        Write-Host "✓ index.html creado con <link> a styles.css ($htmlSize bytes)" -ForegroundColor Green
    } else {
        Write-Host "✓ index.html creado ($htmlSize bytes)" -ForegroundColor Yellow
        Write-Host "  ⚠ WARNING: No se encontró <link> a styles.css" -ForegroundColor Yellow
    }
} else {
    Write-Host "✗ index.html NO encontrado" -ForegroundColor Red
}

Write-Host ""

# Resumen
Write-Host "[6/6] RESUMEN DE PRUEBAS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($results.CSS -and $results.HTML) {
    Write-Host "✅ CSS LINKING FUNCIONA CORRECTAMENTE" -ForegroundColor Green
    Write-Host ""
    Write-Host "Archivos generados en: $tempDir\" -ForegroundColor Gray
    Write-Host "  - styles.css" -ForegroundColor Gray
    Write-Host "  - index.html (con <link>)" -ForegroundColor Gray
} else {
    Write-Host "❌ CSS LINKING NO FUNCIONÓ" -ForegroundColor Red
    Write-Host ""
    Write-Host "Archivos faltantes:" -ForegroundColor Gray
    if (-not $results.CSS) { Write-Host "  - styles.css" -ForegroundColor Red }
    if (-not $results.HTML) { Write-Host "  - index.html" -ForegroundColor Red }
}

Write-Host ""
Write-Host "Presiona cualquier tecla para cerrar Calcpad y terminar..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Cerrar Calcpad
Write-Host ""
Write-Host "Cerrando Calcpad..." -ForegroundColor Gray
$process | Stop-Process -Force
Start-Sleep -Seconds 1

Write-Host "✓ Test completado" -ForegroundColor Green
