# Script simple para verificar estado de MathEditor
$calcpad = Get-Process -Name "Calcpad" -ErrorAction SilentlyContinue

if ($calcpad) {
    Write-Host "Calcpad esta ejecutandose (PID: $($calcpad.Id))"

    # Usar Get-UIAWindow de UIAutomation module si está disponible
    try {
        Add-Type -AssemblyName UIAutomationClient
        Add-Type -AssemblyName UIAutomationTypes

        $root = [System.Windows.Automation.AutomationElement]::RootElement
        $processCondition = New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
            $calcpad.Id
        )

        $window = $root.FindFirst(
            [System.Windows.Automation.TreeScope]::Children,
            $processCondition
        )

        if ($window) {
            Write-Host "Ventana encontrada: $($window.Current.Name)"
            Write-Host "Buscando controles..."

            # Buscar todos los panes
            $allElements = $window.FindAll(
                [System.Windows.Automation.TreeScope]::Descendants,
                [System.Windows.Automation.Condition]::TrueCondition
            )

            Write-Host "Total elementos encontrados: $($allElements.Count)"

            $mathEditorCount = 0
            $avalonEditCount = 0
            $visibleElements = 0

            foreach ($elem in $allElements) {
                $className = $elem.Current.ClassName
                $name = $elem.Current.Name
                $isVisible = -not $elem.Current.IsOffscreen

                if ($isVisible) {
                    $visibleElements++
                }

                if ($className -match "Math" -or $name -match "Math") {
                    $mathEditorCount++
                    Write-Host "  [MathEditor] $className - $name - Visible: $isVisible"
                }

                if ($className -eq "TextEditor" -or $className -match "Avalon") {
                    $avalonEditCount++
                    $bounds = $elem.Current.BoundingRectangle
                    Write-Host "  [AvalonEdit] $className - Visible: $isVisible - Size: $($bounds.Width)x$($bounds.Height)"
                }
            }

            Write-Host ""
            Write-Host "Resumen:"
            Write-Host "  Elementos totales: $($allElements.Count)"
            Write-Host "  Elementos visibles: $visibleElements"
            Write-Host "  MathEditor elements: $mathEditorCount"
            Write-Host "  AvalonEdit elements: $avalonEditCount"
        } else {
            Write-Host "No se pudo encontrar la ventana"
        }
    } catch {
        Write-Host "Error: $_"
    }
} else {
    Write-Host "Calcpad no esta ejecutandose"
}
