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

if ($mainWindow) {
    Write-Host "[OK] Ventana encontrada:" -ForegroundColor Green
    Write-Host "   Name: '$($mainWindow.Current.Name)'" -ForegroundColor White
    Write-Host "   AutomationId: '$($mainWindow.Current.AutomationId)'" -ForegroundColor Gray
    Write-Host ""

    # Buscar todos los GroupBox (los paneles Code y Output son GroupBox)
    $groupBoxCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Group
    )

    $groupBoxes = $mainWindow.FindAll(
        [System.Windows.Automation.TreeScope]::Descendants,
        $groupBoxCondition
    )

    Write-Host "=== GROUPBOX ENCONTRADOS ($($groupBoxes.Count)) ===" -ForegroundColor Yellow
    $codeFound = $false
    $outputFound = $false

    foreach ($gb in $groupBoxes) {
        $name = $gb.Current.Name
        $automationId = $gb.Current.AutomationId
        $helpText = $gb.Current.HelpText

        # Solo mostrar los que tienen nombre
        if ($name) {
            Write-Host "`n  [GroupBox] '$name'" -ForegroundColor White

            if ($automationId) {
                Write-Host "     AutomationId: '$automationId'" -ForegroundColor Green
            } else {
                Write-Host "     AutomationId: [VACIO]" -ForegroundColor Red
            }

            if ($helpText) {
                Write-Host "     HelpText: '$helpText'" -ForegroundColor Gray
            }

            # Marcar si encontramos Code o Output
            if ($name -like "*Code*" -or $name -eq "Code") {
                $codeFound = $true
            }
            if ($name -like "*Output*" -or $name -eq "Output") {
                $outputFound = $true
            }
        }
    }

    Write-Host "`n`n=== BUSQUEDA POR AUTOMATIONID ===" -ForegroundColor Yellow

    # Buscar InputFrame especificamente
    $inputFrameCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
        "InputFrame"
    )
    $inputFrame = $mainWindow.FindFirst(
        [System.Windows.Automation.TreeScope]::Descendants,
        $inputFrameCondition
    )

    if ($inputFrame) {
        Write-Host "[OK] InputFrame encontrado con AutomationId='InputFrame'" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] InputFrame NO encontrado con AutomationId='InputFrame'" -ForegroundColor Red
    }

    # Buscar OutputFrame especificamente
    $outputFrameCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
        "OutputFrame"
    )
    $outputFrame = $mainWindow.FindFirst(
        [System.Windows.Automation.TreeScope]::Descendants,
        $outputFrameCondition
    )

    if ($outputFrame) {
        Write-Host "[OK] OutputFrame encontrado con AutomationId='OutputFrame'" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] OutputFrame NO encontrado con AutomationId='OutputFrame'" -ForegroundColor Red
    }

    # Buscar RichTextBox
    Write-Host "`n=== CONTROLES PRINCIPALES ===" -ForegroundColor Yellow

    $richTextBoxCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
        "RichTextBox"
    )
    $richTextBox = $mainWindow.FindFirst(
        [System.Windows.Automation.TreeScope]::Descendants,
        $richTextBoxCondition
    )

    if ($richTextBox) {
        Write-Host "[OK] RichTextBox encontrado (editor de codigo)" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] RichTextBox NO encontrado con AutomationId" -ForegroundColor Red
    }

    # Buscar WebView2
    $webViewCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
        "WebViewer"
    )
    $webView = $mainWindow.FindFirst(
        [System.Windows.Automation.TreeScope]::Descendants,
        $webViewCondition
    )

    if ($webView) {
        Write-Host "[OK] WebViewer encontrado (panel de output)" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] WebViewer NO encontrado con AutomationId" -ForegroundColor Red
    }

    # Resumen final
    Write-Host "`n`n=== RESUMEN ===" -ForegroundColor Cyan

    if ($codeFound -and $outputFound) {
        Write-Host "[OK] Paneles Code y Output encontrados por Name" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Algunos paneles no encontrados por Name" -ForegroundColor Yellow
    }

    if ($inputFrame -and $outputFrame) {
        Write-Host "[OK] InputFrame y OutputFrame tienen AutomationId configurado" -ForegroundColor Green
        Write-Host "`n   UI Automation esta correctamente implementado!" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] InputFrame y/o OutputFrame NO tienen AutomationId" -ForegroundColor Red
        Write-Host "`n   Se recomienda agregar AutomationProperties al XAML" -ForegroundColor Yellow
        Write-Host "   Ver: ANALISIS_UI_CODE_OUTPUT.md - Solucion 1" -ForegroundColor Gray
    }

} else {
    Write-Host "[FAIL] Ventana de Calcpad no encontrada" -ForegroundColor Red
    Write-Host "`nAsegurate de que Calcpad WPF este abierto" -ForegroundColor Yellow
    Write-Host "Ejecutable: C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\bin\Debug\net10.0-windows\Calcpad.exe`n" -ForegroundColor Gray
}

Write-Host "`n=== FIN DEL TEST ===`n" -ForegroundColor Cyan
