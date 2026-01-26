# Script para probar el TextBox de preview en MathEditor
# 1. Abre Calcpad con un archivo de prueba
# 2. Activa el modo mathCAD (Ctrl+M)
# 3. Hace click en el bloque de codigo externo
# 4. Prueba la edicion en el TextBox de preview

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
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
}
"@

$MOUSEEVENTF_LEFTDOWN = 0x0002
$MOUSEEVENTF_LEFTUP = 0x0004

Write-Host "=== Prueba del TextBox de Preview en MathEditor ===" -ForegroundColor Cyan
Write-Host ""

# Archivos
$testFile = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Examples\Tests\test_preview_simple.cpd"
$calcpadExe = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\bin\Release\net10.0-windows\Calcpad.exe"

# Cerrar instancias previas
Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1

Write-Host "1. Iniciando Calcpad con archivo de prueba..." -ForegroundColor Yellow
Start-Process $calcpadExe -ArgumentList "`"$testFile`""
Start-Sleep -Seconds 4

$proc = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $proc) {
    Write-Host "ERROR: Calcpad no se inicio" -ForegroundColor Red
    exit 1
}

$hwnd = $proc.MainWindowHandle
Write-Host "   Calcpad iniciado (PID: $($proc.Id))" -ForegroundColor Green

# Maximizar y activar
[Win32]::ShowWindow($hwnd, 3) # SW_MAXIMIZE
Start-Sleep -Milliseconds 500
[Win32]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 500

$automation = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)

# Funcion para buscar por AutomationId
function Find-ByAutomationId {
    param($automationId)
    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
        $automationId
    )
    return $automation.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $condition)
}

# Funcion para buscar por tipo
function Find-ByType {
    param($type)
    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        $type
    )
    return $automation.FindAll([System.Windows.Automation.TreeScope]::Descendants, $condition)
}

# Funcion para hacer click en un punto
function Click-At {
    param($x, $y)
    [Win32]::SetCursorPos($x, $y)
    Start-Sleep -Milliseconds 100
    [Win32]::mouse_event($MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    Start-Sleep -Milliseconds 50
    [Win32]::mouse_event($MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    Start-Sleep -Milliseconds 300
}

Write-Host ""
Write-Host "2. Activando modo mathCAD (Ctrl+M)..." -ForegroundColor Yellow
[Win32]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("^m")
Start-Sleep -Seconds 2

Write-Host "   Modo mathCAD activado" -ForegroundColor Green

# Buscar el boton mathCAD para verificar que esta activo
$toggleButtons = Find-ByType ([System.Windows.Automation.ControlType]::Button)
foreach ($btn in $toggleButtons) {
    $name = $btn.Current.Name
    if ($name -eq "mathCAD") {
        Write-Host "   Toggle mathCAD encontrado" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "3. Buscando el area del MathEditor..." -ForegroundColor Yellow

# Refrescar el arbol de automatizacion
$automation = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)

# Buscar el PreviewTextBlock
$previewTextBlock = Find-ByAutomationId "PreviewTextBlock"

if ($previewTextBlock) {
    $bounds = $previewTextBlock.Current.BoundingRectangle
    Write-Host "   PreviewTextBlock encontrado! Bounds: X=$($bounds.X), Y=$($bounds.Y), W=$($bounds.Width), H=$($bounds.Height)" -ForegroundColor Green

    if ($bounds.Width -gt 0) {
        Write-Host "   El MathEditor esta activo!" -ForegroundColor Green
    }
    else {
        Write-Host "   PreviewTextBlock no tiene dimensiones (Width=0), el MathEditor no esta activo" -ForegroundColor Yellow
    }
}
else {
    Write-Host "   PreviewTextBlock no encontrado aun" -ForegroundColor Yellow
}

# Hacer click en el area del editor para activar el MathEditor
Write-Host ""
Write-Host "4. Haciendo click en el area del editor..." -ForegroundColor Yellow

$windowBounds = $automation.Current.BoundingRectangle
$editorClickX = [int]($windowBounds.X + 200)
$editorClickY = [int]($windowBounds.Y + 450)  # Donde deberia estar el bloque @{c}

Click-At $editorClickX $editorClickY
Write-Host "   Click en ($editorClickX, $editorClickY)" -ForegroundColor DarkGray
Start-Sleep -Milliseconds 500

# Refrescar y buscar de nuevo
$automation = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
$previewTextBlock = Find-ByAutomationId "PreviewTextBlock"

if ($previewTextBlock) {
    $bounds = $previewTextBlock.Current.BoundingRectangle
    $name = $previewTextBlock.Current.Name

    Write-Host ""
    Write-Host "5. Estado del PreviewTextBlock:" -ForegroundColor Yellow
    Write-Host "   Name: '$name'" -ForegroundColor Cyan
    Write-Host "   Bounds: X=$($bounds.X), Y=$($bounds.Y), W=$($bounds.Width), H=$($bounds.Height)"

    if ($bounds.Width -gt 0) {
        Write-Host ""
        Write-Host "6. Haciendo click en el PreviewTextBlock para editar..." -ForegroundColor Yellow

        $clickX = [int]($bounds.X + 50)
        $clickY = [int]($bounds.Y + $bounds.Height / 2)

        Click-At $clickX $clickY
        Write-Host "   Click en ($clickX, $clickY)" -ForegroundColor DarkGray
        Start-Sleep -Milliseconds 500

        # Buscar el PreviewEditTextBox
        $previewEditTextBox = Find-ByAutomationId "PreviewEditTextBox"

        if ($previewEditTextBox) {
            $tbBounds = $previewEditTextBox.Current.BoundingRectangle

            Write-Host ""
            Write-Host "7. Estado del PreviewEditTextBox:" -ForegroundColor Yellow
            Write-Host "   Bounds: X=$($tbBounds.X), Y=$($tbBounds.Y), W=$($tbBounds.Width), H=$($tbBounds.Height)"

            if ($tbBounds.Width -gt 0) {
                Write-Host "   TextBox VISIBLE!" -ForegroundColor Green

                # Obtener valor actual
                try {
                    $valuePattern = $previewEditTextBox.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                    if ($valuePattern) {
                        $value = $valuePattern.Current.Value
                        Write-Host "   Valor actual: '$value'" -ForegroundColor Cyan
                    }
                } catch {
                    Write-Host "   (no ValuePattern disponible)" -ForegroundColor DarkGray
                }

                Write-Host ""
                Write-Host "8. Probando escritura: 'TEST '..." -ForegroundColor Yellow
                [System.Windows.Forms.SendKeys]::SendWait("TEST ")
                Start-Sleep -Milliseconds 500

                # Verificar
                try {
                    $valuePattern = $previewEditTextBox.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                    if ($valuePattern) {
                        $newValue = $valuePattern.Current.Value
                        Write-Host "   Valor despues: '$newValue'" -ForegroundColor Cyan
                    }
                } catch {}

                Write-Host ""
                Write-Host "9. Probando Backspace..." -ForegroundColor Yellow
                [System.Windows.Forms.SendKeys]::SendWait("{BACKSPACE}{BACKSPACE}")
                Start-Sleep -Milliseconds 300

                try {
                    $valuePattern = $previewEditTextBox.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                    if ($valuePattern) {
                        $finalValue = $valuePattern.Current.Value
                        Write-Host "   Valor final: '$finalValue'" -ForegroundColor Cyan
                    }
                } catch {}

                Write-Host ""
                Write-Host "10. Presionando Enter para confirmar..." -ForegroundColor Yellow
                [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
                Start-Sleep -Milliseconds 500

                # Verificar que se cerro
                $previewEditTextBox = Find-ByAutomationId "PreviewEditTextBox"
                if ($previewEditTextBox) {
                    $tbBounds = $previewEditTextBox.Current.BoundingRectangle
                    if ($tbBounds.Width -eq 0) {
                        Write-Host "    TextBox cerrado correctamente" -ForegroundColor Green
                    }
                }
            }
            else {
                Write-Host "   TextBox NO visible (Width=0)" -ForegroundColor Red
            }
        }
        else {
            Write-Host "   PreviewEditTextBox NO encontrado" -ForegroundColor Red
        }
    }
    else {
        Write-Host "   PreviewTextBlock no visible (Width=0)" -ForegroundColor Red
    }
}
else {
    Write-Host "   PreviewTextBlock no encontrado" -ForegroundColor Red

    # Debug: listar todos los elementos para ver que hay
    Write-Host ""
    Write-Host "DEBUG: Listando elementos relevantes..." -ForegroundColor Magenta

    $allElements = Find-ByType ([System.Windows.Automation.ControlType]::Text)
    $count = 0
    foreach ($elem in $allElements) {
        $autoId = $elem.Current.AutomationId
        $name = $elem.Current.Name
        $bounds = $elem.Current.BoundingRectangle

        if ($autoId -or $name -match "@\{" -or $name -match "Calcpad" -or $name -match "mathCAD" -or $name -match "Expresi") {
            $displayName = if ($name.Length -gt 50) { $name.Substring(0, 50) + "..." } else { $name }
            Write-Host "  [$count] AutoId='$autoId' Name='$displayName' Y=$($bounds.Y)"
            $count++
        }
    }
}

Write-Host ""
Write-Host "=== Prueba Finalizada ===" -ForegroundColor Cyan
