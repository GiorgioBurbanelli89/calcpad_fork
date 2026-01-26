# Instalar DLL en Mathcad Prime
$source = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Tests\mathcad_fem.dll"
$dest = "C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions\"

Write-Host "Copiando DLL a Mathcad Prime..."
Copy-Item $source $dest -Force
Write-Host "Listo!"
