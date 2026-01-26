Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms

Write-Output "SIMULANDO CLICK EN PREVIEW BAR"
Write-Output "==============================="

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
    Write-Output "ERROR: Calcpad no encontrado"
    exit 1
}

$allElements = $calcpadWindow.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)

$previewTextBlock = $null
foreach ($element in $allElements) {
    if ($element.Current.AutomationId -eq "PreviewTextBlock") {
        $previewTextBlock = $element
        break
    }
}

if ($null -eq $previewTextBlock) {
    Write-Output "ERROR: PreviewTextBlock no encontrado"
    exit 1
}

Write-Output "PreviewTextBlock encontrado"
Write-Output "Texto: $($previewTextBlock.Current.Name)"

try {
    $rect = $previewTextBlock.Current.BoundingRectangle
    $clickX = [int]($rect.X + ($rect.Width / 2))
    $clickY = [int]($rect.Y + ($rect.Height / 2))

    Write-Output "Haciendo click en: X=$clickX, Y=$clickY"

    [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($clickX, $clickY)
    Start-Sleep -Milliseconds 300

    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class MouseOps {
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, int dwExtraInfo);
    public const uint LEFTDOWN = 0x0002;
    public const uint LEFTUP = 0x0004;
    public static void Click() {
        mouse_event(LEFTDOWN, 0, 0, 0, 0);
        mouse_event(LEFTUP, 0, 0, 0, 0);
    }
}
"@

    [MouseOps]::Click()
    Write-Output "Click ejecutado"

    Start-Sleep -Seconds 2

    Write-Output ""
    Write-Output "Verificando si aparecio PreviewEditor..."
    $allElements = $calcpadWindow.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)

    $found = $false
    foreach ($element in $allElements) {
        $className = $element.Current.ClassName
        $autoId = $element.Current.AutomationId

        if ($autoId -eq "PreviewEditor") {
            $isVisible = -not $element.Current.IsOffscreen
            Write-Output "PreviewEditor encontrado!"
            Write-Output "  ClassName: $className"
            Write-Output "  Visible: $isVisible"
            $found = $true
            break
        }
    }

    if (-not $found) {
        Write-Output "PreviewEditor NO aparecio (puede necesitar mas tiempo)"
    }

} catch {
    Write-Output "ERROR: $_"
}

Write-Output ""
Write-Output "==============================="
Write-Output "Verifica visualmente si el editor se abrio"
Write-Output "==============================="
