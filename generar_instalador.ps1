# Script PowerShell para generar instalador de Calcpad Fork
# Versión: 1.0.1
# Fecha: 2026-01-22

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Generador de Instalador Calcpad Fork" -ForegroundColor Cyan
Write-Host "  Versión 1.0.1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Buscar iscc.exe en ubicaciones comunes
Write-Host "Buscando Inno Setup Compiler..." -ForegroundColor Yellow

$isccPaths = @(
    "C:\Program Files (x86)\Inno Setup 6\iscc.exe",
    "C:\Program Files\Inno Setup 6\iscc.exe",
    "C:\Program Files (x86)\Inno Setup 5\iscc.exe",
    "C:\Program Files\Inno Setup 5\iscc.exe"
)

$iscc = $null
foreach ($path in $isccPaths) {
    if (Test-Path $path) {
        $iscc = $path
        Write-Host "✓ Encontrado: $path" -ForegroundColor Green
        break
    }
}

if (-not $iscc) {
    Write-Host ""
    Write-Host "❌ ERROR: No se encontró Inno Setup Compiler" -ForegroundColor Red
    Write-Host ""
    Write-Host "Inno Setup no está instalado en tu sistema." -ForegroundColor Yellow
    Write-Host "Descárgalo desde: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Opciones:" -ForegroundColor Cyan
    Write-Host "  1. Instalar Inno Setup y volver a ejecutar este script"
    Write-Host "  2. Usar distribución portable (sin instalador)"
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""

# Verificar que existe el archivo .iss
$issFile = "CalcpadWpfInstaller.iss"
if (-not (Test-Path $issFile)) {
    Write-Host "❌ ERROR: No se encontró $issFile" -ForegroundColor Red
    Write-Host "Asegúrate de ejecutar este script desde la carpeta raíz del proyecto." -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "Script del instalador: $issFile ✓" -ForegroundColor Green
Write-Host ""

# Verificar archivos Release
$releasePath = "Calcpad.Wpf\bin\Release\net10.0-windows\Calcpad.exe"
if (-not (Test-Path $releasePath)) {
    Write-Host "⚠ ADVERTENCIA: No se encontraron archivos Release" -ForegroundColor Yellow
    Write-Host "Compilando proyecto en modo Release..." -ForegroundColor Yellow
    Write-Host ""

    & dotnet build Calcpad.Wpf\Calcpad.Wpf.csproj -c Release --no-incremental

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "❌ ERROR: Falló la compilación" -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }

    Write-Host ""
    Write-Host "✓ Compilación completada" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Archivos Release: OK ✓" -ForegroundColor Green
    Write-Host ""
}

# Compilar el instalador
Write-Host "Generando instalador..." -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray

& $iscc $issFile

Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host ""

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ ÉXITO: Instalador generado correctamente!" -ForegroundColor Green
    Write-Host ""

    $installerPath = "Installer\CalcpadFork-Setup-1.0.1.exe"
    if (Test-Path $installerPath) {
        $size = (Get-Item $installerPath).Length / 1MB
        Write-Host "Ubicación: $installerPath" -ForegroundColor Cyan
        Write-Host "Tamaño: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan
        Write-Host ""

        # Preguntar si abrir la carpeta
        $response = Read-Host "¿Abrir carpeta del instalador? (S/N)"
        if ($response -eq 'S' -or $response -eq 's') {
            & explorer.exe (Split-Path $installerPath -Parent)
        }
    }
} else {
    Write-Host "❌ ERROR: Falló la generación del instalador" -ForegroundColor Red
    Write-Host "Revisa los mensajes de error arriba." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host ""
Write-Host "Presiona Enter para salir..."
Read-Host
