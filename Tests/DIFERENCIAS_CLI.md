# Diferencias entre Calcpad.Cli y Calcpad.Wpf

## Resumen Ejecutivo

**Calcpad.Cli** y **Calcpad.Wpf** son DOS programas diferentes con propósitos distintos.

---

## Comparación Rápida

| Característica | Calcpad.Cli | Calcpad.Wpf |
|----------------|-------------|-------------|
| **Tipo** | CLI puro (consola) | GUI (interfaz gráfica) |
| **Ejecutable** | `Cli.exe` | `Calcpad.exe` |
| **Ubicación** | `Calcpad.Cli/bin/Release/net10.0/` | `Calcpad.Wpf/bin/Release/net10.0-windows/` |
| **Interfaz** | Terminal/consola | Ventana WPF |
| **Uso principal** | Generar HTML/PDF sin GUI | Editar y calcular archivos .cpd |
| **Argumentos** | `archivo.cpd [salida.html] [-s]` | `archivo.cpd` (solo para abrir) |
| **Genera HTML** | ✅ Sí, sin abrir GUI | ❌ No, solo abre en editor |
| **Modo interactivo** | ✅ Sí (REPL) | ✅ Sí (editor) |
| **Automatización** | ✅ Perfecto para scripts | ❌ Requiere GUI |

---

## Calcpad.Cli (CLI Puro)

### Ubicación
```
Calcpad.Cli/bin/Release/net10.0/Cli.exe
```

### Propósito
- **Generar HTML/PDF/DOCX desde línea de comandos**
- **Automatización** de conversión de archivos
- **Modo interactivo** (REPL) para cálculos rápidos

### Sintaxis
```bash
# Generar HTML (abre automáticamente)
Cli.exe archivo.cpd

# Especificar archivo de salida
Cli.exe archivo.cpd resultado.html

# Modo silencioso (no abre navegador)
Cli.exe archivo.cpd resultado.html -s

# Generar PDF
Cli.exe archivo.cpd resultado.pdf

# Generar DOCX
Cli.exe archivo.cpd resultado.docx

# Modo interactivo (REPL)
Cli.exe
```

### Comandos Interactivos
```
NEW         - Nuevo cálculo
OPEN        - Abrir archivo .cpc
SAVE        - Guardar archivo .cpc
LIST        - Listar archivos guardados
EXIT        - Salir
RESET       - Reiniciar cálculos
CLS         - Limpiar pantalla
DEL         - Borrar última línea
DEG/RAD/GRA - Cambiar unidades angulares
SETTINGS    - Editar configuración
LICENSE     - Ver licencia
HELP        - Ayuda
```

### Ejemplo de Uso
```bash
# Terminal
C:\> Cli.exe test.cpd test.html -s

# Resultado: test.html generado (sin abrir navegador)
```

### Características
- ✅ **Sin interfaz gráfica**
- ✅ **Perfecto para automatización**
- ✅ **Soporta batch processing**
- ✅ **Genera múltiples formatos** (HTML, PDF, DOCX)
- ✅ **Modo silencioso** con `-s`
- ✅ **Modo interactivo** (REPL) sin argumentos

---

## Calcpad.Wpf (Interfaz Gráfica)

### Ubicación
```
Calcpad.Wpf/bin/Release/net10.0-windows/Calcpad.exe
```

### Propósito
- **Editor visual** de archivos .cpd
- **Interfaz gráfica** para cálculos
- **Vista previa en tiempo real**

### Sintaxis
```bash
# Abrir archivo en el editor
Calcpad.exe archivo.cpd

# Sin argumentos: abre editor vacío
Calcpad.exe
```

### Características
- ✅ **Editor visual** con syntax highlighting
- ✅ **Vista previa** HTML en tiempo real
- ✅ **Depuración interactiva**
- ✅ **Autocompletado** de funciones
- ✅ **Snippets** de código
- ✅ **Folding** de código
- ❌ **NO genera HTML desde CLI** (requiere GUI)
- ❌ **NO tiene modo silencioso**
- ❌ **NO es para automatización**

### Comportamiento con Argumentos
```bash
# Esto ABRE la GUI con el archivo cargado
Calcpad.exe archivo.cpd

# NO genera HTML automáticamente
# El usuario debe presionar "Calculate" en la GUI
```

---

## ¿Cuál usar?

### Usa **Calcpad.Cli** si:
- ✅ Quieres **generar HTML sin abrir GUI**
- ✅ Necesitas **automatizar** conversiones
- ✅ Estás en un **script** o **CI/CD**
- ✅ Quieres **modo batch** (procesar múltiples archivos)
- ✅ Necesitas **silencio** (sin ventanas)

### Usa **Calcpad.Wpf** si:
- ✅ Quieres **editar** archivos .cpd visualmente
- ✅ Necesitas **depurar** cálculos paso a paso
- ✅ Quieres **vista previa** en tiempo real
- ✅ Prefieres **interfaz gráfica**
- ✅ Necesitas **autocompletado** y **snippets**

---

## Ejemplos Comparados

### Ejemplo 1: Generar HTML

**Con Calcpad.Cli (CORRECTO para automatización):**
```bash
Cli.exe test.cpd test.html -s
# Resultado: test.html generado sin abrir nada
```

**Con Calcpad.Wpf (NO funciona para CLI):**
```bash
Calcpad.exe test.cpd
# Resultado: Abre la GUI con el archivo cargado
# NO genera HTML automáticamente
```

### Ejemplo 2: Editar Archivo

**Con Calcpad.Cli (NO es ideal):**
```bash
Cli.exe test.cpd
# Abre modo interactivo, pero sin editor visual
```

**Con Calcpad.Wpf (CORRECTO para edición):**
```bash
Calcpad.exe test.cpd
# Abre editor visual con syntax highlighting
```

---

## En Nuestro Sistema de Comparación

### ¿Qué usamos?

**Calcpad.Cli** ✅

### ¿Por qué?

Porque necesitamos:
- ✅ Generar HTML sin GUI
- ✅ Automatizar con scripts
- ✅ Ejecutar desde `run_comparison.bat`

### Comando usado
```bash
Calcpad.Cli/bin/Release/net10.0/Cli.exe mathcad_fem_comparison.cpd mathcad_fem_comparison.html
```

---

## Resumen de Diferencias Clave

### Arquitectura

**Calcpad.Cli:**
```
Input: archivo.cpd
  ↓
CalcpadReader.Read()
  ↓
CalcpadProcessor.ProcessCode()
  ↓
ExpressionParser.Parse()
  ↓
Converter.ToHtml()
  ↓
Output: archivo.html (archivo físico)
```

**Calcpad.Wpf:**
```
Input: archivo.cpd
  ↓
MainWindow.GetInputTextFromFile()
  ↓
MathEditor (UI)
  ↓
CalculateAsync()
  ↓
Output: WebView2 (vista en GUI)
```

---

## Librerías Compartidas

Ambos usan las mismas bibliotecas core:
- ✅ `Calcpad.Core` - Motor de cálculo
- ✅ `Calcpad.Common` - Funcionalidades comunes
- ✅ `Calcpad.OpenXml` - Generación de documentos

Diferencia:
- **Calcpad.Cli** usa `Converter.cs` propio
- **Calcpad.Wpf** usa `WebView2Wrapper.cs` para UI

---

## ¿Son Compatibles?

**Sí**, ambos:
- ✅ Leen el mismo formato `.cpd`
- ✅ Usan el mismo motor de cálculo
- ✅ Generan los mismos resultados
- ✅ Soportan MultLangCode

**Diferencia:**
- **Calcpad.Cli** genera archivos físicos (HTML/PDF/DOCX)
- **Calcpad.Wpf** muestra resultados en interfaz visual

---

## En la Práctica

### Workflow típico:

1. **Desarrollo/Edición:**
   ```bash
   Calcpad.exe test.cpd
   # Edita en GUI, prueba cálculos
   ```

2. **Automatización/Producción:**
   ```bash
   Cli.exe test.cpd test.html -s
   # Genera HTML en batch sin GUI
   ```

---

## Conclusión

| Aspecto | Calcpad.Cli | Calcpad.Wpf |
|---------|-------------|-------------|
| **Naturaleza** | CLI puro | GUI application |
| **Para automatización** | ✅ SÍ | ❌ NO |
| **Para edición** | ⚠️ Limitado | ✅ SÍ |
| **Genera HTML CLI** | ✅ SÍ | ❌ NO |
| **Abre navegador** | ⚠️ Opcional | ❌ N/A |
| **Scripts/batch** | ✅ SÍ | ❌ NO |

---

**En nuestro caso:**
Usamos **Calcpad.Cli** porque necesitamos generar HTML automáticamente sin abrir la interfaz gráfica, perfecto para comparar con Mathcad.

**Calcpad.Wpf solo abre archivos en el editor**, no genera HTML desde CLI.
