# Monitor Calcpad in Real-Time
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms

Write-Host "=== Monitor Calcpad en Tiempo Real ===" -ForegroundColor Cyan
Write-Host "Monitoreando dialogos, ventanas y eventos..." -ForegroundColor Yellow
Write-Host "Presiona Ctrl+C para terminar" -ForegroundColor Gray
Write-Host ""

$calcpadProcess = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $calcpadProcess) {
    Write-Host "ERROR: Calcpad no esta corriendo" -ForegroundColor Red
    exit 1
}

Write-Host "Calcpad PID: $($calcpadProcess.Id)" -ForegroundColor Green
Write-Host ""

$root = [System.Windows.Automation.AutomationElement]::RootElement
$seenWindows = @{}
$lastClipboardHasImage = $false

while ($true) {
    # Check clipboard status
    $clipboardHasImage = [System.Windows.Forms.Clipboard]::ContainsImage()
    if ($clipboardHasImage -ne $lastClipboardHasImage) {
        $timestamp = Get-Date -Format "HH:mm:ss"
        if ($clipboardHasImage) {
            Write-Host "[$timestamp] CLIPBOARD: Imagen detectada en portapapeles" -ForegroundColor Green
        } else {
            Write-Host "[$timestamp] CLIPBOARD: Sin imagen" -ForegroundColor Gray
        }
        $lastClipboardHasImage = $clipboardHasImage
    }

    # Find all windows
    $windowCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Window
    )
    $allWindows = $root.FindAll([System.Windows.Automation.TreeScope]::Children, $windowCondition)

    foreach ($window in $allWindows) {
        $procId = $window.Current.ProcessId
        $name = $window.Current.Name
        $className = $window.Current.ClassName
        $key = "$procId|$name|$className"

        # Only track Calcpad windows
        if ($procId -eq $calcpadProcess.Id) {
            if (-not $seenWindows.ContainsKey($key)) {
                $seenWindows[$key] = Get-Date
                $timestamp = Get-Date -Format "HH:mm:ss"

                # Skip main window
                if ($name -notmatch "Calcpad Fork Branch") {
                    Write-Host ""
                    Write-Host "[$timestamp] === NUEVA VENTANA ===" -ForegroundColor Yellow
                    Write-Host "  Titulo: '$name'" -ForegroundColor White
                    Write-Host "  Clase: '$className'" -ForegroundColor Gray

                    # List all controls
                    try {
                        $controls = $window.FindAll(
                            [System.Windows.Automation.TreeScope]::Descendants,
                            [System.Windows.Automation.Condition]::TrueCondition
                        )

                        Write-Host "  Controles ($($controls.Count)):" -ForegroundColor Cyan
                        foreach ($ctrl in $controls) {
                            $ctrlType = $ctrl.Current.ControlType.ProgrammaticName -replace "ControlType.", ""
                            $ctrlName = $ctrl.Current.Name
                            $ctrlId = $ctrl.Current.AutomationId

                            if ($ctrlName -or $ctrlId) {
                                $info = "    [$ctrlType]"
                                if ($ctrlName) { $info += " Name='$ctrlName'" }
                                if ($ctrlId) { $info += " Id='$ctrlId'" }
                                Write-Host $info -ForegroundColor Gray
                            }
                        }
                    } catch {
                        Write-Host "  (No se pudo leer controles)" -ForegroundColor DarkGray
                    }
                    Write-Host ""
                }
            }
        }
    }

    # Also check for MessageBox dialogs (#32770)
    $msgBoxCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ClassNameProperty,
        "#32770"
    )
    $messageBoxes = $root.FindAll([System.Windows.Automation.TreeScope]::Children, $msgBoxCondition)

    foreach ($msgBox in $messageBoxes) {
        $procId = $msgBox.Current.ProcessId
        $name = $msgBox.Current.Name
        $key = "msgbox|$procId|$name"

        if ($procId -eq $calcpadProcess.Id -and -not $seenWindows.ContainsKey($key)) {
            $seenWindows[$key] = Get-Date
            $timestamp = Get-Date -Format "HH:mm:ss"

            Write-Host ""
            Write-Host "[$timestamp] === MESSAGEBOX ===" -ForegroundColor Magenta
            Write-Host "  Titulo: '$name'" -ForegroundColor White

            # Get text content
            $textCondition = New-Object System.Windows.Automation.PropertyCondition(
                [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
                [System.Windows.Automation.ControlType]::Text
            )
            $texts = $msgBox.FindAll([System.Windows.Automation.TreeScope]::Descendants, $textCondition)
            foreach ($text in $texts) {
                if ($text.Current.Name) {
                    Write-Host "  Mensaje: '$($text.Current.Name)'" -ForegroundColor Yellow
                }
            }

            # Get buttons
            $btnCondition = New-Object System.Windows.Automation.PropertyCondition(
                [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
                [System.Windows.Automation.ControlType]::Button
            )
            $buttons = $msgBox.FindAll([System.Windows.Automation.TreeScope]::Descendants, $btnCondition)
            $btnNames = ($buttons | ForEach-Object { $_.Current.Name }) -join ", "
            Write-Host "  Botones: $btnNames" -ForegroundColor Cyan
            Write-Host ""
        }
    }

    # Clean up old entries (windows that closed)
    $toRemove = @()
    foreach ($key in $seenWindows.Keys) {
        $age = (Get-Date) - $seenWindows[$key]
        if ($age.TotalSeconds > 60) {
            # Check if window still exists
            $stillExists = $false
            foreach ($window in $allWindows) {
                $procId = $window.Current.ProcessId
                $name = $window.Current.Name
                $className = $window.Current.ClassName
                $checkKey = "$procId|$name|$className"
                if ($checkKey -eq $key) {
                    $stillExists = $true
                    break
                }
            }
            if (-not $stillExists -and $key -notmatch "Calcpad Fork Branch") {
                $toRemove += $key
            }
        }
    }
    foreach ($key in $toRemove) {
        $seenWindows.Remove($key)
        $timestamp = Get-Date -Format "HH:mm:ss"
        Write-Host "[$timestamp] Ventana cerrada: $($key.Split('|')[1])" -ForegroundColor DarkGray
    }

    Start-Sleep -Milliseconds 200
}
