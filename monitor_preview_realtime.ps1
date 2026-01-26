# ========================================
# MONITOR EN TIEMPO REAL: Preview ↔ Canvas
# ========================================
# Monitorea la sincronización mientras el usuario ejecuta acciones

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$ErrorActionPreference = "Continue"

Clear-Host

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MONITOR EN TIEMPO REAL - Preview Sync" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host ""

# Variables para tracking de cambios
$lastPreviewText = ""
$lastEditorText = ""
$lastEditorVisible = $false
$iterationCount = 0

# Función para obtener timestamp
function Get-Timestamp {
    return (Get-Date).ToString("HH:mm:ss.fff")
}

# Función para encontrar Calcpad
function Find-CalcpadWindow {
    $automation = [System.Windows.Automation.AutomationElement]::RootElement
    $windows = $automation.FindAll(
        [System.Windows.Automation.TreeScope]::Children,
        [System.Windows.Automation.Condition]::TrueCondition
    )

    foreach ($window in $windows) {
        $name = $window.Current.Name
        if ($name -like "*Calcpad*") {
            return $window
        }
    }
    return $null
}

# Función para obtener todos los elementos
function Get-AllElements {
    param($window)

    if ($null -eq $window) { return @() }

    try {
        return $window.FindAll(
            [System.Windows.Automation.TreeScope]::Descendants,
            [System.Windows.Automation.Condition]::TrueCondition
        )
    } catch {
        return @()
    }
}

# Loop principal de monitoreo
Write-Host "[$(Get-Timestamp)] Iniciando monitoreo..." -ForegroundColor Green
Write-Host ""

try {
    while ($true) {
        $iterationCount++

        # Encontrar ventana de Calcpad
        $calcpadWindow = Find-CalcpadWindow

        if ($null -eq $calcpadWindow) {
            Write-Host "[$(Get-Timestamp)] ⚠ Esperando Calcpad..." -ForegroundColor Yellow
            Start-Sleep -Milliseconds 1000
            continue
        }

        # Obtener todos los elementos
        $allElements = Get-AllElements -window $calcpadWindow

        # ========================================
        # Buscar PreviewTextBlock
        # ========================================
        $previewTextBlock = $null
        $currentPreviewText = ""

        foreach ($element in $allElements) {
            $autoId = $element.Current.AutomationId
            if ($autoId -eq "PreviewTextBlock") {
                $previewTextBlock = $element
                $currentPreviewText = $element.Current.Name
                break
            }
        }

        # ========================================
        # Buscar PreviewEditor (AvalonEdit)
        # ========================================
        $previewEditor = $null
        $currentEditorText = ""
        $isEditorVisible = $false

        foreach ($element in $allElements) {
            $autoId = $element.Current.AutomationId
            $className = $element.Current.ClassName

            if ($autoId -eq "PreviewEditor" -or ($className -like "*TextEditor*" -and $autoId -like "*Preview*")) {
                $previewEditor = $element
                $isEditorVisible = -not $element.Current.IsOffscreen

                # Intentar obtener texto
                try {
                    $valuePattern = $element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
                    if ($null -ne $valuePattern) {
                        $currentEditorText = $valuePattern.Current.Value
                    }
                } catch {
                    # Intentar con TextPattern
                    try {
                        $textPattern = $element.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
                        if ($null -ne $textPattern) {
                            $range = $textPattern.DocumentRange
                            $currentEditorText = $range.GetText(-1)
                        }
                    } catch {
                        $currentEditorText = "(No disponible)"
                    }
                }
                break
            }
        }

        # ========================================
        # Detectar cambios y mostrar
        # ========================================
        $hasChanges = $false

        # Header de iteración (cada 10 iteraciones o si hay cambios)
        if ($iterationCount % 10 -eq 1) {
            Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
            Write-Host "Iteración: #$iterationCount | Timestamp: $(Get-Timestamp)" -ForegroundColor DarkGray
        }

        # Cambios en PreviewTextBlock
        if ($currentPreviewText -ne $lastPreviewText) {
            $hasChanges = $true
            Write-Host ""
            Write-Host "[$(Get-Timestamp)] 📝 CAMBIO en PreviewTextBlock:" -ForegroundColor Cyan
            Write-Host "  ANTES: '$lastPreviewText'" -ForegroundColor Red
            Write-Host "  AHORA: '$currentPreviewText'" -ForegroundColor Green
            $lastPreviewText = $currentPreviewText
        }

        # Cambios en PreviewEditor (texto)
        if ($currentEditorText -ne $lastEditorText) {
            $hasChanges = $true
            Write-Host ""
            Write-Host "[$(Get-Timestamp)] ✏️  CAMBIO en PreviewEditor (texto):" -ForegroundColor Yellow
            Write-Host "  ANTES: '$lastEditorText'" -ForegroundColor Red
            Write-Host "  AHORA: '$currentEditorText'" -ForegroundColor Green
            $lastEditorText = $currentEditorText
        }

        # Cambios en visibilidad del PreviewEditor
        if ($isEditorVisible -ne $lastEditorVisible) {
            $hasChanges = $true
            Write-Host ""
            Write-Host "[$(Get-Timestamp)] 👁️  CAMBIO en PreviewEditor (visibilidad):" -ForegroundColor Magenta
            Write-Host "  ANTES: $(if ($lastEditorVisible) { 'VISIBLE' } else { 'OCULTO' })" -ForegroundColor Red
            Write-Host "  AHORA: $(if ($isEditorVisible) { 'VISIBLE' } else { 'OCULTO' })" -ForegroundColor Green
            $lastEditorVisible = $isEditorVisible
        }

        # Estado actual (solo mostrar cada 10 iteraciones si no hay cambios)
        if ($hasChanges -or ($iterationCount % 10 -eq 0)) {
            Write-Host ""
            Write-Host "┌─ ESTADO ACTUAL ─────────────────────────────────────┐" -ForegroundColor DarkCyan
            Write-Host "│ PreviewTextBlock: " -NoNewline -ForegroundColor White
            Write-Host "'$currentPreviewText'" -ForegroundColor Cyan
            Write-Host "│ PreviewEditor:    " -NoNewline -ForegroundColor White
            if ($isEditorVisible) {
                Write-Host "VISIBLE - Texto: '$currentEditorText'" -ForegroundColor Green
            } else {
                Write-Host "OCULTO" -ForegroundColor Gray
            }
            Write-Host "└─────────────────────────────────────────────────────┘" -ForegroundColor DarkCyan
        }

        # Indicador de actividad (sin cambios)
        if (-not $hasChanges -and ($iterationCount % 10 -ne 0)) {
            Write-Host "." -NoNewline -ForegroundColor DarkGray
        }

        # Pausa antes de la siguiente iteración
        Start-Sleep -Milliseconds 500
    }
} catch {
    Write-Host ""
    Write-Host ""
    Write-Host "[$(Get-Timestamp)] ⚠ Monitoreo detenido" -ForegroundColor Yellow
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Monitor finalizado." -ForegroundColor Green
Write-Host ""
