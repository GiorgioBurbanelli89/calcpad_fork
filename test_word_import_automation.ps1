# Script de automatización para probar importación de Word a Calcpad
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$docxFile = "C:\Users\j-b-j\Downloads\calculo_estructural_escalera_metalica.docx"
$outputFile = "word_import_output.html"

Write-Host "======================================"
Write-Host "Test de importación Word -> Calcpad"
Write-Host "======================================"
Write-Host "Documento: $docxFile"
Write-Host ""

# Esperar a que Calcpad esté corriendo
Start-Sleep -Seconds 2

# Usar UIAutomation para encontrar la ventana de Calcpad
$automation = [System.Windows.Automation.AutomationElement]
$condition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::NameProperty,
    "Calcpad"
)

Write-Host "Buscando ventana de Calcpad..."
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$calcpadWindow = $desktop.FindFirst(
    [System.Windows.Automation.TreeScope]::Children,
    $condition
)

if ($calcpadWindow -eq $null) {
    Write-Host "ERROR: No se encontró la ventana de Calcpad" -ForegroundColor Red
    exit 1
}

Write-Host "Ventana encontrada: $($calcpadWindow.Current.Name)" -ForegroundColor Green

# Buscar el botón de Word
Write-Host "`nBuscando botón de Word..."

# Enviar Ctrl+O para abrir archivo
Write-Host "Simulando Ctrl+O para abrir archivo..."
[System.Windows.Forms.SendKeys]::SendWait("^o")
Start-Sleep -Milliseconds 500

# Escribir la ruta del archivo
[System.Windows.Forms.SendKeys]::SendWait($docxFile)
Start-Sleep -Milliseconds 500

# Presionar Enter
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Seconds 2

Write-Host "Archivo abierto, esperando procesamiento..."
Start-Sleep -Seconds 3

# Ahora vamos a leer directamente el archivo generado usando el CLI
Write-Host "`n======================================"
Write-Host "Probando con Calcpad CLI directamente"
Write-Host "======================================"

# Primero, convertir usando DocxReader
$dllPath = "Calcpad.Wpf\bin\Debug\net10.0-windows\net10.0\Calcpad.OpenXml.dll"
if (Test-Path $dllPath) {
    Write-Host "Cargando DocxReader..."

    # Crear un script de C# temporal para ejecutar
    $csCode = @"
using System;
using System.IO;
using System.Reflection;

class TestDocx {
    static void Main() {
        try {
            var dllPath = @"$dllPath";
            var assembly = Assembly.LoadFrom(dllPath);
            var readerType = assembly.GetType("Calcpad.OpenXml.DocxReader");

            if (readerType == null) {
                Console.WriteLine("ERROR: No se encontró DocxReader");
                return;
            }

            var reader = Activator.CreateInstance(readerType);
            var method = readerType.GetMethod("ReadToHtml");

            if (method == null) {
                Console.WriteLine("ERROR: No se encontró ReadToHtml");
                return;
            }

            var docxPath = @"$docxFile";
            Console.WriteLine("Convirtiendo: " + docxPath);

            var html = method.Invoke(reader, new object[] { docxPath });

            Console.WriteLine("\n========== OUTPUT HTML ==========");
            Console.WriteLine(html);
            Console.WriteLine("\n========== FIN OUTPUT ==========");

            File.WriteAllText(@"$outputFile", html.ToString());
            Console.WriteLine("\nGuardado en: $outputFile");
        }
        catch (Exception ex) {
            Console.WriteLine("ERROR: " + ex.Message);
            Console.WriteLine(ex.StackTrace);
        }
    }
}
"@

    # Guardar y compilar
    $csFile = "test_docx_temp.cs"
    $csCode | Out-File -FilePath $csFile -Encoding UTF8

    Write-Host "Compilando script de prueba..."
    $exeFile = "test_docx_temp.exe"

    # Compilar con csc
    & "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /out:$exeFile $csFile /r:$dllPath 2>&1 | Out-Null

    if (Test-Path $exeFile) {
        Write-Host "Ejecutando conversor..." -ForegroundColor Yellow
        & ".\$exeFile"
    } else {
        Write-Host "No se pudo compilar el script de prueba"
    }

    # Limpiar archivos temporales
    Remove-Item -Path $csFile -ErrorAction SilentlyContinue
    Remove-Item -Path $exeFile -ErrorAction SilentlyContinue
}

Write-Host "`n======================================"
Write-Host "Revisando output en navegador..."
Write-Host "======================================"

if (Test-Path $outputFile) {
    Start-Process $outputFile
    Write-Host "Output abierto en navegador" -ForegroundColor Green
} else {
    Write-Host "No se generó archivo de output" -ForegroundColor Red
}
