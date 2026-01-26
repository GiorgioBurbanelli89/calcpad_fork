# Monitor Calcpad Paste Operations in Real-Time
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Write-Host "=== Monitor de Pegado en Calcpad ===" -ForegroundColor Cyan
Write-Host "Este script monitoreara cualquier dialogo o ventana que aparezca" -ForegroundColor Yellow
Write-Host "Presiona Ctrl+C para terminar" -ForegroundColor Yellow
Write-Host ""

$calcpadProcess = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $calcpadProcess) {
    Write-Host "ERROR: Calcpad no esta corriendo" -ForegroundColor Red
    exit 1
}

$root = [System.Windows.Automation.AutomationElement]::RootElement
$lastWindowCount = 0
$seenWindows = @{}

Write-Host "Monitoreando Calcpad (PID: $($calcpadProcess.Id))..." -ForegroundColor Green
Write-Host "Esperando que pegues una imagen con Ctrl+V..." -ForegroundColor Cyan
Write-Host ""

while ($true) {
    $windowCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Window
    )

    $allWindows = $root.FindAll([System.Windows.Automation.TreeScope]::Children, $windowCondition)

    foreach ($window in $allWindows) {
        $pid = $window.Current.ProcessId
        $name = $window.Current.Name
        $key = "$pid|$name"

        # Only show windows from Calcpad process that we haven't seen
        if ($pid -eq $calcpadProcess.Id -and -not $seenWindows.ContainsKey($key)) {
            $seenWindows[$key] = $true
            $timestamp = Get-Date -Format "HH:mm:ss"

            if ($name -notmatch "Calcpad Fork Branch") {
                Write-Host "[$timestamp] NUEVA VENTANA DETECTADA:" -ForegroundColor Yellow
                Write-Host "  Nombre: '$name'" -ForegroundColor White
                Write-Host "  ClassName: '$($window.Current.ClassName)'" -ForegroundColor Gray

                # List controls
                $controls = $window.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
                Write-Host "  Controles:" -ForegroundColor Cyan
                foreach ($ctrl in $controls) {
                    $ctrlType = $ctrl.Current.ControlType.ProgrammaticName -replace "ControlType.", ""
                    $ctrlName = $ctrl.Current.Name
                    $ctrlId = $ctrl.Current.AutomationId
                    if ($ctrlName -or $ctrlId) {
                        Write-Host "    [$ctrlType] Name='$ctrlName' Id='$ctrlId'" -ForegroundColor Gray
                    }
                }
                Write-Host ""
            }
        }
    }

    # Also check for any message boxes
    $messageBoxCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ClassNameProperty,
        "#32770"
    )
    $messageBoxes = $root.FindAll([System.Windows.Automation.TreeScope]::Children, $messageBoxCondition)

    foreach ($msgBox in $messageBoxes) {
        $pid = $msgBox.Current.ProcessId
        $name = $msgBox.Current.Name
        $key = "msgbox|$pid|$name"

        if ($pid -eq $calcpadProcess.Id -and -not $seenWindows.ContainsKey($key)) {
            $seenWindows[$key] = $true
            $timestamp = Get-Date -Format "HH:mm:ss"
            Write-Host "[$timestamp] MESSAGEBOX DETECTADO:" -ForegroundColor Magenta
            Write-Host "  Titulo: '$name'" -ForegroundColor White

            # Get text content
            $textCondition = New-Object System.Windows.Automation.PropertyCondition(
                [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
                [System.Windows.Automation.ControlType]::Text
            )
            $texts = $msgBox.FindAll([System.Windows.Automation.TreeScope]::Descendants, $textCondition)
            foreach ($text in $texts) {
                Write-Host "  Texto: '$($text.Current.Name)'" -ForegroundColor Yellow
            }
            Write-Host ""
        }
    }

    Start-Sleep -Milliseconds 200
}
