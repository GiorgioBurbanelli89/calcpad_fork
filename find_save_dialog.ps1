# Buscar dialogo de guardar
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

Write-Host "Buscando dialogo de guardar PDF..." -ForegroundColor Cyan

$automation = [System.Windows.Automation.AutomationElement]::RootElement

$windowCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Window
)

$allWindows = $automation.FindAll(
    [System.Windows.Automation.TreeScope]::Children,
    $windowCondition
)

Write-Host "Total ventanas abiertas: $($allWindows.Count)" -ForegroundColor Yellow
Write-Host ""

foreach ($window in $allWindows) {
    $windowName = $window.Current.Name
    $windowClass = $window.Current.ClassName

    Write-Host "Ventana: '$windowName' (Class: $windowClass)" -ForegroundColor Gray

    if ($windowName -match "Guardar|Save|PDF" -or $windowClass -eq "#32770") {
        Write-Host "  >>> POSIBLE DIALOGO ENCONTRADO <<<" -ForegroundColor Green
        Write-Host "  Name: $windowName" -ForegroundColor Cyan
        Write-Host "  Class: $windowClass" -ForegroundColor Cyan
    }
}
