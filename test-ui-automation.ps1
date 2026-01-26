# Test UI Automation - Verificar que controles estan visibles
Write-Host "=== VERIFICACION UI AUTOMATION ===" -ForegroundColor Cyan
Write-Host ""

$calcpad = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue

if (-not $calcpad) {
    Write-Host "ERROR: Calcpad no esta ejecutandose" -ForegroundColor Red
    Write-Host "Ejecuta primero: Calcpad.Wpf\bin\Release\net10.0-windows\Calcpad.exe" -ForegroundColor Yellow
    exit 1
}

Write-Host "Calcpad ejecutandose (PID: $($calcpad.Id))" -ForegroundColor Green
Write-Host ""

# Cargar UI Automation
try {
    Add-Type -AssemblyName UIAutomationClient
    Add-Type -AssemblyName UIAutomationTypes
    Write-Host "UI Automation cargado correctamente" -ForegroundColor Green
} catch {
    Write-Host "ERROR: No se pudo cargar UI Automation" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Buscando ventana de Calcpad..." -ForegroundColor Cyan

$root = [System.Windows.Automation.AutomationElement]::RootElement
$processCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    $calcpad.Id
)

try {
    $window = $root.FindFirst(
        [System.Windows.Automation.TreeScope]::Children,
        $processCondition
    )

    if ($window) {
        Write-Host "Ventana encontrada: $($window.Current.Name)" -ForegroundColor Green
        Write-Host "BoundingRect: $($window.Current.BoundingRectangle)" -ForegroundColor Gray
        Write-Host ""

        # Buscar botones de modo
        Write-Host "Buscando boton de modo..." -ForegroundColor Cyan
        $buttonCondition = New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
            [System.Windows.Automation.ControlType]::Button
        )

        try {
            $buttons = $window.FindAll(
                [System.Windows.Automation.TreeScope]::Descendants,
                $buttonCondition
            )

            if ($buttons.Count -gt 0) {
                foreach ($btn in $buttons) {
                    $name = $btn.Current.Name
                    if ($name -match "Code|mathCAD|Visual") {
                        Write-Host "  Boton: $name - Enabled: $($btn.Current.IsEnabled)" -ForegroundColor Yellow
                    }
                }
            }
        } catch {
            Write-Host "  No se pudieron enumerar botones" -ForegroundColor Yellow
        }

        Write-Host ""
        Write-Host "Instrucciones:" -ForegroundColor White
        Write-Host "1. Presiona el boton 'mathCAD' para cambiar a modo Visual" -ForegroundColor Gray
        Write-Host "2. Abre un archivo (Ctrl+O)" -ForegroundColor Gray
        Write-Host "3. Verifica que el contenido se renderiza correctamente" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Si el contenido aparece, el FIX funciona correctamente!" -ForegroundColor Green

    } else {
        Write-Host "ERROR: No se pudo encontrar la ventana" -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR durante la busqueda: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== FIN ===" -ForegroundColor Cyan
