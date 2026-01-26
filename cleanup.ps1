# Script de Limpieza - Calcpad Fork v1.0.0
# Elimina archivos temporales, cache y compilaciones debug

Write-Host "=== LIMPIEZA DE ARCHIVOS INNECESARIOS ===" -ForegroundColor Cyan
Write-Host ""

$rootPath = "C:\Users\j-b-j\Documents\Calcpad-7.5.7"
Set-Location $rootPath

$totalFreed = 0

# 1. Limpiar carpetas bin/obj en modo Debug
Write-Host "1. Limpiando carpetas bin/obj Debug..." -ForegroundColor Yellow
$debugFolders = Get-ChildItem -Path . -Recurse -Directory -Filter "bin" -ErrorAction SilentlyContinue |
    Where-Object { $_.Parent.Name -notlike "*Release*" }
$debugFolders += Get-ChildItem -Path . -Recurse -Directory -Filter "obj" -ErrorAction SilentlyContinue |
    Where-Object { $_.Parent.Name -notlike "*Release*" }

foreach ($folder in $debugFolders) {
    if ($folder.FullName -notlike "*\bin\Release*" -and $folder.FullName -notlike "*\obj\Release*") {
        try {
            $size = (Get-ChildItem -Path $folder.FullName -Recurse -File -ErrorAction SilentlyContinue |
                Measure-Object -Property Length -Sum).Sum
            Remove-Item -Path $folder.FullName -Recurse -Force -ErrorAction SilentlyContinue
            $totalFreed += $size
            Write-Host "  Eliminado: $($folder.FullName)" -ForegroundColor Gray
        } catch {
            Write-Host "  Saltado: $($folder.FullName)" -ForegroundColor DarkGray
        }
    }
}

# 2. Limpiar archivos temporales de Visual Studio
Write-Host ""
Write-Host "2. Limpiando archivos .vs..." -ForegroundColor Yellow
$vsFiles = Get-ChildItem -Path . -Recurse -Directory -Filter ".vs" -ErrorAction SilentlyContinue
foreach ($file in $vsFiles) {
    try {
        $size = (Get-ChildItem -Path $file.FullName -Recurse -File -ErrorAction SilentlyContinue |
            Measure-Object -Property Length -Sum).Sum
        Remove-Item -Path $file.FullName -Recurse -Force -ErrorAction SilentlyContinue
        $totalFreed += $size
        Write-Host "  Eliminado: $($file.FullName)" -ForegroundColor Gray
    } catch {}
}

# 3. Limpiar archivos temporales de compilación
Write-Host ""
Write-Host "3. Limpiando archivos temporales *.tmp, *.log..." -ForegroundColor Yellow
$tempExtensions = @("*.tmp", "*.log", "*.bak", "*.user", "*.suo")
foreach ($ext in $tempExtensions) {
    $files = Get-ChildItem -Path . -Recurse -Filter $ext -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        try {
            $totalFreed += $file.Length
            Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
            Write-Host "  Eliminado: $($file.Name)" -ForegroundColor Gray
        } catch {}
    }
}

# 4. Limpiar archivos temporales de Claude (tmpclaude-*)
Write-Host ""
Write-Host "4. Limpiando archivos temporales de Claude..." -ForegroundColor Yellow
$claudeFiles = Get-ChildItem -Path . -Filter "tmpclaude-*" -ErrorAction SilentlyContinue
foreach ($file in $claudeFiles) {
    try {
        if ($file.Length) {
            $totalFreed += $file.Length
        }
        Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
        Write-Host "  Eliminado: $($file.Name)" -ForegroundColor Gray
    } catch {}
}

# 5. Limpiar archivos de SAP2000 temporales
Write-Host ""
Write-Host "5. Limpiando archivos SAP2000 temporales (.\$2k, .OUT, etc.)..." -ForegroundColor Yellow
$sap2000Extensions = @("*.\$2k", "*.OUT", "*.K_0", "*.K_I", "*.K_J", "*.K_M", "*.Y", "*.Y\$\$", "*.Y00", "*.Y01", "*.Y_", "*.Y_1", "*.msh", "*.ico", "*.sdb")
foreach ($ext in $sap2000Extensions) {
    $files = Get-ChildItem -Path . -Filter $ext -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        try {
            $totalFreed += $file.Length
            Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
            Write-Host "  Eliminado: $($file.Name)" -ForegroundColor Gray
        } catch {}
    }
}

# 6. Limpiar cache de git (solo loose objects)
Write-Host ""
Write-Host "6. Limpiando cache de git..." -ForegroundColor Yellow
try {
    git gc --auto --quiet 2>$null
    git prune 2>$null
    Write-Host "  Git garbage collection ejecutado" -ForegroundColor Gray
} catch {
    Write-Host "  Saltado (git no disponible)" -ForegroundColor DarkGray
}

# 7. Limpiar archivos de NuGet packages duplicados
Write-Host ""
Write-Host "7. Limpiando packages NuGet locales..." -ForegroundColor Yellow
$nugetCache = "$env:USERPROFILE\.nuget\packages"
if (Test-Path $nugetCache) {
    Write-Host "  Limpiando cache NuGet..." -ForegroundColor Gray
    dotnet nuget locals all --clear 2>$null
}

# 8. Limpiar archivos de PowerShell temporales
Write-Host ""
Write-Host "8. Limpiando scripts PowerShell temporales..." -ForegroundColor Yellow
$psScripts = @("check_*.ps1", "test_*.ps1", "monitor*.ps1", "inspect*.ps1", "simple_*.ps1",
               "verify_*.ps1", "automated_*.ps1", "debug*.ps1", "capture_*.ps1")
foreach ($pattern in $psScripts) {
    $files = Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        # No eliminar cleanup.ps1
        if ($file.Name -ne "cleanup.ps1") {
            try {
                $totalFreed += $file.Length
                Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
                Write-Host "  Eliminado: $($file.Name)" -ForegroundColor Gray
            } catch {}
        }
    }
}

# Resumen final
Write-Host ""
Write-Host "=== LIMPIEZA COMPLETADA ===" -ForegroundColor Green
Write-Host ""
$freedMB = [math]::Round($totalFreed / 1MB, 2)
$freedGB = [math]::Round($totalFreed / 1GB, 2)

if ($freedGB -gt 0.1) {
    Write-Host "Espacio liberado: $freedGB GB" -ForegroundColor Cyan
} else {
    Write-Host "Espacio liberado: $freedMB MB" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Archivos eliminados:" -ForegroundColor Yellow
Write-Host "  - Carpetas bin/obj Debug" -ForegroundColor Gray
Write-Host "  - Archivos .vs" -ForegroundColor Gray
Write-Host "  - Archivos temporales (*.tmp, *.log, *.bak)" -ForegroundColor Gray
Write-Host "  - Archivos Claude temporales" -ForegroundColor Gray
Write-Host "  - Archivos SAP2000 temporales" -ForegroundColor Gray
Write-Host "  - Scripts PowerShell de testing" -ForegroundColor Gray
Write-Host "  - Cache de git (garbage collection)" -ForegroundColor Gray
Write-Host "  - Cache de NuGet" -ForegroundColor Gray
Write-Host ""
Write-Host "Archivos PRESERVADOS:" -ForegroundColor Green
Write-Host "  - bin/Release (instalador)" -ForegroundColor Gray
Write-Host "  - Código fuente" -ForegroundColor Gray
Write-Host "  - Documentación (.md)" -ForegroundColor Gray
Write-Host "  - Ejemplos" -ForegroundColor Gray
Write-Host "  - LICENSE" -ForegroundColor Gray
Write-Host ""
