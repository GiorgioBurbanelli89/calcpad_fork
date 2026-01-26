# Script para hacer clic en el boton PDF
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

Write-Host "=== HACIENDO CLIC EN BOTON PDF ===" -ForegroundColor Cyan
Write-Host ""

# Buscar proceso de Calcpad
$calcpadProcess = Get-Process | Where-Object { $_.ProcessName -eq "Calcpad" } | Select-Object -First 1

if ($null -eq $calcpadProcess) {
    Write-Host "ERROR: Calcpad no esta en ejecucion" -ForegroundColor Red
    exit 1
}

Write-Host "Proceso Calcpad encontrado (PID: $($calcpadProcess.Id))" -ForegroundColor Green

# Obtener elemento raiz
$automation = [System.Windows.Automation.AutomationElement]::RootElement

# Buscar ventana de Calcpad
$condition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    $calcpadProcess.Id
)

$mainWindow = $automation.FindFirst(
    [System.Windows.Automation.TreeScope]::Children,
    $condition
)

if ($null -eq $mainWindow) {
    Write-Host "ERROR: No se pudo encontrar la ventana de Calcpad" -ForegroundColor Red
    exit 1
}

Write-Host "Ventana encontrada: $($mainWindow.Current.Name)" -ForegroundColor Green

# Buscar boton PDF por AutomationId
$pdfButtonCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
    "PdfButton"
)

$pdfButton = $mainWindow.FindFirst(
    [System.Windows.Automation.TreeScope]::Descendants,
    $pdfButtonCondition
)

if ($null -eq $pdfButton) {
    Write-Host "ERROR: No se encontro el boton PDF" -ForegroundColor Red
    exit 1
}

Write-Host "Boton PDF encontrado" -ForegroundColor Green
Write-Host "  Tooltip: $($pdfButton.Current.HelpText)" -ForegroundColor Gray
Write-Host "  Enabled: $($pdfButton.Current.IsEnabled)" -ForegroundColor Gray

# Hacer clic en el boton
Write-Host ""
Write-Host "Haciendo clic en el boton PDF..." -ForegroundColor Yellow

try {
    $invokePattern = $pdfButton.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    $invokePattern.Invoke()
    Write-Host "CLIC EJECUTADO EXITOSAMENTE" -ForegroundColor Green

    Write-Host ""
    Write-Host "Esperando dialogo de guardar..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2

    # Buscar dialogo de guardar archivo
    $dialogCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Window
    )

    $allWindows = $automation.FindAll(
        [System.Windows.Automation.TreeScope]::Children,
        $dialogCondition
    )

    foreach ($window in $allWindows) {
        $windowName = $window.Current.Name
        if ($windowName -match "Guardar|Save|PDF") {
            Write-Host "Dialogo encontrado: $windowName" -ForegroundColor Green

            # Buscar campo de nombre de archivo (ComboBox o Edit)
            $comboCondition = New-Object System.Windows.Automation.OrCondition(
                (New-Object System.Windows.Automation.PropertyCondition(
                    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
                    [System.Windows.Automation.ControlType]::Edit
                )),
                (New-Object System.Windows.Automation.PropertyCondition(
                    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
                    [System.Windows.Automation.ControlType]::ComboBox
                ))
            )

            $fileNameControl = $window.FindFirst(
                [System.Windows.Automation.TreeScope]::Descendants,
                $comboCondition
            )

            if ($null -ne $fileNameControl) {
                Write-Host "Campo de nombre encontrado" -ForegroundColor Green

                # Establecer nombre de archivo
                $outputPath = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\test_markdown_indice.pdf"

                try {
                    $valuePattern = $fileNameControl.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                    $valuePattern.SetValue($outputPath)
                    Write-Host "Ruta establecida: $outputPath" -ForegroundColor Cyan
                } catch {
                    Write-Host "ADVERTENCIA: No se pudo establecer el valor directamente" -ForegroundColor Yellow
                }

                Start-Sleep -Seconds 1

                # Buscar boton Guardar/Save
                $buttonCondition = New-Object System.Windows.Automation.PropertyCondition(
                    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
                    [System.Windows.Automation.ControlType]::Button
                )

                $buttons = $window.FindAll(
                    [System.Windows.Automation.TreeScope]::Descendants,
                    $buttonCondition
                )

                foreach ($btn in $buttons) {
                    $btnName = $btn.Current.Name
                    $btnId = $btn.Current.AutomationId

                    if ($btnName -match "Guardar|Save" -or $btnId -eq "1") {
                        Write-Host "Boton Guardar encontrado: $btnName (Id: $btnId)" -ForegroundColor Green

                        try {
                            $saveInvokePattern = $btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
                            $saveInvokePattern.Invoke()
                            Write-Host "BOTON GUARDAR PRESIONADO" -ForegroundColor Green

                            Start-Sleep -Seconds 3

                            # Verificar que se creo el PDF
                            if (Test-Path $outputPath) {
                                $fileInfo = Get-Item $outputPath
                                Write-Host ""
                                Write-Host "========================================" -ForegroundColor Green
                                Write-Host "PDF GENERADO EXITOSAMENTE" -ForegroundColor Green
                                Write-Host "========================================" -ForegroundColor Green
                                Write-Host ""
                                Write-Host "Archivo: $outputPath" -ForegroundColor Cyan
                                Write-Host "Tamano: $($fileInfo.Length) bytes" -ForegroundColor Cyan
                                Write-Host "Fecha: $($fileInfo.LastWriteTime)" -ForegroundColor Cyan
                                Write-Host ""
                                Write-Host "Abriendo PDF..." -ForegroundColor Yellow
                                Start-Process $outputPath
                                Write-Host "PDF abierto. Verifica los enlaces del indice." -ForegroundColor Green
                            } else {
                                Write-Host "ADVERTENCIA: El PDF no se encontro en la ubicacion esperada" -ForegroundColor Yellow
                            }

                            break
                        } catch {
                            Write-Host "ERROR al presionar Guardar: $($_.Exception.Message)" -ForegroundColor Red
                        }
                    }
                }
            } else {
                Write-Host "No se encontro el campo de nombre de archivo" -ForegroundColor Yellow
            }

            break
        }
    }

} catch {
    Write-Host "ERROR al hacer clic: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== PROCESO COMPLETADO ===" -ForegroundColor Cyan
