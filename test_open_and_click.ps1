# Script para abrir un archivo con codigo externo y probar el preview TextBox
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

Write-Host "=== Prueba Completa: Abrir archivo y probar TextBox ===" -ForegroundColor Cyan

# Archivo con codigo externo
$testFile = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Examples\MultLangCode_Demo.cpd"

$proc = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $proc) {
    Write-Host "Iniciando Calcpad con el archivo de prueba..." -ForegroundColor Yellow
    Start-Process "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\bin\Release\net10.0-windows\Calcpad.exe" -ArgumentList "`"$testFile`""
    Start-Sleep -Seconds 4
    $proc = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Select-Object -First 1
}

if (-not $proc) {
    Write-Host "ERROR: No se pudo iniciar Calcpad" -ForegroundColor Red
    exit 1
}

$hwnd = $proc.MainWindowHandle
Write-Host "Calcpad PID: $($proc.Id)"

[Win32]::ShowWindow($hwnd, 9)
[Win32]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 500

# Si Calcpad ya estaba corriendo, abrir el archivo con Ctrl+O
if (-not $args) {
    Write-Host "Abriendo archivo de prueba con Ctrl+O..." -ForegroundColor Yellow
    [System.Windows.Forms.SendKeys]::SendWait("^o")
    Start-Sleep -Seconds 1

    # Escribir la ruta del archivo
    [System.Windows.Forms.SendKeys]::SendWait($testFile)
    Start-Sleep -Milliseconds 500
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Start-Sleep -Seconds 2
}

# Activar ventana de nuevo
[Win32]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 500

$automation = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)

# Funcion para buscar elementos
function Find-Elements {
    param($type)

    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        $type
    )
    return $automation.FindAll([System.Windows.Automation.TreeScope]::Descendants, $condition)
}

# Hacer click en el area del MathEditor para asegurar que tiene foco
Write-Host "`nBuscando el area de edicion..." -ForegroundColor Yellow

$panes = Find-Elements ([System.Windows.Automation.ControlType]::Pane)
$canvases = Find-Elements ([System.Windows.Automation.ControlType]::Custom)

# Buscar el canvas del editor (deberia estar cerca de la parte superior izquierda)
$editorArea = $null
foreach ($pane in $panes) {
    $bounds = $pane.Current.BoundingRectangle
    $className = $pane.Current.ClassName
    if ($bounds.Y -lt 500 -and $bounds.Height -gt 100 -and $className -like "*Canvas*") {
        Write-Host "  Encontrado Canvas: Class='$className' Bounds=($($bounds.X),$($bounds.Y),$($bounds.Width),$($bounds.Height))"
        $editorArea = $pane
    }
}

# Hacer click en el centro de la ventana (donde deberia estar el editor)
$windowBounds = $automation.Current.BoundingRectangle
$clickX = [int]($windowBounds.X + 300)
$clickY = [int]($windowBounds.Y + 400)

Write-Host "`nHaciendo click en el area del editor ($clickX, $clickY)..." -ForegroundColor Cyan
[Win32]::SetCursorPos($clickX, $clickY)
Start-Sleep -Milliseconds 100
[Win32]::mouse_event($MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
Start-Sleep -Milliseconds 50
[Win32]::mouse_event($MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
Start-Sleep -Milliseconds 500

# Esperar y buscar elementos de preview
Write-Host "`nBuscando elementos de preview..." -ForegroundColor Yellow
$texts = Find-Elements ([System.Windows.Automation.ControlType]::Text)

$previewText = $null
foreach ($text in $texts) {
    $name = $text.Current.Name
    $bounds = $text.Current.BoundingRectangle

    if ($name -match "@\{" -or $name -match "Ln \d+:" -or $name -match "\|") {
        Write-Host "  PREVIEW: '$name'" -ForegroundColor Green
        Write-Host "    Bounds: ($($bounds.X), $($bounds.Y), $($bounds.Width), $($bounds.Height))"
        $previewText = $text
    }
}

if (-not $previewText) {
    # Buscar la barra beige (preview bar) por posicion
    Write-Host "`nBuscando barra de preview por posicion..." -ForegroundColor Yellow

    foreach ($text in $texts) {
        $bounds = $text.Current.BoundingRectangle
        $name = $text.Current.Name

        # La barra de preview deberia estar cerca del top, Y < 350
        if ($bounds.Y -gt 250 -and $bounds.Y -lt 350 -and $bounds.Width -gt 50) {
            Write-Host "  Candidato: Name='$($name.Substring(0, [Math]::Min(40, $name.Length)))...' Y=$($bounds.Y)"

            if ($name -match "Calcpad" -or $name -match "Expresi") {
                $previewText = $text
            }
        }
    }
}

if ($previewText) {
    $bounds = $previewText.Current.BoundingRectangle
    $clickX = [int]($bounds.X + $bounds.Width / 2)
    $clickY = [int]($bounds.Y + $bounds.Height / 2)

    Write-Host "`nHaciendo click en preview ($clickX, $clickY)..." -ForegroundColor Cyan
    [Win32]::SetCursorPos($clickX, $clickY)
    Start-Sleep -Milliseconds 100
    [Win32]::mouse_event($MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    Start-Sleep -Milliseconds 50
    [Win32]::mouse_event($MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    Start-Sleep -Milliseconds 500

    # Buscar TextBoxes
    Write-Host "`nTextBoxes despues del click:" -ForegroundColor Yellow
    $edits = Find-Elements ([System.Windows.Automation.ControlType]::Edit)

    foreach ($edit in $edits) {
        $autoId = $edit.Current.AutomationId
        $bounds = $edit.Current.BoundingRectangle
        $visible = $bounds.Width -gt 0 -and $bounds.Height -gt 0

        if ($visible) {
            Write-Host "  AutomationId='$autoId' Bounds=($($bounds.X),$($bounds.Y),$($bounds.Width),$($bounds.Height))"
            try {
                $valuePattern = $edit.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                if ($valuePattern) {
                    $value = $valuePattern.Current.Value
                    Write-Host "    Valor: '$value'" -ForegroundColor Green
                }
            } catch {}
        }
    }

    # Escribir algo
    Write-Host "`nEscribiendo 'HOLA ' y luego Backspace..." -ForegroundColor Cyan
    [System.Windows.Forms.SendKeys]::SendWait("HOLA ")
    Start-Sleep -Milliseconds 500

    [System.Windows.Forms.SendKeys]::SendWait("{BACKSPACE}")
    Start-Sleep -Milliseconds 300

    [System.Windows.Forms.SendKeys]::SendWait("{BACKSPACE}")
    Start-Sleep -Milliseconds 300

    # Verificar resultado
    Write-Host "`nResultado final:" -ForegroundColor Yellow
    $edits = Find-Elements ([System.Windows.Automation.ControlType]::Edit)
    foreach ($edit in $edits) {
        $bounds = $edit.Current.BoundingRectangle
        if ($bounds.Width -gt 0 -and $bounds.Y -lt 400) {
            try {
                $valuePattern = $edit.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                if ($valuePattern) {
                    $value = $valuePattern.Current.Value
                    Write-Host "  Valor final: '$value'" -ForegroundColor Yellow
                }
            } catch {}
        }
    }

    # Presionar Escape para cerrar
    Write-Host "`nPresionando Escape para cerrar el TextBox..." -ForegroundColor Cyan
    [System.Windows.Forms.SendKeys]::SendWait("{ESCAPE}")
}
else {
    Write-Host "`nNo se encontro la barra de preview" -ForegroundColor Red
    Write-Host "Asegurate de que el archivo tenga bloques @{c} o @{python}"
}

Write-Host "`nPrueba completada." -ForegroundColor Green
