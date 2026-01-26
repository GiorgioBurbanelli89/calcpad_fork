# Monitor de UI de Calcpad - observa elementos en tiempo real
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

Write-Host "=== Monitor de UI de Calcpad ===" -ForegroundColor Cyan
Write-Host "Este script monitorea los cambios en la UI mientras usas Calcpad"
Write-Host "Presiona Ctrl+C para detener`n"

# Esperar a que Calcpad este corriendo
$maxWait = 30
$waited = 0
while (-not (Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue) -and $waited -lt $maxWait) {
    Write-Host "Esperando a Calcpad..."
    Start-Sleep -Seconds 1
    $waited++
}

$calcpadProcess = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $calcpadProcess) {
    Write-Host "ERROR: Calcpad no encontrado" -ForegroundColor Red
    exit 1
}

$hwnd = $calcpadProcess.MainWindowHandle
$automation = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
Write-Host "Calcpad conectado (PID: $($calcpadProcess.Id))" -ForegroundColor Green

# Funcion para obtener informacion de elementos
function Get-ElementInfo {
    param($element)
    if ($null -eq $element) { return "null" }

    $name = $element.Current.Name
    $type = $element.Current.ControlType.ProgrammaticName -replace "ControlType.", ""
    $automationId = $element.Current.AutomationId
    $bounds = $element.Current.BoundingRectangle

    return "[$type] AutomationId='$automationId' Name='$name' Bounds=($($bounds.Left),$($bounds.Top),$($bounds.Width),$($bounds.Height))"
}

# Funcion para buscar TextBoxes visibles
function Get-VisibleTextBoxes {
    $textBoxCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Edit
    )

    $textBoxes = $automation.FindAll([System.Windows.Automation.TreeScope]::Descendants, $textBoxCondition)
    return $textBoxes
}

# Funcion para buscar TextBlocks con contenido de preview
function Get-PreviewTextBlocks {
    $textBlockCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Text
    )

    $textBlocks = $automation.FindAll([System.Windows.Automation.TreeScope]::Descendants, $textBlockCondition)
    $previews = @()

    foreach ($tb in $textBlocks) {
        $name = $tb.Current.Name
        if ($name -match "@\{" -or $name -match "Ln \d+:" -or $name -match "Calcpad:") {
            $previews += $tb
        }
    }
    return $previews
}

# Funcion para obtener el elemento con foco
function Get-FocusedElement {
    try {
        return [System.Windows.Automation.AutomationElement]::FocusedElement
    } catch {
        return $null
    }
}

$lastFocusInfo = ""
$lastTextBoxCount = 0
$lastPreviewText = ""

Write-Host "`nMonitoreando... (actualiza cada 500ms)`n" -ForegroundColor Yellow

while ($true) {
    try {
        # Verificar que Calcpad siga corriendo
        if (-not (Get-Process -Id $calcpadProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Host "`nCalcpad cerrado. Saliendo..." -ForegroundColor Red
            break
        }

        # Obtener elemento con foco
        $focused = Get-FocusedElement
        $focusInfo = Get-ElementInfo $focused

        if ($focusInfo -ne $lastFocusInfo) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] FOCO: $focusInfo" -ForegroundColor Magenta
            $lastFocusInfo = $focusInfo
        }

        # Contar TextBoxes visibles
        $textBoxes = Get-VisibleTextBoxes
        if ($textBoxes.Count -ne $lastTextBoxCount) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] TextBoxes visibles: $($textBoxes.Count)" -ForegroundColor Cyan
            foreach ($tb in $textBoxes) {
                $info = Get-ElementInfo $tb
                Write-Host "    $info"

                # Intentar obtener el texto del TextBox
                $valuePattern = $tb.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern) -as [System.Windows.Automation.ValuePattern]
                if ($valuePattern) {
                    $value = $valuePattern.Current.Value
                    Write-Host "    Texto: '$value'" -ForegroundColor Green
                }
            }
            $lastTextBoxCount = $textBoxes.Count
        }

        # Buscar TextBlocks de preview
        $previews = Get-PreviewTextBlocks
        foreach ($preview in $previews) {
            $previewText = $preview.Current.Name
            if ($previewText -ne $lastPreviewText) {
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Preview: '$previewText'" -ForegroundColor Yellow
                $lastPreviewText = $previewText
            }
        }

        Start-Sleep -Milliseconds 500
    }
    catch {
        Write-Host "Error: $_" -ForegroundColor Red
        Start-Sleep -Seconds 1
    }
}
