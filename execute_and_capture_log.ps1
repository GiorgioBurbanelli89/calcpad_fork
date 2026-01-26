# Ejecutar Continue y capturar log con instrumentación

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$debuggerProcess = Get-Process | Where-Object { $_.ProcessName -eq "CalcpadDebugger" } | Select-Object -First 1

if ($null -eq $debuggerProcess) {
    Write-Host "ERROR: Depurador no esta ejecutandose" -ForegroundColor Red
    exit 1
}

$automation = [System.Windows.Automation.AutomationElement]::RootElement
$condition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    [int]$debuggerProcess.Id
)

$mainWindow = $automation.FindFirst([System.Windows.Automation.TreeScope]::Children, $condition)

Write-Host "=== EJECUTANDO CODIGO ===" -ForegroundColor Cyan
Write-Host ""

# Ejecutar Continue (F5)
$btnContinue = $mainWindow.FindFirst(
    [System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
        "btnContinue"
    ))
)

if ($null -ne $btnContinue -and $btnContinue.Current.IsEnabled) {
    Write-Host "Presionando Continue (F5)..." -ForegroundColor Yellow
    $invokePattern = $btnContinue.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    $invokePattern.Invoke()
    
    Write-Host "Esperando finalizacion..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}

Write-Host ""
Write-Host "=== LOG DE INSTRUMENTACION ===" -ForegroundColor Cyan
Write-Host ""

# Leer output
$outputBox = $mainWindow.FindFirst(
    [System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
        "outputTextBox"
    ))
)

if ($null -ne $outputBox) {
    $valuePattern = $outputBox.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
    $output = $valuePattern.Current.Value
    
    # Mostrar solo las ultimas 40 lineas
    $lines = $output -split "`n" | Select-Object -Last 40
    
    foreach ($line in $lines) {
        if ($line -match "^.+\[Linea \d+\]") {
            Write-Host $line -ForegroundColor Green
        } elseif ($line -match "avalonia" -or $line -match "Avalonia") {
            Write-Host $line -ForegroundColor Yellow
        } elseif ($line -match "ERROR|Error|error") {
            Write-Host $line -ForegroundColor Red
        } elseif ($line -match "^\s*�") {
            Write-Host $line -ForegroundColor Cyan
        } else {
            Write-Host $line
        }
    }
}

Write-Host ""
