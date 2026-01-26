# Script para encontrar el OUTPUT de ejecucion (no el codigo fuente)

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$calcpadProcess = Get-Process | Where-Object { $_.ProcessName -eq "Calcpad" } | Select-Object -First 1

if ($calcpadProcess) {
    Write-Host "Calcpad PID: $($calcpadProcess.Id)" -ForegroundColor Green

    $automation = [System.Windows.Automation.AutomationElement]::RootElement
    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
        $calcpadProcess.Id
    )
    $calcpadWindow = $automation.FindFirst([System.Windows.Automation.TreeScope]::Children, $condition)

    if ($calcpadWindow) {
        Write-Host "`nBuscando TODOS los controles con texto...`n" -ForegroundColor Cyan

        # Buscar TODOS los elementos que puedan tener texto
        $allElements = $calcpadWindow.FindAll([System.Windows.Automation.TreeScope]::Descendants,
            [System.Windows.Automation.Condition]::TrueCondition)

        $foundOutputs = @()
        $elementNum = 0

        foreach ($element in $allElements) {
            $elementNum++
            try {
                $controlType = $element.Current.ControlType.ProgrammaticName
                $name = $element.Current.Name
                $automationId = $element.Current.AutomationId

                # Intentar obtener texto con TextPattern
                try {
                    $textPattern = $element.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
                    if ($textPattern) {
                        $text = $textPattern.DocumentRange.GetText(-1)

                        if ($text -and $text.Length -gt 50) {
                            # Buscar indicadores de que es OUTPUT de ejecucion
                            $isOutput = $false
                            $reason = ""

                            if ($text -match "Error|Traceback|UnicodeEncodeError") {
                                $isOutput = $true
                                $reason = "CONTIENE ERRORES"
                            }
                            elseif ($text -match "Executing|Compilando|JavaScript compiled") {
                                $isOutput = $true
                                $reason = "MENSAJES DE EJECUCION"
                            }
                            elseif ($text -match "^\[OK\]|\[X\]") {
                                $isOutput = $true
                                $reason = "OUTPUT DE PYTHON"
                            }
                            elseif ($text -notmatch "@\{ts\}|@\{html\}|@\{python\}|@\{end") {
                                # No tiene tags de codigo = posible output
                                if ($text.Length -lt 2000) {
                                    $isOutput = $true
                                    $reason = "SIN TAGS DE CODIGO"
                                }
                            }

                            if ($isOutput) {
                                $foundOutputs += @{
                                    Num = $foundOutputs.Count + 1
                                    ControlType = $controlType
                                    Name = $name
                                    AutomationId = $automationId
                                    Length = $text.Length
                                    Text = $text
                                    Reason = $reason
                                }
                            }
                        }
                    }
                } catch {}

                # Intentar obtener texto con ValuePattern (para Edit controls)
                try {
                    $valuePattern = $element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                    if ($valuePattern) {
                        $text = $valuePattern.Current.Value

                        if ($text -and $text.Length -gt 50) {
                            $isOutput = $false
                            $reason = ""

                            if ($text -match "Error|Traceback|UnicodeEncodeError") {
                                $isOutput = $true
                                $reason = "CONTIENE ERRORES (ValuePattern)"
                            }
                            elseif ($text -match "Executing|Compilando") {
                                $isOutput = $true
                                $reason = "MENSAJES EJECUCION (ValuePattern)"
                            }

                            if ($isOutput) {
                                $foundOutputs += @{
                                    Num = $foundOutputs.Count + 1
                                    ControlType = $controlType
                                    Name = $name
                                    AutomationId = $automationId
                                    Length = $text.Length
                                    Text = $text
                                    Reason = $reason
                                }
                            }
                        }
                    }
                } catch {}

            } catch {}
        }

        Write-Host "Elementos analizados: $elementNum" -ForegroundColor Yellow
        Write-Host "Posibles OUTPUT encontrados: $($foundOutputs.Count)`n" -ForegroundColor Green

        if ($foundOutputs.Count -eq 0) {
            Write-Host "NO SE ENCONTRO OUTPUT DE EJECUCION" -ForegroundColor Red
            Write-Host "Posibles razones:" -ForegroundColor Yellow
            Write-Host "  1. El archivo no ha sido ejecutado (presionar F5)" -ForegroundColor White
            Write-Host "  2. El output esta en un panel no accesible por UI Automation" -ForegroundColor White
            Write-Host "  3. El output esta vacio o muy corto" -ForegroundColor White
        }
        else {
            foreach ($output in $foundOutputs) {
                Write-Host "========================================" -ForegroundColor Magenta
                Write-Host "OUTPUT #$($output.Num) - $($output.Reason)" -ForegroundColor Cyan
                Write-Host "========================================" -ForegroundColor Magenta
                Write-Host "ControlType: $($output.ControlType)" -ForegroundColor Yellow
                Write-Host "Name: $($output.Name)" -ForegroundColor Yellow
                Write-Host "AutomationId: $($output.AutomationId)" -ForegroundColor Yellow
                Write-Host "Longitud: $($output.Length) caracteres" -ForegroundColor Yellow
                Write-Host ""

                $text = $output.Text

                # Mostrar texto completo si es corto, sino primeros y ultimos chars
                if ($text.Length -lt 3000) {
                    Write-Host $text -ForegroundColor White
                }
                else {
                    Write-Host "=== INICIO (1500 chars) ===" -ForegroundColor Green
                    Write-Host $text.Substring(0, 1500) -ForegroundColor White
                    Write-Host "`n=== ... OMITIDO $($text.Length - 3000) chars ... ===`n" -ForegroundColor Yellow
                    Write-Host "=== FINAL (1500 chars) ===" -ForegroundColor Green
                    Write-Host $text.Substring($text.Length - 1500) -ForegroundColor White
                }

                # Buscar y resaltar errores
                if ($text -match "Error|Traceback|UnicodeEncodeError") {
                    Write-Host "`n`n!!! ERRORES DETECTADOS !!!" -ForegroundColor Red -BackgroundColor Yellow
                    $lines = $text -split "`r?`n"
                    $errorContext = @()
                    for ($i = 0; $i -lt $lines.Count; $i++) {
                        if ($lines[$i] -match "Error|Traceback") {
                            $start = [Math]::Max(0, $i - 3)
                            $end = [Math]::Min($lines.Count - 1, $i + 10)
                            Write-Host "`nContexto del error (lineas $start-$end):" -ForegroundColor Yellow
                            for ($j = $start; $j -le $end; $j++) {
                                if ($j -eq $i) {
                                    Write-Host ">>> $($lines[$j])" -ForegroundColor Red -BackgroundColor White
                                }
                                else {
                                    Write-Host "    $($lines[$j])" -ForegroundColor Red
                                }
                            }
                        }
                    }
                }

                Write-Host "`n"
            }
        }

    }
    else {
        Write-Host "No se encontro ventana de Calcpad" -ForegroundColor Red
    }
}
else {
    Write-Host "Calcpad no esta ejecutandose" -ForegroundColor Red
}
