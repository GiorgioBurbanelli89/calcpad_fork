# Open test file and calculate
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

Start-Sleep -Seconds 2

$calcpadProcess = Get-Process | Where-Object { $_.ProcessName -eq "Calcpad" } | Select-Object -First 1

if ($null -eq $calcpadProcess) {
    Write-Host "ERROR: Calcpad no esta en ejecucion" -ForegroundColor Red
    exit 1
}

Write-Host "Proceso Calcpad: PID $($calcpadProcess.Id)" -ForegroundColor Green

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

Write-Host "Ventana: $($mainWindow.Current.Name)" -ForegroundColor Cyan

# Buscar TextEditor (AvalonEdit)
$textEditorCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
    "TextEditor"
)

$textEditor = $mainWindow.FindFirst(
    [System.Windows.Automation.TreeScope]::Descendants,
    $textEditorCondition
)

if ($null -ne $textEditor) {
    Write-Host "TextEditor encontrado" -ForegroundColor Green

    # Get ValuePattern to set text
    $valuePattern = $textEditor.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)

    # Read test file content
    $testContent = Get-Content "C:\Users\j-b-j\Documents\Calcpad-7.5.7\test_autocomplete_calcpad.cpd" -Raw

    # Set content
    $valuePattern.SetValue($testContent)
    Write-Host "Archivo de prueba cargado" -ForegroundColor Green

    Start-Sleep -Milliseconds 500

    # Find Calculate button
    $calculateCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
        "CalculateButton"
    )

    $calculateButton = $mainWindow.FindFirst(
        [System.Windows.Automation.TreeScope]::Descendants,
        $calculateCondition
    )

    if ($null -ne $calculateButton) {
        Write-Host "Calculate button encontrado" -ForegroundColor Green

        # Click Calculate
        $invokePattern = $calculateButton.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
        $invokePattern.Invoke()

        Write-Host "Calculate button presionado!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Esperando 3 segundos para que se procese..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3

        Write-Host ""
        Write-Host "Revisa el log de debug:" -ForegroundColor Cyan
        Write-Host "======================================" -ForegroundColor Cyan

        # Show last 20 lines of debug log
        $debugLog = "$env:TEMP\calcpad-debug.txt"
        if (Test-Path $debugLog) {
            Get-Content $debugLog -Tail 20
        } else {
            Write-Host "Log no encontrado en $debugLog" -ForegroundColor Red
        }
    } else {
        Write-Host "ERROR: Calculate button no encontrado" -ForegroundColor Red
    }
} else {
    Write-Host "ERROR: TextEditor no encontrado" -ForegroundColor Red
}
