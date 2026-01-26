# Resumen: Snippets HTML/CSS/TS + Folding Mejorado

**Fecha**: 2026-01-21
**Estado**: ✅ COMPILADO Y LISTO PARA PROBAR

---

## 1. Snippets HTML/CSS/TypeScript (COMPLETADO ✅)

### Qué se implementó:
- Sistema de snippets tipo Emmet para AvalonEdit
- Detección automática de contexto (@{html}, @{css}, @{ts}, @{js})
- Preview completo del template antes de insertar
- Cursor posicionado automáticamente después de insertar

### Snippets disponibles:

**HTML** (dentro de `@{html}`):
- `html` / `html:5` → HTML5 boilerplate completo
- `div`, `p`, `h1`, `h2`, `h3` → Elementos básicos
- `a`, `link`, `script`, `style` → Referencias externas
- `button`, `input`, `form` → Elementos de formulario
- `table`, `ul`, `ol` → Estructuras de lista/tabla

**CSS** (dentro de `@{css}`):
- `flex` → Contenedor flexbox con justify-content y align-items
- `grid` → Grid con 3 columnas y gap
- `center` → Centrar elemento con margin y text-align

**TypeScript/JavaScript** (dentro de `@{ts}` o `@{js}`):
- `function` → Declaración de función
- `arrow` → Arrow function con const
- `class` → Clase con constructor
- `interface` → Interface de TypeScript
- `log` → console.log()

### Cómo usar:
1. Abre Calcpad y presiona "Code" para asegurarte de estar en AvalonEdit (NO MathEditor)
2. Dentro de un bloque `@{html}`, escribe "html" y espera
3. Aparecerá popup con preview completo del HTML5 boilerplate
4. Presiona Tab o Enter para insertar
5. El cursor se posicionará automáticamente en `<body>`

### Archivos modificados:
- `HtmlSnippets.cs` (NUEVO) - Define todos los snippets
- `MainWindow.AvalonEdit.cs` - Detecta contexto y muestra snippets
  - `GetCurrentBlockContext()` - Detecta bloque actual con stack
  - `ShowSnippetAutocomplete()` - Filtra y muestra snippets
  - `SnippetCompletionData` - Implementa ICompletionData con preview

---

## 2. Code Folding Mejorado (COMPLETADO ✅)

### Problema original:
- FoldingMargin (+/-) no aparecía en AvalonEdit
- Usuario veía `@{html}...@{end html}` sin forma de colapsar

### Solución implementada:
1. **Forzar visibilidad de FoldingMargin**:
   - Eliminar márgenes existentes
   - Crear nuevo FoldingMargin con colores personalizados
   - Insertarlo en posición 0 de LeftMargins
   - Asignar FoldingManager correctamente

2. **Bloques soportados**:
   - Externos: `@{c}`, `@{cpp}`, `@{fortran}`, `@{python}`, `@{html}`, `@{css}`, `@{ts}`, `@{js}`, etc.
   - Calcpad: `#if...#end if`, `#for...#loop`, `#def...#end def`
   - SVG: `$svg...$end`
   - HTML tags: `<div>...</div>`, `<head>...</head>`, etc.

### Cómo probar:
1. Abre `test_folding.cpd` en Calcpad
2. **IMPORTANTE**: Presiona el botón "Code" en la barra superior para cambiar a **AvalonEdit**
   - Si estás en MathEditor (editor visual), NO verás el folding
   - El folding SOLO funciona en AvalonEdit (modo Code)
3. Busca en el margen izquierdo los símbolos **▼** (triángulo hacia abajo)
4. Click en **▼** para colapsar el bloque
5. Click en **▶** (triángulo hacia derecha) para expandir

### Archivos modificados:
- `MainWindow.AvalonEdit.cs` (InitializeAvalonEdit):
  - Líneas 36-56: Código para forzar FoldingMargin visible
  - Colores personalizados: fondo gris claro (#F0F0F0), marcador gris (#808080)

---

## 3. Problemas Conocidos y Próximos Pasos

### ❌ MathEditor NO soporta folding actualmente
**Problema**: En la screenshot_22.png se ve MathEditor mostrando `@{html}` sin folding.

**Causa**: MathEditor es un control completamente diferente que renderiza ecuaciones matemáticas, NO usa AvalonEdit. El folding solo funciona en AvalonEdit.

**Solución propuesta**:
1. Modificar MathEditor.FromCalcpad() para detectar bloques externos
2. Crear elementos colapsables que se muestren como `| HTML [+]`
3. Reemplazar PreviewTextBlock superior con AvalonEdit pequeño para mostrar script completo

**Estado**: PENDIENTE (requiere modificar MathEditorControl.xaml.cs)

### ❌ Mensajes dinámicos de compilación
**Problema**: Lenguajes compilados (C, C++, Fortran) no muestran "Compiling... 1.2s" dinámicamente.

**Solución propuesta**: Agregar timer en MultLangCodeRunner para actualizar estado de compilación.

**Estado**: PENDIENTE

---

## 4. Archivos de Prueba Creados

1. **test_snippets.cpd**:
   - Archivo para probar snippets HTML/CSS/TS/JS
   - Incluye instrucciones detalladas
   - Bloques de ejemplo para cada lenguaje

2. **test_folding.cpd**:
   - Archivo para probar code folding
   - Incluye bloques de todos los tipos (HTML, CSS, C, Fortran, etc.)
   - Instrucciones paso a paso

---

## 5. Diferencias entre Editores

### RichTextBox (Editor Clásico)
- Editor original de Calcpad
- No tiene snippets ni folding avanzado
- Alternativa compatible para usuarios legacy

### AvalonEdit (Editor Avanzado) ✅
- Editor de código moderno
- **Snippets HTML/CSS/TS** ✅
- **Code Folding visible** ✅
- Syntax highlighting mejorado
- **Úsalo presionando el botón "Code"**

### MathEditor (Editor Visual) ⏳
- Para editar ecuaciones matemáticas visualmente
- NO compila ni ejecuta código externo
- Muestra bloques externos como texto azul
- **Folding pendiente de implementar**

---

## 6. Cómo Cambiar entre Editores

1. **Alternar RichTextBox ↔ AvalonEdit**:
   - NO visible en UI (uso interno)
   - AvalonEdit es el editor por defecto ahora

2. **Alternar Code ↔ MathEditor**:
   - Botón verde "Code" / "Visual" en barra superior
   - "Code" → Modo código (AvalonEdit) ← **USA ESTE PARA SNIPPETS Y FOLDING**
   - "Visual" → Modo visual (MathEditor)

---

## 7. Resumen de Lo Implementado

| Funcionalidad | Estado | Editor | Notas |
|--------------|---------|--------|-------|
| Snippets HTML/CSS/TS | ✅ | AvalonEdit | Preview completo, 23 snippets total |
| Code Folding | ✅ | AvalonEdit | Todos los bloques soportados |
| Folding en MathEditor | ⏳ | MathEditor | Pendiente implementar |
| Script view con AvalonEdit | ⏳ | MathEditor | Pendiente implementar |
| Mensajes dinámicos compilación | ⏳ | Todos | Pendiente implementar |
| temp_multilang folder | ✅ | Todos | Creada automáticamente |

---

## 8. Instrucciones para Probar

### Para Snippets:
```bash
cd "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\bin\Release\net10.0-windows"
start Calcpad.exe "C:\Users\j-b-j\Documents\Calcpad-7.5.7\test_snippets.cpd"
```

1. Asegúrate de estar en modo "Code" (AvalonEdit)
2. Posiciónate dentro de `@{html}` block
3. Escribe "html" y espera popup
4. Presiona Tab/Enter

### Para Folding:
```bash
cd "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\bin\Release\net10.0-windows"
start Calcpad.exe "C:\Users\j-b-j\Documents\Calcpad-7.5.7\test_folding.cpd"
```

1. **CRÍTICO**: Presiona botón "Code" para estar en AvalonEdit
2. Busca **▼** en margen izquierdo
3. Click para colapsar/expandir

---

## 9. Próximos Commits (Git)

Cuando confirmes que todo funciona, haremos:

```bash
git checkout -b feature/snippets-and-folding
git add .
git commit -m "Add HTML/CSS/TS snippets and improve code folding

- Implement Emmet-style snippets for HTML, CSS, TypeScript/JavaScript
- 23 snippets total with full template preview
- Context-aware autocomplete inside @{html}, @{css}, @{ts} blocks
- Force FoldingMargin visibility in AvalonEdit
- Support folding for all external language blocks
- Create test files: test_snippets.cpd, test_folding.cpd
- Fix temp_multilang folder creation

Files modified:
- HtmlSnippets.cs (NEW)
- MainWindow.AvalonEdit.cs
- MultLangConfig.json

Co-authored-by: Claude Sonnet 4.5 <noreply@anthropic.com>"

git push origin feature/snippets-and-folding
```

Luego merge a master cuando esté todo probado.

---

**Ejecutable**: `Calcpad.Wpf\bin\Release\net10.0-windows\Calcpad.exe`
**Errores de compilación**: 0
**Warnings**: 68 (nullable annotations - no críticos)
