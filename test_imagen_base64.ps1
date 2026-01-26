# Script para probar el sistema de imágenes Base64 en Calcpad WPF
$ErrorActionPreference = "Continue"
$LogFile = "test_imagen_log.txt"

# Limpiar log anterior
if (Test-Path $LogFile) { Remove-Item $LogFile }

Write-Host "Iniciando prueba del sistema Base64 de imágenes..." -ForegroundColor Cyan

# 1. Iniciar Calcpad WPF
$calcpadPath = ".\Calcpad.Wpf\bin\Release\net10.0-windows\Calcpad.exe"
if (-not (Test-Path $calcpadPath)) {
    Write-Host "ERROR: No se encontró Calcpad.Wpf.exe en $calcpadPath" -ForegroundColor Red
    exit 1
}

Write-Host "Iniciando Calcpad WPF..." -ForegroundColor Green
$process = Start-Process -FilePath $calcpadPath -PassThru -WindowStyle Normal

# Esperar a que se inicie
Start-Sleep -Seconds 3

try {
    # 2. Buscar la ventana de Calcpad
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type @"
        using System;
        using System.Runtime.InteropServices;
        public class Win32 {
            [DllImport("user32.dll")]
            public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
            [DllImport("user32.dll")]
            public static extern bool SetForegroundWindow(IntPtr hWnd);
        }
"@

    Start-Sleep -Seconds 2
    $hwnd = [Win32]::FindWindow($null, "Calcpad")
    if ($hwnd -eq [IntPtr]::Zero) {
        Write-Host "No se pudo encontrar la ventana de Calcpad" -ForegroundColor Yellow
    } else {
        [Win32]::SetForegroundWindow($hwnd) | Out-Null
        Write-Host "Ventana de Calcpad encontrada y activada" -ForegroundColor Green
    }

    # 3. Simular Ctrl+O para abrir archivo
    Start-Sleep -Seconds 1
    [System.Windows.Forms.SendKeys]::SendWait("^o")
    Write-Host "Enviado Ctrl+O para abrir archivo..." -ForegroundColor Cyan

    Start-Sleep -Seconds 2

    # 4. Escribir la ruta del archivo de prueba
    $testFile = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\test_imagen_pequeña.cpd"
    [System.Windows.Forms.SendKeys]::SendWait($testFile)
    Start-Sleep -Seconds 1
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")

    Write-Host "Archivo de prueba enviado: $testFile" -ForegroundColor Green

    # 5. Esperar a que cargue
    Start-Sleep -Seconds 3

    # 6. Presionar F5 para calcular
    Write-Host "Presionando F5 para calcular..." -ForegroundColor Cyan
    [System.Windows.Forms.SendKeys]::SendWait("{F5}")

    # 7. Esperar a que se procese
    Start-Sleep -Seconds 5

    # 8. Verificar el log de debug
    $debugLog = "$env:TEMP\calcpad-debug.txt"
    if (Test-Path $debugLog) {
        Write-Host "`n=== LOG DE DEBUG ===" -ForegroundColor Yellow
        Get-Content $debugLog | Select-Object -Last 30
    }

    # 9. Buscar el archivo HTML de salida generado
    $htmlOutput = "test_salida.html"
    if (Test-Path $htmlOutput) {
        Write-Host "`n=== VERIFICANDO HTML GENERADO ===" -ForegroundColor Yellow

        $htmlContent = Get-Content $htmlOutput -Raw

        # Buscar marcadores MULTILANG_OUTPUT
        if ($htmlContent -match "<!--MULTILANG_OUTPUT:") {
            Write-Host "ADVERTENCIA: Todavía hay marcadores MULTILANG_OUTPUT sin procesar" -ForegroundColor Red
            $htmlContent | Select-String "<!--MULTILANG_OUTPUT:" | Select-Object -First 3
        }

        # Buscar imágenes Base64
        if ($htmlContent -match "data:image/") {
            Write-Host "ÉXITO: Se encontraron imágenes Base64 embebidas en el HTML" -ForegroundColor Green
            $matches = [regex]::Matches($htmlContent, 'src="data:image/(\w+);base64,([^"]{0,50})')
            foreach ($match in $matches) {
                Write-Host "  - Formato: $($match.Groups[1].Value), Base64: $($match.Groups[2].Value)..." -ForegroundColor Cyan
            }
        } else {
            Write-Host "NO se encontraron imágenes Base64 en el HTML" -ForegroundColor Red
        }

        # Buscar errores
        if ($htmlContent -match "Error|error|ERROR") {
            Write-Host "`nSe encontraron errores en el HTML:" -ForegroundColor Yellow
            $htmlContent | Select-String "error|Error|ERROR" | Select-Object -First 5
        }
    } else {
        Write-Host "No se encontró el archivo HTML de salida" -ForegroundColor Yellow
    }

    Write-Host "`n=== PRUEBA COMPLETA ===" -ForegroundColor Cyan
    Write-Host "Calcpad sigue ejecutándose. Presiona Enter para cerrarlo o Ctrl+C para dejarlo abierto." -ForegroundColor Yellow
    Read-Host

} finally {
    # Cerrar Calcpad si sigue ejecutándose
    if (-not $process.HasExited) {
        Write-Host "Cerrando Calcpad..." -ForegroundColor Cyan
        $process.CloseMainWindow() | Out-Null
        Start-Sleep -Seconds 2
        if (-not $process.HasExited) {
            $process.Kill()
        }
    }
}

Write-Host "`nPrueba finalizada." -ForegroundColor Green
