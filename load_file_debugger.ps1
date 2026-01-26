Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms

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

# Buscar boton por AutomationId
$buttonCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
    "btnLoad"
)

$loadButton = $mainWindow.FindFirst(
    [System.Windows.Automation.TreeScope]::Descendants,
    $buttonCondition
)

if ($null -ne $loadButton) {
    Write-Host "Haciendo clic en 'Cargar Archivo'..." -ForegroundColor Yellow
    
    $invokePattern = $loadButton.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    $invokePattern.Invoke()
    
    Start-Sleep -Milliseconds 800
    
    # Escribir ruta del archivo
    Write-Host "Escribiendo ruta del archivo..." -ForegroundColor Yellow
    [System.Windows.Forms.SendKeys]::SendWait("C:\Users\j-b-j\Documents\Calcpad-7.5.7\test_simple_progress.cpd")
    Start-Sleep -Milliseconds 300
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    
    Start-Sleep -Milliseconds 500
    
    Write-Host "Archivo cargado exitosamente" -ForegroundColor Green
} else {
    Write-Host "No se encontro el boton btnLoad" -ForegroundColor Red
}
