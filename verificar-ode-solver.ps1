# Script de Verificacion del ODE Solver
# Fecha: 2026-01-26
# Version: 7.5.8-symbolic+odes

Write-Host "=================================="
Write-Host "VERIFICACION DEL ODE SOLVER"
Write-Host "=================================="
Write-Host ""

# 1. Verificar que el CLI este compilado
$cliPath = "Calcpad.Cli\bin\Release\net10.0\Cli.exe"
if (-Not (Test-Path $cliPath)) {
    Write-Host "ERROR: CLI no encontrado. Compilando..."
    dotnet build Calcpad.Cli\Calcpad.Cli.csproj -c Release
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Fallo la compilacion"
        exit 1
    }
}
Write-Host "OK: CLI encontrado"

# 2. Verificar archivo de prueba
$testFile = "Examples\Test-ODE-Simple.cpd"
if (-Not (Test-Path $testFile)) {
    Write-Host "ERROR: Archivo de prueba no encontrado: $testFile"
    exit 1
}
Write-Host "OK: Archivo de prueba encontrado"

# 3. Generar HTML
Write-Host ""
Write-Host "Generando HTML..."
$outputFile = "Examples\test-ode-verificacion.html"
& $cliPath $testFile $outputFile -s

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Fallo la generacion de HTML"
    exit 1
}
Write-Host "OK: HTML generado: $outputFile"

# 4. Contar errores
Write-Host ""
Write-Host "Analizando HTML..."
$htmlContent = Get-Content $outputFile -Raw

# Contar usando Select-String
$errorMatches = Select-String -InputObject $htmlContent -Pattern 'class="err"' -AllMatches
$errorCount = if ($errorMatches) { $errorMatches.Matches.Count } else { 0 }

$ecuacionMatches = Select-String -InputObject $htmlContent -Pattern '<b>Ecuaci' -AllMatches
$ecuacionCount = if ($ecuacionMatches) { $ecuacionMatches.Matches.Count } else { 0 }

$solucionMatches = Select-String -InputObject $htmlContent -Pattern '<b>Soluci' -AllMatches
$solucionCount = if ($solucionMatches) { $solucionMatches.Matches.Count } else { 0 }

Write-Host ""
Write-Host "=================================="
Write-Host "RESULTADOS"
Write-Host "=================================="

# Errores
Write-Host "Errores de parsing: $errorCount (esperado: 0)"

# Ecuaciones
Write-Host "Ecuaciones encontradas: $ecuacionCount (esperado: 8)"

# Soluciones
Write-Host "Soluciones encontradas: $solucionCount (esperado: 8)"

Write-Host ""
Write-Host "=================================="

# Resultado final
if ($errorCount -eq 0 -and $ecuacionCount -eq 8 -and $solucionCount -eq 8) {
    Write-Host "VERIFICACION COMPLETA: EXITO"
    Write-Host ""
    Write-Host "El solver de ODEs esta funcionando correctamente."
    Write-Host "Archivo generado: $outputFile"
    Write-Host ""

    # Preguntar si quiere abrir el HTML
    $response = Read-Host "Desea abrir el HTML en el navegador? (s/n)"
    if ($response -eq 's' -or $response -eq 'S') {
        Start-Process $outputFile
    }

    exit 0
} else {
    Write-Host "VERIFICACION COMPLETA: FALLIDA"
    Write-Host ""
    Write-Host "Revise los errores arriba."
    exit 1
}
