# Changelog - Calcpad Fork

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [1.0.4] - 2026-01-22

### ✨ Nueva Funcionalidad

#### Formateo de Vectores y Matrices
- Vectores `[2;3;4]` ahora se muestran con estilo de matriz (bordes) en lugar de texto plano
- Matrices `[2;3|4;5]` se muestran como matrices 2D con bordes
- Funciona en todos los modos: `#noc`, `#equ`, `#show`
- Soporta valores literales y variables: `[x;y;z]` también se formatea

### 📄 Archivos Modificados
- `Calcpad.Core/Output/OutputWriter.cs` - Métodos abstractos FormatVectorExpression/FormatMatrixExpression
- `Calcpad.Core/Output/HtmWriter.cs` - Implementación HTML con clase .matrix
- `Calcpad.Core/Output/TextWriter.cs` - Implementación texto plano
- `Calcpad.Core/Output/XmlWriter.cs` - Implementación XML para Word
- `Calcpad.Core/Parsers/MathParser/MathParser.Output.cs` - RenderVectorToken/RenderMatrixToken

---

## [1.0.3] - 2026-01-22

### ✨ Nueva Funcionalidad

#### Directivas de Importación Inline
- **@{mathcad:archivo.mcdx}** - Importa y convierte archivos Mathcad Prime
- **@{smathstudio:archivo.sm}** o **@{smath:archivo.sm}** - Importa y convierte archivos SMath Studio
- Las directivas se procesan durante la lectura del archivo y se reemplazan por código Calcpad convertido
- Soporte para rutas absolutas y relativas

#### Conversores de Archivos
- **McdxConverter**: Conversión completa de hojas de cálculo Mathcad Prime a formato Calcpad
  - Matrices en orden column-major correcto
  - Regiones de texto convertidas a comentarios
  - Sistema de advertencias para características no soportadas

- **SMathConverter**: Parsing completo de archivos XML de SMath Studio
  - Conversión de expresiones matemáticas con mapeo de operadores
  - Soporte para matrices y vectores
  - Traducción de nombres de funciones (ej: `ceil` → `ceiling`, `transpose` → `transp`)

#### Botones de Toolbar para Import/Export
- **M↓** (Naranja): Importar desde Mathcad Prime
- **M↑** (Naranja): Exportar a Mathcad Prime (placeholder)
- **S↓** (Verde): Importar desde SMath Studio
- **S↑** (Verde): Exportar a SMath Studio (placeholder)

### 🖥️ CLI
- Soporte para archivos `.mcdx` en Calcpad CLI
- Soporte para archivos `.sm` en Calcpad CLI
- Nueva opción `-cpd` para convertir sin procesar

### 📄 Archivos Modificados
- `Calcpad.Common/CalcpadReader.cs` - Procesamiento de directivas de importación
- `Calcpad.Common/McdxConverter.cs` - Conversor Mathcad Prime
- `Calcpad.Common/SMathConverter.cs` - Conversor SMath Studio
- `Calcpad.Cli/Program.cs` - Soporte CLI para .mcdx y .sm
- `Calcpad.Wpf/MainWindow.xaml` - Botones de toolbar
- `Calcpad.Wpf/MainWindow.xaml.cs` - Handlers de import/export

---

## [1.0.2] - 2026-01-22

### 🐛 Corregido

#### AutoComplete Manager - Crash crítico
- **ArgumentNullException:** Corregido crash al seleccionar item del autocompletado
  - Error: "Value cannot be null. (Parameter 'position1')"
  - Ubicación: `AutoCompleteManager.cs:1012` en método `EndAutoComplete()`
  - Causa: `_autoCompleteStart` era null al crear `TextRange`
  - Fix: Agregadas 3 validaciones null al inicio del método
  - Impacto: Alto - Previene crash durante uso normal del autocompletado

### 📄 Archivos Modificados
- `Calcpad.Wpf/AutoCompleteManager.cs` (+13 líneas de validación)

### ✅ Testing
- Compilación: ✅ Exitosa (0 errores)
- Validaciones: ✅ 3 null checks agregados

---

## [1.0.1] - 2026-01-22

### 🐛 Corregido

#### Preview Editor - 5 bugs críticos
- **Pipe duplicado:** Eliminada duplicación del marcador `|` en el preview editor al hacer click repetidamente
- **Cursor invisible:** Cursor ahora aparece correctamente usando `Dispatcher.BeginInvoke` para establecer posición después del renderizado
- **Editor no reabre:** Corregido problema donde el editor solo funcionaba en el primer uso
- **Bloqueo inmediato:** Agregada protección temporal de 500ms contra `LostFocus` prematuro
- **Parameter count mismatch:** Reemplazado uso incorrecto de `Dispatcher.BeginInvoke` con `DispatcherTimer`

#### Memory Leaks - 2 fixes críticos
- **Cursor timer:** Agregado evento `Unloaded` para detener `_cursorTimer` al cerrar el control
- **Preview timer:** Convertido timer de protección a campo de clase para permitir cleanup en `Unloaded`

#### Validaciones - 2 fixes críticos
- **Application.Current.MainWindow:** Creado método `GetDpiScale()` con validación null para 4 ocurrencias
- **Índices de array:** Agregada validación de límites en loop de selección de texto

### ✨ Mejorado

- Sincronización bidireccional completa entre preview bar y canvas de MathEditor
- Manejo robusto de timers con cleanup apropiado
- Validaciones de null para prevenir crashes en tests y casos edge
- Performance mejorada al eliminar memory leaks acumulativos

### 📚 Documentación

- `AUDITORIA_COMPLETA_MATHEDITOR.md` - Auditoría exhaustiva identificando 21 categorías de problemas
- `FIXES_CRITICOS_MEMORY_LEAKS_APLICADOS.md` - Detalles de los 4 fixes críticos
- `RESUMEN_FINAL_TODOS_LOS_FIXES.md` - Resumen completo de todos los fixes (13 mejoras)
- `TODOS_LOS_FIXES_APLICADOS.md` - Flujo completo y testing de los 5 bugs del preview editor
- `FIXES_COMPLETOS_PREVIEW_EDITOR.md` - Detalles técnicos de bugs #1, #2, #3

### 🔧 Archivos Modificados

- `Calcpad.Wpf/MathEditor/MathEditorControl.xaml.cs` (+238 líneas)
- `Calcpad.Wpf/MathEditor/MathEditorControl.xaml` (+38 líneas)
- `Calcpad.Wpf/MathEditor/MathExternalBlock.cs` (+43 líneas)
- `Calcpad.Common/GlobalParser.cs` (+101 líneas)
- `Calcpad.Common/MultLangCode/MultLangProcessor.cs` (+54 líneas)
- `Calcpad.Core/Parsers/ExpressionParser/ExpressionParser.cs` (+8 líneas)
- `Calcpad.Wpf/MainWindow.xaml`, `MainWindow.xaml.cs` (actualizaciones menores)

**Total:** +439 líneas, -47 líneas

### ✅ Testing

- Compilación: ✅ Exitosa (0 errores, 11 warnings nullable)
- Unit tests: ⏳ Pendiente
- User acceptance: ⏳ Pendiente

---

## [1.0.0] - 2026-01-21

### ✨ Agregado

#### MathEditor - Funcionalidades principales
- **Modo Visual completo:** Editor visual con rendering en canvas para ecuaciones matemáticas
- **Bloques externos:** Soporte para C, C++, C#, HTML, CSS, TypeScript, JavaScript, Python, Octave/MATLAB
- **Preview bar:** Barra de preview con sincronización bidireccional para edición de código
- **Snippets automáticos:** Sistema de snippets con autocompletado para funciones matemáticas
- **Code folding:** Plegado de código para bloques externos

#### Lenguajes externos soportados
- **C/C++/C#:** Ejecución con GCC, MSVC, Clang
- **HTML/CSS:** Renderizado en WebView2
- **TypeScript:** Transpilación y ejecución con Bun
- **JavaScript:** Ejecución con Node.js
- **Python:** Ejecución con Python interpreter
- **Octave/MATLAB:** Ejecución de scripts numéricos

#### Sistema de archivos
- **Archivos separados:** Generación automática de archivos .html, .css, .ts individuales
- **Guardado inteligente:** Botón "Save Web Files" para guardar todos los archivos web generados
- **Sincronización:** Actualización automática al editar bloques de código

### 🔧 Configuración

- `MultLangConfig.json`: Configuración centralizada de todos los lenguajes
- Paths configurables para compiladores y runtimes
- Argumentos personalizables por lenguaje

### 📚 Documentación inicial

- `HTML_CSS_TYPESCRIPT_LISTO.txt` - Guía de uso de HTML/CSS/TypeScript
- `TYPESCRIPT_@TS_CONFIGURADO.md` - Configuración de TypeScript
- `COMO_FUNCIONA_AWATIF_UI.md` - Integración con Awatif
- `CHEAT_SHEET_HTML_CSS_TS.txt` - Referencia rápida

### 📦 Instalador

- Script Inno Setup para Windows
- Verificación de .NET 10 Desktop Runtime
- Asociación de archivos .cpd
- Creación de shortcuts en escritorio y menú inicio

### 📄 Licencia

- Licenciado bajo MIT License
- Fork del proyecto original Calcpad por Proektsft

---

## Convenciones de Commits

Este proyecto usa los siguientes prefijos de commits:

- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bugs
- `docs:` - Cambios en documentación
- `style:` - Formateo, puntos y comas faltantes, etc.
- `refactor:` - Refactorización de código
- `test:` - Agregar tests faltantes
- `chore:` - Mantenimiento
- `build:` - Cambios en sistema de build
- `perf:` - Mejoras de performance

---

## Links

- [Repositorio](https://github.com/GiorgioBurbanelli89/calcpad_fork)
- [Calcpad Original](https://github.com/Proektsoftbg/Calcpad)
- [Issues](https://github.com/GiorgioBurbanelli89/calcpad_fork/issues)
