# Monitor del log en tiempo real
$logPath = "C:\Users\j-b-j\Desktop\calcpad_debug.log"
$lastSize = 0

Write-Output "========================================="
Write-Output "MONITOREANDO LOG: $logPath"
Write-Output "========================================="
Write-Output ""
Write-Output "Esperando eventos... (Ctrl+C para detener)"
Write-Output ""

# Verificar si el archivo existe
if (-not (Test-Path $logPath)) {
    Write-Output "ADVERTENCIA: El archivo de log no existe todavia"
    Write-Output "Se creara cuando hagas la primera accion en Calcpad"
    Write-Output ""
}

while ($true) {
    if (Test-Path $logPath) {
        $currentSize = (Get-Item $logPath).Length

        if ($currentSize -gt $lastSize) {
            # Leer solo las líneas nuevas
            $newContent = Get-Content $logPath -Encoding UTF8 -Tail 100

            # Mostrar las últimas 50 líneas
            $newContent | Select-Object -Last 50

            $lastSize = $currentSize
        }
    }

    Start-Sleep -Milliseconds 500
}
