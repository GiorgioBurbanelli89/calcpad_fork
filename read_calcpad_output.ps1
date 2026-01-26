# Lee el contenido de output de Calcpad usando UI Automation

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$calcpad = Get-Process | Where-Object { $_.ProcessName -eq "Calcpad" }

if (-not $calcpad) {
    Write-Host "ERROR: Calcpad no esta ejecutandose"
    exit 1
}

Write-Host "Buscando elementos de UI en Calcpad..."
Write-Host ""

$automation = [System.Windows.Automation.AutomationElement]::RootElement
$condition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    $calcpad.Id
)

$window = $automation.FindFirst([System.Windows.Automation.TreeScope]::Children, $condition)

if (-not $window) {
    Write-Host "ERROR: No se pudo encontrar ventana"
    exit 1
}

Write-Host "Ventana: $($window.Current.Name)"
Write-Host ""

# Buscar elementos Edit (textbox/richtextbox)
$editCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Edit
)

$edits = $window.FindAll([System.Windows.Automation.TreeScope]::Descendants, $editCondition)

Write-Host "Elementos de texto encontrados: $($edits.Count)"
Write-Host ""

$count = 0
foreach ($edit in $edits) {
    $count++
    $name = $edit.Current.Name
    $className = $edit.Current.ClassName
    $id = $edit.Current.AutomationId

    # Try to get text value
    $valuePattern = $null
    try {
        $valuePattern = $edit.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
    } catch {}

    $text = ""
    if ($valuePattern) {
        $text = $valuePattern.Current.Value
    }

    Write-Host "[$count] Elemento de texto:"
    Write-Host "    Nombre: $name"
    Write-Host "    Clase: $className"
    Write-Host "    ID: $id"

    if ($text) {
        $preview = if ($text.Length -gt 200) { $text.Substring(0, 200) + "..." } else { $text }
        Write-Host "    Texto ($($text.Length) chars): $preview"
    }
    Write-Host ""

    if ($count -ge 5) {
        Write-Host "... (mostrando primeros 5)"
        break
    }
}

# Buscar elementos Document (WebView2 o similar)
$documentCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Document
)

$documents = $window.FindAll([System.Windows.Automation.TreeScope]::Descendants, $documentCondition)

Write-Host ""
Write-Host "Elementos documento encontrados: $($documents.Count)"
Write-Host ""

foreach ($doc in $documents) {
    Write-Host "Documento:"
    Write-Host "    Nombre: $($doc.Current.Name)"
    Write-Host "    Clase: $($doc.Current.ClassName)"
}
