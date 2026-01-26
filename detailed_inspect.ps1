Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$proc = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $proc) {
    Write-Host "ERROR: Calcpad no esta ejecutandose"
    exit 1
}

Write-Host "=== CALCPAD ENCONTRADO ===" -ForegroundColor Green
Write-Host "PID: $($proc.Id)"
Write-Host "Title: $($proc.MainWindowTitle)"
Write-Host ""

# Get automation element
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
    Write-Host "No se pudo obtener ventana de Calcpad via UI Automation"
    exit
}

Write-Host "=== BUSCANDO CONTROLES ===" -ForegroundColor Yellow
$walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker

function Get-ElementInfo($elem, $depth = 0) {
    if ($depth -gt 8) { return }
    
    try {
        $indent = "  " * $depth
        $name = $elem.Current.Name
        $className = $elem.Current.ClassName
        $controlType = $elem.Current.ControlType.ProgrammaticName
        $automationId = $elem.Current.AutomationId
        
        # Solo mostrar elementos interesantes
        if ($controlType -like "*Edit*" -or $controlType -like "*Document*" -or 
            $controlType -like "*Text*" -or $automationId -like "*Editor*" -or
            $automationId -like "*Output*" -or $className -like "*WebView*" -or
            $className -like "*TextEditor*") {
            
            Write-Host "$indent[$controlType] Name='$name' Class='$className' Id='$automationId'" -ForegroundColor Cyan
            
            # Try to get text value
            try {
                $valuePattern = $elem.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                if ($valuePattern) {
                    $value = $valuePattern.Current.Value
                    if ($value -and $value.Length -gt 0) {
                        $preview = $value.Substring(0, [Math]::Min(100, $value.Length))
                        Write-Host "$indent  VALUE: $preview..." -ForegroundColor Gray
                    }
                }
            } catch {}
            
            # Try to get text pattern
            try {
                $textPattern = $elem.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
                if ($textPattern) {
                    $text = $textPattern.DocumentRange.GetText(200)
                    if ($text) {
                        Write-Host "$indent  TEXT: $text" -ForegroundColor Gray
                    }
                }
            } catch {}
        }
        
        # Recurse children
        $child = $walker.GetFirstChild($elem)
        while ($child) {
            Get-ElementInfo $child ($depth + 1)
            $child = $walker.GetNextSibling($child)
        }
    } catch {
        # Ignore errors
    }
}

Get-ElementInfo $calcpadWin

Write-Host ""
Write-Host "=== INSPECCION COMPLETA ===" -ForegroundColor Green
