# Presiona F5 en Calcpad para calcular

Add-Type -AssemblyName System.Windows.Forms

# Buscar Calcpad
$calcpad = Get-Process | Where-Object { $_.ProcessName -eq "Calcpad" }

if (-not $calcpad) {
    Write-Host "ERROR: Calcpad no esta ejecutandose"
    exit 1
}

Write-Host "Calcpad encontrado, enviando F5..."

# Traer ventana al frente
$null = [System.Reflection.Assembly]::LoadWithPartialName("Microsoft.VisualBasic")
[Microsoft.VisualBasic.Interaction]::AppActivate($calcpad.Id)
Start-Sleep -Milliseconds 500

# Enviar F5
[System.Windows.Forms.SendKeys]::SendWait("{F5}")

Write-Host "F5 enviado, esperando 3 segundos..."
Start-Sleep -Seconds 3

Write-Host "Listo, ejecuta monitor_calcpad_simple.ps1 para ver resultados"
