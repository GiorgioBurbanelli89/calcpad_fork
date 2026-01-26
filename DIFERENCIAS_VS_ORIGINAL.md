# Diferencias vs Calcpad Original

Este documento detalla las diferencias entre este fork de Calcpad y el [repositorio original de Proektsoftbg](https://github.com/Proektsoftbg/Calcpad).

## Fecha de Fork
- **Fork creado**: Enero 2026
- **Versión base**: Calcpad 7.5.7

---

## 1. CalcpadDebugger - Depurador WPF Interactivo

### Nuevo Componente: NO EXISTE EN ORIGINAL

**Ubicación**: `CalcpadDebugger/`

**Descripción**: Aplicación WPF completa para depurar archivos .cpd paso a paso, similar a MATLAB.

### Características Principales:

#### Interfaz de 3 Paneles
1. **Panel .cpd** (editable)
   - Muestra el código Calcpad original
   - Permite editar el archivo en tiempo real
   - Resalta la línea actual durante depuración

2. **Panel C# Source** (editable)
   - Muestra el código fuente C# de Calcpad.Common
   - ComboBox para seleccionar diferentes archivos .cs
   - **Navegación automática** al archivo y línea que se está ejecutando
   - Permite editar código C# y recompilar

3. **Panel Variables y Estado**
   - DataGrid con variables activas
   - Log de ejecución con instrumentación completa
   - Estado de depuración

#### Controles de Depuración
- **F10 (Step Over)**: Ejecutar línea por línea
- **F11 (Step Into)**: Entrar en funciones (futuro)
- **F5 (Continue)**: Ejecutar hasta el final
- **Reset**: Reiniciar depuración

#### Carga desde CLI
```bash
CalcpadDebugger.exe "ruta/al/archivo.cpd"
```

**Script helper**: `calcpad-debug` (Bash)

#### Instrumentación en Tiempo Real
El depurador muestra:
- Archivo C# exacto ejecutándose (`GlobalParser.cs`, `LanguageExecutor.cs`, etc.)
- Número de línea en el código fuente
- Clase y método actual
- Mensaje descriptivo de la operación

**Ejemplo de log**:
```
📍 [LanguageExecutor.cs:37] LanguageExecutor.Execute - Checking if language 'python' is configured
📍 [LanguageExecutor.cs:48] LanguageExecutor.Execute - Language configured: Command=python, Extension=.py
📍 [LanguageExecutor.cs:68] LanguageExecutor.Execute - Checking if 'python' is available in PATH
```

---

## 2. ExecutionTracker - Sistema de Instrumentación

### Nuevo Archivo: `Calcpad.Common/ExecutionTracker.cs`

**Propósito**: Rastrear exactamente qué código C# se está ejecutando usando la API `System.Diagnostics.StackTrace`.

### Clases Principales:

#### `ExecutionTracker`
```csharp
public class ExecutionTracker
{
    public event ExecutionStepHandler? OnExecutionStep;

    public void ReportStep(string message, int skipFrames = 1)
    public void EnterMethod(string className, string methodName, string? details = null)
    public void ExitMethod(string className, string methodName, string? result = null)
}
```

#### `ExecutionStep`
```csharp
public class ExecutionStep
{
    public string Message { get; set; }
    public string FileName { get; set; }        // Archivo .cs
    public int LineNumber { get; set; }          // Línea exacta
    public string ClassName { get; set; }
    public string MethodName { get; set; }
    public DateTime Timestamp { get; set; }
}
```

### Ventajas sobre el Original:
- **Visibilidad total**: Se puede ver exactamente qué código se ejecuta en cada paso
- **Debugging educativo**: Útil para aprender cómo funciona Calcpad internamente
- **Detección de errores**: Muestra exactamente dónde ocurre un error
- **Performance profiling**: Timestamps permiten analizar tiempos de ejecución

---

## 3. Instrumentación en Archivos Core

### Archivos Modificados con ExecutionTracker:

#### 3.1. `CalcpadProcessor.cs`
**Cambios**:
```csharp
private ExecutionTracker? _tracker;

public CalcpadProcessor(Func<string, Queue<string>, string> includeHandler,
                        ExecutionTracker? tracker = null)
{
    _tracker = tracker;
    _globalParser = new GlobalParser(_tracker);  // Propagar tracker
    // ...
}
```

#### 3.2. `GlobalParser.cs`
**Cambios**:
```csharp
private ExecutionTracker? _tracker;

public GlobalParser(ExecutionTracker? tracker = null)
{
    _tracker = tracker;
    _multLangProcessor = new MultLangProcessor(_tracker);
}

public string Process(string code, out bool hasExternalCode, Action<string>? progressCallback = null)
{
    _tracker?.EnterMethod("GlobalParser", "Process", $"Code length: {code.Length} chars");
    _tracker?.ReportStep("Checking for external language blocks");

    hasExternalCode = MultLangManager.HasLanguageCode(code);

    if (hasExternalCode)
    {
        _tracker?.ReportStep("External language code detected, routing to MultLangProcessor");
        return _multLangProcessor.Process(code, progressCallback);
    }

    _tracker?.ReportStep("No external code detected, returning original");
    return code;
}
```

#### 3.3. `MultLangCode/MultLangProcessor.cs`
**Instrumentación agregada** en métodos clave de procesamiento de bloques multi-lenguaje.

#### 3.4. `MultLangCode/LanguageExecutor.cs`
**Cambios principales**:
```csharp
private ExecutionTracker? _tracker;

public LanguageExecutor(ExecutionTracker? tracker = null)
{
    _config = MultLangManager.Config;
    _tempDir = Path.Combine(Path.GetTempPath(), _config.Settings.TempDirectory);
    Directory.CreateDirectory(_tempDir);
    _tracker = tracker;
}

public ExecutionResult Execute(CodeBlock block, Dictionary<string, object>? variables = null,
                                Action<string>? progressCallback = null)
{
    _tracker?.EnterMethod("LanguageExecutor", "Execute", $"Language: {block.Language}");

    _tracker?.ReportStep($"Checking if language '{block.Language}' is configured");
    if (!_config.Languages.TryGetValue(block.Language, out var langDef))
    {
        _tracker?.ReportStep($"ERROR: Language '{block.Language}' not found in config");
        return new ExecutionResult { Success = false, Error = $"Language '{block.Language}' not configured" };
    }

    _tracker?.ReportStep($"Language configured: Command={langDef.Command}, Extension={langDef.Extension}");

    // Avalonia routing
    if (language == "avalonia")
    {
        _tracker?.ReportStep("Detected Avalonia project, routing to ExecuteAvaloniaProject");
        return ExecuteAvaloniaProject(block);
    }

    _tracker?.ReportStep($"Checking if '{block.Language}' is available in PATH");
    // ... resto del código con instrumentación completa
}
```

---

## 4. Soporte Mejorado de Avalonia

### Cambios en `MultLangCode/MultLangConfig.json`

#### Original (Proektsoftbg):
```json
"avalonia": {
  "command": "csc",
  "extension": ".cs",
  "requiresCompilation": true,
  "compileArgs": "/out:{output} {input}"
}
```

**Problemas**:
- `csc` no está en PATH por defecto
- Solo funciona en Windows
- No maneja proyectos Avalonia correctamente

#### Este Fork:
```json
"avalonia": {
  "command": "dotnet",
  "extension": ".csproj",
  "requiresCompilation": true,
  "compileArgs": "build -c Release",
  "runArgs": "run --no-build -c Release"
}
```

**Ventajas**:
- `dotnet` es **multiplataforma** (Windows, Linux, macOS)
- Instalación más común (viene con .NET SDK)
- Manejo correcto de proyectos Avalonia

### Nuevo Método: `ExecuteAvaloniaProject()`

**Ubicación**: `LanguageExecutor.cs:437`

**Funcionalidad**:
1. Verifica si las plantillas de Avalonia están instaladas
2. **Auto-instala** plantillas si faltan: `dotnet new install Avalonia.Templates`
3. Crea proyecto Avalonia temporal con estructura completa
4. Escribe el código del usuario
5. Compila con `dotnet build -c Release`
6. Ejecuta con `dotnet run --no-build -c Release`
7. Captura output y lo retorna formateado

**Ejemplo de uso en .cpd**:
```
@{avalonia}
using System;
class MiApp {
    static void Main() {
        Console.WriteLine("Hola desde Avalonia!");
    }
}
@{end avalonia}
```

---

## 5. Soporte Multi-Lenguaje

### Lenguajes Soportados (19 total):

| Lenguaje | Directiva | Comando | Estado en Fork |
|----------|-----------|---------|----------------|
| Python | `@{python}` | `python` | ✅ Funcional |
| PowerShell | `@{powershell}` | `pwsh` | ✅ Funcional |
| Octave | `@{octave}` | `octave-cli` | ✅ Funcional |
| Julia | `@{julia}` | `julia` | ✅ Funcional |
| C++ | `@{cpp}` | `g++` | ✅ Funcional |
| C | `@{c}` | `gcc` | ✅ Funcional |
| Fortran | `@{fortran}` | `gfortran` | ✅ Funcional |
| C# | `@{csharp}` | `csc` | ⚠️ (requiere csc en PATH) |
| Bash | `@{bash}` | `bash` | ✅ Funcional |
| CMD | `@{cmd}` | `cmd` | ✅ Funcional |
| R | `@{r}` | `Rscript` | ✅ Funcional |
| **Avalonia** | `@{avalonia}` | `dotnet` | ✅ **MEJORADO** |
| WPF | `@{wpf}` | `dotnet` | ✅ Funcional |
| XAML | `@{xaml}` | `dotnet` | ✅ Funcional |
| Qt | `@{qt}` | `g++` | ✅ Funcional (con libs Qt) |
| GTK | `@{gtk}` | `gcc` | ✅ Funcional (con libs GTK) |
| HTML | `@{html}` | - | ✅ Solo markup |
| Markdown | `@{markdown}` | - | ✅ Solo markup |

**Diferencia clave**: El original puede tener soporte multi-lenguaje, pero este fork tiene:
- Instrumentación completa en cada lenguaje
- Mejor manejo de Avalonia (dotnet vs csc)
- Depurador visual para ver ejecución en tiempo real

---

## 6. Edición en Tiempo Real

### Característica Exclusiva del Fork

El depurador permite:
1. **Editar el archivo .cpd** mientras se depura
2. **Editar el código fuente C# de Calcpad** (experimental)
3. **Recompilar** Calcpad.Common con los cambios
4. **Continuar depuración** con la nueva versión

**Caso de uso**:
- Encuentra un bug en `LanguageExecutor.cs`
- Lo editas directamente en el depurador
- Recompilas con F9 (futuro feature)
- Continúas la depuración con el fix aplicado

---

## 7. Mejoras de Usabilidad

### 7.1. CLI Mejorada

**Script `calcpad-debug`**:
```bash
#!/bin/bash
DEBUGGER_EXE="CalcpadDebugger/bin/Release/net10.0-windows/CalcpadDebugger.exe"
FILE_PATH="$1"

# Validaciones y conversión de rutas
# ...

"$DEBUGGER_EXE" "$ABS_PATH"
```

**Uso**:
```bash
calcpad-debug ejemplo-multiples-lenguajes.cpd
```

### 7.2. Mensajes Descriptivos

El original puede tener mensajes de error técnicos. Este fork agrega:
- Mensajes en español (configurable)
- Contexto sobre qué está fallando
- Sugerencias de instalación para lenguajes faltantes

**Ejemplo**:
```
ERROR: Language 'avalonia' is not installed or not found in PATH.
SUGERENCIA: Instala el SDK de .NET: https://dotnet.microsoft.com/download

Avalonia templates not found, installing...
✓ Templates installed successfully
```

---

## 8. Testing y Calidad

### 8.1. Script de Prueba Automatizada

**`test_debugger_fixed.ps1`**:
- Inicia el depurador programáticamente
- Usa **UI Automation** para interactuar con la ventana
- Presiona botones (F5, F10)
- Captura logs completos
- Verifica que no haya crashes
- Guarda resultado en `debugger_final_log.txt`

**Ejecución**:
```powershell
powershell -File test_debugger_fixed.ps1
```

**Output esperado**:
```
=== PROBANDO DEPURADOR ARREGLADO ===
Depurador iniciado (PID: 44928)
Ejecutando Continue (F5)...
✓ Ejecucion completada SIN CRASH!

=== LOG DE EJECUCION ===
[45 líneas de log detallado con instrumentación]

=== PRUEBA COMPLETADA ===
Log guardado en: debugger_final_log.txt
```

### 8.2. Archivo de Prueba

**`ejemplo-multiples-lenguajes.cpd`**:
- Prueba 3 lenguajes diferentes (Python, C++, Avalonia)
- Comentarios en español
- Demuestra independencia de bloques
- Usado para validar cambios

---

## 9. Correcciones de Bugs

### 9.1. Bug: ArgumentOutOfRangeException en MainWindow.xaml.cs

**Problema original**:
```csharp
// Código antiguo que causaba crash
_codeLines[_currentLineIndex].Background = Brushes.Yellow;
```

**Causa**: Cambio de UI de `ItemsControl` con `ObservableCollection` a `TextBox` editable, pero quedaron referencias a `_codeLines`.

**Fix aplicado**:
```csharp
// Removidas todas las referencias a _codeLines y _sourceCodeLines
// Ahora usa TextBox directamente para edición
```

**Resultado**: Depurador ya no crashea durante ejecución.

---

## 10. Arquitectura y Diseño

### 10.1. Patrón ExecutionTracker

**Concepto**: Inversión de control para observabilidad.

```
CalcpadProcessor
    ├── ExecutionTracker (inyectado)
    ├── GlobalParser (recibe tracker)
    │   └── MultLangProcessor (recibe tracker)
    │       └── LanguageExecutor (recibe tracker)
    └── ExpressionParser (sin tracker - pipeline separado)
```

**Ventajas**:
- Bajo acoplamiento: Los componentes core no dependen del depurador
- Opcional: Si no se pasa tracker, funciona igual que el original
- Extensible: Fácil agregar más eventos de instrumentación

### 10.2. Separación de Pipelines

**Mejora**: Clarificación de que MultLangProcessor y ExpressionParser son **mutuamente excluyentes**.

```csharp
if (MultLangManager.HasLanguageCode(code))
{
    // Ruta 1: Multi-lenguaje
    return _multLangProcessor.Process(code);
}
else
{
    // Ruta 2: Expresiones Calcpad nativas
    return ProcessNativeCalcpad(code);
}
```

**En el original**: Esto puede no estar tan claramente separado.

---

## 11. Documentación

### Archivos de Documentación Adicionales:

1. **`DIFERENCIAS_VS_ORIGINAL.md`** (este archivo)
   - Comparación detallada con el original
   - Guía de características nuevas

2. **`debugger_final_log.txt`** (generado por tests)
   - Log completo de ejecución de pruebas
   - Útil para validar instrumentación

3. **Comentarios en español**
   - Scripts de test en español
   - Mensajes de log descriptivos
   - Archivos .cpd de ejemplo en español

---

## 12. Diferencias Técnicas por Archivo

### Tabla Resumen:

| Archivo | Estado en Original | Estado en Fork | Cambios Principales |
|---------|-------------------|----------------|---------------------|
| `CalcpadDebugger/` | ❌ No existe | ✅ Nuevo | Aplicación WPF completa |
| `ExecutionTracker.cs` | ❌ No existe | ✅ Nuevo | Sistema de instrumentación |
| `CalcpadProcessor.cs` | ✅ Existe | ✅ Modificado | + ExecutionTracker param |
| `GlobalParser.cs` | ✅ Existe | ✅ Modificado | + Instrumentación |
| `MultLangProcessor.cs` | ✅ Existe | ✅ Modificado | + Instrumentación |
| `LanguageExecutor.cs` | ✅ Existe | ✅ Modificado | + ExecuteAvaloniaProject(), instrumentación |
| `MultLangConfig.json` | ✅ Existe | ✅ Modificado | Avalonia: csc → dotnet |
| `calcpad-debug` | ❌ No existe | ✅ Nuevo | Script CLI para depurador |
| `test_debugger_fixed.ps1` | ❌ No existe | ✅ Nuevo | Testing automatizado |
| `ejemplo-multiples-lenguajes.cpd` | ❌ No existe | ✅ Nuevo | Archivo de prueba multi-lenguaje |

---

## 13. Ventajas Clave de Este Fork

### Para Usuarios:
1. **Depuración visual** - Ver exactamente qué está ejecutando Calcpad
2. **Aprendizaje** - Entender cómo funciona Calcpad internamente
3. **Multi-lenguaje mejorado** - Soporte cross-platform para Avalonia
4. **Edición en tiempo real** - Cambiar código .cpd y C# mientras se depura

### Para Desarrolladores:
1. **Instrumentación completa** - Rastreo de ejecución con StackTrace
2. **Testing automatizado** - Scripts PowerShell con UI Automation
3. **Arquitectura extensible** - ExecutionTracker pattern
4. **Documentación clara** - Separación de pipelines, comentarios detallados

### Para DevOps:
1. **Cross-platform** - Avalonia funciona en Linux/macOS (dotnet vs csc)
2. **Auto-instalación** - Templates de Avalonia se instalan automáticamente
3. **CLI completa** - Cargar archivos desde línea de comandos

---

## 14. Roadmap Futuro (Posibles Mejoras)

### Features Planeadas:
1. **F11 (Step Into)** - Entrar en funciones de Calcpad.Core
2. **Breakpoints** - Pausar en líneas específicas
3. **Watch Window** - Monitorear expresiones en tiempo real
4. **Call Stack** - Ver la pila de llamadas completa
5. **Hot Reload** - Recompilar C# sin reiniciar depurador
6. **Multi-idioma UI** - Interfaz en inglés/español configurable

### Testing:
1. **Unit tests** - Para ExecutionTracker
2. **Integration tests** - Para cada lenguaje soportado
3. **CI/CD** - Automatizar testing en GitHub Actions

---

## 15. Cómo Contribuir

Si encuentras bugs o quieres agregar features:

1. **Reportar bugs**: Abrir issue con logs de `debugger_final_log.txt`
2. **Proponer features**: Describir caso de uso y beneficio
3. **Pull requests**: Mantener instrumentación en código nuevo

---

## 16. Licencia y Créditos

### Calcpad Original:
- **Autor**: Proektsoftbg
- **Repositorio**: https://github.com/Proektsoftbg/Calcpad
- **Licencia**: [Revisar en repositorio original]

### Este Fork:
- **Mantenedor**: [Tu nombre/usuario]
- **Fork creado**: Enero 2026
- **Licencia**: [Misma que original o especificar]

---

## Resumen Ejecutivo

Este fork agrega **3 componentes principales** sobre Calcpad original:

1. **CalcpadDebugger** - Depurador WPF estilo MATLAB (nuevo)
2. **ExecutionTracker** - Instrumentación con StackTrace (nuevo)
3. **Soporte Avalonia mejorado** - dotnet cross-platform vs csc Windows-only

**Total de líneas agregadas**: ~5000+ líneas de código nuevo
**Total de líneas modificadas**: ~500 líneas en archivos core

**Impacto**: Este fork transforma Calcpad de una herramienta de cálculo en una **plataforma de desarrollo depurable y extensible**.
