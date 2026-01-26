# Test de sincronización Preview - Final
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

Write-Output "========================================="
Write-Output "TEST SINCRONIZACION PREVIEW FINAL"
Write-Output "========================================="
Write-Output ""

# Buscar Calcpad
Write-Output "[1/6] Buscando ventana de Calcpad..."
$automation = [System.Windows.Automation.AutomationElement]::RootElement
$windows = $automation.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)

$calcpadWindow = $null
foreach ($window in $windows) {
    if ($window.Current.Name -like "*Calcpad*") {
        $calcpadWindow = $window
        Write-Output "  ✓ Encontrado: $($window.Current.Name)"
        break
    }
}

if ($null -eq $calcpadWindow) {
    Write-Output "  ✗ ERROR: No se encontró Calcpad"
    exit 1
}

Start-Sleep -Seconds 2

# Obtener todos los elementos
Write-Output ""
Write-Output "[2/6] Inspeccionando controles..."
$allElements = $calcpadWindow.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
Write-Output "  Total elementos: $($allElements.Count)"

# Buscar PreviewTextBlock
Write-Output ""
Write-Output "[3/6] Buscando PreviewTextBlock..."
$previewTextBlock = $null
foreach ($element in $allElements) {
    if ($element.Current.AutomationId -eq "PreviewTextBlock") {
        $previewTextBlock = $element
        $text = $element.Current.Name
        $isVisible = -not $element.Current.IsOffscreen
        Write-Output "  ✓ PreviewTextBlock encontrado"
        Write-Output "  Texto: '$text'"
        Write-Output "  Visible: $isVisible"
        break
    }
}

if ($null -eq $previewTextBlock) {
    Write-Output "  ⚠ PreviewTextBlock NO encontrado"
}

# Buscar PreviewEditor (AvalonEdit)
Write-Output ""
Write-Output "[4/6] Buscando PreviewEditor (AvalonEdit)..."
$previewEditor = $null
foreach ($element in $allElements) {
    $className = $element.Current.ClassName
    $autoId = $element.Current.AutomationId

    if ($className -like "*TextEditor*" -or $autoId -eq "PreviewEditor") {
        $isVisible = -not $element.Current.IsOffscreen
        Write-Output "  ✓ Encontrado control tipo editor"
        Write-Output "  ClassName: $className"
        Write-Output "  AutomationId: $autoId"
        Write-Output "  Visible: $isVisible"

        if ($autoId -eq "PreviewEditor") {
            $previewEditor = $element
            Write-Output "  ✓✓ Este es PreviewEditor del XAML!"
        }
    }
}

if ($null -eq $previewEditor) {
    Write-Output "  ⚠ PreviewEditor NO encontrado explícitamente"
}

# Buscar EditorCanvas
Write-Output ""
Write-Output "[5/6] Buscando EditorCanvas (MathEditor)..."
foreach ($element in $allElements) {
    $autoId = $element.Current.AutomationId
    if ($autoId -eq "EditorCanvas") {
        Write-Output "  ✓ EditorCanvas encontrado"
        break
    }
}

# Verificar estado del archivo
Write-Output ""
Write-Output "[6/6] Verificando archivo test_code_c.cpd..."
$testFile = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\test_code_c.cpd"
if (Test-Path $testFile) {
    Write-Output "  ✓ Archivo existe"
    Write-Output ""
    Write-Output "  CONTENIDO:"
    Get-Content $testFile | ForEach-Object { Write-Output "  $_" }
} else {
    Write-Output "  ✗ Archivo NO existe"
}

Write-Output ""
Write-Output "========================================="
Write-Output "INSTRUCCIONES PARA PRUEBA MANUAL:"
Write-Output "========================================="
Write-Output "1. Verificar que el preview bar muestra:"
Write-Output "   '@{c} Ln X: codigo...|'"
Write-Output ""
Write-Output "2. Hacer CLICK en el preview bar (texto amarillo)"
Write-Output "   - Debe aparecer un editor AvalonEdit"
Write-Output "   - El TextBlock debe ocultarse"
Write-Output ""
Write-Output "3. Escribir en el editor que aparece"
Write-Output "   - Los cambios deben verse en el canvas"
Write-Output "   - En tiempo real mientras escribes"
Write-Output ""
Write-Output "4. Presionar ENTER"
Write-Output "   - El editor debe cerrarse"
Write-Output "   - El canvas debe actualizarse completamente"
Write-Output ""
Write-Output "========================================="
Write-Output "Test completado"
Write-Output "========================================="
