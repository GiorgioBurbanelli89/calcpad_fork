Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$debuggerProcess = Get-Process | Where-Object { $_.ProcessName -eq "CalcpadDebugger" } | Select-Object -First 1

if ($null -eq $debuggerProcess) {
    Write-Host "No debugger running" -ForegroundColor Red
    exit 1
}

$automation = [System.Windows.Automation.AutomationElement]::RootElement
$condition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    [int]$debuggerProcess.Id
)

$mainWindow = $automation.FindFirst([System.Windows.Automation.TreeScope]::Children, $condition)

# Leer output completo
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
    
    Write-Host "=== OUTPUT COMPLETO ===" -ForegroundColor Cyan
    Write-Host $output
}
