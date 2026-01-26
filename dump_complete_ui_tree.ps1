# Volcar TODA la jerarquia UI con TODOS los textos

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

function Get-AllText($element, $depth = 0) {
    $indent = "  " * $depth
    $texts = @()

    try {
        $controlType = $element.Current.ControlType.ProgrammaticName
        $name = $element.Current.Name
        $automationId = $element.Current.AutomationId
        $className = $element.Current.ClassName

        # Obtener texto
        $text = ""

        # Name
        if ($name) {
            $text = $name
        }

        # TextPattern
        try {
            $textPattern = $element.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
            if ($textPattern) {
                $docText = $textPattern.DocumentRange.GetText(-1)
                if ($docText -and $docText.Length -gt $text.Length) {
                    $text = $docText
                }
            }
        } catch {}

        # ValuePattern
        try {
            $valuePattern = $element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
            if ($valuePattern) {
                $valText = $valuePattern.Current.Value
                if ($valText -and $valText.Length -gt $text.Length) {
                    $text = $valText
                }
            }
        } catch {}

        # Si tiene texto con error keywords, guardarlo
        if ($text -and $text -match "Error|Traceback|UnicodeEncodeError|Exception|Failed") {
            $texts += @{
                Depth = $depth
                ControlType = $controlType
                Name = $name
                AutomationId = $automationId
                ClassName = $className
                Text = $text
            }
        }

        # Recorrer hijos
        try {
            $children = $element.FindAll([System.Windows.Automation.TreeScope]::Children,
                [System.Windows.Automation.Condition]::TrueCondition)

            foreach ($child in $children) {
                $childTexts = Get-AllText $child ($depth + 1)
                if ($childTexts) {
                    $texts += $childTexts
                }
            }
        } catch {}

    } catch {}

    return $texts
}

$calcpadProcess = Get-Process | Where-Object { $_.ProcessName -eq "Calcpad" } | Select-Object -First 1

if ($calcpadProcess) {
    Write-Host "Buscando errores en TODO el arbol UI de Calcpad..." -ForegroundColor Cyan
    Write-Host "PID: $($calcpadProcess.Id)`n" -ForegroundColor Yellow

    $automation = [System.Windows.Automation.AutomationElement]::RootElement
    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
        $calcpadProcess.Id
    )
    $calcpadWindow = $automation.FindFirst([System.Windows.Automation.TreeScope]::Children, $condition)

    if ($calcpadWindow) {
        Write-Host "Ventana encontrada: $($calcpadWindow.Current.Name)`n" -ForegroundColor Green

        $errorsFound = Get-AllText $calcpadWindow 0

        if ($errorsFound -and $errorsFound.Count -gt 0) {
            Write-Host "========================================" -ForegroundColor Red -BackgroundColor Yellow
            Write-Host "  ERRORES ENCONTRADOS: $($errorsFound.Count)" -ForegroundColor Red -BackgroundColor Yellow
            Write-Host "========================================" -ForegroundColor Red -BackgroundColor Yellow
            Write-Host ""

            $num = 0
            foreach ($item in $errorsFound) {
                $num++
                Write-Host "========================================" -ForegroundColor Red
                Write-Host "ERROR #$num (Profundidad: $($item.Depth))" -ForegroundColor Red
                Write-Host "========================================" -ForegroundColor Red
                Write-Host "ControlType: $($item.ControlType)" -ForegroundColor Yellow
                Write-Host "Name: $($item.Name)" -ForegroundColor Yellow
                Write-Host "AutomationId: $($item.AutomationId)" -ForegroundColor Yellow
                Write-Host "ClassName: $($item.ClassName)" -ForegroundColor Yellow
                Write-Host ""
                Write-Host "TEXTO:" -ForegroundColor Cyan

                $text = $item.Text
                if ($text.Length -lt 2000) {
                    Write-Host $text -ForegroundColor White
                } else {
                    Write-Host $text.Substring(0, 1000) -ForegroundColor White
                    Write-Host "`n... [texto largo, mostrando primeros 1000 chars] ...`n" -ForegroundColor Yellow
                    Write-Host $text.Substring([Math]::Max(0, $text.Length - 1000)) -ForegroundColor White
                }

                # Extraer lineas con Error
                Write-Host "`nLINEAS CON ERROR:" -ForegroundColor Red -BackgroundColor Yellow
                $lines = $text -split "`r?`n"
                foreach ($line in $lines) {
                    if ($line -match "Error|Traceback|Exception|Failed") {
                        Write-Host "  $line" -ForegroundColor Red
                    }
                }

                Write-Host "`n"
            }
        }
        else {
            Write-Host "[!] NO SE ENCONTRARON TEXTOS CON PALABRAS CLAVE DE ERROR" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Esto puede significar:" -ForegroundColor Cyan
            Write-Host "  1. El archivo se ejecuto correctamente sin errores" -ForegroundColor White
            Write-Host "  2. El output esta en una ventana separada (navegador, consola)" -ForegroundColor White
            Write-Host "  3. El error esta en un control no accesible (WebView, Canvas)" -ForegroundColor White
            Write-Host ""
            Write-Host "Acciones sugeridas:" -ForegroundColor Cyan
            Write-Host "  - Toma screenshot de Calcpad y dimelo" -ForegroundColor White
            Write-Host "  - Copia manualmente el texto del error y pegalo" -ForegroundColor White
            Write-Host "  - Verifica si hay ventanas popup o consola abiertas" -ForegroundColor White
        }

    }
    else {
        Write-Host "No se pudo obtener ventana de Calcpad" -ForegroundColor Red
    }
}
else {
    Write-Host "Calcpad no esta ejecutandose" -ForegroundColor Red
}
