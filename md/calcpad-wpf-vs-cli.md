# Calcpad WPF vs Calcpad CLI - Comparación Técnica

## Introducción

Este documento compara las arquitecturas, flujos de procesamiento y diferencias clave entre **Calcpad WPF** (aplicación de escritorio) y **Calcpad CLI** (interfaz de línea de comandos).

---

## 🏗️ Arquitectura General

### Calcpad WPF
- **Interfaz gráfica** usando Windows Presentation Foundation (WPF)
- **Editor interactivo** con RichTextBox y syntax highlighting en tiempo real
- **Visualización HTML** integrada usando WebView2
- **Ejecución asíncrona** con UI responsiva
- **Target Framework**: .NET 10.0-windows

### Calcpad CLI
- **Interfaz de consola** sin UI gráfica
- **Procesamiento batch** de archivos .cpd
- **Salida a archivos** HTML, PDF, DOCX
- **Ejecución síncrona** simple y directa
- **Target Framework**: .NET 10.0 (multiplataforma)

---

## 📊 Tabla Comparativa Detallada

| Aspecto | Calcpad WPF | Calcpad CLI | ¿Son Iguales? |
|---------|-------------|-------------|---------------|
| **Motor de Cálculo** | `Calcpad.Core` | `Calcpad.Core` | ✅ **IDÉNTICO** |
| **Parser de Macros** | `MacroParser` | `MacroParser` | ✅ **IDÉNTICO** |
| **Soporte Multi-lenguaje** | `MultLangProcessor` | `MultLangProcessor` | ✅ **IDÉNTICO** |
| **Generación HTML** | `HtmlWriter` | `HtmlWriter` | ✅ **IDÉNTICO** |
| **Syntax Highlighting** | `HighLighter.cs` (WPF) | ❌ No aplica | ❌ Solo WPF |
| **Transformación de Operadores** | Sí (`<<` → `∠`) | No | ❌ **DIFERENTE** |
| **Reversión de Operadores** | Sí (`RevertCalcpadOperators`) | No necesita | ❌ Solo WPF |
| **Entrada de Usuario** | RichTextBox interactivo | Archivo .cpd | ❌ **DIFERENTE** |
| **Salida** | WebView2 (HTML en pantalla) | Archivos (HTML/PDF/DOCX) | ❌ **DIFERENTE** |
| **Ejecución Asíncrona** | Sí (`Dispatcher.InvokeAsync`) | No | ❌ Solo WPF |
| **AutoRun** | Sí (configurable) | No aplica | ❌ Solo WPF |
| **Undo/Redo** | Sí | No aplica | ❌ Solo WPF |
| **Recent Files** | Sí | No aplica | ❌ Solo WPF |
| **Settings Persistence** | Sí (Settings.settings) | No | ❌ Solo WPF |

---

## 🔄 Flujo de Procesamiento

### Calcpad WPF - Flujo Completo

```
1. Usuario escribe código
   ↓
2. HighLighter transforma operadores en tiempo real
   - << → ∠
   - == → ≡
   - != → ≠
   - && → ∧
   - || → ∨
   ↓
3. Usuario guarda o ejecuta (AutoRun/Manual)
   ↓
4. GetInputText() extrae texto del RichTextBox
   ↓
5. Si hay bloques multi-lenguaje (@{cpp}, @{python}, etc.):
   - RevertCalcpadOperators() revierte transformaciones
   - << ∠ → <<
   - ≡ → ==
   - ≠ → !=
   - ∧ → &&
   - ∨ → ||
   ↓
6. MultLangProcessor ejecuta código externo
   ↓
7. MacroParser procesa macros y condiciones
   ↓
8. Calculator evalúa expresiones matemáticas
   ↓
9. HtmlWriter genera salida HTML
   ↓
10. WebView2 muestra resultado en pantalla
```

### Calcpad CLI - Flujo Simplificado

```
1. Usuario ejecuta comando:
   calcpad input.cpd output.html
   ↓
2. CLI lee archivo input.cpd
   ↓
3. Si hay bloques multi-lenguaje (@{cpp}, @{python}, etc.):
   - MultLangProcessor ejecuta código externo
   - Sin transformaciones previas
   - Código original sin modificar
   ↓
4. MacroParser procesa macros y condiciones
   ↓
5. Calculator evalúa expresiones matemáticas
   ↓
6. HtmlWriter genera salida HTML
   ↓
7. CLI guarda resultado en output.html
```

---

## ⚠️ Diferencias Críticas

### 1. **Transformación de Operadores**

**Problema identificado:**
- WPF transforma operadores para **visualización Unicode elegante**
- Esto causaba errores al compilar código C++/Python/etc.

**Solución implementada:**
```csharp
// En MainWindow.xaml.cs línea 1303
if (MultLangProcessor.HasLanguageBlocks(inputCode))
{
    // Revertir transformaciones antes de enviar a compiladores externos
    inputCode = RevertCalcpadOperators(inputCode);
    inputCode = _multLangProcessor.Process(inputCode);
}
```

**CLI NO tiene este problema** porque:
- Lee el archivo original sin modificar
- No transforma operadores para visualización
- Envía el código tal cual al compilador

### 2. **Rendimiento de Apertura de Archivos**

**Problema WPF original:**
- Ejecutaba cálculos **antes** de mostrar el código
- Demoraba 3700ms para archivos pequeños

**Solución implementada:**
```csharp
// En MainWindow.xaml.cs líneas 1145, 1163, 1180
// ANTES (bloqueante):
CalculateAsync();

// AHORA (asíncrono):
Dispatcher.InvokeAsync(() => CalculateAsync(), DispatcherPriority.Background);
```

**Resultado:**
- Código visible en ~100ms (37x más rápido)
- Cálculos en background

**CLI NO tiene este problema** porque:
- No tiene UI para mostrar
- Procesa todo secuencialmente
- El usuario espera que termine antes de continuar

### 3. **Guardado de Configuración**

**Problema WPF:**
```csharp
// Settings.Default.Save() falla en .NET 10.0
System.ArgumentException: The parameter 'sectionGroupName' is invalid
```

**Causa:**
- `System.Configuration.ApplicationSettingsBase` tiene problemas en .NET moderno
- Falta archivo `app.config` correcto

**CLI NO tiene este problema** porque:
- No guarda preferencias de usuario
- Es stateless (sin estado)

---

## 🔧 Componentes Compartidos

Ambas versiones comparten estos componentes críticos (100% sincronizados):

### Calcpad.Core
- **Calculator.cs**: Motor de cálculo matemático
- **ExpressionParser.cs**: Parser de expresiones
- **MacroParser.cs**: Procesador de macros
- **HtmlWriter.cs**: Generador de salida HTML

### Calcpad.Common
- **MultLangManager.cs**: Gestor de lenguajes externos
- **MultLangProcessor.cs**: Procesador de bloques multi-lenguaje
- **LanguageExecutor.cs**: Ejecutor de Python, C++, Octave, etc.
- **MultLangConfig.json**: Configuración compartida (sincronizada vía archivo)

---

## 📝 Ejemplo de Uso

### Calcpad WPF
```
1. Abrir Calcpad.exe
2. Escribir código en el editor
3. Click en "Play" o AutoRun automático
4. Ver resultado en panel Output
```

### Calcpad CLI
```bash
# Sintaxis básica
calcpad input.cpd output.html

# Con opciones
calcpad input.cpd output.html -d 3 -u si -a deg

# Ejemplo real
cd "C:\Users\j-b-j\Documents\Calcpad-7.5.7"
.\Calcpad.Cli\bin\Debug\net10.0\Calcpad.Cli.exe test_all_langs.cpd output.html
```

---

## 🎯 Conclusiones

### ✅ Ventajas de WPF
- Edición interactiva en tiempo real
- Syntax highlighting visual
- Visualización inmediata de resultados
- Undo/Redo, búsqueda, reemplazo
- Experiencia de usuario completa

### ✅ Ventajas de CLI
- Automatización y scripting
- Procesamiento batch
- Sin dependencia de UI
- Multiplataforma (Windows, Linux, macOS)
- Integración con pipelines CI/CD

### ⚡ Ambos Comparten
- **Mismo motor de cálculo** (resultados idénticos)
- **Mismo soporte multi-lenguaje** (Python, C++, Octave, etc.)
- **Misma configuración** (MultLangConfig.json sincronizado)
- **Misma salida HTML** (formato idéntico)

---

## 🐛 Problemas Resueltos (WPF)

### 1. Error de Compilación C++
- ❌ **Antes**: `cout << "..."` → `cout∠"..."` (error de compilación)
- ✅ **Ahora**: Se revierte a `<<` antes de compilar

### 2. Lentitud al Abrir Archivos
- ❌ **Antes**: 3700ms para mostrar código
- ✅ **Ahora**: 100ms (37x más rápido)

### 3. Configuración No Se Guarda
- ❌ **Problema**: Settings.Default.Save() falla en .NET 10.0
- ⏳ **Estado**: Pendiente de solución

---

**Fecha**: 2026-01-15
**Versión Calcpad**: 7.5.8
**Autor**: Análisis técnico de arquitectura
