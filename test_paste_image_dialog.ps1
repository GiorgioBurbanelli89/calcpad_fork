# Test Paste Image Dialog in Calcpad WPF
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Write-Host "=== Test Paste Image Dialog ===" -ForegroundColor Cyan

# Find Calcpad window
$calcpadProcess = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $calcpadProcess) {
    Write-Host "ERROR: Calcpad no esta corriendo" -ForegroundColor Red
    exit 1
}

Write-Host "Calcpad encontrado: PID $($calcpadProcess.Id)" -ForegroundColor Green

# Get automation element
$root = [System.Windows.Automation.AutomationElement]::RootElement
$condition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    $calcpadProcess.Id
)
$calcpadWindow = $root.FindFirst([System.Windows.Automation.TreeScope]::Children, $condition)

if (-not $calcpadWindow) {
    Write-Host "ERROR: No se pudo encontrar la ventana de Calcpad" -ForegroundColor Red
    exit 1
}

Write-Host "Ventana encontrada: $($calcpadWindow.Current.Name)" -ForegroundColor Green

# Create a small test image in clipboard
Write-Host "`nCreando imagen de prueba en el portapapeles..." -ForegroundColor Yellow
$bitmap = New-Object System.Drawing.Bitmap(100, 100)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.Clear([System.Drawing.Color]::LightBlue)
$graphics.FillEllipse([System.Drawing.Brushes]::Red, 25, 25, 50, 50)
$graphics.DrawString("Test", [System.Drawing.SystemFonts]::DefaultFont, [System.Drawing.Brushes]::Black, 35, 40)
$graphics.Dispose()

[System.Windows.Forms.Clipboard]::SetImage($bitmap)
$bitmap.Dispose()

Write-Host "Imagen copiada al portapapeles" -ForegroundColor Green

# Focus Calcpad window
Write-Host "`nEnfocando ventana de Calcpad..." -ForegroundColor Yellow
try {
    $windowPattern = $calcpadWindow.GetCurrentPattern([System.Windows.Automation.WindowPattern]::Pattern)
    $windowPattern.SetWindowVisualState([System.Windows.Automation.WindowVisualState]::Normal)
} catch {
    Write-Host "No se pudo usar WindowPattern, intentando con SetForegroundWindow..." -ForegroundColor Yellow
}

# Use SetForegroundWindow
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
}
"@

[Win32]::SetForegroundWindow($calcpadProcess.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 500

Write-Host "`nEnviando Ctrl+V para pegar imagen..." -ForegroundColor Yellow
[System.Windows.Forms.SendKeys]::SendWait("^v")

Start-Sleep -Seconds 2

# Look for the paste dialog
Write-Host "`nBuscando dialogo de pegado..." -ForegroundColor Yellow

$dialogCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Window
)

$allWindows = $root.FindAll([System.Windows.Automation.TreeScope]::Children, $dialogCondition)
$dialogFound = $false

foreach ($window in $allWindows) {
    $windowName = $window.Current.Name
    Write-Host "  Ventana encontrada: '$windowName'" -ForegroundColor Gray

    if ($windowName -match "Pegar Imagen" -or $windowName -match "Paste Image") {
        Write-Host "`n*** DIALOGO DE PEGAR IMAGEN ENCONTRADO! ***" -ForegroundColor Green
        $dialogFound = $true

        # List all controls in the dialog
        Write-Host "`nControles en el dialogo:" -ForegroundColor Cyan
        $allControls = $window.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)

        foreach ($control in $allControls) {
            $ctrlType = $control.Current.ControlType.ProgrammaticName
            $ctrlName = $control.Current.Name
            $ctrlId = $control.Current.AutomationId

            if ($ctrlName -or $ctrlId) {
                Write-Host "  [$ctrlType] Name='$ctrlName' AutomationId='$ctrlId'" -ForegroundColor White
            }
        }

        # Try to find and click Cancel to close dialog
        $cancelCondition = New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::NameProperty,
            "Cancelar"
        )
        $cancelButton = $window.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cancelCondition)

        if ($cancelButton) {
            Write-Host "`nCerrando dialogo con boton Cancelar..." -ForegroundColor Yellow
            $invokePattern = $cancelButton.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
            $invokePattern.Invoke()
        }

        break
    }
}

if (-not $dialogFound) {
    Write-Host "`nNo se encontro el dialogo de Pegar Imagen" -ForegroundColor Red
    Write-Host "Posibles razones:" -ForegroundColor Yellow
    Write-Host "  - El portapapeles no contiene una imagen valida" -ForegroundColor Yellow
    Write-Host "  - El cursor no esta en una posicion valida del editor" -ForegroundColor Yellow
    Write-Host "  - Hubo un error en el codigo" -ForegroundColor Yellow

    # Check for any error dialogs
    foreach ($window in $allWindows) {
        if ($window.Current.ProcessId -eq $calcpadProcess.Id -and $window.Current.Name -ne $calcpadWindow.Current.Name) {
            Write-Host "`nVentana secundaria encontrada: '$($window.Current.Name)'" -ForegroundColor Magenta
        }
    }
}

Write-Host "`n=== Test completado ===" -ForegroundColor Cyan
