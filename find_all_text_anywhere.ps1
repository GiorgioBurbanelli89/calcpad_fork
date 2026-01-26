# Buscar TODO el texto en CUALQUIER control de Calcpad

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
        Write-Host "Ventana: $($calcpadWindow.Current.Name)`n" -ForegroundColor Cyan

        # Buscar TODOS los elementos
        $allElements = $calcpadWindow.FindAll([System.Windows.Automation.TreeScope]::Descendants,
            [System.Windows.Automation.Condition]::TrueCondition)

        Write-Host "Total elementos encontrados: $($allElements.Count)`n" -ForegroundColor Yellow

        $textsFound = @()

        foreach ($element in $allElements) {
            try {
                $controlType = $element.Current.ControlType.ProgrammaticName
                $name = $element.Current.Name
                $automationId = $element.Current.AutomationId
                $className = $element.Current.ClassName

                # Obtener cualquier texto del elemento
                $text = ""

                # Intentar Name
                if ($name -and $name.Length -gt 20) {
                    $text = $name
                }

                # Intentar TextPattern
                if (-not $text) {
                    try {
                        $textPattern = $element.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
                        if ($textPattern) {
                            $text = $textPattern.DocumentRange.GetText(-1)
                        }
                    } catch {}
                }

                # Intentar ValuePattern
                if (-not $text) {
                    try {
                        $valuePattern = $element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                        if ($valuePattern) {
                            $text = $valuePattern.Current.Value
                        }
                    } catch {}
                }

                # Si tiene texto significativo, guardarlo
                if ($text -and $text.Length -gt 30) {
                    # Buscar indicadores de errores
                    $hasError = $text -match "Error|Traceback|UnicodeEncodeError|Exception|Failed|charmap"

                    if ($hasError -or $text.Length -gt 100) {
                        $textsFound += @{
                            ControlType = $controlType
                            Name = if ($name.Length -gt 50) { $name.Substring(0, 50) + "..." } else { $name }
                            AutomationId = $automationId
                            ClassName = $className
                            Length = $text.Length
                            Text = $text
                            HasError = $hasError
                        }
                    }
                }

            } catch {}
        }

        Write-Host "Textos significativos encontrados: $($textsFound.Count)`n" -ForegroundColor Green

        # Primero mostrar los que tienen errores
        $withErrors = $textsFound | Where-Object { $_.HasError }
        $withoutErrors = $textsFound | Where-Object { -not $_.HasError }

        if ($withErrors.Count -gt 0) {
            Write-Host "========================================" -ForegroundColor Red -BackgroundColor Yellow
            Write-Host "  TEXTOS CON ERRORES: $($withErrors.Count)" -ForegroundColor Red -BackgroundColor Yellow
            Write-Host "========================================" -ForegroundColor Red -BackgroundColor Yellow
            Write-Host ""

            $num = 0
            foreach ($item in $withErrors) {
                $num++
                Write-Host "========================================" -ForegroundColor Red
                Write-Host "ERROR #$num" -ForegroundColor Red
                Write-Host "========================================" -ForegroundColor Red
                Write-Host "ControlType: $($item.ControlType)" -ForegroundColor Yellow
                Write-Host "Name: $($item.Name)" -ForegroundColor Yellow
                Write-Host "AutomationId: $($item.AutomationId)" -ForegroundColor Yellow
                Write-Host "ClassName: $($item.ClassName)" -ForegroundColor Yellow
                Write-Host "Length: $($item.Length) chars" -ForegroundColor Yellow
                Write-Host ""

                $text = $item.Text
                Write-Host "TEXTO COMPLETO:" -ForegroundColor Cyan
                Write-Host $text -ForegroundColor White
                Write-Host "`n"
            }
        }

        # Luego mostrar algunos sin errores (solo los primeros 5)
        if ($withoutErrors.Count -gt 0) {
            Write-Host "========================================" -ForegroundColor Cyan
            Write-Host "  OTROS TEXTOS (sin errores): $($withoutErrors.Count)" -ForegroundColor Cyan
            Write-Host "  Mostrando primeros 5..." -ForegroundColor Cyan
            Write-Host "========================================" -ForegroundColor Cyan
            Write-Host ""

            $num = 0
            foreach ($item in $withoutErrors) {
                $num++
                if ($num -le 5) {
                    Write-Host "Texto #$num - $($item.ControlType) - $($item.Length) chars" -ForegroundColor Gray
                    Write-Host "Name: $($item.Name)" -ForegroundColor Gray

                    if ($item.Length -lt 500) {
                        Write-Host $item.Text -ForegroundColor DarkGray
                    } else {
                        Write-Host $item.Text.Substring(0, 300) -ForegroundColor DarkGray
                        Write-Host "... [texto truncado] ..." -ForegroundColor DarkGray
                    }
                    Write-Host ""
                }
            }
        }

        # Resumen
        Write-Host "========================================" -ForegroundColor Magenta
        Write-Host "RESUMEN:" -ForegroundColor Magenta
        Write-Host "========================================" -ForegroundColor Magenta
        Write-Host "Total elementos UI: $($allElements.Count)" -ForegroundColor Yellow
        Write-Host "Textos significativos: $($textsFound.Count)" -ForegroundColor Yellow
        Write-Host "Textos con ERRORES: $($withErrors.Count)" -ForegroundColor $(if ($withErrors.Count -gt 0) { "Red" } else { "Green" })
        Write-Host "Textos sin errores: $($withoutErrors.Count)" -ForegroundColor Yellow

        if ($withErrors.Count -eq 0) {
            Write-Host "`n[OK] NO SE ENCONTRARON ERRORES EN NINGÚN CONTROL" -ForegroundColor Green
            Write-Host "El archivo parece estar ejecutándose correctamente o no ha sido ejecutado aún." -ForegroundColor Cyan
        }

    }
    else {
        Write-Host "No se encontró ventana de Calcpad" -ForegroundColor Red
    }
}
else {
    Write-Host "Calcpad no está ejecutándose" -ForegroundColor Red
}
