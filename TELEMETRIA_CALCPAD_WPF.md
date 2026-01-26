# Sistema de Telemetría en Tiempo Real - Calcpad WPF

## ¿Qué es esto?

Un sistema de monitoreo en tiempo real que registra TODO lo que pasa en Calcpad WPF, similar a cómo se puede ver la salida de Calcpad CLI en la consola.

## Archivos de Telemetría

**Ubicación**: `C:\Users\j-b-j\AppData\Local\Temp\Calcpad\`

**Formato de nombre**: `calcpad_telemetry_YYYYMMDD_HHMMSS.log`

**Ejemplo**: `calcpad_telemetry_20260118_125012.log`

Cada vez que abres Calcpad WPF, se crea un nuevo archivo de telemetría con la fecha y hora.

## ¿Qué se registra?

### 1. Información de Inicio
```
================================================================================
CALCPAD WPF - TELEMETRY SESSION START
Timestamp: 2026-01-18 12:50:12.636
Machine: OCTAVE
User: j-b-j
OS: Microsoft Windows NT 10.0.26200.0
.NET Version: 10.0.2
Working Directory: C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\bin\Debug\net10.0-windows
Telemetry File: C:\Users\j-b-j\AppData\Local\Temp\Calcpad\calcpad_telemetry_20260118_125012.log
================================================================================
```

### 2. Estado de UI Automation
```
[00:00:00.010] [UI_AUTOMATION] Control: InputFrame
  Data: { ControlName: InputFrame, HasAutomationId: True, AutomationId: InputFrame }
[00:00:00.011] [UI_AUTOMATION] Control: OutputFrame
  Data: { ControlName: OutputFrame, HasAutomationId: True, AutomationId: OutputFrame }
[00:00:00.011] [UI_AUTOMATION] Control: WebViewer
  Data: { ControlName: WebViewer, HasAutomationId: True, AutomationId: WebViewer }
```

### 3. Cálculos (F5)
```
[00:00:11.521] [OPERATION_START] CalculateAsync
  Data: { ToWebForm: False }
[00:00:11.521] [CALCULATE] Starting calculation
  Data: { InputCodeLength: 563 }
```

### 4. Procesamiento de Código
```
[00:00:18.291] [PROCESS] ProcessCode completed
  Data: { Success: True, MultilangProcessed: False, HasMacroErrors: False, ProcessedCodeLength: 337 }
```

**Campos importantes:**
- `Success`: ¿Se procesó correctamente?
- `MultilangProcessed`: ¿Se ejecutó código externo (Python, PowerShell, etc.)?
- `HasMacroErrors`: ¿Hubo errores en macros?
- `ProcessedCodeLength`: Tamaño del código procesado

### 5. Actualizaciones del Panel Output
```
[00:00:18.463] [WEBVIEW] Navigation
  Data: { URL: Final HTML result, ContentLength: 30931 }
[00:00:18.463] [OUTPUT] Rendering final HTML to WebViewer
  Data: { HtmlLength: 30931, MultilangProcessed: False }
```

**Aquí puedes ver:**
- Cada vez que el panel Output se actualiza
- Tamaño del HTML que se está renderizando
- Si fue por MultLang o procesamiento normal

### 6. Mensajes de Progreso (MultLang)
```
[00:00:17.750] [PROGRESS] Progress update: Ejecutando Python...
  Data: { HtmlLength: 895 }
[00:00:17.843] [PROGRESS] Progress update: Python completado
  Data: { HtmlLength: 895 }
```

### 7. Métricas de Rendimiento
```
[00:00:18.545] [METRIC] Operation_CalculateAsync: 7023 ms
```

Duración de cada operación en milisegundos.

### 8. Errores
```
[00:00:20.123] [ERROR] [PROCESS]
  Context: ProcessCode failed
  Exception: InvalidOperationException
  Message: Syntax error in line 42
  StackTrace: ...
```

## Cómo Monitorear en Tiempo Real

### Opción 1: Script PowerShell Automático (Recomendado)

```powershell
cd C:\Users\j-b-j\Documents\Calcpad-7.5.7
.\monitor-telemetry.ps1 -Latest
```

Este script:
- Encuentra automáticamente el archivo de telemetría más reciente
- Muestra las últimas 20 líneas
- Monitorea en tiempo real nuevas entradas (como `tail -f`)
- Usa colores para diferentes tipos de eventos

**Colores:**
- 🔴 Rojo: Errores
- 🟡 Amarillo: Advertencias
- 🔵 Azul: Mensajes de progreso
- 🟢 Verde: Inicio/fin de operaciones
- 🟣 Magenta: Métricas de rendimiento
- ⚪ Blanco: Output y WebView
- ⚫ Gris: Otros

**Para detener**: Presiona `Ctrl+C`

### Opción 2: Ver archivo específico

```powershell
.\monitor-telemetry.ps1 -FilePath "C:\Users\j-b-j\AppData\Local\Temp\Calcpad\calcpad_telemetry_20260118_125012.log"
```

### Opción 3: Leer archivo directamente

```powershell
# Ver todo el archivo
cat "C:\Users\j-b-j\AppData\Local\Temp\Calcpad\calcpad_telemetry_*.log" | tail -50

# Monitorear en tiempo real (PowerShell nativo)
Get-Content "C:\Users\j-b-j\AppData\Local\Temp\Calcpad\calcpad_telemetry_*.log" -Tail 20 -Wait
```

### Opción 4: Abrir en editor de texto

```powershell
notepad "C:\Users\j-b-j\AppData\Local\Temp\Calcpad\calcpad_telemetry_*.log"
```

## Casos de Uso

### Caso 1: Debugging del Panel Output

**Problema**: El panel Output no se actualiza cuando ejecuto código MultLang

**Solución**: Monitorea la telemetría en tiempo real

1. Abre dos ventanas:
   - Ventana 1: Calcpad WPF
   - Ventana 2: PowerShell con `.\monitor-telemetry.ps1 -Latest`

2. En Calcpad WPF, presiona F5

3. En PowerShell, verás:
   ```
   [OPERATION_START] CalculateAsync
   [CALCULATE] Starting calculation
   [PROGRESS] Progress update: Ejecutando Python...
   [PROCESS] ProcessCode completed
   [WEBVIEW] Navigation - Final HTML result
   [OUTPUT] Rendering final HTML to WebViewer
   [OPERATION_END] CalculateAsync (Duration: 7023 ms)
   ```

4. Si NO ves `[WEBVIEW] Navigation`, significa que el Output no se está actualizando
5. Si ves `[ERROR]`, ahí está el problema

### Caso 2: Verificar si MultLang se está ejecutando

Busca en el log:
```
[PROCESS] ProcessCode completed
  Data: { ... MultilangProcessed: True ... }
```

- `MultilangProcessed: True` = Código externo se ejecutó
- `MultilangProcessed: False` = Solo procesamiento Calcpad normal

### Caso 3: Medir rendimiento

```powershell
cat telemetry.log | grep "\[METRIC\]"
```

Output:
```
[METRIC] Operation_CalculateAsync: 7023 ms
[METRIC] Operation_CalculateAsync: 352 ms
```

### Caso 4: Encontrar errores

```powershell
cat telemetry.log | grep "\[ERROR\]" -A 5
```

Muestra todos los errores con 5 líneas de contexto.

## Integración con Claude Code

Cuando Claude Code te ayuda con Calcpad WPF, puede pedirte:

```
"Por favor corre esto y pega el log de telemetría:"
.\monitor-telemetry.ps1 -Latest
```

Luego presionas F5 en Calcpad WPF, y Claude verá EXACTAMENTE qué está pasando internamente.

## Ejemplo de Sesión Completa

```
=== MONITORING CALCPAD WPF TELEMETRY ===
File: C:\Users\j-b-j\AppData\Local\Temp\Calcpad\calcpad_telemetry_20260118_125012.log

--- ÚLTIMAS 20 LÍNEAS ---

[00:00:00.002] [STARTUP] MainWindow constructor started
[00:00:00.010] [UI_AUTOMATION] Control: InputFrame (HasAutomationId: True)
[00:00:00.011] [UI_AUTOMATION] Control: OutputFrame (HasAutomationId: True)

--- LIVE UPDATES ---

[00:00:11.521] [OPERATION_START] CalculateAsync
[00:00:11.521] [CALCULATE] Starting calculation (InputCodeLength: 563)
[00:00:11.522] [WEBVIEW] Navigation - Initial Calcpad comments (ContentLength: 490)
[00:00:17.750] [PROGRESS] Progress update: Ejecutando Python...
[00:00:17.843] [PROGRESS] Progress update: Python completado
[00:00:18.291] [PROCESS] ProcessCode completed (Success: True, MultilangProcessed: True)
[00:00:18.463] [WEBVIEW] Navigation - Final HTML result (ContentLength: 30931)
[00:00:18.463] [OUTPUT] Rendering final HTML to WebViewer
[00:00:18.545] [OPERATION_END] CalculateAsync (Duration: 7023 ms)
[00:00:18.545] [METRIC] Operation_CalculateAsync: 7023 ms
```

## Configuración Avanzada

### Deshabilitar Telemetría

En `MainWindow.xaml.cs`, después de la línea:
```csharp
CalcpadTelemetry.LogEvent("STARTUP", "MainWindow constructor started");
```

Agrega:
```csharp
CalcpadTelemetry.Disable();
```

### Habilitar solo en Debug

En `CalcpadTelemetry.cs`, cambia el constructor:
```csharp
static CalcpadTelemetry()
{
    #if DEBUG
        _isEnabled = true;
    #else
        _isEnabled = false;
    #endif

    // ...
}
```

## Archivo de Código

- **Clase de telemetría**: `Calcpad.Wpf\CalcpadTelemetry.cs`
- **Integración en MainWindow**: `Calcpad.Wpf\MainWindow.xaml.cs`
- **Script de monitoreo**: `monitor-telemetry.ps1`

## Resumen

✅ **Antes**: No podías ver qué pasaba en Calcpad WPF
✅ **Ahora**: Todo se registra en un log que puedes monitorear en tiempo real
✅ **Beneficio**: Debugging inmediato, similar a Calcpad CLI

**Para empezar ahora mismo:**
```powershell
cd C:\Users\j-b-j\Documents\Calcpad-7.5.7
.\monitor-telemetry.ps1 -Latest
```

Luego abre Calcpad WPF y observa la magia. 🎉
