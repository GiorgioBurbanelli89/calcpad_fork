# INSTRUCCIONES - Testing UI Automation en Calcpad WPF

## Calcpad WPF Compilado y Ejecutándose

✅ **Compilación exitosa**
```
Calcpad.Wpf -> C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\bin\Debug\net10.0-windows\Calcpad.dll
```

✅ **Ejecutable:**
```
C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\bin\Debug\net10.0-windows\Calcpad.exe
```

## Cómo Verificar el Problema con UI Automation

### Opción 1: Usar Inspect.exe (Windows SDK)

**1. Buscar Inspect.exe:**
```powershell
# Ubicaciones comunes:
C:\Program Files (x86)\Windows Kits\10\bin\10.0.XXXXX.0\x64\inspect.exe
C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\inspect.exe
```

**2. Ejecutar Inspect.exe:**
```powershell
# Desde PowerShell:
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\inspect.exe"
```

**3. Pasos para verificar:**
1. Abre Calcpad WPF
2. En Inspect.exe, hacer clic en el ícono "Highlight" (primer botón)
3. Mover el mouse sobre el panel "Code" en Calcpad WPF
4. Verificar en Inspect.exe:
   - ¿Aparece `AutomationId`?
   - ¿Aparece `Name`?
   - ¿Qué `ControlType` tiene?

**4. Repetir para el panel "Output"**

### Opción 2: Usar PowerShell con UI Automation

**Crear script: `test-calcpad-ui.ps1`**
```powershell
# Cargar ensamblado de UI Automation
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

# Esperar a que Calcpad esté abierto
Write-Host "Buscando ventana de Calcpad..." -ForegroundColor Cyan

# Buscar ventana principal
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$calcpadCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::NameProperty,
    "Calcpad VM 7.5.8"
)

$mainWindow = $desktop.FindFirst(
    [System.Windows.Automation.TreeScope]::Children,
    $calcpadCondition
)

if ($mainWindow) {
    Write-Host "✅ Ventana encontrada: $($mainWindow.Current.Name)" -ForegroundColor Green

    # Buscar todos los GroupBox
    $groupBoxCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Group
    )

    $groupBoxes = $mainWindow.FindAll(
        [System.Windows.Automation.TreeScope]::Descendants,
        $groupBoxCondition
    )

    Write-Host "`n=== GroupBox encontrados ===" -ForegroundColor Yellow
    foreach ($gb in $groupBoxes) {
        $name = $gb.Current.Name
        $automationId = $gb.Current.AutomationId
        $helpText = $gb.Current.HelpText

        Write-Host "  Name: '$name'" -ForegroundColor White
        Write-Host "  AutomationId: '$automationId'" -ForegroundColor $(if($automationId){"Green"}else{"Red"})
        Write-Host "  HelpText: '$helpText'" -ForegroundColor Gray
        Write-Host ""
    }

    # Buscar específicamente por AutomationId
    Write-Host "=== Buscar por AutomationId ===" -ForegroundColor Yellow

    $inputFrameCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
        "InputFrame"
    )
    $inputFrame = $mainWindow.FindFirst(
        [System.Windows.Automation.TreeScope]::Descendants,
        $inputFrameCondition
    )

    if ($inputFrame) {
        Write-Host "✅ InputFrame encontrado con AutomationId" -ForegroundColor Green
    } else {
        Write-Host "❌ InputFrame NO encontrado con AutomationId" -ForegroundColor Red
    }

    $outputFrameCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
        "OutputFrame"
    )
    $outputFrame = $mainWindow.FindFirst(
        [System.Windows.Automation.TreeScope]::Descendants,
        $outputFrameCondition
    )

    if ($outputFrame) {
        Write-Host "✅ OutputFrame encontrado con AutomationId" -ForegroundColor Green
    } else {
        Write-Host "❌ OutputFrame NO encontrado con AutomationId" -ForegroundColor Red
    }

} else {
    Write-Host "❌ Ventana de Calcpad no encontrada" -ForegroundColor Red
    Write-Host "Asegúrate de que Calcpad WPF esté abierto" -ForegroundColor Yellow
}
```

**Ejecutar:**
```powershell
cd C:\Users\j-b-j\Documents\Calcpad-7.5.7
.\test-calcpad-ui.ps1
```

### Opción 3: Ver logs de debug

**Durante la ejecución, ver logs:**
```powershell
Get-Content "C:\Users\j-b-j\AppData\Local\Temp\calcpad-debug.txt" -Tail 50 -Wait
```

## Qué Esperar Ver

### ANTES de agregar AutomationProperties:

```
=== GroupBox encontrados ===
  Name: 'Code'
  AutomationId: ''           ← VACÍO
  HelpText: ''

  Name: 'Output'
  AutomationId: ''           ← VACÍO
  HelpText: ''

❌ InputFrame NO encontrado con AutomationId
❌ OutputFrame NO encontrado con AutomationId
```

### DESPUÉS de agregar AutomationProperties:

```
=== GroupBox encontrados ===
  Name: 'Code Editor'
  AutomationId: 'InputFrame'  ← PRESENTE
  HelpText: 'Calcpad code editor with syntax highlighting'

  Name: 'Output Viewer'
  AutomationId: 'OutputFrame' ← PRESENTE
  HelpText: 'Calculation results and rendered output'

✅ InputFrame encontrado con AutomationId
✅ OutputFrame encontrado con AutomationId
```

## Prueba de MultLang

### 1. Abre test_multilang.cpd

En Calcpad WPF:
1. File → Open
2. Seleccionar: `C:\Users\j-b-j\Documents\Calcpad-7.5.7\test_multilang.cpd`

### 2. Observa los paneles

**Panel Code (izquierda) debería mostrar:**
```
"Prueba de MultLangCode con Calcpad
'Calculo en Calcpad:
a = 5
b = 10
c = a + b

@{python}
import math
...
@{end python}
```

**Panel Output (derecha) al presionar F5:**
```
[Fase 1] ⏳ Ejecutando Python...
[Fase 2] Python: 5 + 10 = 15
         Raiz cuadrada de 15: 3.8730
[Fase 3] ⏳ Ejecutando PowerShell...
[Fase 4] PowerShell: 5 + 10 = 15
         Fecha actual: 2026-01-18
[Fase 5] Cálculos de Calcpad:
         c = 15
         d = 30
```

### 3. Verificar con Inspect.exe durante ejecución

Mientras Calcpad está procesando:
1. Inspect.exe → Highlight activado
2. Mover mouse sobre panel Output
3. Verificar:
   - ¿El contenido está cambiando?
   - ¿Inspect.exe detecta los cambios?
   - ¿Hay eventos de `LiveRegionChanged`?

## Problemas Conocidos y Fixes

### Problema 1: AutomationId vacío

**Síntoma:** Script de PowerShell no encuentra InputFrame/OutputFrame

**Fix:** Editar MainWindow.xaml y agregar AutomationProperties (ver ANALISIS_UI_CODE_OUTPUT.md Solución 1)

### Problema 2: Cambios dinámicos no detectados

**Síntoma:** Panel Output se actualiza pero Inspect.exe no lo detecta

**Fix:** Agregar `AutomationProperties.LiveSetting="Polite"` al OutputFrame

### Problema 3: WebViewer no accesible

**Síntoma:** No se puede acceder al contenido HTML del WebView2

**Fix:** Agregar AutomationProperties al WebView2 mismo

## Siguiente Paso

1. ✅ Calcpad WPF compilado y ejecutado
2. ⏳ Ejecutar test-calcpad-ui.ps1 para verificar estado actual
3. ⏳ Editar MainWindow.xaml para agregar AutomationProperties
4. ⏳ Recompilar y probar nuevamente
5. ⏳ Verificar que Inspect.exe ahora detecta los controles

**¿Quieres que proceda con el Paso 2 o prefieres probar manualmente primero?**
