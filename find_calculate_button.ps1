# Find Calculate button
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$calcpadProcess = Get-Process | Where-Object { $_.ProcessName -eq "Calcpad" } | Select-Object -First 1

if ($null -eq $calcpadProcess) {
    Write-Host "ERROR: Calcpad no esta en ejecucion" -ForegroundColor Red
    exit 1
}

$automation = [System.Windows.Automation.AutomationElement]::RootElement

$condition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    $calcpadProcess.Id
)

$mainWindow = $automation.FindFirst(
    [System.Windows.Automation.TreeScope]::Children,
    $condition
)

if ($null -eq $mainWindow) {
    Write-Host "ERROR: Ventana no encontrada" -ForegroundColor Red
    exit 1
}

Write-Host "Buscando botones..." -ForegroundColor Cyan
Write-Host ""

# Find all buttons
$buttonCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Button
)

$buttons = $mainWindow.FindAll(
    [System.Windows.Automation.TreeScope]::Descendants,
    $buttonCondition
)

Write-Host "Encontrados $($buttons.Count) botones:" -ForegroundColor Green
Write-Host ""

foreach ($button in $buttons) {
    $name = $button.Current.Name
    $automationId = $button.Current.AutomationId
    $className = $button.Current.ClassName

    if ($name -match "Calculate" -or $automationId -match "Calculate" -or $name -eq "=") {
        Write-Host "[CALCULATE BUTTON FOUND]" -ForegroundColor Yellow
        Write-Host "  Name: $name" -ForegroundColor Cyan
        Write-Host "  AutomationId: $automationId" -ForegroundColor Cyan
        Write-Host "  ClassName: $className" -ForegroundColor Cyan
        Write-Host ""
    }
}
