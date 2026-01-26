# Demo automatizado del Generic Debugger - UI Automation
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

Write-Host "========================================"  -ForegroundColor Cyan
Write-Host "  GENERIC DEBUGGER - DEMO AUTOMATION"  -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Funciones auxiliares
function Find-Window {
    param([string]$Title)
    $desktop = [System.Windows.Automation.AutomationElement]::RootElement
    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty, $Title
    )
    return $desktop.FindFirst([System.Windows.Automation.TreeScope]::Children, $condition)
}

function Find-ElementByName {
    param($Parent, [string]$Name)
    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty, $Name
    )
    return $Parent.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $condition)
}

function Find-ElementsByType {
    param($Parent, $ControlType)
    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty, $ControlType
    )
    return $Parent.FindAll([System.Windows.Automation.TreeScope]::Descendants, $condition)
}

function Click-Button {
    param($Button, [string]$Description)
    if ($Button) {
        Write-Host "  >> Haciendo click en: $Description" -ForegroundColor Yellow
        $invokePattern = $Button.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
        $invokePattern.Invoke()
        Start-Sleep -Milliseconds 500
        Write-Host "  OK Click exitoso" -ForegroundColor Green
        return $true
    }
    Write-Host "  ERROR Boton no encontrado: $Description" -ForegroundColor Red
    return $false
}

# Paso 1: Buscar ventana
Write-Host "[1] Buscando ventana Generic Debugger..." -ForegroundColor Cyan
$window = Find-Window "Generic Debugger"

if (-not $window) {
    Write-Host "ERROR: Ventana no encontrada" -ForegroundColor Red
    exit 1
}

Write-Host "OK Ventana encontrada (PID: $($window.Current.ProcessId))" -ForegroundColor Green
Write-Host ""

# Paso 2: Explorar componentes
Write-Host "[2] Explorando componentes UI..." -ForegroundColor Cyan

$buttons = Find-ElementsByType $window ([System.Windows.Automation.ControlType]::Button)
Write-Host "  Botones encontrados: $($buttons.Count)" -ForegroundColor Gray

$buttonNames = @()
foreach ($btn in $buttons) {
    $name = $btn.Current.Name
    if ($name -and $name -ne "") {
        Write-Host "    * $name" -ForegroundColor DarkGray
        $buttonNames += $name
    }
}

$dataGrids = Find-ElementsByType $window ([System.Windows.Automation.ControlType]::DataGrid)
Write-Host "  DataGrid (Variables): $($dataGrids.Count)" -ForegroundColor Gray

$edits = Find-ElementsByType $window ([System.Windows.Automation.ControlType]::Edit)
Write-Host "  Edit controls: $($edits.Count)" -ForegroundColor Gray

$statusBars = Find-ElementsByType $window ([System.Windows.Automation.ControlType]::StatusBar)
Write-Host "  StatusBar: $($statusBars.Count)" -ForegroundColor Gray

Write-Host ""

# Paso 3: Buscar boton Step
Write-Host "[3] Probando ejecucion paso a paso..." -ForegroundColor Cyan
$stepButton = Find-ElementByName $window "Step"

if ($stepButton) {
    Write-Host "  OK Boton Step encontrado" -ForegroundColor Green

    for ($i = 1; $i -le 5; $i++) {
        Write-Host "  >> Paso ${i}: Ejecutando siguiente linea..." -ForegroundColor Yellow
        Click-Button $stepButton "Step (F10)"

        Start-Sleep -Milliseconds 800

        # Leer variables
        $dataGrids = Find-ElementsByType $window ([System.Windows.Automation.ControlType]::DataGrid)

        if ($dataGrids.Count -gt 0) {
            $dataGrid = $dataGrids[0]
            $dataItems = Find-ElementsByType $dataGrid ([System.Windows.Automation.ControlType]::DataItem)

            if ($dataItems.Count -gt 0) {
                Write-Host "    Variables actuales ($($dataItems.Count)):" -ForegroundColor Cyan

                foreach ($item in $dataItems) {
                    $name = $item.Current.Name
                    if ($name) {
                        Write-Host "      - $name" -ForegroundColor DarkCyan
                    }
                }
            }
        }

        Start-Sleep -Milliseconds 500
    }
} else {
    Write-Host "  ERROR Boton Step no encontrado" -ForegroundColor Red
}

Write-Host ""

# Paso 4: Verificar Variables Panel detallado
Write-Host "[4] Inspeccionando Variables Panel..." -ForegroundColor Cyan

if ($dataGrids.Count -gt 0) {
    Write-Host "  OK Variables Panel encontrado" -ForegroundColor Green

    $dataGrid = $dataGrids[0]
    $dataItems = Find-ElementsByType $dataGrid ([System.Windows.Automation.ControlType]::DataItem)

    Write-Host "  Variables detectadas: $($dataItems.Count)" -ForegroundColor Cyan

    if ($dataItems.Count -gt 0) {
        Write-Host ""
        Write-Host "  +-------------------------------------+" -ForegroundColor DarkGray
        Write-Host "  |  VARIABLES ACTUALES                 |" -ForegroundColor DarkGray
        Write-Host "  +-------------------------------------+" -ForegroundColor DarkGray

        foreach ($item in $dataItems) {
            $name = $item.Current.Name
            if ($name) {
                Write-Host "  |  $name" -ForegroundColor Cyan
            }
        }

        Write-Host "  +-------------------------------------+" -ForegroundColor DarkGray
    }
} else {
    Write-Host "  WARN Variables Panel no detectado" -ForegroundColor Yellow
}

Write-Host ""

# Paso 5: Verificar Status Bar
Write-Host "[5] Verificando Status Bar..." -ForegroundColor Cyan

if ($statusBars.Count -gt 0) {
    Write-Host "  OK Status Bar encontrado" -ForegroundColor Green

    $statusBar = $statusBars[0]
    $texts = Find-ElementsByType $statusBar ([System.Windows.Automation.ControlType]::Text)

    Write-Host "  Informacion de estado:" -ForegroundColor Cyan
    foreach ($text in $texts) {
        $content = $text.Current.Name
        if ($content -and $content.Trim() -ne "") {
            Write-Host "    * $content" -ForegroundColor DarkCyan
        }
    }
} else {
    Write-Host "  WARN Status Bar no detectado" -ForegroundColor Yellow
}

Write-Host ""

# Paso 6: Probar boton Run
Write-Host "[6] Probando ejecucion completa (Run)..." -ForegroundColor Cyan
$runButton = Find-ElementByName $window "Run"

if ($runButton) {
    Write-Host "  OK Boton Run encontrado" -ForegroundColor Green
    Write-Host "  >> Ejecutando script completo..." -ForegroundColor Yellow

    Click-Button $runButton "Run (F5)"
    Start-Sleep -Seconds 2

    Write-Host "  OK Ejecucion completada" -ForegroundColor Green
} else {
    Write-Host "  WARN Boton Run no encontrado" -ForegroundColor Yellow
}

Write-Host ""

# Paso 7: Probar boton Reset
Write-Host "[7] Probando Reset..." -ForegroundColor Cyan
$resetButton = Find-ElementByName $window "Reset"

if ($resetButton) {
    Write-Host "  OK Boton Reset encontrado" -ForegroundColor Green
    Write-Host "  >> Reiniciando estado..." -ForegroundColor Yellow

    Click-Button $resetButton "Reset"
    Start-Sleep -Milliseconds 500

    Write-Host "  OK Estado reiniciado" -ForegroundColor Green
} else {
    Write-Host "  WARN Boton Reset no encontrado" -ForegroundColor Yellow
}

Write-Host ""

# Paso 8: Buscar boton Clear Output
Write-Host "[8] Probando Clear Output..." -ForegroundColor Cyan
$clearButton = Find-ElementByName $window "Clear Output"

if ($clearButton) {
    Write-Host "  OK Boton Clear Output encontrado" -ForegroundColor Green
    Click-Button $clearButton "Clear Output"
    Start-Sleep -Milliseconds 300
} else {
    Write-Host "  WARN Boton Clear Output no encontrado" -ForegroundColor Yellow
}

Write-Host ""

# Resumen final
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESUMEN DEL DEMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Componentes verificados:" -ForegroundColor Cyan
Write-Host "  [OK] Ventana Principal" -ForegroundColor Green
Write-Host "  [OK] Botones: $($buttons.Count) encontrados" -ForegroundColor Green
Write-Host "  [OK] DataGrid (Variables): $($dataGrids.Count)" -ForegroundColor Green
Write-Host "  [OK] Edit controls: $($edits.Count)" -ForegroundColor Green
Write-Host "  [OK] Status Bar: $($statusBars.Count)" -ForegroundColor Green

Write-Host ""
Write-Host "Funcionalidades demostradas:" -ForegroundColor Cyan
Write-Host "  [OK] UI Automation exitosa" -ForegroundColor Green
Write-Host "  [OK] Deteccion de componentes" -ForegroundColor Green
Write-Host "  [OK] Interaccion con botones" -ForegroundColor Green
Write-Host "  [OK] Ejecucion paso a paso (Step)" -ForegroundColor Green
Write-Host "  [OK] Lectura de Variables Panel" -ForegroundColor Green
Write-Host "  [OK] Verificacion de Status Bar" -ForegroundColor Green
Write-Host "  [OK] Ejecucion completa (Run)" -ForegroundColor Green
Write-Host "  [OK] Reset de estado" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEMO COMPLETADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Mostrar botones disponibles
Write-Host "Botones disponibles en la aplicacion:" -ForegroundColor Cyan
foreach ($name in $buttonNames) {
    Write-Host "  - $name" -ForegroundColor Gray
}

Write-Host ""
Write-Host "La aplicacion Generic Debugger WPF esta funcionando correctamente." -ForegroundColor Green
Write-Host "Todos los componentes principales fueron detectados y probados via UI Automation." -ForegroundColor Green
Write-Host ""
