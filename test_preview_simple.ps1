Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

Write-Output "TEST SINCRONIZACION PREVIEW"
Write-Output "==========================="
Write-Output ""

$automation = [System.Windows.Automation.AutomationElement]::RootElement
$windows = $automation.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)

$calcpadWindow = $null
foreach ($window in $windows) {
    if ($window.Current.Name -like "*Calcpad*") {
        $calcpadWindow = $window
        Write-Output "Calcpad encontrado: $($window.Current.Name)"
        break
    }
}

if ($null -eq $calcpadWindow) {
    Write-Output "ERROR: Calcpad no encontrado"
    exit 1
}

Start-Sleep -Seconds 1

Write-Output ""
Write-Output "Buscando controles..."
$allElements = $calcpadWindow.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
Write-Output "Total elementos: $($allElements.Count)"

Write-Output ""
Write-Output "PreviewTextBlock:"
foreach ($element in $allElements) {
    if ($element.Current.AutomationId -eq "PreviewTextBlock") {
        $text = $element.Current.Name
        $isVisible = -not $element.Current.IsOffscreen
        Write-Output "  Encontrado: SI"
        Write-Output "  Texto: $text"
        Write-Output "  Visible: $isVisible"
        break
    }
}

Write-Output ""
Write-Output "PreviewEditor (AvalonEdit):"
$found = $false
foreach ($element in $allElements) {
    $className = $element.Current.ClassName
    $autoId = $element.Current.AutomationId

    if ($className -like "*TextEditor*" -and $autoId -eq "PreviewEditor") {
        $isVisible = -not $element.Current.IsOffscreen
        Write-Output "  Encontrado: SI"
        Write-Output "  ClassName: $className"
        Write-Output "  Visible: $isVisible"
        $found = $true
        break
    }
}

if (-not $found) {
    Write-Output "  Encontrado: NO (esto es normal si no se ha hecho click en preview)"
}

Write-Output ""
Write-Output "EditorCanvas:"
foreach ($element in $allElements) {
    if ($element.Current.AutomationId -eq "EditorCanvas") {
        Write-Output "  Encontrado: SI"
        break
    }
}

Write-Output ""
Write-Output "==========================="
Write-Output "INSTRUCCIONES:"
Write-Output "1. Haz CLICK en el preview bar (texto amarillo)"
Write-Output "2. Escribe en el editor que aparece"
Write-Output "3. Verifica que se actualiza el canvas"
Write-Output "4. Presiona ENTER para cerrar"
Write-Output "==========================="
