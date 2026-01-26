# Test Paste Image Dialog in Calcpad WPF - Version 2
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);
    [DllImport("user32.dll")]
    public static extern void mouse_event(int dwFlags, int dx, int dy, int dwData, int dwExtraInfo);
    public const int MOUSEEVENTF_LEFTDOWN = 0x02;
    public const int MOUSEEVENTF_LEFTUP = 0x04;
}
"@

Write-Host "=== Test Paste Image Dialog v2 ===" -ForegroundColor Cyan

# Find Calcpad window
$calcpadProcess = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $calcpadProcess) {
    Write-Host "ERROR: Calcpad no esta corriendo" -ForegroundColor Red
    exit 1
}

Write-Host "Calcpad encontrado: PID $($calcpadProcess.Id)" -ForegroundColor Green

# Get window bounds
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

$bounds = $calcpadWindow.Current.BoundingRectangle
Write-Host "Ventana: $($calcpadWindow.Current.Name)" -ForegroundColor Green
Write-Host "Posicion: X=$($bounds.X), Y=$($bounds.Y), W=$($bounds.Width), H=$($bounds.Height)" -ForegroundColor Gray

# Focus window
[Win32]::SetForegroundWindow($calcpadProcess.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 300

# Find the RichTextBox (editor area) - it's on the left side
Write-Host "`nBuscando area del editor..." -ForegroundColor Yellow

$docCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Document
)
$editors = $calcpadWindow.FindAll([System.Windows.Automation.TreeScope]::Descendants, $docCondition)

Write-Host "Documentos encontrados: $($editors.Count)" -ForegroundColor Gray

foreach ($editor in $editors) {
    $edBounds = $editor.Current.BoundingRectangle
    Write-Host "  Editor: Name='$($editor.Current.Name)' AutomationId='$($editor.Current.AutomationId)'" -ForegroundColor White
    Write-Host "    Bounds: X=$($edBounds.X), Y=$($edBounds.Y), W=$($edBounds.Width), H=$($edBounds.Height)" -ForegroundColor Gray
}

# Click in the middle-left of the window (editor area is typically on the left)
$clickX = [int]($bounds.X + 200)
$clickY = [int]($bounds.Y + 300)

Write-Host "`nHaciendo clic en el editor en ($clickX, $clickY)..." -ForegroundColor Yellow
[Win32]::SetCursorPos($clickX, $clickY)
Start-Sleep -Milliseconds 100
[Win32]::mouse_event([Win32]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
Start-Sleep -Milliseconds 50
[Win32]::mouse_event([Win32]::MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
Start-Sleep -Milliseconds 300

# Create test image
Write-Host "`nCreando imagen de prueba..." -ForegroundColor Yellow
$bitmap = New-Object System.Drawing.Bitmap(100, 100)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.Clear([System.Drawing.Color]::LightBlue)
$graphics.FillEllipse([System.Drawing.Brushes]::Red, 25, 25, 50, 50)
$graphics.DrawString("Test", [System.Drawing.SystemFonts]::DefaultFont, [System.Drawing.Brushes]::Black, 35, 40)
$graphics.Dispose()
[System.Windows.Forms.Clipboard]::SetImage($bitmap)
$bitmap.Dispose()
Write-Host "Imagen copiada al portapapeles" -ForegroundColor Green

# Wait and check clipboard
Start-Sleep -Milliseconds 200
$hasImage = [System.Windows.Forms.Clipboard]::ContainsImage()
Write-Host "Portapapeles contiene imagen: $hasImage" -ForegroundColor $(if($hasImage){"Green"}else{"Red"})

# Send Ctrl+V
Write-Host "`nEnviando Ctrl+V..." -ForegroundColor Yellow
[System.Windows.Forms.SendKeys]::SendWait("^v")

# Wait for dialog
Start-Sleep -Seconds 2

# Look for dialog
Write-Host "`nBuscando dialogo..." -ForegroundColor Yellow

$windowCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Window
)

# Search for dialogs owned by Calcpad
$calcpadWindows = $root.FindAll([System.Windows.Automation.TreeScope]::Children, $windowCondition)
$dialogFound = $false

foreach ($window in $calcpadWindows) {
    if ($window.Current.ProcessId -eq $calcpadProcess.Id) {
        $windowName = $window.Current.Name
        Write-Host "  Ventana Calcpad: '$windowName'" -ForegroundColor White

        if ($windowName -match "Pegar" -or $windowName -match "Paste" -or $windowName -match "Image") {
            Write-Host "`n*** DIALOGO ENCONTRADO! ***" -ForegroundColor Green
            $dialogFound = $true

            # List controls
            $allControls = $window.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
            Write-Host "Controles:" -ForegroundColor Cyan
            foreach ($control in $allControls) {
                $ctrlType = $control.Current.ControlType.ProgrammaticName -replace "ControlType.", ""
                $ctrlName = $control.Current.Name
                if ($ctrlName) {
                    Write-Host "  [$ctrlType] $ctrlName" -ForegroundColor Gray
                }
            }

            # Close dialog
            $cancelBtn = $window.FindFirst([System.Windows.Automation.TreeScope]::Descendants,
                (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, "Cancelar")))
            if ($cancelBtn) {
                Write-Host "`nCerrando dialogo..." -ForegroundColor Yellow
                $cancelBtn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
            }
            break
        }
    }
}

if (-not $dialogFound) {
    Write-Host "`nDialogo NO encontrado" -ForegroundColor Red

    # Check if there's any MessageBox
    Write-Host "`nRevisando si hay MessageBox..." -ForegroundColor Yellow
    foreach ($window in $calcpadWindows) {
        if ($window.Current.ProcessId -eq $calcpadProcess.Id) {
            $className = $window.Current.ClassName
            Write-Host "  Window: '$($window.Current.Name)' Class='$className'" -ForegroundColor Gray
        }
    }
}

Write-Host "`n=== Test completado ===" -ForegroundColor Cyan
