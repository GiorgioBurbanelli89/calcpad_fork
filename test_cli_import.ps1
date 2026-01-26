# Test directo con Calcpad CLI para ver output real
$docxFile = "C:\Users\j-b-j\Downloads\calculo_estructural_escalera_metalica.docx"
$xlsxFile = "C:\Users\j-b-j\Downloads\HOJA DE CALCULO 23-01-2026.xlsx"

Write-Host "======================================"
Write-Host "Test Calcpad CLI - Importación Word"
Write-Host "======================================"

# Buscar el ejecutable de Calcpad CLI
$cliPath = "Calcpad.Cli\bin\Debug\net10.0\Calcpad.Cli.exe"

if (-not (Test-Path $cliPath)) {
    Write-Host "Compilando Calcpad.Cli..."
    Push-Location Calcpad.Cli
    dotnet build --configuration Debug
    Pop-Location
}

if (Test-Path $cliPath) {
    Write-Host "`n1. Probando importación de WORD (.docx)" -ForegroundColor Cyan
    Write-Host "   Archivo: calculo_estructural_escalera_metalica.docx"

    # Verificar si hay un comando de importación
    $result = & $cliPath "--help" 2>&1
    Write-Host $result

    # Intentar importar directamente
    if (Test-Path $docxFile) {
        Write-Host "`n   Convirtiendo con import..."
        & $cliPath "import" $docxFile "word_output.cpd" 2>&1 | Tee-Object -Variable wordOutput

        if (Test-Path "word_output.cpd") {
            Write-Host "`n   Contenido generado:" -ForegroundColor Yellow
            Get-Content "word_output.cpd" | Select-Object -First 100
        }

        Write-Host "`n   Generando HTML..."
        & $cliPath "word_output.cpd" "word_output.html" 2>&1

        if (Test-Path "word_output.html") {
            Write-Host "   Abriendo HTML..." -ForegroundColor Green
            Start-Process "word_output.html"
        }
    }

    Write-Host "`n2. Probando importación de EXCEL (.xlsx)" -ForegroundColor Cyan
    Write-Host "   Archivo: HOJA DE CALCULO 23-01-2026.xlsx"

    if (Test-Path $xlsxFile) {
        Write-Host "`n   Convirtiendo..."
        & $cliPath "import" $xlsxFile "excel_output.cpd" 2>&1 | Tee-Object -Variable excelOutput

        if (Test-Path "excel_output.cpd") {
            Write-Host "`n   Contenido generado:" -ForegroundColor Yellow
            Get-Content "excel_output.cpd" | Select-Object -First 100
        }

        Write-Host "`n   Generando HTML..."
        & $cliPath "excel_output.cpd" "excel_output.html" 2>&1

        if (Test-Path "excel_output.html") {
            Write-Host "   Abriendo HTML..." -ForegroundColor Green
            Start-Process "excel_output.html"
        }
    }
} else {
    Write-Host "ERROR: No se encontró Calcpad.Cli.exe" -ForegroundColor Red
}

Write-Host "`n======================================"
Write-Host "Revisando comandos disponibles..."
Write-Host "======================================"

# Revisar el código de Program.cs para ver qué comandos hay
if (Test-Path "Calcpad.Cli\Program.cs") {
    Write-Host "`nRevisando comandos en Program.cs..."
    Select-String -Path "Calcpad.Cli\Program.cs" -Pattern "import|docx|xlsx" -Context 2,2 |
        ForEach-Object { Write-Host $_.Line }
}
