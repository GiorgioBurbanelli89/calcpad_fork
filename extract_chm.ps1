# Extraer contenido del archivo CHM
$chmPath = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\CSI_OAPI_Documentation.chm"
$outputPath = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_API_Info.txt"

# Usar hh.exe para ver el contenido
$tempHtml = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\temp_chm.html"

# Intentar abrir el CHM y extraer la tabla de contenidos
try {
    # Usar objeto COM para leer el CHM
    $shell = New-Object -ComObject Shell.Application

    Write-Host "Archivo CHM encontrado: $chmPath"
    Write-Host "Este archivo contiene la documentaci�n de la API de SAP2000 OAPI"
    Write-Host ""
    Write-Host "Para ver el contenido completo, ejecuta:"
    Write-Host "hh.exe `"$chmPath`""

    # Listar propiedades del archivo
    $fileInfo = Get-Item $chmPath
    Write-Host ""
    Write-Host "Tama�o: $($fileInfo.Length) bytes"
    Write-Host "Fecha de modificaci�n: $($fileInfo.LastWriteTime)"

} catch {
    Write-Host "Error: $_"
}
