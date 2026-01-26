# Calcpad Debugger Avanzado

## 🎯 Descripción

Un depurador estilo IDE que permite:
- **Depurar archivos .cpd paso a paso** (F10, F11, F5)
- **Ver y editar el código fuente C# de Calcpad** mientras depuras
- **Navegación automática** al código fuente que se está ejecutando
- **Compilar cambios** en tiempo real con un solo clic

## 🚀 Uso

```bash
./calcpad-debugger
```

## 📋 Interfaz

### Panel Izquierdo: Código .cpd
- Editor de texto completo del archivo .cpd
- **Editable**: Puedes modificar el código mientras depuras
- Botón **💾 Guardar** para guardar cambios

### Panel Central: Código Fuente C#
- Muestra el código fuente de Calcpad (.cs files)
- **ComboBox** para navegar entre archivos: GlobalParser.cs, LanguageExecutor.cs, etc.
- **Editable**: Puedes modificar el código fuente
- Botón **💾 Guardar** para guardar cambios
- Botón **🔨 Compilar** para compilar el proyecto

### Panel Derecho: Variables y Estado
- **Variables**: Grid con nombre, valor y tipo de cada variable
- **Estado**: Información de ejecución actual

### Panel Inferior: Log de Ejecución
- Muestra cada paso con formato:
  ```
  📍 [FileName.cs:LineNumber] ClassName.MethodName - Message
  ```

## 🔍 Ejemplo: Rastreando el Error de Avalonia

Cuando ejecutas `ejemplo-multiples-lenguajes.cpd` con el bloque `@{avalonia}`:

```cpd
'=== 3. C# con Avalonia ===

@{avalonia}
using System;

class CalculadoraSimple {
    static void Main() {
        Console.WriteLine("Hola desde C# (Avalonia)");
        int a = 100;
        int b = 50;
        Console.WriteLine($"División: {a} / {b} = {a/b}");
    }
}
@{end avalonia}
```

### El depurador mostrará:

```
📍 [GlobalParser.cs:35] GlobalParser.Process - Checking for external language blocks
📍 [GlobalParser.cs:36] GlobalParser.Process - Found external code blocks
📍 [MultLangProcessor.cs:XX] MultLangProcessor.Process - Processing block: avalonia
📍 [LanguageExecutor.cs:35] LanguageExecutor.Execute - Language: avalonia
📍 [LanguageExecutor.cs:37] LanguageExecutor.Execute - Checking if language 'avalonia' is configured
📍 [LanguageExecutor.cs:48] LanguageExecutor.Execute - Language configured: Command=dotnet, Extension=.csproj
📍 [LanguageExecutor.cs:63] LanguageExecutor.Execute - Checking if 'avalonia' is available in PATH
📍 [LanguageExecutor.cs:66] LanguageExecutor.Execute - ERROR: 'avalonia' not found in PATH
```

### Navegación Automática:
- El ComboBox cambiará a **LanguageExecutor.cs**
- El cursor saltará a la **línea 66**
- Verás el código exacto:
  ```csharp
  if (!MultLangManager.IsLanguageAvailable(block.Language))
  {
      _tracker?.ReportStep($"ERROR: '{block.Language}' not found in PATH");
      return new ExecutionResult
      {
          Success = false,
          Error = $"Language '{block.Language}' not found in PATH. Please install {langDef.Command}"
      };
  }
  ```

## 🛠️ Flujo de Trabajo

1. **Cargar archivo**: Click en "📂 Cargar Archivo" → Seleccionar .cpd
2. **Depurar**: Presiona F10 (Step Over) o F5 (Continue)
3. **Observar**:
   - Panel inferior muestra: `📍 [File.cs:Line] Class.Method - Message`
   - Panel central navega automáticamente al archivo y línea
4. **Editar** (si es necesario):
   - Modifica el código C# en el panel central
   - Click en **💾 Guardar**
   - Click en **🔨 Compilar**
5. **Reiniciar**: Click en "🔄 Reset" para volver a ejecutar

## 📝 Atajos de Teclado

- **F5**: Continue (ejecutar hasta el final)
- **F10**: Step Over (siguiente línea)
- **F11**: Step Into (entrar en función)

## 🔧 Archivos con Instrumentación

Los siguientes archivos tienen rastreo completo:
- `Calcpad.Common/GlobalParser.cs`
- `Calcpad.Common/CalcpadProcessor.cs`
- `Calcpad.Common/MultLangCode/MultLangProcessor.cs`
- `Calcpad.Common/MultLangCode/LanguageExecutor.cs`

## 💡 Beneficios

1. **No más debugging a ciegas**: Ves exactamente qué código se ejecuta
2. **Edición en vivo**: Modifica y recompila sin salir del depurador
3. **Aprendizaje**: Entiende cómo funciona Calcpad internamente
4. **Debugging eficiente**: Encuentra bugs rápidamente
