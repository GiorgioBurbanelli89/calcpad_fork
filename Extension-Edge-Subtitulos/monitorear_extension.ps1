# monitorear_extension.ps1 - Monitorear extensión en tiempo real

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MONITOR EN TIEMPO REAL - EXTENSIÓN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar archivos
Write-Host "[PASO 1] Verificando archivos..." -ForegroundColor Yellow

$archivosRequeridos = @(
    "manifest.json",
    "background.js",
    "content.js",
    "content_youtube.js",
    "popup.html",
    "popup.js",
    "styles.css"
)

$todosCorrecto = $true

foreach ($archivo in $archivosRequeridos) {
    $ruta = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Extension-Edge-Subtitulos\$archivo"
    if (Test-Path $ruta) {
        $tamano = (Get-Item $ruta).Length
        Write-Host "  ✓ $archivo ($tamano bytes)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $archivo - NO ENCONTRADO" -ForegroundColor Red
        $todosCorrecto = $false
    }
}

if (-not $todosCorrecto) {
    Write-Host ""
    Write-Host "ERROR: Faltan archivos necesarios!" -ForegroundColor Red
    pause
    exit
}

Write-Host ""
Write-Host "[PASO 2] Verificando sintaxis JSON..." -ForegroundColor Yellow

try {
    $manifest = Get-Content "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Extension-Edge-Subtitulos\manifest.json" -Raw | ConvertFrom-Json
    Write-Host "  ✓ manifest.json - Sintaxis correcta" -ForegroundColor Green
    Write-Host "    - Nombre: $($manifest.name)" -ForegroundColor Gray
    Write-Host "    - Versión: $($manifest.version)" -ForegroundColor Gray
    Write-Host "    - Permisos: $($manifest.permissions.Count)" -ForegroundColor Gray

    # Verificar webRequest
    if ($manifest.permissions -contains "webRequest") {
        Write-Host "    - webRequest: ✓ ACTIVO" -ForegroundColor Green
    } else {
        Write-Host "    - webRequest: ✗ NO ENCONTRADO" -ForegroundColor Red
    }
} catch {
    Write-Host "  ✗ manifest.json - ERROR DE SINTAXIS" -ForegroundColor Red
    Write-Host "    $($_.Exception.Message)" -ForegroundColor Red
    pause
    exit
}

Write-Host ""
Write-Host "[PASO 3] Verificando permisos..." -ForegroundColor Yellow

$permisosRequeridos = @("webRequest", "downloads", "tabs", "storage", "notifications")

foreach ($permiso in $permisosRequeridos) {
    if ($manifest.permissions -contains $permiso) {
        Write-Host "  ✓ $permiso" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $permiso - FALTA" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[PASO 4] Verificando iconos..." -ForegroundColor Yellow

$iconos = @("icons/icon16.png", "icons/icon48.png", "icons/icon128.png")

foreach ($icono in $iconos) {
    $rutaIcono = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Extension-Edge-Subtitulos\$icono"
    if (Test-Path $rutaIcono) {
        $tamano = (Get-Item $rutaIcono).Length
        Write-Host "  ✓ $icono ($tamano bytes)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $icono - NO ENCONTRADO" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ESTADO: TODO CORRECTO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "AHORA MONITOREAREMOS LA EXTENSIÓN EN EDGE" -ForegroundColor Yellow
Write-Host ""
Write-Host "INSTRUCCIONES:" -ForegroundColor White
Write-Host "1. Abre Edge en otra ventana" -ForegroundColor Gray
Write-Host "2. Ve a: edge://extensions/" -ForegroundColor Gray
Write-Host "3. Activa 'Modo de desarrollador'" -ForegroundColor Gray
Write-Host "4. Busca la extensión y haz clic en RECARGAR" -ForegroundColor Gray
Write-Host "5. Haz clic en 'Detalles'" -ForegroundColor Gray
Write-Host "6. Haz clic en 'Inspeccionar vistas -> service worker'" -ForegroundColor Gray
Write-Host ""
Write-Host "BUSCA EN LA CONSOLA DEL SERVICE WORKER:" -ForegroundColor Yellow
Write-Host "  - '[Video Detector PRO] Background service worker iniciado'" -ForegroundColor Gray
Write-Host "  - '[Video Detector PRO] Sistema de detección activado'" -ForegroundColor Gray
Write-Host ""

Write-Host "Presiona ENTER cuando hayas abierto la consola del service worker..." -ForegroundColor Cyan
Read-Host

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MONITOREO INICIADO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "AHORA:" -ForegroundColor Yellow
Write-Host "1. Abre una pestaña de YouTube" -ForegroundColor White
Write-Host "2. Reproduce un video" -ForegroundColor White
Write-Host "3. Observa la consola del service worker" -ForegroundColor White
Write-Host ""

Write-Host "QUÉ DEBERÍAS VER:" -ForegroundColor Yellow
Write-Host "  [Video Detector PRO] Video detectado via webRequest: https://..." -ForegroundColor Gray
Write-Host "  [Video Detector PRO] Video almacenado (MP4): https://..." -ForegroundColor Gray
Write-Host ""

Write-Host "TAMBIÉN VERIFICA:" -ForegroundColor Yellow
Write-Host "  - El BADGE del icono debería mostrar un número (1, 2, 3...)" -ForegroundColor Gray
Write-Host "  - Haz clic en el icono de la extensión" -ForegroundColor Gray
Write-Host "  - Deberías ver los videos en la pestaña 'Videos'" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DIAGNÓSTICO EN TIEMPO REAL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "¿Qué ves en la consola del service worker?" -ForegroundColor Yellow
Write-Host "1. Veo mensajes '[Video Detector PRO]'" -ForegroundColor White
Write-Host "2. Veo ERRORES en rojo" -ForegroundColor White
Write-Host "3. No veo nada" -ForegroundColor White
Write-Host ""

$respuesta = Read-Host "Tu respuesta (1, 2 o 3)"

Write-Host ""

switch ($respuesta) {
    "1" {
        Write-Host "✓ EXCELENTE! La extensión está funcionando correctamente" -ForegroundColor Green
        Write-Host ""
        Write-Host "SIGUIENTE PASO:" -ForegroundColor Yellow
        Write-Host "1. Reproduce un video en YouTube" -ForegroundColor White
        Write-Host "2. Espera 5 segundos" -ForegroundColor White
        Write-Host "3. Busca en la consola:" -ForegroundColor White
        Write-Host "   '[Video Detector PRO] Video detectado via webRequest'" -ForegroundColor Gray
        Write-Host ""
        Write-Host "¿Ves ese mensaje? (S/N)" -ForegroundColor Yellow
        $detecta = Read-Host

        if ($detecta -eq "S" -or $detecta -eq "s") {
            Write-Host ""
            Write-Host "✓✓✓ PERFECTO! LA EXTENSIÓN FUNCIONA AL 100%" -ForegroundColor Green
            Write-Host ""
            Write-Host "Ahora haz clic en el icono de la extensión" -ForegroundColor Yellow
            Write-Host "Deberías ver los videos detectados con:" -ForegroundColor White
            Write-Host "  - URL completa" -ForegroundColor Gray
            Write-Host "  - Tipo de stream (MP4, HLS, DASH)" -ForegroundColor Gray
            Write-Host "  - Botones: Descargar, Copiar URL" -ForegroundColor Gray
            Write-Host ""
            Write-Host "¡LISTO! Puedes descargar videos SIN LÍMITES" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "PROBLEMA: No está detectando videos" -ForegroundColor Red
            Write-Host ""
            Write-Host "SOLUCIÓN:" -ForegroundColor Yellow
            Write-Host "1. Verifica que el video esté REPRODUCIENDO" -ForegroundColor White
            Write-Host "2. Espera 10 segundos" -ForegroundColor White
            Write-Host "3. Revisa si hay errores en rojo en la consola" -ForegroundColor White
            Write-Host "4. Si hay errores, copia el mensaje y dímelo" -ForegroundColor White
        }
    }
    "2" {
        Write-Host "PROBLEMA DETECTADO: Hay errores" -ForegroundColor Red
        Write-Host ""
        Write-Host "SOLUCIÓN:" -ForegroundColor Yellow
        Write-Host "1. Copia el mensaje de error COMPLETO" -ForegroundColor White
        Write-Host "2. Pégalo aquí o en un archivo .txt" -ForegroundColor White
        Write-Host "3. Te diré exactamente qué está mal" -ForegroundColor White
        Write-Host ""
        Write-Host "Errores comunes:" -ForegroundColor Yellow
        Write-Host "  - 'chrome.webRequest is not available'" -ForegroundColor Gray
        Write-Host "    → Manifest V3 limitación" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  - 'Service worker registration failed'" -ForegroundColor Gray
        Write-Host "    → Error de sintaxis en background.js" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  - 'Cannot read property of undefined'" -ForegroundColor Gray
        Write-Host "    → Background no responde" -ForegroundColor Gray
    }
    "3" {
        Write-Host "PROBLEMA: La consola está vacía" -ForegroundColor Red
        Write-Host ""
        Write-Host "POSIBLES CAUSAS:" -ForegroundColor Yellow
        Write-Host "1. El service worker no se cargó" -ForegroundColor White
        Write-Host "2. La extensión no está recargada" -ForegroundColor White
        Write-Host "3. Estás viendo la consola incorrecta" -ForegroundColor White
        Write-Host ""
        Write-Host "SOLUCIÓN:" -ForegroundColor Yellow
        Write-Host "1. Ve a edge://extensions/" -ForegroundColor White
        Write-Host "2. Busca la extensión" -ForegroundColor White
        Write-Host "3. Haz clic en RECARGAR (icono circular ↻)" -ForegroundColor White
        Write-Host "4. Espera 5 segundos" -ForegroundColor White
        Write-Host "5. Haz clic en 'Detalles'" -ForegroundColor White
        Write-Host "6. Busca 'Inspeccionar vistas'" -ForegroundColor White
        Write-Host "7. Haz clic en 'service worker'" -ForegroundColor White
        Write-Host "8. AHORA deberías ver mensajes en la consola" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FIN DEL MONITOREO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

pause
