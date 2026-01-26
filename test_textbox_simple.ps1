# Prueba simple del TextBox de preview
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
}
"@

Write-Host "=== Prueba del TextBox de Preview ===" -ForegroundColor Cyan

# Buscar Calcpad
$proc = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $proc) {
    Write-Host "Calcpad no esta corriendo" -ForegroundColor Red
    exit 1
}

$hwnd = $proc.MainWindowHandle
Write-Host "Calcpad PID: $($proc.Id), Handle: $hwnd"

# Activar ventana
[Win32]::ShowWindow($hwnd, 9)
[Win32]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 500

$automation = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)

# Funcion para imprimir arbol de elementos
function Print-Tree {
    param($element, $depth = 0, $maxDepth = 3)

    if ($depth -gt $maxDepth) { return }

    $indent = "  " * $depth
    $type = $element.Current.ControlType.ProgrammaticName -replace "ControlType.", ""
    $name = $element.Current.Name
    $autoId = $element.Current.AutomationId
    $className = $element.Current.ClassName
    $bounds = $element.Current.BoundingRectangle

    $isOnScreen = $bounds.Width -gt 0 -and $bounds.Height -gt 0
    $color = if ($isOnScreen) { "White" } else { "DarkGray" }

    # Mostrar solo elementos relevantes
    if ($type -eq "Edit" -or $type -eq "Text" -or $autoId -like "*Preview*" -or $name -like "*@*") {
        Write-Host "$indent[$type] AutoId='$autoId' Name='$($name.Substring(0, [Math]::Min(50, $name.Length)))' Class='$className' Visible=$isOnScreen" -ForegroundColor $color
    }

    $children = $element.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($child in $children) {
        Print-Tree -element $child -depth ($depth + 1) -maxDepth $maxDepth
    }
}

Write-Host "`nArbol de elementos relevantes:" -ForegroundColor Yellow
Print-Tree -element $automation -maxDepth 6

# Buscar todos los Edit (TextBox)
Write-Host "`n--- TextBoxes (Edit controls) ---" -ForegroundColor Cyan
$editCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Edit
)
$edits = $automation.FindAll([System.Windows.Automation.TreeScope]::Descendants, $editCondition)

Write-Host "Total de TextBoxes encontrados: $($edits.Count)"
foreach ($edit in $edits) {
    $autoId = $edit.Current.AutomationId
    $name = $edit.Current.Name
    $bounds = $edit.Current.BoundingRectangle
    $visible = $bounds.Width -gt 0 -and $bounds.Height -gt 0

    Write-Host "  AutomationId='$autoId' Name='$name' Visible=$visible Bounds=($($bounds.X),$($bounds.Y),$($bounds.Width),$($bounds.Height))"

    # Intentar obtener valor
    try {
        $valuePattern = $edit.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
        if ($valuePattern) {
            $value = $valuePattern.Current.Value
            Write-Host "    Valor: '$value'" -ForegroundColor Green
        }
    } catch {
        Write-Host "    (no ValuePattern)" -ForegroundColor DarkGray
    }
}

# Buscar TextBlocks con contenido de preview
Write-Host "`n--- TextBlocks con contenido de preview ---" -ForegroundColor Cyan
$textCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Text
)
$texts = $automation.FindAll([System.Windows.Automation.TreeScope]::Descendants, $textCondition)

foreach ($text in $texts) {
    $name = $text.Current.Name
    $autoId = $text.Current.AutomationId
    $bounds = $text.Current.BoundingRectangle

    if ($name -match "@\{" -or $name -match "Ln \d+:" -or $autoId -like "*Preview*") {
        Write-Host "  AutomationId='$autoId' Name='$name'" -ForegroundColor Yellow
        Write-Host "    Bounds: X=$($bounds.X), Y=$($bounds.Y), W=$($bounds.Width), H=$($bounds.Height)"
    }
}

Write-Host "`nPrueba completada." -ForegroundColor Green
