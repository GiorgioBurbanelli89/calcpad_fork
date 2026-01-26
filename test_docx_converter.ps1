# Script de prueba para el convertidor de DOCX a CPD
# Uso: .\test_docx_converter.ps1

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "   CONVERTIDOR DOCX -> CPD      " -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Ruta al CLI de Calcpad
$cliPath = ".\Calcpad.Cli\bin\Debug\net10.0\Calcpad.Cli.exe"

# Verificar que el CLI existe
if (-not (Test-Path $cliPath)) {
    Write-Host "ERROR: No se encuentra Calcpad.Cli.exe" -ForegroundColor Red
    Write-Host "Compilando el proyecto..." -ForegroundColor Yellow
    dotnet build Calcpad.Cli/Calcpad.Cli.csproj -c Debug
    if (-not (Test-Path $cliPath)) {
        Write-Host "ERROR: No se pudo compilar Calcpad.Cli" -ForegroundColor Red
        exit 1
    }
}

# Buscar archivos DOCX de ejemplo
$docxFiles = Get-ChildItem -Path "Examples" -Filter "*.docx" -Recurse | Select-Object -First 3

if ($docxFiles.Count -eq 0) {
    Write-Host "No se encontraron archivos DOCX de ejemplo" -ForegroundColor Yellow
    Write-Host "Creando un archivo DOCX de prueba simple..." -ForegroundColor Yellow

    # Crear archivo de prueba
    $testDocx = "test_sample.docx"
    Write-Host "Por favor, coloque un archivo DOCX de prueba en: $testDocx" -ForegroundColor Yellow
    exit
}

Write-Host "Archivos DOCX encontrados:" -ForegroundColor Green
$docxFiles | ForEach-Object { Write-Host "  - $($_.FullName)" -ForegroundColor Gray }
Write-Host ""

# Probar conversión de cada archivo
foreach ($docx in $docxFiles) {
    Write-Host "----------------------------------------" -ForegroundColor Cyan
    Write-Host "Convirtiendo: $($docx.Name)" -ForegroundColor Yellow
    Write-Host "Ruta completa: $($docx.FullName)" -ForegroundColor Gray
    Write-Host ""

    $outputFile = "$($docx.BaseName)_converted.cpd"
    $outputPath = Join-Path (Split-Path $docx.FullName) $outputFile

    Write-Host "Comando:" -ForegroundColor Cyan
    Write-Host "  $cliPath `"$($docx.FullName)`" -cpd" -ForegroundColor Gray
    Write-Host ""

    # Ejecutar conversión
    try {
        & $cliPath "$($docx.FullName)" "-cpd"

        # Verificar si se creó el archivo de salida
        $cpdFile = $docx.FullName -replace "\.docx$", ".cpd"
        if (Test-Path $cpdFile) {
            Write-Host "SUCCESS: Archivo convertido a:" -ForegroundColor Green
            Write-Host "  $cpdFile" -ForegroundColor Green
            Write-Host ""

            # Mostrar primeras líneas del archivo convertido
            Write-Host "Primeras 30 líneas del archivo CPD:" -ForegroundColor Cyan
            Get-Content $cpdFile -TotalCount 30 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
            Write-Host "  ..." -ForegroundColor Gray
            Write-Host ""
        } else {
            Write-Host "WARNING: No se encontró el archivo de salida" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }

    Write-Host ""
}

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Conversión completada          " -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NOTA: Para usar el convertidor manualmente:" -ForegroundColor Yellow
Write-Host "  Sintaxis: Calcpad.Cli.exe `"archivo.docx`" -cpd" -ForegroundColor White
Write-Host ""
Write-Host "Ejemplos:" -ForegroundColor Yellow
Write-Host "  # Convertir DOCX a CPD (solo convertir)" -ForegroundColor Gray
Write-Host "  Calcpad.Cli.exe `"documento.docx`" -cpd" -ForegroundColor White
Write-Host ""
Write-Host "  # Convertir DOCX a CPD y especificar archivo de salida" -ForegroundColor Gray
Write-Host "  Calcpad.Cli.exe `"documento.docx`" `"salida.cpd`" -cpd" -ForegroundColor White
Write-Host ""
Write-Host "  # Convertir DOCX a HTML (procesar con Calcpad)" -ForegroundColor Gray
Write-Host "  Calcpad.Cli.exe `"documento.docx`" `"salida.html`"" -ForegroundColor White
Write-Host ""
