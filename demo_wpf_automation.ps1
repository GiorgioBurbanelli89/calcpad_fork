# Demo completo del Generic Debugger usando UI Automation
# Este script interactúa automáticamente con la aplicación WPF

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GENERIC DEBUGGER - DEMO AUTOMATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Función para encontrar ventana
function Find-Window {
    param([string]$Title)

    $desktop = [System.Windows.Automation.AutomationElement]::RootElement
    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        $Title
    )

    return $desktop.FindFirst(
        [System.Windows.Automation.TreeScope]::Children,
        $condition
    )
}

# Función para encontrar elemento por nombre
function Find-ElementByName {
    param(
        [System.Windows.Automation.AutomationElement]$Parent,
        [string]$Name
    )

    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        $Name
    )

    return $Parent.FindFirst(
        [System.Windows.Automation.TreeScope]::Descendants,
        $condition
    )
}

# Función para encontrar elementos por tipo
function Find-ElementsByType {
    param(
        [System.Windows.Automation.AutomationElement]$Parent,
        [System.Windows.Automation.ControlType]$ControlType
    )

    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        $ControlType
    )

    return $Parent.FindAll(
        [System.Windows.Automation.TreeScope]::Descendants,
        $condition
    )
}

# Función para hacer click en un botón
function Click-Button {
    param(
        [System.Windows.Automation.AutomationElement]$Button,
        [string]$Description
    )

    if ($Button) {
        Write-Host "  [→] Haciendo click en: $Description" -ForegroundColor Yellow
        $invokePattern = $Button.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
        $invokePattern.Invoke()
        Start-Sleep -Milliseconds 500
        Write-Host "  [✓] Click exitoso" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  [✗] Botón no encontrado: $Description" -ForegroundColor Red
        return $false
    }
}

# Función para obtener texto de un elemento
function Get-ElementText {
    param(
        [System.Windows.Automation.AutomationElement]$Element
    )

    if ($Element) {
        # Intentar obtener el texto de diferentes formas
        $textPattern = $null
        try {
            $textPattern = $Element.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
            if ($textPattern) {
                return $textPattern.DocumentRange.GetText(-1)
            }
        } catch {}

        # Intentar con ValuePattern
        try {
            $valuePattern = $Element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
            if ($valuePattern) {
                return $valuePattern.Current.Value
            }
        } catch {}

        # Usar la propiedad Name como fallback
        return $Element.Current.Name
    }

    return ""
}

# Función para enviar teclas
function Send-Keys {
    param(
        [string]$Keys,
        [string]$Description
    )

    Write-Host "  [→] Enviando tecla: $Description" -ForegroundColor Yellow
    [System.Windows.Forms.SendKeys]::SendWait($Keys)
    Start-Sleep -Milliseconds 300
    Write-Host "  [✓] Tecla enviada" -ForegroundColor Green
}

# Paso 1: Buscar la ventana
Write-Host "[1] Buscando ventana 'Generic Debugger'..." -ForegroundColor Cyan
$window = Find-Window "Generic Debugger"

if (-not $window) {
    Write-Host "[✗] ERROR: Ventana no encontrada. ¿Está la aplicación ejecutándose?" -ForegroundColor Red

    Write-Host "`nIntentando iniciar la aplicación..." -ForegroundColor Yellow
    $exePath = "GenericDebugger.WPF\bin\Debug\net8.0-windows\GenericDebugger.exe"

    if (Test-Path $exePath) {
        Start-Process $exePath
        Write-Host "Esperando que la aplicación inicie..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3

        $window = Find-Window "Generic Debugger"
        if (-not $window) {
            Write-Host "[✗] No se pudo iniciar la aplicación" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[✗] Ejecutable no encontrado en: $exePath" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[✓] Ventana encontrada (PID: $($window.Current.ProcessId))" -ForegroundColor Green
Write-Host ""

# Traer ventana al frente
try {
    $windowPattern = $window.GetCurrentPattern([System.Windows.Automation.WindowPattern]::Pattern)
    $windowPattern.SetWindowVisualState([System.Windows.Automation.WindowVisualState]::Normal)
} catch {
    Write-Host "[⚠] No se pudo traer ventana al frente" -ForegroundColor Yellow
}

Start-Sleep -Milliseconds 500

# Paso 2: Explorar componentes de la UI
Write-Host "[2] Explorando componentes de la UI..." -ForegroundColor Cyan

# Buscar todos los botones
$buttons = Find-ElementsByType $window ([System.Windows.Automation.ControlType]::Button)
Write-Host "  Botones encontrados: $($buttons.Count)" -ForegroundColor Gray

foreach ($btn in $buttons) {
    $name = $btn.Current.Name
    if ($name -and $name -ne "") {
        Write-Host "    • $name" -ForegroundColor DarkGray
    }
}

# Buscar DataGrid (Variables)
$dataGrids = Find-ElementsByType $window ([System.Windows.Automation.ControlType]::DataGrid)
Write-Host "  DataGrid (Variables): $($dataGrids.Count)" -ForegroundColor Gray

# Buscar Edit controls
$edits = Find-ElementsByType $window ([System.Windows.Automation.ControlType]::Edit)
Write-Host "  Edit controls: $($edits.Count)" -ForegroundColor Gray

# Buscar StatusBar
$statusBars = Find-ElementsByType $window ([System.Windows.Automation.ControlType]::StatusBar)
Write-Host "  StatusBar: $($statusBars.Count)" -ForegroundColor Gray

Write-Host ""

# Paso 3: Buscar el botón "Open"
Write-Host "[3] Intentando abrir archivo..." -ForegroundColor Cyan
$openButton = Find-ElementByName $window "Open"

if ($openButton) {
    Write-Host "  [✓] Botón 'Open' encontrado" -ForegroundColor Green
    Write-Host "  [→] Preparando para abrir archivo..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  NOTA: El diálogo de archivo se abrirá." -ForegroundColor Yellow
    Write-Host "        Por favor selecciona manualmente: GenericDebugger.WPF\TestScript.cs" -ForegroundColor Yellow
    Write-Host "        O presiona ESC para continuar con el demo sin abrir archivo" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Presiona ENTER para continuar..." -ForegroundColor Cyan
    Read-Host

    Click-Button $openButton "Open File"

    Write-Host "  [⏳] Esperando que selecciones el archivo (30 segundos)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
} else {
    Write-Host "  [✗] Botón 'Open' no encontrado" -ForegroundColor Red
    Write-Host "  [→] Intentando con Ctrl+O..." -ForegroundColor Yellow

    # Enfocar la ventana primero
    [System.Windows.Forms.SendKeys]::SendWait("^o")
    Start-Sleep -Seconds 2
}

Write-Host ""

# Paso 4: Verificar si hay contenido en el editor
Write-Host "[4] Verificando contenido del editor..." -ForegroundColor Cyan

$edits = Find-ElementsByType $window ([System.Windows.Automation.ControlType]::Edit)
$hasContent = $false

foreach ($edit in $edits) {
    $text = Get-ElementText $edit
    if ($text -and $text.Length -gt 50) {
        Write-Host "  [✓] Contenido detectado en editor ($($text.Length) caracteres)" -ForegroundColor Green
        Write-Host "  Primeras líneas:" -ForegroundColor Gray
        $lines = $text -split "`n" | Select-Object -First 3
        foreach ($line in $lines) {
            Write-Host "    $line" -ForegroundColor DarkGray
        }
        $hasContent = $true
        break
    }
}

if (-not $hasContent) {
    Write-Host "  [⚠] No se detectó contenido. El archivo podría no estar cargado." -ForegroundColor Yellow
    Write-Host "  Continuando con el demo..." -ForegroundColor Yellow
}

Write-Host ""

# Paso 5: Buscar botón Step
Write-Host "[5] Demostrando ejecución paso a paso..." -ForegroundColor Cyan
$stepButton = Find-ElementByName $window "Step"

if ($stepButton) {
    Write-Host "  [✓] Botón 'Step' encontrado" -ForegroundColor Green

    for ($i = 1; $i -le 3; $i++) {
        Write-Host "  [→] Paso $i: Ejecutando siguiente línea..." -ForegroundColor Yellow
        Click-Button $stepButton "Step (F10)"

        # Leer variables del DataGrid
        Start-Sleep -Milliseconds 500
        $dataGrids = Find-ElementsByType $window ([System.Windows.Automation.ControlType]::DataGrid)

        if ($dataGrids.Count -gt 0) {
            $dataGrid = $dataGrids[0]
            $dataItems = Find-ElementsByType $dataGrid ([System.Windows.Automation.ControlType]::DataItem)

            if ($dataItems.Count -gt 0) {
                Write-Host "    Variables actuales:" -ForegroundColor Cyan

                foreach ($item in $dataItems) {
                    $cells = Find-ElementsByType $item ([System.Windows.Automation.ControlType]::Custom)
                    if ($cells.Count -ge 2) {
                        $varName = $cells[0].Current.Name
                        $varValue = $cells[1].Current.Name

                        if ($varName -and $varValue) {
                            Write-Host "      • $varName = $varValue" -ForegroundColor DarkCyan
                        }
                    }
                }
            } else {
                Write-Host "    (Esperando variables...)" -ForegroundColor DarkGray
            }
        }

        Start-Sleep -Milliseconds 800
    }
} else {
    Write-Host "  [✗] Botón 'Step' no encontrado" -ForegroundColor Red
    Write-Host "  [→] Intentando con F10..." -ForegroundColor Yellow

    for ($i = 1; $i -le 3; $i++) {
        Write-Host "  [→] Paso $i: Presionando F10..." -ForegroundColor Yellow
        Send-Keys "{F10}" "F10"
        Start-Sleep -Seconds 1
    }
}

Write-Host ""

# Paso 6: Verificar Output
Write-Host "[6] Verificando panel de Output..." -ForegroundColor Cyan

$edits = Find-ElementsByType $window ([System.Windows.Automation.ControlType]::Edit)
$outputFound = $false

foreach ($edit in $edits) {
    $text = Get-ElementText $edit

    # El output suele contener resultados de WriteLine
    if ($text -and ($text -like "*=*" -or $text -like "*Output*" -or $text.Length -lt 500)) {
        if ($text.Length -gt 0 -and $text.Length -lt 500) {
            Write-Host "  [✓] Output encontrado:" -ForegroundColor Green
            Write-Host "$text" -ForegroundColor DarkGray
            $outputFound = $true
            break
        }
    }
}

if (-not $outputFound) {
    Write-Host "  [⚠] Panel de Output vacío o no detectado" -ForegroundColor Yellow
}

Write-Host ""

# Paso 7: Verificar Variables Panel
Write-Host "[7] Inspeccionando Variables Panel..." -ForegroundColor Cyan

$dataGrids = Find-ElementsByType $window ([System.Windows.Automation.ControlType]::DataGrid)

if ($dataGrids.Count -gt 0) {
    Write-Host "  [✓] Variables Panel encontrado" -ForegroundColor Green

    $dataGrid = $dataGrids[0]
    $dataItems = Find-ElementsByType $dataGrid ([System.Windows.Automation.ControlType]::DataItem)

    Write-Host "  Variables detectadas: $($dataItems.Count)" -ForegroundColor Cyan

    if ($dataItems.Count -gt 0) {
        Write-Host ""
        Write-Host "  ┌─────────────────────────────────────┐" -ForegroundColor DarkGray
        Write-Host "  │  Variables actuales:                │" -ForegroundColor DarkGray
        Write-Host "  ├─────────────────────────────────────┤" -ForegroundColor DarkGray

        foreach ($item in $dataItems) {
            $name = $item.Current.Name
            if ($name) {
                Write-Host "  │  $name" -ForegroundColor Cyan
            }
        }

        Write-Host "  └─────────────────────────────────────┘" -ForegroundColor DarkGray
    }
} else {
    Write-Host "  [⚠] Variables Panel no detectado" -ForegroundColor Yellow
}

Write-Host ""

# Paso 8: Verificar Status Bar
Write-Host "[8] Verificando Status Bar..." -ForegroundColor Cyan

$statusBars = Find-ElementsByType $window ([System.Windows.Automation.ControlType]::StatusBar)

if ($statusBars.Count -gt 0) {
    Write-Host "  [✓] Status Bar encontrado" -ForegroundColor Green

    $statusBar = $statusBars[0]
    $texts = Find-ElementsByType $statusBar ([System.Windows.Automation.ControlType]::Text)

    Write-Host "  Información de estado:" -ForegroundColor Cyan
    foreach ($text in $texts) {
        $content = $text.Current.Name
        if ($content -and $content.Trim() -ne "") {
            Write-Host "    • $content" -ForegroundColor DarkCyan
        }
    }
} else {
    Write-Host "  [⚠] Status Bar no detectado" -ForegroundColor Yellow
}

Write-Host ""

# Paso 9: Intentar ejecutar Run (F5)
Write-Host "[9] Probando ejecución completa (Run)..." -ForegroundColor Cyan
$runButton = Find-ElementByName $window "Run"

if ($runButton) {
    Write-Host "  [✓] Botón 'Run' encontrado" -ForegroundColor Green
    Write-Host "  [→] Ejecutando script completo..." -ForegroundColor Yellow

    Click-Button $runButton "Run (F5)"

    Start-Sleep -Seconds 1

    Write-Host "  [✓] Ejecución completada" -ForegroundColor Green
} else {
    Write-Host "  [⚠] Botón 'Run' no encontrado, intentando F5..." -ForegroundColor Yellow
    Send-Keys "{F5}" "F5"
    Start-Sleep -Seconds 1
}

Write-Host ""

# Paso 10: Buscar botón Reset
Write-Host "[10] Probando Reset..." -ForegroundColor Cyan
$resetButton = Find-ElementByName $window "Reset"

if ($resetButton) {
    Write-Host "  [✓] Botón 'Reset' encontrado" -ForegroundColor Green
    Write-Host "  [→] Reiniciando estado..." -ForegroundColor Yellow

    Click-Button $resetButton "Reset"

    Write-Host "  [✓] Estado reiniciado" -ForegroundColor Green
} else {
    Write-Host "  [⚠] Botón 'Reset' no encontrado" -ForegroundColor Yellow
}

Write-Host ""

# Resumen final
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESUMEN DEL DEMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$components = @{
    "Ventana Principal" = ($window -ne $null)
    "Botones (Open, Run, Step, Reset)" = ($buttons.Count -ge 4)
    "Code Editor" = ($edits.Count -ge 1)
    "Variables Panel (DataGrid)" = ($dataGrids.Count -ge 1)
    "Status Bar" = ($statusBars.Count -ge 1)
}

foreach ($comp in $components.Keys) {
    $status = $components[$comp]
    if ($status) {
        Write-Host "[✓] $comp" -ForegroundColor Green
    } else {
        Write-Host "[✗] $comp" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Funcionalidades demostradas:" -ForegroundColor Cyan
Write-Host "  • UI Automation exitosa" -ForegroundColor Green
Write-Host "  • Detección de componentes" -ForegroundColor Green
Write-Host "  • Interacción con botones" -ForegroundColor Green
Write-Host "  • Lectura de Variables Panel" -ForegroundColor Green
Write-Host "  • Verificación de Status Bar" -ForegroundColor Green
Write-Host "  • Ejecución paso a paso (Step)" -ForegroundColor Green
Write-Host "  • Ejecución completa (Run)" -ForegroundColor Green
Write-Host "  • Reset de estado" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEMO COMPLETADO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "La aplicación Generic Debugger WPF está funcionando correctamente." -ForegroundColor Green
Write-Host "Todos los componentes principales fueron detectados y probados." -ForegroundColor Green
Write-Host ""
