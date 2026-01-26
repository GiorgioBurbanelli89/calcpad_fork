Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms

$debuggerProcess = Get-Process | Where-Object { $_.ProcessName -eq "CalcpadDebugger" } | Select-Object -First 1
$automation = [System.Windows.Automation.AutomationElement]::RootElement
$condition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    $debuggerProcess.Id
)
$mainWindow = $automation.FindFirst([System.Windows.Automation.TreeScope]::Children, $condition)

# Hacer clic en Cargar Archivo
$btnLoad = $mainWindow.FindFirst(
    [System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
        "btnLoad"
    ))
)

if ($null -ne $btnLoad) {
    Write-Host "Cargando ejemplo-multiples-lenguajes.cpd..." -ForegroundColor Yellow
    
    $invokePattern = $btnLoad.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    $invokePattern.Invoke()
    
    Start-Sleep -Milliseconds 800
    
    [System.Windows.Forms.SendKeys]::SendWait("C:\Users\j-b-j\Documents\Calcpad-7.5.7\ejemplo-multiples-lenguajes.cpd")
    Start-Sleep -Milliseconds 300
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    
    Start-Sleep -Milliseconds 500
    Write-Host "Archivo cargado" -ForegroundColor Green
}
