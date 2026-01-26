# Script para generar HTML de ejemplo con Calcpad CLI

$calcpadCli = "Calcpad.Cli\bin\Release\net10.0\Cli.exe"
$inputFile = "Examples\Multiple-Syntax-Parser-Demo.cpd"
$outputFile = "Examples\multiple-syntax-parser-demo.html"

Write-Host "Generando HTML del ejemplo de parsers múltiples..." -ForegroundColor Cyan

# Verificar que el CLI existe
if (-not (Test-Path $calcpadCli)) {
    Write-Host "Error: CLI no encontrado en $calcpadCli" -ForegroundColor Red
    Write-Host "Compilando CLI..." -ForegroundColor Yellow
    dotnet build Calcpad.Cli\Calcpad.Cli.csproj -c Release
}

# Ejecutar CLI
try {
    & dotnet $calcpadCli.Replace(".exe", ".dll") $inputFile -html $outputFile

    if (Test-Path $outputFile) {
        Write-Host "HTML generado exitosamente: $outputFile" -ForegroundColor Green

        # Abrir en navegador
        Start-Process $outputFile
    } else {
        Write-Host "Error: No se generó el archivo HTML" -ForegroundColor Red
    }
} catch {
    Write-Host "Error ejecutando CLI: $_" -ForegroundColor Red
}
