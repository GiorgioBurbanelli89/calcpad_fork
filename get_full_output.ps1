# Script para obtener TODO el output de Calcpad

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$calcpadProcess = Get-Process | Where-Object { $_.ProcessName -eq "Calcpad" } | Select-Object -First 1

if ($calcpadProcess) {
    $automation = [System.Windows.Automation.AutomationElement]::RootElement
    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
        $calcpadProcess.Id
    )
    $calcpadWindow = $automation.FindFirst([System.Windows.Automation.TreeScope]::Children, $condition)

    if ($calcpadWindow) {
        # Buscar elementos Document
        $docCondition = New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
            [System.Windows.Automation.ControlType]::Document
        )

        $docElements = $calcpadWindow.FindAll([System.Windows.Automation.TreeScope]::Descendants, $docCondition)

        Write-Host "Documentos encontrados: $($docElements.Count)" -ForegroundColor Yellow
        Write-Host ""

        $docNum = 0
        foreach ($doc in $docElements) {
            $docNum++
            try {
                $textPattern = $doc.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
                if ($textPattern) {
                    $documentRange = $textPattern.DocumentRange
                    $text = $documentRange.GetText(-1)

                    Write-Host "========================================"  -ForegroundColor Cyan
                    Write-Host "DOCUMENTO #$docNum - Longitud: $($text.Length) caracteres" -ForegroundColor Green
                    Write-Host "========================================"  -ForegroundColor Cyan

                    # Si el texto es corto, mostrarlo completo
                    if ($text.Length -lt 5000) {
                        Write-Host $text
                    } else {
                        # Mostrar inicio y final
                        Write-Host "=== INICIO (2000 chars) ===" -ForegroundColor Yellow
                        Write-Host $text.Substring(0, 2000)
                        Write-Host "`n=== FINAL (3000 chars) ===" -ForegroundColor Yellow
                        Write-Host $text.Substring($text.Length - 3000)
                    }

                    # Buscar específicamente errores
                    if ($text -match "Error|Traceback|UnicodeEncodeError") {
                        Write-Host "`n`n!!! ERRORES DETECTADOS !!!" -ForegroundColor Red -BackgroundColor Yellow
                        $lines = $text -split "`r?`n"
                        $errorContext = @()
                        for ($i = 0; $i -lt $lines.Count; $i++) {
                            if ($lines[$i] -match "Error|Traceback") {
                                # Capturar 3 líneas antes y 5 después del error
                                $start = [Math]::Max(0, $i - 3)
                                $end = [Math]::Min($lines.Count - 1, $i + 5)
                                for ($j = $start; $j -le $end; $j++) {
                                    $errorContext += $lines[$j]
                                }
                            }
                        }
                        $errorContext | ForEach-Object { Write-Host $_ -ForegroundColor Red }
                    }

                    Write-Host "`n"
                }
            } catch {
                Write-Host "Error al obtener texto del documento #$docNum : $_" -ForegroundColor Red
            }
        }
    }
}
