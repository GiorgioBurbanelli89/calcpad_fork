# Test simple automatico
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

Write-Output "========================================="
Write-Output "TEST AUTOMATICO SIMPLE"
Write-Output "========================================="

# Abrir archivo
$testFile = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\test_code_c.cpd"
Write-Output "Abriendo: $testFile"
Start-Process "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\bin\Release\net10.0-windows\Calcpad.exe" -ArgumentList "`"$testFile`""

Start-Sleep -Seconds 3

# Buscar Calcpad
$automation = [System.Windows.Automation.AutomationElement]::RootElement
$windows = $automation.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)

$calcpadWindow = $null
foreach ($window in $windows) {
    if ($window.Current.Name -like "*Calcpad*") {
        $calcpadWindow = $window
        Write-Output "Calcpad encontrado: $($window.Current.Name)"
        break
    }
}

if ($null -eq $calcpadWindow) {
    Write-Output "ERROR: No se encontro Calcpad"
    exit 1
}

Start-Sleep -Seconds 2

# Inspeccionar controles
Write-Output ""
Write-Output "Inspeccionando controles..."

$allElements = $calcpadWindow.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
Write-Output "Total elementos: $($allElements.Count)"

# Buscar PreviewTextBlock
$previewTextBlock = $null
foreach ($element in $allElements) {
    if ($element.Current.AutomationId -eq "PreviewTextBlock") {
        $previewTextBlock = $element
        $text = $element.Current.Name
        Write-Output ""
        Write-Output "PreviewTextBlock encontrado:"
        Write-Output "  Texto: '$text'"
        break
    }
}

# Buscar PreviewEditor
$previewEditor = $null
foreach ($element in $allElements) {
    if ($element.Current.AutomationId -eq "PreviewEditor") {
        $previewEditor = $element
        $isVisible = -not $element.Current.IsOffscreen
        Write-Output ""
        Write-Output "PreviewEditor encontrado:"
        Write-Output "  Visible: $isVisible"
        break
    }
}

# Ver log
Write-Output ""
Write-Output "========================================="
Write-Output "Verificando log..."
$logPath = "C:\Users\j-b-j\Desktop\calcpad_debug.log"

if (Test-Path $logPath) {
    Write-Output "Log existe en: $logPath"
    Write-Output ""
    Write-Output "ULTIMAS 30 LINEAS:"
    Get-Content $logPath -Tail 30 | ForEach-Object { Write-Output $_ }
} else {
    Write-Output "Log NO existe aun"
}

Write-Output ""
Write-Output "========================================="
Write-Output "Test completado"
Write-Output "========================================="
