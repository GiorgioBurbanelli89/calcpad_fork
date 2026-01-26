Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$debuggerProcess = Get-Process | Where-Object { $_.ProcessName -eq "CalcpadDebugger" } | Select-Object -First 1

if ($null -eq $debuggerProcess) {
    Write-Host "CalcpadDebugger no esta ejecutandose" -ForegroundColor Red
    exit 1
}

Write-Host "Depurador encontrado (PID: $($debuggerProcess.Id))" -ForegroundColor Green

$automation = [System.Windows.Automation.AutomationElement]::RootElement
$condition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    $debuggerProcess.Id
)

$mainWindow = $automation.FindFirst(
    [System.Windows.Automation.TreeScope]::Children,
    $condition
)

if ($null -eq $mainWindow) {
    Write-Host "No se pudo encontrar la ventana principal" -ForegroundColor Red
    exit 1
}

Write-Host "Ventana: $($mainWindow.Current.Name)" -ForegroundColor Cyan
Write-Host ""

# Buscar el boton "Cargar Archivo"
$buttonCondition = New-Object System.Windows.Automation.AndCondition(@(
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Button
    )),
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        "Cargar Archivo"
    ))
))

$loadButton = $mainWindow.FindFirst(
    [System.Windows.Automation.TreeScope]::Descendants,
    $buttonCondition
)

if ($null -ne $loadButton) {
    Write-Host "Boton 'Cargar Archivo' encontrado" -ForegroundColor Green
    Write-Host "Haciendo clic..." -ForegroundColor Yellow
    
    $invokePattern = $loadButton.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    $invokePattern.Invoke()
    
    Start-Sleep -Milliseconds 500
    
    # Buscar el dialogo de archivo
    Write-Host "Buscando dialogo de archivo..." -ForegroundColor Yellow
    
    Start-Sleep -Milliseconds 1000
    
    # Enviar la ruta del archivo directamente
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.SendKeys]::SendWait("C:\Users\j-b-j\Documents\Calcpad-7.5.7\test_simple_progress.cpd")
    Start-Sleep -Milliseconds 300
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    
    Write-Host "Archivo cargado" -ForegroundColor Green
} else {
    Write-Host "No se pudo encontrar el boton 'Cargar Archivo'" -ForegroundColor Red
}
