# Press Calculate button
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

# Find Calculate button by name "="
$buttonCondition = New-Object System.Windows.Automation.AndCondition(
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Button
    )),
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        "="
    ))
)

$calculateButton = $mainWindow.FindFirst(
    [System.Windows.Automation.TreeScope]::Descendants,
    $buttonCondition
)

if ($null -ne $calculateButton) {
    Write-Host "Calculate button encontrado, presionando..." -ForegroundColor Green

    # Click Calculate
    $invokePattern = $calculateButton.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    $invokePattern.Invoke()

    Write-Host "Calculate button presionado!" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "ERROR: Calculate button no encontrado" -ForegroundColor Red
}
