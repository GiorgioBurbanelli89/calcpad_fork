# Script de prueba final para el TextBox de preview
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

Write-Host "=== Prueba Final del TextBox de Preview ===" -ForegroundColor Cyan
Write-Host ""

# Iniciar Calcpad con un archivo de prueba
$testFile = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Examples\MultLangCode_Demo.cpd"
$calcpadExe = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\bin\Release\net10.0-windows\Calcpad.exe"

# Cerrar instancias previas
Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1

Write-Host "Iniciando Calcpad con: $testFile" -ForegroundColor Yellow
Start-Process $calcpadExe -ArgumentList "`"$testFile`""
Start-Sleep -Seconds 5

$proc = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $proc) {
    Write-Host "ERROR: Calcpad no se inicio" -ForegroundColor Red
    exit 1
}

$hwnd = $proc.MainWindowHandle
Write-Host "Calcpad iniciado (PID: $($proc.Id))" -ForegroundColor Green

[Win32]::ShowWindow($hwnd, 3) # SW_MAXIMIZE
[Win32]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 1000

$automation = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)

# Funcion para buscar elementos por AutomationId
function Find-ByAutomationId {
    param($automationId)

    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
        $automationId
    )
    return $automation.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $condition)
}

# Funcion para buscar elementos por tipo
function Find-ByType {
    param($type)

    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        $type
    )
    return $automation.FindAll([System.Windows.Automation.TreeScope]::Descendants, $condition)
}

# Buscar el PreviewTextBlock por AutomationId
Write-Host "`nBuscando PreviewTextBlock..." -ForegroundColor Yellow
$previewTextBlock = Find-ByAutomationId "PreviewTextBlock"

if ($previewTextBlock) {
    $bounds = $previewTextBlock.Current.BoundingRectangle
    $name = $previewTextBlock.Current.Name
    Write-Host "  ENCONTRADO! Name='$name'" -ForegroundColor Green
    Write-Host "  Bounds: X=$($bounds.X), Y=$($bounds.Y), W=$($bounds.Width), H=$($bounds.Height)"

    if ($bounds.Width -gt 0) {
        # Hacer click en el PreviewTextBlock
        $clickX = [int]($bounds.X + 50)
        $clickY = [int]($bounds.Y + $bounds.Height / 2)

        Write-Host "`nHaciendo click en PreviewTextBlock ($clickX, $clickY)..." -ForegroundColor Cyan
        [Win32]::SetCursorPos($clickX, $clickY)
        Start-Sleep -Milliseconds 200
        [Win32]::mouse_event($MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        Start-Sleep -Milliseconds 50
        [Win32]::mouse_event($MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        Start-Sleep -Milliseconds 500

        # Buscar el PreviewEditTextBox
        Write-Host "`nBuscando PreviewEditTextBox..." -ForegroundColor Yellow
        $previewEditTextBox = Find-ByAutomationId "PreviewEditTextBox"

        if ($previewEditTextBox) {
            $tbBounds = $previewEditTextBox.Current.BoundingRectangle
            Write-Host "  ENCONTRADO! Bounds: W=$($tbBounds.Width), H=$($tbBounds.Height)"

            if ($tbBounds.Width -gt 0) {
                Write-Host "  TextBox esta VISIBLE!" -ForegroundColor Green

                # Intentar obtener el valor actual
                try {
                    $valuePattern = $previewEditTextBox.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                    if ($valuePattern) {
                        $value = $valuePattern.Current.Value
                        Write-Host "  Valor actual: '$value'" -ForegroundColor Green
                    }
                } catch {
                    Write-Host "  No se pudo obtener ValuePattern: $_" -ForegroundColor DarkGray
                }

                # Probar escribir
                Write-Host "`nProbando escritura: 'HOLA'..." -ForegroundColor Cyan
                [System.Windows.Forms.SendKeys]::SendWait("HOLA")
                Start-Sleep -Milliseconds 500

                # Verificar resultado
                try {
                    $valuePattern = $previewEditTextBox.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                    if ($valuePattern) {
                        $newValue = $valuePattern.Current.Value
                        Write-Host "  Valor despues de escribir: '$newValue'" -ForegroundColor Yellow
                    }
                } catch {}

                # Probar Backspace
                Write-Host "`nProbando Backspace..." -ForegroundColor Cyan
                [System.Windows.Forms.SendKeys]::SendWait("{BACKSPACE}")
                Start-Sleep -Milliseconds 300
                [System.Windows.Forms.SendKeys]::SendWait("{BACKSPACE}")
                Start-Sleep -Milliseconds 300

                # Verificar resultado
                try {
                    $valuePattern = $previewEditTextBox.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                    if ($valuePattern) {
                        $finalValue = $valuePattern.Current.Value
                        Write-Host "  Valor final: '$finalValue'" -ForegroundColor Yellow
                    }
                } catch {}

                # Presionar Escape para cerrar
                Write-Host "`nPresionando Escape..." -ForegroundColor Cyan
                [System.Windows.Forms.SendKeys]::SendWait("{ESCAPE}")
                Start-Sleep -Milliseconds 500

                # Verificar que el TextBox se oculto
                $previewEditTextBox = Find-ByAutomationId "PreviewEditTextBox"
                if ($previewEditTextBox) {
                    $tbBounds = $previewEditTextBox.Current.BoundingRectangle
                    if ($tbBounds.Width -eq 0) {
                        Write-Host "  TextBox se oculto correctamente" -ForegroundColor Green
                    } else {
                        Write-Host "  TextBox sigue visible (Width=$($tbBounds.Width))" -ForegroundColor Yellow
                    }
                }
            }
            else {
                Write-Host "  TextBox NO esta visible (Width=0)" -ForegroundColor Red
            }
        }
        else {
            Write-Host "  PreviewEditTextBox NO encontrado" -ForegroundColor Red
        }
    }
    else {
        Write-Host "  PreviewTextBlock no tiene dimensiones visibles (Width=0)" -ForegroundColor Red
    }
}
else {
    Write-Host "  PreviewTextBlock NO encontrado" -ForegroundColor Red

    # Buscar todos los TextBlocks para debug
    Write-Host "`nListando todos los TextBlocks con contenido relevante:" -ForegroundColor Yellow
    $texts = Find-ByType ([System.Windows.Automation.ControlType]::Text)
    foreach ($text in $texts) {
        $name = $text.Current.Name
        $autoId = $text.Current.AutomationId
        $bounds = $text.Current.BoundingRectangle

        if ($autoId -or $name -match "@\{" -or $name -match "Ln " -or $name -match "Calcpad") {
            Write-Host "  AutoId='$autoId' Name='$($name.Substring(0, [Math]::Min(60, $name.Length)))' Y=$($bounds.Y)"
        }
    }
}

Write-Host "`n=== Prueba Finalizada ===" -ForegroundColor Cyan
