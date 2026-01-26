# Test automático con UI Automation
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms

Write-Output "========================================="
Write-Output "TEST AUTOMATICO - Calcpad Preview Sync"
Write-Output "========================================="
Write-Output ""

# Paso 1: Abrir el archivo de prueba
Write-Output "[1/7] Abriendo archivo de prueba..."
$testFile = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\test_code_c.cpd"

# Intentar abrir Calcpad con el archivo
Start-Process "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\bin\Release\net10.0-windows\Calcpad.exe" -ArgumentList "`"$testFile`""

Write-Output "  Esperando que Calcpad se abra..."
Start-Sleep -Seconds 3

# Paso 2: Buscar ventana de Calcpad
Write-Output ""
Write-Output "[2/7] Buscando ventana de Calcpad..."
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

# Paso 3: Obtener todos los elementos
Write-Output ""
Write-Output "[3/7] Inspeccionando controles..."
try {
    $allElements = $calcpadWindow.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    Write-Output "  Total elementos: $($allElements.Count)"
} catch {
    Write-Output "  ✗ ERROR: No se pudieron obtener elementos"
    Write-Output "  $_"
    exit 1
}

# Paso 4: Buscar PreviewTextBlock
Write-Output ""
Write-Output "[4/7] Buscando PreviewTextBlock..."
$previewTextBlock = $null
foreach ($element in $allElements) {
    if ($element.Current.AutomationId -eq "PreviewTextBlock") {
        $previewTextBlock = $element
        $text = $element.Current.Name
        Write-Output "  ✓ PreviewTextBlock encontrado"
        Write-Output "  Texto: '$text'"
        break
    }
}

if ($null -eq $previewTextBlock) {
    Write-Output "  ⚠ PreviewTextBlock NO encontrado (normal si no hay archivo cargado)"
} else {
    # Paso 5: Intentar hacer click en PreviewTextBlock
    Write-Output ""
    Write-Output "[5/7] Intentando hacer click en PreviewTextBlock..."

    try {
        $rect = $previewTextBlock.Current.BoundingRectangle
        $clickX = [int]($rect.X + ($rect.Width / 2))
        $clickY = [int]($rect.Y + ($rect.Height / 2))

        Write-Output "  Posición calculada: X=$clickX, Y=$clickY"

        # Mover mouse y hacer click
        [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($clickX, $clickY)
        Start-Sleep -Milliseconds 500

        # Simular click
        Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class MouseOperations {
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, int dwExtraInfo);

    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP = 0x0004;

    public static void Click() {
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
    }
}
"@

        [MouseOperations]::Click()
        Write-Output "  ✓ Click simulado"
        Start-Sleep -Seconds 1

    } catch {
        Write-Output "  ✗ ERROR al hacer click: $_"
    }
}

# Paso 6: Verificar si apareció PreviewEditor
Write-Output ""
Write-Output "[6/7] Verificando si apareció PreviewEditor..."
Start-Sleep -Seconds 1

try {
    $allElements = $calcpadWindow.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)

    $previewEditor = $null
    foreach ($element in $allElements) {
        $autoId = $element.Current.AutomationId
        if ($autoId -eq "PreviewEditor") {
            $previewEditor = $element
            $isVisible = -not $element.Current.IsOffscreen
            Write-Output "  ✓ PreviewEditor encontrado"
            Write-Output "  Visible: $isVisible"

            # Intentar obtener texto
            try {
                $valuePattern = $element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                if ($null -ne $valuePattern) {
                    $text = $valuePattern.Current.Value
                    Write-Output "  Texto: '$text'"
                }
            } catch {
                Write-Output "  (No se pudo obtener texto)"
            }
            break
        }
    }

    if ($null -eq $previewEditor) {
        Write-Output "  ⚠ PreviewEditor NO apareció después del click"
    }
} catch {
    Write-Output "  ✗ ERROR: $_"
}

# Paso 7: Verificar log
Write-Output ""
Write-Output "[7/7] Verificando log de debug..."
$logPath = "C:\Users\j-b-j\Desktop\calcpad_debug.log"

if (Test-Path $logPath) {
    Write-Output "  ✓ Archivo de log existe"
    $logContent = Get-Content $logPath -Tail 50
    Write-Output ""
    Write-Output "========== ULTIMAS 50 LINEAS DEL LOG =========="
    $logContent | ForEach-Object { Write-Output $_ }
    Write-Output "==============================================="
} else {
    Write-Output "  ⚠ Archivo de log NO existe aún"
    Write-Output "  Ubicación esperada: $logPath"
}

Write-Output ""
Write-Output "========================================="
Write-Output "Test completado"
Write-Output "========================================="
