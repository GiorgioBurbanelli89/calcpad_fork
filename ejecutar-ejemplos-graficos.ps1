# ============================================
# EJECUTAR EJEMPLOS DE GRÁFICAS FEM
# Python y Octave desde Calcpad CLI
# ============================================

$calcpadCli = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Cli\bin\Release\net10.0-windows\Calcpad.Cli.exe"
$outputDir = "C:\Users\j-b-j\AppData\Local\Temp"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                            ║" -ForegroundColor Cyan
Write-Host "║        EJEMPLOS DE GRÁFICAS MESH FEM                       ║" -ForegroundColor Cyan
Write-Host "║        Python y Octave desde Calcpad CLI                   ║" -ForegroundColor Cyan
Write-Host "║                                                            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar que existe Calcpad CLI
if (-not (Test-Path $calcpadCli)) {
    Write-Host "❌ ERROR: Calcpad CLI no encontrado en:" -ForegroundColor Red
    Write-Host $calcpadCli -ForegroundColor Red
    Write-Host ""
    Write-Host "Compila primero con:" -ForegroundColor Yellow
    Write-Host "  cd C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Cli" -ForegroundColor White
    Write-Host "  dotnet build -c Release" -ForegroundColor White
    exit 1
}

Write-Host "✓ Calcpad CLI encontrado" -ForegroundColor Green
Write-Host ""

# ============================================
# EJEMPLO 1: PYTHON
# ============================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
Write-Host "  1️⃣  EJECUTANDO EJEMPLO PYTHON" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
Write-Host ""

$pythonExample = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Examples\FEM-Mesh-Python.cpd"
$pythonOutput = "$outputDir\FEM-Mesh-Python.html"

if (Test-Path $pythonExample) {
    Write-Host "📄 Archivo: FEM-Mesh-Python.cpd" -ForegroundColor White
    Write-Host "⏳ Ejecutando..." -ForegroundColor Yellow
    Write-Host ""

    # Ejecutar Calcpad CLI
    & $calcpadCli $pythonExample $pythonOutput

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Ejecutado exitosamente" -ForegroundColor Green
        Write-Host "📊 Output HTML: $pythonOutput" -ForegroundColor Cyan
        Write-Host "🖼️  Imágenes generadas:" -ForegroundColor Cyan
        Write-Host "   - fem_mesh_python.png" -ForegroundColor White
        Write-Host "   - fem_mesh_python_optimized.png" -ForegroundColor White
        Write-Host "   - fem_mesh_python_blueprint.png" -ForegroundColor White
        Write-Host ""

        # Abrir HTML
        Write-Host "🌐 Abriendo en navegador..." -ForegroundColor Yellow
        Start-Process $pythonOutput
        Start-Sleep -Seconds 2
    } else {
        Write-Host ""
        Write-Host "❌ Error al ejecutar" -ForegroundColor Red
        Write-Host "Código de salida: $LASTEXITCODE" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Archivo no encontrado: $pythonExample" -ForegroundColor Red
}

Write-Host ""
Write-Host "Presiona Enter para continuar con Octave..." -ForegroundColor Yellow
Read-Host

# ============================================
# EJEMPLO 2: OCTAVE
# ============================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
Write-Host "  2️⃣  EJECUTANDO EJEMPLO OCTAVE" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
Write-Host ""

$octaveExample = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Examples\FEM-Mesh-Octave.cpd"
$octaveOutput = "$outputDir\FEM-Mesh-Octave.html"

if (Test-Path $octaveExample) {
    Write-Host "📄 Archivo: FEM-Mesh-Octave.cpd" -ForegroundColor White
    Write-Host "⏳ Ejecutando..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "⚠️  NOTA: Requiere GNU Octave instalado y configurado" -ForegroundColor Yellow
    Write-Host ""

    # Ejecutar Calcpad CLI
    & $calcpadCli $octaveExample $octaveOutput

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Ejecutado exitosamente" -ForegroundColor Green
        Write-Host "📊 Output HTML: $octaveOutput" -ForegroundColor Cyan
        Write-Host "🖼️  Imágenes generadas:" -ForegroundColor Cyan
        Write-Host "   - fem_mesh_octave.png" -ForegroundColor White
        Write-Host "   - fem_mesh_octave_3d.png" -ForegroundColor White
        Write-Host "   - fem_mesh_octave_colors.png" -ForegroundColor White
        Write-Host ""

        # Abrir HTML
        Write-Host "🌐 Abriendo en navegador..." -ForegroundColor Yellow
        Start-Process $octaveOutput
        Start-Sleep -Seconds 2
    } else {
        Write-Host ""
        Write-Host "❌ Error al ejecutar" -ForegroundColor Red
        Write-Host "Código de salida: $LASTEXITCODE" -ForegroundColor Red
        Write-Host ""
        Write-Host "💡 Posibles causas:" -ForegroundColor Yellow
        Write-Host "   1. Octave no está instalado" -ForegroundColor White
        Write-Host "   2. Octave no está configurado en Calcpad" -ForegroundColor White
        Write-Host "   3. Ruta incorrecta en configuración" -ForegroundColor White
        Write-Host ""
        Write-Host "Para configurar Octave:" -ForegroundColor Cyan
        Write-Host "   - Instalar desde: https://octave.org/download" -ForegroundColor White
        Write-Host "   - Configurar en Calcpad: Tools > External Languages > Octave" -ForegroundColor White
    }
} else {
    Write-Host "❌ Archivo no encontrado: $octaveExample" -ForegroundColor Red
}

# ============================================
# RESUMEN
# ============================================

Write-Host ""
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                      📊 RESUMEN                            ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Archivos de salida:" -ForegroundColor Cyan
Write-Host "  📁 Directorio: $outputDir" -ForegroundColor White
Write-Host ""
Write-Host "HTMLs generados:" -ForegroundColor Cyan
Write-Host "  📄 FEM-Mesh-Python.html" -ForegroundColor White
Write-Host "  📄 FEM-Mesh-Octave.html" -ForegroundColor White
Write-Host ""
Write-Host "Imágenes generadas:" -ForegroundColor Cyan
Write-Host "  Python:" -ForegroundColor Yellow
Write-Host "    🖼️  fem_mesh_python.png" -ForegroundColor White
Write-Host "    🖼️  fem_mesh_python_optimized.png" -ForegroundColor White
Write-Host "    🖼️  fem_mesh_python_blueprint.png" -ForegroundColor White
Write-Host ""
Write-Host "  Octave:" -ForegroundColor Yellow
Write-Host "    🖼️  fem_mesh_octave.png" -ForegroundColor White
Write-Host "    🖼️  fem_mesh_octave_3d.png" -ForegroundColor White
Write-Host "    🖼️  fem_mesh_octave_colors.png" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para abrir imágenes directamente:" -ForegroundColor Yellow
Write-Host "  explorer $outputDir" -ForegroundColor White
Write-Host ""

Read-Host "Presiona Enter para salir"
