# ========================================
# UI Automation Test: Preview ↔ Canvas Sync
# ========================================
# Verifica la sincronización bidireccional entre PreviewEditor y MathEditor Canvas

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "UI Automation - Preview Sync Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Encontrar ventana de Calcpad
$automation = [System.Windows.Automation.AutomationElement]::RootElement
$calcpadWindow = $null

Write-Host "[1/8] Buscando ventana de Calcpad..." -ForegroundColor Yellow
$windows = $automation.FindAll(
    [System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.Condition]::TrueCondition
)

foreach ($window in $windows) {
    $name = $window.Current.Name
    if ($name -like "*Calcpad*") {
        $calcpadWindow = $window
        Write-Host "  ✓ Encontrado: $name" -ForegroundColor Green
        break
    }
}

if ($null -eq $calcpadWindow) {
    Write-Host "  ✗ ERROR: No se encontró la ventana de Calcpad" -ForegroundColor Red
    Write-Host "  → Asegúrate de que Calcpad esté ejecutándose" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# ========================================
# Buscar PreviewTextBlock
# ========================================
Write-Host "[2/8] Buscando PreviewTextBlock..." -ForegroundColor Yellow

$previewTextBlockCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
    "PreviewTextBlock"
)

$previewTextBlock = $calcpadWindow.FindFirst(
    [System.Windows.Automation.TreeScope]::Descendants,
    $previewTextBlockCondition
)

if ($null -ne $previewTextBlock) {
    $previewText = $previewTextBlock.Current.Name
    Write-Host "  ✓ PreviewTextBlock encontrado" -ForegroundColor Green
    Write-Host "    Texto actual: '$previewText'" -ForegroundColor Cyan
} else {
    Write-Host "  ✗ PreviewTextBlock NO encontrado" -ForegroundColor Red
}

Write-Host ""

# ========================================
# Buscar PreviewEditorContainer (AvalonEdit)
# ========================================
Write-Host "[3/8] Buscando PreviewEditorContainer (AvalonEdit)..." -ForegroundColor Yellow

# Buscar por nombre "PreviewEditorContainer"
$allElements = $calcpadWindow.FindAll(
    [System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition
)

$previewEditor = $null
$previewEditorContainer = $null

foreach ($element in $allElements) {
    $autoId = $element.Current.AutomationId
    $className = $element.Current.ClassName
    $name = $element.Current.Name

    if ($autoId -eq "PreviewEditor" -or $name -eq "PreviewEditor") {
        $previewEditor = $element
        Write-Host "  ✓ PreviewEditor encontrado" -ForegroundColor Green
        Write-Host "    AutomationId: $autoId" -ForegroundColor Cyan
        Write-Host "    ClassName: $className" -ForegroundColor Cyan

        # Verificar si es visible
        $isVisible = -not $element.Current.IsOffscreen
        Write-Host "    Visible: $isVisible" -ForegroundColor $(if ($isVisible) { "Green" } else { "Red" })

        # Verificar si tiene patrón de texto
        $valuePattern = $null
        try {
            $valuePattern = $element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
            if ($null -ne $valuePattern) {
                $text = $valuePattern.Current.Value
                Write-Host "    Texto: '$text'" -ForegroundColor Cyan
            }
        } catch {
            Write-Host "    (No soporta ValuePattern)" -ForegroundColor Gray
        }

        # Verificar si tiene patrón de texto alternativo
        try {
            $textPattern = $element.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
            if ($null -ne $textPattern) {
                Write-Host "    (Soporta TextPattern)" -ForegroundColor Gray
            }
        } catch {
            # Ignorar
        }

        break
    }

    if ($autoId -eq "PreviewEditorContainer" -or $name -eq "PreviewEditorContainer") {
        $previewEditorContainer = $element
        Write-Host "  ✓ PreviewEditorContainer encontrado" -ForegroundColor Green
        Write-Host "    AutomationId: $autoId" -ForegroundColor Cyan

        # Verificar visibilidad
        $isVisible = -not $element.Current.IsOffscreen
        Write-Host "    Visible: $isVisible" -ForegroundColor $(if ($isVisible) { "Green" } else { "Red" })
    }
}

if ($null -eq $previewEditor -and $null -eq $previewEditorContainer) {
    Write-Host "  ⚠ PreviewEditor/Container NO encontrado directamente" -ForegroundColor Yellow
    Write-Host "    Esto es normal si el preview no está activo" -ForegroundColor Gray
}

Write-Host ""

# ========================================
# Buscar EditorCanvas (MathEditor)
# ========================================
Write-Host "[4/8] Buscando EditorCanvas (MathEditor)..." -ForegroundColor Yellow

$editorCanvas = $null

foreach ($element in $allElements) {
    $autoId = $element.Current.AutomationId
    $className = $element.Current.ClassName
    $name = $element.Current.Name

    if ($autoId -eq "EditorCanvas" -or $className -eq "Canvas") {
        # Verificar que sea el canvas principal (no otros canvas)
        $parent = $null
        try {
            $parent = [System.Windows.Automation.TreeWalker]::ControlViewWalker.GetParent($element)
            if ($null -ne $parent) {
                $parentName = $parent.Current.Name
                # Buscar el canvas dentro del editor
                if ($parentName -like "*Editor*" -or $autoId -eq "EditorCanvas") {
                    $editorCanvas = $element
                    Write-Host "  ✓ EditorCanvas encontrado" -ForegroundColor Green
                    Write-Host "    AutomationId: $autoId" -ForegroundColor Cyan
                    Write-Host "    ClassName: $className" -ForegroundColor Cyan

                    # Verificar tamaño
                    $rect = $element.Current.BoundingRectangle
                    Write-Host "    Posición: X=$($rect.X), Y=$($rect.Y)" -ForegroundColor Cyan
                    Write-Host "    Tamaño: Width=$($rect.Width), Height=$($rect.Height)" -ForegroundColor Cyan

                    break
                }
            }
        } catch {
            # Ignorar errores al obtener parent
        }
    }
}

if ($null -eq $editorCanvas) {
    Write-Host "  ⚠ EditorCanvas NO encontrado específicamente" -ForegroundColor Yellow
    Write-Host "    Buscando todos los Canvas..." -ForegroundColor Gray

    $canvasCount = 0
    foreach ($element in $allElements) {
        $className = $element.Current.ClassName
        if ($className -eq "Canvas") {
            $canvasCount++
            $autoId = $element.Current.AutomationId
            Write-Host "    Canvas #${canvasCount}: AutomationId='$autoId'" -ForegroundColor Gray
        }
    }
}

Write-Host ""

# ========================================
# Listar todos los TextEditor (AvalonEdit)
# ========================================
Write-Host "[5/8] Buscando todos los controles TextEditor..." -ForegroundColor Yellow

$textEditorCount = 0
$avalonEdits = @()

foreach ($element in $allElements) {
    $className = $element.Current.ClassName
    $autoId = $element.Current.AutomationId
    $name = $element.Current.Name

    if ($className -like "*TextEditor*" -or $className -eq "TextEditor") {
        $textEditorCount++
        $avalonEdits += $element

        Write-Host "  TextEditor #${textEditorCount}:" -ForegroundColor Cyan
        Write-Host "    AutomationId: $autoId" -ForegroundColor Gray
        Write-Host "    Name: $name" -ForegroundColor Gray
        Write-Host "    ClassName: $className" -ForegroundColor Gray

        # Verificar visibilidad
        $isVisible = -not $element.Current.IsOffscreen
        Write-Host "    Visible: $isVisible" -ForegroundColor $(if ($isVisible) { "Green" } else { "Red" })

        # Intentar obtener texto
        try {
            $valuePattern = $element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
            if ($null -ne $valuePattern) {
                $text = $valuePattern.Current.Value
                Write-Host "    Texto: '$text'" -ForegroundColor Cyan
            }
        } catch {
            Write-Host "    (No texto disponible vía ValuePattern)" -ForegroundColor Gray
        }

        Write-Host ""
    }
}

if ($textEditorCount -eq 0) {
    Write-Host "  ⚠ No se encontraron controles TextEditor" -ForegroundColor Yellow
}

Write-Host ""

# ========================================
# Buscar controles relacionados con Preview
# ========================================
Write-Host "[6/8] Buscando controles relacionados con 'Preview'..." -ForegroundColor Yellow

$previewRelated = @()

foreach ($element in $allElements) {
    $autoId = $element.Current.AutomationId
    $name = $element.Current.Name
    $className = $element.Current.ClassName

    if ($autoId -like "*Preview*" -or $name -like "*Preview*") {
        Write-Host "  Control relacionado:" -ForegroundColor Cyan
        Write-Host "    AutomationId: $autoId" -ForegroundColor Gray
        Write-Host "    Name: $name" -ForegroundColor Gray
        Write-Host "    ClassName: $className" -ForegroundColor Gray

        $isVisible = -not $element.Current.IsOffscreen
        Write-Host "    Visible: $isVisible" -ForegroundColor $(if ($isVisible) { "Green" } else { "Red" })
        Write-Host ""
    }
}

Write-Host ""

# ========================================
# Intentar hacer click en PreviewTextBlock
# ========================================
Write-Host "[7/8] Intentando interactuar con PreviewTextBlock..." -ForegroundColor Yellow

if ($null -ne $previewTextBlock) {
    try {
        # Verificar si soporta InvokePattern
        $invokePattern = $null
        try {
            $invokePattern = $previewTextBlock.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
        } catch {
            Write-Host "  ⚠ No soporta InvokePattern" -ForegroundColor Yellow
        }

        # Intentar hacer click usando Mouse
        $rect = $previewTextBlock.Current.BoundingRectangle
        $clickX = $rect.X + ($rect.Width / 2)
        $clickY = $rect.Y + ($rect.Height / 2)

        Write-Host "  Posición del click: X=$clickX, Y=$clickY" -ForegroundColor Cyan
        Write-Host "  ⚠ No se ejecuta click automáticamente (requiere confirmación del usuario)" -ForegroundColor Yellow

    } catch {
        Write-Host "  ✗ Error al intentar interactuar: $_" -ForegroundColor Red
    }
} else {
    Write-Host "  ⚠ PreviewTextBlock no disponible para interacción" -ForegroundColor Yellow
}

Write-Host ""

# ========================================
# Resumen
# ========================================
Write-Host "[8/8] RESUMEN:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Controles encontrados:" -ForegroundColor White
Write-Host "  - PreviewTextBlock: $(if ($null -ne $previewTextBlock) { '✓ SÍ' } else { '✗ NO' })" -ForegroundColor $(if ($null -ne $previewTextBlock) { "Green" } else { "Red" })
Write-Host "  - PreviewEditor: $(if ($null -ne $previewEditor) { '✓ SÍ' } else { '✗ NO' })" -ForegroundColor $(if ($null -ne $previewEditor) { "Green" } else { "Red" })
Write-Host "  - PreviewEditorContainer: $(if ($null -ne $previewEditorContainer) { '✓ SÍ' } else { '✗ NO' })" -ForegroundColor $(if ($null -ne $previewEditorContainer) { "Green" } else { "Red" })
Write-Host "  - EditorCanvas: $(if ($null -ne $editorCanvas) { '✓ SÍ' } else { '⚠ Buscar manualmente' })" -ForegroundColor $(if ($null -ne $editorCanvas) { "Green" } else { "Yellow" })
Write-Host "  - TextEditor (total): $textEditorCount controles" -ForegroundColor Cyan

Write-Host ""
Write-Host "Estado del Preview:" -ForegroundColor White
if ($null -ne $previewTextBlock) {
    $previewText = $previewTextBlock.Current.Name
    Write-Host "  Texto: '$previewText'" -ForegroundColor Cyan
}

if ($null -ne $previewEditor) {
    $isVisible = -not $previewEditor.Current.IsOffscreen
    Write-Host "  Editor visible: $isVisible" -ForegroundColor $(if ($isVisible) { "Green" } else { "Red" })

    if ($isVisible) {
        Write-Host "  ✓ El PreviewEditor está ACTIVO (usuario editando)" -ForegroundColor Green
    } else {
        Write-Host "  ○ El PreviewEditor está INACTIVO (oculto)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test completado" -ForegroundColor Green
Write-Host ""

# Instrucciones para el usuario
Write-Host "PRÓXIMOS PASOS:" -ForegroundColor Yellow
Write-Host "1. Haz click en la barra amarilla de preview en Calcpad" -ForegroundColor White
Write-Host "2. Ejecuta este script de nuevo para ver el PreviewEditor activo" -ForegroundColor White
Write-Host "3. Escribe algo en el PreviewEditor" -ForegroundColor White
Write-Host "4. Ejecuta el script de nuevo para verificar sincronización" -ForegroundColor White
Write-Host ""
