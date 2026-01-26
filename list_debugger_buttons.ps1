Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$debuggerProcess = Get-Process | Where-Object { $_.ProcessName -eq "CalcpadDebugger" } | Select-Object -First 1

if ($null -eq $debuggerProcess) {
    Write-Host "CalcpadDebugger no esta ejecutandose" -ForegroundColor Red
    exit 1
}

$automation = [System.Windows.Automation.AutomationElement]::RootElement
$condition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    $debuggerProcess.Id
)

$mainWindow = $automation.FindFirst(
    [System.Windows.Automation.TreeScope]::Children,
    $condition
)

Write-Host "=== BOTONES EN EL DEPURADOR ===" -ForegroundColor Cyan

$allButtons = $mainWindow.FindAll(
    [System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Button
    ))
)

foreach ($btn in $allButtons) {
    $name = $btn.Current.Name
    $enabled = $btn.Current.IsEnabled
    $automationId = $btn.Current.AutomationId
    $color = if ($enabled) { "Green" } else { "Gray" }
    Write-Host "  Nombre: '$name' | ID: '$automationId' | Habilitado: $enabled" -ForegroundColor $color
}
