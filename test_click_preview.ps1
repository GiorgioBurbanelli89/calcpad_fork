# Script para hacer click en el preview y verificar el TextBox
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
    public static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, int dwExtraInfo);
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);
}
"@

$MOUSEEVENTF_LEFTDOWN = 0x0002
$MOUSEEVENTF_LEFTUP = 0x0004

Write-Host "=== Prueba de Click en Preview ===" -ForegroundColor Cyan

$proc = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $proc) {
    Write-Host "Calcpad no esta corriendo" -ForegroundColor Red
    exit 1
}

$hwnd = $proc.MainWindowHandle
[Win32]::ShowWindow($hwnd, 9)
[Win32]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 500

$automation = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)

# Buscar TextBlocks que contengan "Expresion" o "Codigo" (el indicador de modo)
Write-Host "`nBuscando elementos del MathEditor..." -ForegroundColor Yellow

$textCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Text
)

$texts = $automation.FindAll([System.Windows.Automation.TreeScope]::Descendants, $textCondition)
Write-Host "Total TextBlocks: $($texts.Count)"

$modeIndicator = $null
$calcpadLabel = $null
$previewText = $null

foreach ($text in $texts) {
    $name = $text.Current.Name
    $bounds = $text.Current.BoundingRectangle

    # Buscar el indicador de modo
    if ($name -eq "Expresion" -or $name -eq "Expresión" -or $name -match "^(c|python|js|ts|octave)$") {
        Write-Host "  Indicador de modo encontrado: '$name' at ($($bounds.X), $($bounds.Y))" -ForegroundColor Green
        $modeIndicator = $text
    }

    # Buscar "Calcpad:"
    if ($name -eq "Calcpad: " -or $name -eq "Calcpad:") {
        Write-Host "  Label 'Calcpad:' encontrado at ($($bounds.X), $($bounds.Y))" -ForegroundColor Green
        $calcpadLabel = $text
    }

    # Buscar texto con cursor | o con @{
    if ($name -match "\|" -or $name -match "@\{") {
        Write-Host "  Preview text: '$name' at ($($bounds.X), $($bounds.Y))" -ForegroundColor Yellow
        $previewText = $text
    }
}

# Buscar UserControl del MathEditor
$customCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Custom
)
$customs = $automation.FindAll([System.Windows.Automation.TreeScope]::Descendants, $customCondition)
Write-Host "`nControles Custom: $($customs.Count)"

foreach ($custom in $customs) {
    $className = $custom.Current.ClassName
    $autoId = $custom.Current.AutomationId
    $bounds = $custom.Current.BoundingRectangle

    if ($className -like "*MathEditor*" -or $autoId -like "*MathEditor*") {
        Write-Host "  MathEditor encontrado: Class='$className' AutoId='$autoId' Bounds=($($bounds.X),$($bounds.Y),$($bounds.Width),$($bounds.Height))" -ForegroundColor Green
    }
}

# Si encontramos el preview, hacer click en el
if ($previewText) {
    $bounds = $previewText.Current.BoundingRectangle
    $clickX = [int]($bounds.X + $bounds.Width / 2)
    $clickY = [int]($bounds.Y + $bounds.Height / 2)

    Write-Host "`nHaciendo click en preview at ($clickX, $clickY)..." -ForegroundColor Cyan

    [Win32]::SetCursorPos($clickX, $clickY)
    Start-Sleep -Milliseconds 100
    [Win32]::mouse_event($MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    Start-Sleep -Milliseconds 50
    [Win32]::mouse_event($MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    Start-Sleep -Milliseconds 500

    # Buscar TextBox ahora
    Write-Host "`nBuscando TextBox despues del click..." -ForegroundColor Yellow
    $editCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Edit
    )
    $edits = $automation.FindAll([System.Windows.Automation.TreeScope]::Descendants, $editCondition)

    Write-Host "TextBoxes encontrados: $($edits.Count)"
    foreach ($edit in $edits) {
        $autoId = $edit.Current.AutomationId
        $bounds = $edit.Current.BoundingRectangle
        $visible = $bounds.Width -gt 0 -and $bounds.Height -gt 0

        Write-Host "  AutomationId='$autoId' Visible=$visible Bounds=($($bounds.X),$($bounds.Y),$($bounds.Width),$($bounds.Height))"

        try {
            $valuePattern = $edit.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
            if ($valuePattern) {
                $value = $valuePattern.Current.Value
                Write-Host "    Valor: '$value'" -ForegroundColor Green
            }
        } catch {}
    }

    # Probar escribir texto
    Write-Host "`nEscribiendo 'TEST ' en el TextBox..." -ForegroundColor Cyan
    [System.Windows.Forms.SendKeys]::SendWait("TEST ")
    Start-Sleep -Milliseconds 500

    # Verificar cambio
    $edits = $automation.FindAll([System.Windows.Automation.TreeScope]::Descendants, $editCondition)
    foreach ($edit in $edits) {
        $bounds = $edit.Current.BoundingRectangle
        if ($bounds.Width -gt 0 -and $bounds.Y -lt 400) {  # Solo los que estan arriba
            try {
                $valuePattern = $edit.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                if ($valuePattern) {
                    $value = $valuePattern.Current.Value
                    Write-Host "  Valor despues de escribir: '$value'" -ForegroundColor Yellow
                }
            } catch {}
        }
    }
}
else {
    Write-Host "`nNo se encontro el preview text. Necesitas:" -ForegroundColor Red
    Write-Host "1. Abrir un archivo .cpd con bloques de codigo externo (@{c}, @{python}, etc.)"
    Write-Host "2. O escribir codigo en el MathEditor"
}

Write-Host "`nPrueba completada." -ForegroundColor Green
