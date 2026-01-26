Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$debuggerProcess = Get-Process | Where-Object { $_.ProcessName -eq "CalcpadDebugger" } | Select-Object -First 1
$automation = [System.Windows.Automation.AutomationElement]::RootElement
$condition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    $debuggerProcess.Id
)
$mainWindow = $automation.FindFirst([System.Windows.Automation.TreeScope]::Children, $condition)

# Ejecutar 3 pasos
Write-Host "Ejecutando 3 pasos de depuración..." -ForegroundColor Cyan
Write-Host ""

for ($i = 1; $i -le 3; $i++) {
    Write-Host "--- PASO $i ---" -ForegroundColor Yellow
    
    # Hacer clic en Step Over
    $stepButton = $mainWindow.FindFirst(
        [System.Windows.Automation.TreeScope]::Descendants,
        (New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
            "btnStepOver"
        ))
    )
    
    if ($null -ne $stepButton -and $stepButton.Current.IsEnabled) {
        $invokePattern = $stepButton.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
        $invokePattern.Invoke()
        Start-Sleep -Milliseconds 500
        
        # Leer output log
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
            
            # Mostrar las últimas 5 líneas
            $lines = $output -split "`n" | Select-Object -Last 5
            foreach ($line in $lines) {
                if ($line.Trim() -ne "") {
                    Write-Host $line
                }
            }
        }
    }
    
    Write-Host ""
}
