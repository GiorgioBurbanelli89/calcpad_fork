# Inspección completa de todos los controles de Calcpad
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

Write-Output "========================================="
Write-Output "INSPECCION COMPLETA DE CONTROLES"
Write-Output "=========================================`n"

# Encontrar Calcpad
$automation = [System.Windows.Automation.AutomationElement]::RootElement
$windows = $automation.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)

$calcpadWindow = $null
foreach ($window in $windows) {
    if ($window.Current.Name -like "*Calcpad*") {
        $calcpadWindow = $window
        Write-Output "Ventana encontrada: $($window.Current.Name)`n"
        break
    }
}

if ($null -eq $calcpadWindow) {
    Write-Output "ERROR: No se encontro Calcpad"
    exit
}

# Obtener TODOS los elementos
Write-Output "Obteniendo todos los elementos..."
try {
    $allElements = $calcpadWindow.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    Write-Output "Total elementos encontrados: $($allElements.Count)`n"
} catch {
    Write-Output "ERROR al obtener elementos: $_"
    exit
}

# Listar elementos relevantes
Write-Output "========================================="
Write-Output "ELEMENTOS RELEVANTES:"
Write-Output "========================================="

$count = 0
foreach ($element in $allElements) {
    $autoId = $element.Current.AutomationId
    $name = $element.Current.Name
    $className = $element.Current.ClassName
    $controlType = $element.Current.ControlType.ProgrammaticName

    # Filtrar solo elementos interesantes
    $isRelevant = $false

    # Buscar elementos relacionados con Preview o Editor
    if ($autoId -like "*Preview*" -or $name -like "*Preview*") {
        $isRelevant = $true
    }
    if ($autoId -like "*Editor*" -or $name -like "*Editor*") {
        $isRelevant = $true
    }
    if ($className -like "*TextEditor*" -or $className -eq "TextBox") {
        $isRelevant = $true
    }
    if ($className -eq "Canvas" -and $autoId -ne "") {
        $isRelevant = $true
    }
    if ($autoId -eq "PreviewTextBlock" -or $autoId -eq "PreviewEditor" -or $autoId -eq "EditorCanvas") {
        $isRelevant = $true
    }

    if ($isRelevant) {
        $count++
        Write-Output "`n[$count] Control:"
        Write-Output "  AutomationId: $autoId"
        Write-Output "  Name: $name"
        Write-Output "  ClassName: $className"
        Write-Output "  ControlType: $controlType"

        $isOffscreen = $element.Current.IsOffscreen
        Write-Output "  Visible: $(if (-not $isOffscreen) {'SI'} else {'NO'})"

        # Intentar obtener valor/texto
        try {
            $valuePattern = $element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
            if ($null -ne $valuePattern) {
                $value = $valuePattern.Current.Value
                Write-Output "  Valor/Texto: '$value'"
            }
        } catch {}
    }
}

Write-Output "`n========================================="
Write-Output "Total elementos relevantes: $count"
Write-Output "========================================="
