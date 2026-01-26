# Script para abrir el ejemplo de nuevas mejoras de Calcpad
$calcpadExe = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\bin\Release\net8.0-windows\Calcpad.exe"
$demoFile = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Examples\Calcpad-Nuevas-Mejoras-Demo.cpd"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEMOSTRACIÓN DE NUEVAS MEJORAS CALCPAD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Este ejemplo demuestra:" -ForegroundColor Yellow
Write-Host "  ✓ Tablas Markdown (UsePipeTables)" -ForegroundColor Green
Write-Host "  ✓ Función matmul() optimizada" -ForegroundColor Green
Write-Host "  ✓ Integración Python, C#, R, Julia" -ForegroundColor Green
Write-Host "  ✓ HTML embebido mejorado" -ForegroundColor Green
Write-Host "  ✓ Preview dinámico con progreso" -ForegroundColor Green
Write-Host ""

if (Test-Path $calcpadExe) {
    Write-Host "Abriendo Calcpad..." -ForegroundColor Green
    Start-Process $calcpadExe -ArgumentList "`"$demoFile`""
    Write-Host ""
    Write-Host "NOTA: Observa el panel Output mientras carga:" -ForegroundColor Magenta
    Write-Host "  - Verás el preview dinámico con headings y HTML" -ForegroundColor White
    Write-Host "  - Mensaje animado: 'Procesando expresiones...'" -ForegroundColor White
    Write-Host "  - Luego el resultado completo con todas las tablas" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "ERROR: No se encuentra Calcpad.exe en:" -ForegroundColor Red
    Write-Host $calcpadExe -ForegroundColor Red
    Write-Host ""
    Write-Host "Compila el proyecto primero con:" -ForegroundColor Yellow
    Write-Host "  cd C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf" -ForegroundColor White
    Write-Host "  dotnet build -c Release" -ForegroundColor White
}
