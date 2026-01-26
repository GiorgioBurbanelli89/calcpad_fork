# Test UI Automation en Calcpad WPF
# Verifica si los paneles Code y Output tienen AutomationProperties configurados

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

Write-Host "`n=== TEST UI AUTOMATION - CALCPAD WPF ===" -ForegroundColor Cyan
Write-Host "Buscando ventana de Calcpad...`n" -ForegroundColor Yellow

# Buscar ventana principal
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$calcpadCondition = New-Object System.Windows.Automation.AndCondition(
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Window
    )),
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        " Calcpad VM 7.5.8"
    ))
)

$mainWindow = $desktop.FindFirst(
    [System.Windows.Automation.TreeScope]::Children,
    $calcpadCondition
)

if (!$mainWindow) {
    # Intentar sin el espacio inicial
    $calcpadCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        "Calcpad VM 7.5.8"
    )
    $mainWindow = $desktop.FindFirst(
        [System.Windows.Automation.TreeScope]::Children,
        $calcpadCondition
    )
}

if (!$mainWindow) {
    # Buscar cualquier ventana con "Calcpad" en el nombre
    $allWindows = $desktop.FindAll(
        [System.Windows.Automation.TreeScope]::Children,
        [System.Windows.Automation.Condition]::TrueCondition
    )

    foreach ($window in $allWindows) {
        if ($window.Current.Name -like "*Calcpad*") {
            $mainWindow = $window
            break
        }
    }
}

