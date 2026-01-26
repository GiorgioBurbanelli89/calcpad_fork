# Script para probar el TextBox de preview en MathEditor
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms

# Buscar la ventana de Calcpad
$calcpadWindow = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $calcpadWindow) {
    Write-Host "Calcpad no esta corriendo. Iniciando..."
    Start-Process "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\bin\Release\net10.0-windows\Calcpad.exe"
    Start-Sleep -Seconds 3
    $calcpadWindow = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Select-Object -First 1
}

$hwnd = $calcpadWindow.MainWindowHandle
Write-Host "Calcpad encontrado. Handle: $hwnd"

# Activar la ventana
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@

[Win32]::ShowWindow($hwnd, 9) # SW_RESTORE
[Win32]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 500

# Obtener el arbol de automatizacion
$automation = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
Write-Host "`nEstructura de la ventana:"

function Get-ElementTree {
    param($element, $indent = 0)

    $name = $element.Current.Name
    $controlType = $element.Current.ControlType.ProgrammaticName
    $className = $element.Current.ClassName
    $automationId = $element.Current.AutomationId

    $indentStr = "  " * $indent
    Write-Host "$indentStr[$controlType] Name='$name' Class='$className' AutomationId='$automationId'"

    if ($indent -lt 5) {
        $children = $element.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
        foreach ($child in $children) {
            Get-ElementTree -element $child -indent ($indent + 1)
        }
    }
}

Get-ElementTree -element $automation

# Buscar el TextBox de preview (PreviewEditTextBox)
Write-Host "`n`nBuscando TextBox de edicion..."

$textBoxCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Edit
)

$textBoxes = $automation.FindAll([System.Windows.Automation.TreeScope]::Descendants, $textBoxCondition)
Write-Host "TextBoxes encontrados: $($textBoxes.Count)"

foreach ($tb in $textBoxes) {
    $name = $tb.Current.Name
    $automationId = $tb.Current.AutomationId
    $className = $tb.Current.ClassName
    Write-Host "  - Name='$name' AutomationId='$automationId' Class='$className'"
}

# Buscar el TextBlock de preview (para hacer click en el)
$textBlockCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Text
)

$textBlocks = $automation.FindAll([System.Windows.Automation.TreeScope]::Descendants, $textBlockCondition)
Write-Host "`nTextBlocks encontrados: $($textBlocks.Count)"

foreach ($tb in $textBlocks) {
    $name = $tb.Current.Name
    $automationId = $tb.Current.AutomationId
    $bounds = $tb.Current.BoundingRectangle
    if ($name -like "*Calcpad*" -or $name -like "*@*" -or $name -like "*Ln*") {
        Write-Host "  - ENCONTRADO: Name='$name' Bounds=$bounds"
    }
}

Write-Host "`nPrueba completada."
