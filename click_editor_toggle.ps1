# Click en EditorToggleButton para cambiar a MathEditor
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

Write-Output "Buscando Calcpad..."

$automation = [System.Windows.Automation.AutomationElement]::RootElement
$windows = $automation.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)

$calcpadWindow = $null
foreach ($window in $windows) {
    if ($window.Current.Name -like "*Calcpad*") {
        $calcpadWindow = $window
        Write-Output "Calcpad encontrado"
        break
    }
}

if ($null -eq $calcpadWindow) {
    Write-Output "ERROR: No se encontro Calcpad"
    exit 1
}

# Buscar EditorToggleButton
Write-Output "Buscando EditorToggleButton..."
$allElements = $calcpadWindow.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)

$toggleButton = $null
foreach ($element in $allElements) {
    if ($element.Current.AutomationId -eq "EditorToggleButton") {
        $toggleButton = $element
        Write-Output "EditorToggleButton encontrado"
        break
    }
}

if ($null -eq $toggleButton) {
    Write-Output "ERROR: No se encontro EditorToggleButton"
    exit 1
}

# Hacer click usando InvokePattern
Write-Output "Haciendo click en EditorToggleButton..."
try {
    $invokePattern = $toggleButton.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    if ($null -ne $invokePattern) {
        $invokePattern.Invoke()
        Write-Output "Click exitoso"
        Start-Sleep -Seconds 2
    } else {
        Write-Output "ERROR: No soporta InvokePattern"
    }
} catch {
    Write-Output "ERROR: $_"
}

# Verificar si ahora aparecen los controles del MathEditor
Write-Output ""
Write-Output "Verificando controles del MathEditor..."
Start-Sleep -Seconds 1

$allElements = $calcpadWindow.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)

$found = $false
foreach ($element in $allElements) {
    $autoId = $element.Current.AutomationId
    if ($autoId -eq "PreviewTextBlock" -or $autoId -eq "PreviewEditor" -or $autoId -eq "EditorCanvas") {
        Write-Output "  ✓ $autoId encontrado"
        $found = $true
    }
}

if (-not $found) {
    Write-Output "  ⚠ Controles del MathEditor NO encontrados aun"
}

Write-Output ""
Write-Output "Listo"
