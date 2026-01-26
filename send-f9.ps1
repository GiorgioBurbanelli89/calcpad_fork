Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$proc = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $proc) {
    Write-Host "ERROR: Calcpad no esta ejecutandose"
    exit 1
}

Write-Host "=== ENVIANDO F9 A CALCPAD ===" -ForegroundColor Green
Write-Host "PID: $($proc.Id)"

# Get main window handle
$hwnd = $proc.MainWindowHandle
if ($hwnd -eq [IntPtr]::Zero) {
    Write-Host "ERROR: No se pudo obtener ventana principal"
    exit 1
}

# Bring window to foreground
Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    public class Win32 {
        [DllImport("user32.dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
    }
"@

[Win32]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 500

# Send F9 key (VK_F9 = 0x78)
$VK_F9 = 0x78
$KEYEVENTF_KEYUP = 0x0002

Write-Host "Enviando F9..." -ForegroundColor Yellow
[Win32]::keybd_event($VK_F9, 0, 0, [UIntPtr]::Zero)  # Key down
Start-Sleep -Milliseconds 50
[Win32]::keybd_event($VK_F9, 0, $KEYEVENTF_KEYUP, [UIntPtr]::Zero)  # Key up

Write-Host "F9 enviado, esperando procesamiento..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

# Now inspect the output
$automation = [System.Windows.Automation.AutomationElement]::RootElement
$allWindows = $automation.FindAll(
    [System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.Condition]::TrueCondition
)

$calcpadWin = $null
foreach ($win in $allWindows) {
    if ($win.Current.ProcessId -eq $proc.Id) {
        $calcpadWin = $win
        break
    }
}

if (-not $calcpadWin) {
    Write-Host "No se pudo obtener ventana via UI Automation"
    exit 1
}

Write-Host ""
Write-Host "=== BUSCANDO OUTPUT ===" -ForegroundColor Yellow
$walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker

function Find-OutputControl($elem) {
    try {
        $automationId = $elem.Current.AutomationId
        $className = $elem.Current.ClassName
        $controlType = $elem.Current.ControlType.ProgrammaticName

        # Look for OutputFrame GroupBox
        if ($automationId -eq "OutputFrame" -or ($className -eq "GroupBox" -and $elem.Current.Name -like "*Output*")) {
            Write-Host "  [ENCONTRADO] OutputFrame GroupBox" -ForegroundColor Green

            # Try to find WebView2 inside
            $child = $walker.GetFirstChild($elem)
            while ($child) {
                try {
                    $childType = $child.Current.ControlType.ProgrammaticName
                    $childClass = $child.Current.ClassName

                    if ($childClass -like "*WebView*" -or $childClass -like "*Browser*") {
                        Write-Host "  [ENCONTRADO] WebView2: Class='$childClass'" -ForegroundColor Cyan

                        # Try to get document
                        $doc = $walker.GetFirstChild($child)
                        if ($doc) {
                            Write-Host "  [DOCUMENTO]" -ForegroundColor Magenta
                            try {
                                $valuePattern = $doc.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                                if ($valuePattern) {
                                    $value = $valuePattern.Current.Value
                                    if ($value) {
                                        Write-Host "  VALUE LENGTH: $($value.Length) chars" -ForegroundColor Gray
                                        $preview = $value.Substring(0, [Math]::Min(500, $value.Length))
                                        Write-Host "  PREVIEW:" -ForegroundColor Gray
                                        Write-Host $preview
                                    }
                                }
                            } catch {
                                Write-Host "  (No ValuePattern disponible)" -ForegroundColor DarkGray
                            }
                        }
                    }
                } catch {}
                $child = $walker.GetNextSibling($child)
            }
        }

        # Recurse children
        $child = $walker.GetFirstChild($elem)
        while ($child) {
            Find-OutputControl $child
            $child = $walker.GetNextSibling($child)
        }
    } catch {}
}

Find-OutputControl $calcpadWin

Write-Host ""
Write-Host "=== COMPLETO ===" -ForegroundColor Green
