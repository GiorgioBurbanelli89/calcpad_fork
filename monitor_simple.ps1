# Monitor simple en tiempo real - sin colores
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$lastPreviewText = ""
$lastEditorText = ""
$lastEditorVisible = $false
$iteration = 0

function Get-Timestamp {
    return (Get-Date).ToString("HH:mm:ss")
}

Write-Output "========================================="
Write-Output "MONITOR PREVIEW SYNC - TIEMPO REAL"
Write-Output "========================================="
Write-Output "[$(Get-Timestamp)] Iniciando..."
Write-Output ""

while ($true) {
    $iteration++

    # Encontrar Calcpad
    $automation = [System.Windows.Automation.AutomationElement]::RootElement
    $windows = $automation.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)

    $calcpadWindow = $null
    foreach ($window in $windows) {
        if ($window.Current.Name -like "*Calcpad*") {
            $calcpadWindow = $window
            break
        }
    }

    if ($null -eq $calcpadWindow) {
        Write-Output "[$(Get-Timestamp)] Esperando Calcpad..."
        Start-Sleep -Seconds 1
        continue
    }

    # Obtener elementos
    $allElements = $calcpadWindow.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)

    # Buscar PreviewTextBlock
    $currentPreviewText = ""
    foreach ($element in $allElements) {
        if ($element.Current.AutomationId -eq "PreviewTextBlock") {
            $currentPreviewText = $element.Current.Name
            break
        }
    }

    # Buscar PreviewEditor
    $currentEditorText = ""
    $isEditorVisible = $false
    foreach ($element in $allElements) {
        $autoId = $element.Current.AutomationId
        if ($autoId -eq "PreviewEditor") {
            $isEditorVisible = -not $element.Current.IsOffscreen
            try {
                $valuePattern = $element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                if ($null -ne $valuePattern) {
                    $currentEditorText = $valuePattern.Current.Value
                }
            } catch {}
            break
        }
    }

    # Detectar cambios
    $hasChanges = $false

    if ($currentPreviewText -ne $lastPreviewText) {
        Write-Output ""
        Write-Output "[$(Get-Timestamp)] CAMBIO PreviewTextBlock:"
        Write-Output "  Antes: $lastPreviewText"
        Write-Output "  Ahora: $currentPreviewText"
        $lastPreviewText = $currentPreviewText
        $hasChanges = $true
    }

    if ($currentEditorText -ne $lastEditorText) {
        Write-Output ""
        Write-Output "[$(Get-Timestamp)] CAMBIO PreviewEditor texto:"
        Write-Output "  Antes: $lastEditorText"
        Write-Output "  Ahora: $currentEditorText"
        $lastEditorText = $currentEditorText
        $hasChanges = $true
    }

    if ($isEditorVisible -ne $lastEditorVisible) {
        Write-Output ""
        Write-Output "[$(Get-Timestamp)] CAMBIO PreviewEditor visibilidad:"
        Write-Output "  Antes: $(if ($lastEditorVisible) {'VISIBLE'} else {'OCULTO'})"
        Write-Output "  Ahora: $(if ($isEditorVisible) {'VISIBLE'} else {'OCULTO'})"
        $lastEditorVisible = $isEditorVisible
        $hasChanges = $true
    }

    # Estado actual cada 5 iteraciones
    if ($hasChanges -or ($iteration % 5 -eq 0)) {
        Write-Output ""
        Write-Output "--- ESTADO ACTUAL (Iter: $iteration) ---"
        Write-Output "PreviewTextBlock: $currentPreviewText"
        Write-Output "PreviewEditor: $(if ($isEditorVisible) {'VISIBLE'} else {'OCULTO'}) - Texto: $currentEditorText"
        Write-Output "--------------------------------------"
    } else {
        Write-Output "." -NoNewline
    }

    Start-Sleep -Milliseconds 500
}
