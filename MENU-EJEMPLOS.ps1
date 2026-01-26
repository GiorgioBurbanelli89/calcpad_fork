# ============================================
# MENÚ DE EJEMPLOS - CALCPAD 2026
# ============================================

$calcpadExe = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\bin\Release\net8.0-windows\Calcpad.exe"

function Show-Header {
    Clear-Host
    Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                          ║" -ForegroundColor Cyan
    Write-Host "║          CALCPAD 2026 - EJEMPLOS INTEGRADOS             ║" -ForegroundColor Cyan
    Write-Host "║        Mejoras Oficiales + Funcionalidades Custom        ║" -ForegroundColor Cyan
    Write-Host "║                                                          ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Show-Improvements {
    Write-Host "✨ MEJORAS INTEGRADAS DEL REPOSITORIO OFICIAL:" -ForegroundColor Yellow
    Write-Host "   ✓ Tablas Markdown (UsePipeTables)" -ForegroundColor Green
    Write-Host "   ✓ Función matmul() optimizada (Winograd + SIMD)" -ForegroundColor Green
    Write-Host "   ✓ Correcciones issues #711, #712" -ForegroundColor Green
    Write-Host "   ✓ Mejoras en interpolación y strings" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 FUNCIONALIDADES PERSONALIZADAS PRESERVADAS:" -ForegroundColor Magenta
    Write-Host "   ✓ Preview dinámico con mensaje de progreso" -ForegroundColor Green
    Write-Host "   ✓ HTML embebido renderizado correctamente" -ForegroundColor Green
    Write-Host "   ✓ Soporte multi-lenguaje (Python, C#, R, Julia, etc.)" -ForegroundColor Green
    Write-Host "   ✓ Actualización dinámica del Output" -ForegroundColor Green
    Write-Host ""
}

function Show-Menu {
    Write-Host "📚 EJEMPLOS DISPONIBLES:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [1] Ejemplo Completo - Todas las Mejoras" -ForegroundColor White
    Write-Host "      • Tablas Markdown + matmul()" -ForegroundColor DarkGray
    Write-Host "      • Integración Python, C#, R, Julia" -ForegroundColor DarkGray
    Write-Host "      • Análisis estructural completo" -ForegroundColor DarkGray
    Write-Host "      • HTML embebido y preview dinámico" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  [2] Ejemplo Rápido - Tablas y matmul()" -ForegroundColor White
    Write-Host "      • Demostración enfocada en nuevas funciones" -ForegroundColor DarkGray
    Write-Host "      • Tablas de aceros estructurales" -ForegroundColor DarkGray
    Write-Host "      • Comparación de métodos de multiplicación" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  [3] Rectangular Slab FEA (Ejemplo Original)" -ForegroundColor White
    Write-Host "      • Análisis de elementos finitos" -ForegroundColor DarkGray
    Write-Host "      • Demuestra correcciones de HTML" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  [4] Ver Documentación de Mejoras" -ForegroundColor White
    Write-Host "      • Abrir MEJORAS-INTEGRADAS-2026.md" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  [0] Salir" -ForegroundColor Red
    Write-Host ""
}

function Open-Example {
    param($examplePath, $exampleName)

    if (Test-Path $calcpadExe) {
        Write-Host ""
        Write-Host "Abriendo: $exampleName" -ForegroundColor Green
        Write-Host ""
        Write-Host "⏳ OBSERVA EL PANEL OUTPUT:" -ForegroundColor Yellow
        Write-Host "   1. Preview inicial con headings/HTML" -ForegroundColor White
        Write-Host "   2. Mensaje: 'Procesando expresiones...'" -ForegroundColor White
        Write-Host "   3. Resultado final completo" -ForegroundColor White
        Write-Host ""

        Start-Process $calcpadExe -ArgumentList "`"$examplePath`""
        Start-Sleep -Seconds 2
    } else {
        Write-Host ""
        Write-Host "❌ ERROR: Calcpad.exe no encontrado" -ForegroundColor Red
        Write-Host ""
        Write-Host "Compila primero con:" -ForegroundColor Yellow
        Write-Host "  cd C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf" -ForegroundColor White
        Write-Host "  dotnet build -c Release" -ForegroundColor White
        Write-Host ""
        Read-Host "Presiona Enter para continuar"
    }
}

function Open-Documentation {
    $docPath = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\MEJORAS-INTEGRADAS-2026.md"

    if (Test-Path $docPath) {
        Write-Host ""
        Write-Host "Abriendo documentación..." -ForegroundColor Green
        Start-Process $docPath
        Start-Sleep -Seconds 1
    } else {
        Write-Host ""
        Write-Host "❌ ERROR: Archivo de documentación no encontrado" -ForegroundColor Red
        Write-Host ""
        Read-Host "Presiona Enter para continuar"
    }
}

# Main Loop
do {
    Show-Header
    Show-Improvements
    Show-Menu

    $choice = Read-Host "Selecciona una opción"

    switch ($choice) {
        "1" {
            $examplePath = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Examples\Calcpad-Nuevas-Mejoras-Demo.cpd"
            Open-Example $examplePath "Demostración Completa de Mejoras 2026"
        }
        "2" {
            $examplePath = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Examples\Ejemplo-Rapido-Tablas-Matmul.cpd"
            Open-Example $examplePath "Ejemplo Rápido - Tablas Markdown y matmul()"
        }
        "3" {
            $examplePath = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Examples\Structural Design\Concrete\Rectangular Slab FEA.cpd"
            Open-Example $examplePath "Análisis de Losa Rectangular con FEA"
        }
        "4" {
            Open-Documentation
        }
        "0" {
            Write-Host ""
            Write-Host "👋 ¡Hasta luego!" -ForegroundColor Cyan
            Write-Host ""
            break
        }
        default {
            Write-Host ""
            Write-Host "❌ Opción inválida. Presiona Enter para continuar..." -ForegroundColor Red
            Read-Host
        }
    }

} while ($choice -ne "0")
