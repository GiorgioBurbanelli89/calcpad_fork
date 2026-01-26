# ANÁLISIS COMPLETO - MathEditor Preview Synchronization

## FECHA: 2026-01-22
## ESTADO: Revisión exhaustiva completada

---

## 1. ESTRUCTURA ACTUAL (después de git revert)

### 1.1 CONTROLES EN XAML (MathEditorControl.xaml)

Existen **3 controles de preview** definidos en el XAML:

#### A) PreviewTextBlock (líneas 35-40)
```xml
<TextBlock x:Name="PreviewTextBlock" FontFamily="Consolas" FontSize="10"
           Foreground="#333" VerticalAlignment="Center" MinWidth="200"
           TextTrimming="CharacterEllipsis" MaxWidth="600"
           MouseLeftButtonDown="PreviewTextBlock_MouseLeftButtonDown"  ⚠️ HANDLER FALTANTE
           Cursor="IBeam" ToolTip="Click para editar"
           AutomationProperties.AutomationId="PreviewTextBlock"/>
```
- **Propósito**: Mostrar la línea actual con cursor (|)
- **Estado**: Visible por defecto
- **Formato**: `@{c} Ln 4: printf(...);|` (cursor como |)

#### B) PreviewEditor - AvalonEdit en XAML (líneas 46-56)
```xml
<Border x:Name="PreviewEditorContainer" BorderThickness="1" BorderBrush="#1976D2"
        Background="White" Height="20" MinWidth="200" MaxWidth="600"
        VerticalAlignment="Center" Margin="0,0,0,0" Visibility="Collapsed">
    <avalonEdit:TextEditor x:Name="PreviewEditor"
                           FontFamily="Consolas" FontSize="10"
                           Background="White" Foreground="#333"
                           KeyDown="PreviewEditor_KeyDown"              ⚠️ HANDLER FALTANTE
                           LostFocus="PreviewEditor_LostFocus"          ⚠️ HANDLER FALTANTE
                           TextChanged="PreviewEditor_TextChanged"/>    ⚠️ HANDLER FALTANTE
</Border>
```
- **Propósito**: Editor para editar la línea del preview
- **Estado**: Collapsed por defecto (se muestra al hacer click en PreviewTextBlock)
- **Problema**: Definido en XAML pero sus event handlers NO existen en C#

#### C) PreviewEditTextBox - DEPRECATED (líneas 60-67)
```xml
<TextBox x:Name="PreviewEditTextBox" FontFamily="Consolas" FontSize="10"
         Foreground="#333" VerticalAlignment="Center" MinWidth="200"
         MaxWidth="600" Visibility="Collapsed" BorderThickness="1"
         KeyDown="PreviewEditTextBox_KeyDown"                ⚠️ HANDLER FALTANTE
         LostFocus="PreviewEditTextBox_LostFocus"            ⚠️ HANDLER FALTANTE
         TextChanged="PreviewEditTextBox_TextChanged"        ⚠️ HANDLER FALTANTE
         AutomationProperties.AutomationId="PreviewEditTextBox"/>
```
- **Propósito**: TextBox antiguo (antes de migrar a AvalonEdit)
- **Estado**: Deprecated, mantener para referencia
- **Problema**: Event handlers tampoco existen

---

### 1.2 CÓDIGO C# (MathEditorControl.xaml.cs)

#### A) Campo _previewEditor (línea 87)
```csharp
private TextEditor _previewEditor;
```

Este es un **AvalonEdit creado programáticamente**, NO el que está en XAML.

#### B) Método InitializePreviewEditor() (líneas 155-194)
```csharp
private void InitializePreviewEditor()
{
    if (PreviewEditorContainer == null) return;

    _previewEditor = new TextEditor
    {
        FontFamily = new FontFamily("Consolas"),
        FontSize = 10,
        Background = Brushes.Transparent,
        BorderThickness = new Thickness(0),
        IsReadOnly = true,  // ⚠️ SOLO LECTURA
        // ...
    };

    // Cargar syntax highlighting
    // ...

    PreviewEditorContainer.Child = _previewEditor;  // ⚠️ Se coloca en el mismo contenedor
}
```

**PROBLEMA CRÍTICO**:
- El XAML define `PreviewEditor` dentro de `PreviewEditorContainer`
- El C# crea `_previewEditor` y lo pone en `PreviewEditorContainer.Child`
- **¿Qué prevalece?** El C# sobrescribe el contenido del contenedor

#### C) Método UpdatePreview() (líneas 1101-1165)
```csharp
private void UpdatePreview()
{
    if (PreviewTextBlock == null) return;

    if (_currentElement is MathExternalBlock externalBlock)
    {
        UpdatePreviewForExternalBlock(externalBlock);
        return;
    }

    // ... construir lineText con cursor |

    PreviewTextBlock.Text = lineText;           // ✅ Actualiza TextBlock

    if (_previewEditor != null)                 // ⚠️ Actualiza _previewEditor programático
    {
        _previewEditor.Text = lineText;         // NO actualiza PreviewEditor del XAML
    }
}
```

#### D) Método UpdatePreviewForExternalBlock() (líneas 1171-1200)
```csharp
private void UpdatePreviewForExternalBlock(MathExternalBlock externalBlock)
{
    var lines = externalBlock.GetCodeLines();
    int lineIdx = externalBlock.CursorLine;
    int cursorPos = externalBlock.CursorPosition;

    // Construir texto con cursor
    string beforeCursor = currentLine.Substring(0, cursorPos);
    string afterCursor = currentLine.Substring(cursorPos);

    string lineText = $"@{{{externalBlock.Language.ToLower()}}} Ln {lineIdx + 1}: {beforeCursor}|{afterCursor}";

    PreviewTextBlock.Text = lineText;           // ✅ Actualiza TextBlock

    if (_previewEditor != null)                 // ⚠️ Actualiza _previewEditor programático
    {
        _previewEditor.Text = lineText;         // NO actualiza PreviewEditor del XAML
    }
}
```

---

### 1.3 MODELO (MathExternalBlock.cs)

```csharp
public class MathExternalBlock : MathElement
{
    public string Language { get; set; }      // "c", "html", "typescript", etc.
    public string Code { get; set; }          // Código completo (multilínea)
    public bool IsCollapsed { get; set; }     // [+] o [-]

    public int CursorPosition { get; set; } = 0;  // Posición dentro de la línea actual
    public int CursorLine { get; set; } = 0;      // Línea actual (0-based)
    public bool IsEditing { get; set; } = false;

    public string[] GetCodeLines() { ... }        // Split por \n
    public string GetCurrentLine() { ... }        // Obtiene línea en CursorLine
    public void SetCurrentLine(string newContent) { ... }  // Actualiza línea en CursorLine
}
```

---

## 2. FLUJO ACTUAL DE SINCRONIZACIÓN

### 2.1 Canvas → Preview (✅ FUNCIONA)

```
Usuario edita en Canvas
    ↓
UpdatePreview() se ejecuta
    ↓
PreviewTextBlock.Text = "@{c} Ln 4: printf(...);|"
    ↓
_previewEditor.Text = "@{c} Ln 4: printf(...);|"
    ↓
✅ Usuario ve cambios en preview bar
```

### 2.2 Preview → Canvas (❌ NO FUNCIONA)

```
Usuario hace click en PreviewTextBlock
    ↓
⚠️ PreviewTextBlock_MouseLeftButtonDown() NO EXISTE
    ↓
❌ No pasa nada
```

**SI EXISTIERAN LOS HANDLERS:**
```
Usuario hace click en PreviewTextBlock
    ↓
PreviewTextBlock_MouseLeftButtonDown() se ejecuta
    ↓
PreviewTextBlock.Visibility = Collapsed
PreviewEditorContainer.Visibility = Visible
PreviewEditor.Text = texto con prefijo
PreviewEditor.Focus()
    ↓
Usuario escribe en PreviewEditor
    ↓
PreviewEditor_TextChanged() se ejecuta
    ↓
ApplyPreviewEditFromAvalonEdit(finalApply: false)
    ↓
Extraer texto sin prefijo "@{c} Ln 4: "
    ↓
externalBlock.SetCurrentLine(newText)
    ↓
UpdateCurrentElementInCanvas() o Render()
    ↓
✅ Canvas se actualiza en tiempo real
    ↓
Usuario presiona Enter
    ↓
PreviewEditor_KeyDown() detecta Enter
    ↓
ApplyPreviewEditFromAvalonEdit(finalApply: true)
    ↓
Render() completo
PreviewEditor.Visibility = Collapsed
PreviewTextBlock.Visibility = Visible
```

---

## 3. PROBLEMAS IDENTIFICADOS

### 3.1 DUPLICACIÓN DE AVALONEDITS ⚠️⚠️⚠️

**Hay DOS instancias de AvalonEdit para el mismo propósito:**

1. **PreviewEditor** - Definido en XAML (línea 46)
   - Tiene event handlers definidos en XAML
   - Visibility = Collapsed por defecto

2. **_previewEditor** - Creado programáticamente (línea 159)
   - Se crea en InitializePreviewEditor()
   - Se coloca en PreviewEditorContainer.Child
   - IsReadOnly = true
   - NO tiene event handlers

**CONFLICTO:**
- PreviewEditorContainer en XAML tiene PreviewEditor como hijo
- InitializePreviewEditor() pone _previewEditor como PreviewEditorContainer.Child
- El último en ejecutarse sobrescribe al otro

### 3.2 EVENT HANDLERS FALTANTES ❌

Después del `git revert`, estos handlers NO EXISTEN en el C#:

1. `PreviewTextBlock_MouseLeftButtonDown` - Para abrir el editor
2. `PreviewEditor_TextChanged` - Para sincronizar en tiempo real
3. `PreviewEditor_KeyDown` - Para detectar Enter
4. `PreviewEditor_LostFocus` - Para cerrar el editor
5. `PreviewEditTextBox_TextChanged` - Deprecated pero referenciado
6. `PreviewEditTextBox_KeyDown` - Deprecated pero referenciado
7. `PreviewEditTextBox_LostFocus` - Deprecated pero referenciado

**Resultado:** 7 errores de compilación

### 3.3 ACTUALIZACIÓN INCORRECTA 🔄

UpdatePreview() actualiza:
- `PreviewTextBlock.Text` ✅
- `_previewEditor.Text` ⚠️ (instancia programática que podría no estar visible)

Pero NO actualiza:
- `PreviewEditor.Text` ❌ (instancia del XAML con los event handlers)

---

## 4. SOLUCIONES POSIBLES

### OPCIÓN 1: Usar solo PreviewEditor del XAML (RECOMENDADA) ⭐

**Ventajas:**
- Usa el control ya definido en XAML
- Event handlers en XAML son claros y declarativos
- No hay duplicación
- Más simple de mantener

**Pasos:**
1. Eliminar campo `_previewEditor`
2. Eliminar método `InitializePreviewEditor()`
3. Implementar los 7 event handlers faltantes
4. Modificar `UpdatePreview()` y `UpdatePreviewForExternalBlock()` para actualizar `PreviewEditor` en lugar de `_previewEditor`

**Código necesario:**
```csharp
// 1. Click para abrir editor
private void PreviewTextBlock_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
{
    if (_currentElement is MathExternalBlock externalBlock)
    {
        // Construir texto con prefijo
        var lines = externalBlock.GetCodeLines();
        string currentLine = lines[externalBlock.CursorLine];
        string prefix = $"@{{{externalBlock.Language.ToLower()}}} Ln {externalBlock.CursorLine + 1}: ";
        string fullText = prefix + currentLine;

        // Mostrar editor
        PreviewTextBlock.Visibility = Visibility.Collapsed;
        PreviewEditorContainer.Visibility = Visibility.Visible;
        PreviewEditor.Text = fullText;
        PreviewEditor.CaretOffset = prefix.Length + externalBlock.CursorPosition;
        PreviewEditor.Focus();
    }
}

// 2. Sincronización en tiempo real
private void PreviewEditor_TextChanged(object sender, EventArgs e)
{
    if (_isApplyingPreviewEdit) return;
    if (PreviewEditor == null || !PreviewEditor.IsFocused) return;
    ApplyPreviewEditFromAvalonEdit(finalApply: false);
}

// 3. Detectar Enter
private void PreviewEditor_KeyDown(object sender, KeyEventArgs e)
{
    if (e.Key == Key.Enter)
    {
        ApplyPreviewEditFromAvalonEdit(finalApply: true);
        e.Handled = true;
    }
}

// 4. Cerrar al perder foco
private void PreviewEditor_LostFocus(object sender, RoutedEventArgs e)
{
    ApplyPreviewEditFromAvalonEdit(finalApply: true);
}

// 5. Método principal de sincronización
private bool _isApplyingPreviewEdit = false;

private void ApplyPreviewEditFromAvalonEdit(bool finalApply = true)
{
    if (_isApplyingPreviewEdit) return;
    if (_currentElement is not MathExternalBlock externalBlock) return;

    _isApplyingPreviewEdit = true;

    try
    {
        // Extraer texto sin prefijo
        string fullText = PreviewEditor.Text;
        string pattern = @"^@\{[^\}]+\}\s+Ln\s+\d+:\s*";
        string newText = System.Text.RegularExpressions.Regex.Replace(fullText, pattern, "");

        // Actualizar modelo
        externalBlock.SetCurrentLine(newText);

        // Actualizar cursor
        string prefix = fullText.Substring(0, fullText.Length - newText.Length);
        int caretInText = Math.Max(0, PreviewEditor.CaretOffset - prefix.Length);
        externalBlock.CursorPosition = Math.Max(0, Math.Min(caretInText, newText.Length));

        if (finalApply)
        {
            // Render completo y cerrar editor
            Render();
            PreviewEditorContainer.Visibility = Visibility.Collapsed;
            PreviewTextBlock.Visibility = Visibility.Visible;
            EditorCanvas.Focus();
        }
        else
        {
            // Actualización ligera sin parseo
            UpdateCurrentElementInCanvas();
        }
    }
    finally
    {
        _isApplyingPreviewEdit = false;
    }
}

// 6. Método para actualización ligera (sin Render completo)
private void UpdateCurrentElementInCanvas()
{
    if (_currentElement != null)
    {
        EditorCanvas.InvalidateVisual();
    }
}
```

### OPCIÓN 2: Usar solo _previewEditor programático

**Ventajas:**
- Control total sobre inicialización
- Ya existe parte del código

**Desventajas:**
- Más código
- Event handlers deben suscribirse programáticamente
- Menos declarativo

**NO RECOMENDADA** - más compleja sin beneficios claros

---

## 5. PLAN DE IMPLEMENTACIÓN RECOMENDADO

### PASO 1: Limpiar duplicación
1. Eliminar campo `_previewEditor` (línea 87)
2. Eliminar método `InitializePreviewEditor()` (líneas 155-194)
3. Eliminar todas las referencias a `_previewEditor` en UpdatePreview() y UpdatePreviewForExternalBlock()

### PASO 2: Implementar event handlers
1. Crear `PreviewTextBlock_MouseLeftButtonDown()`
2. Crear `PreviewEditor_TextChanged()`
3. Crear `PreviewEditor_KeyDown()`
4. Crear `PreviewEditor_LostFocus()`
5. Crear `ApplyPreviewEditFromAvalonEdit()`
6. Crear `UpdateCurrentElementInCanvas()`
7. Añadir campo `private bool _isApplyingPreviewEdit = false;`

### PASO 3: Actualizar métodos existentes
1. Modificar `UpdatePreview()` para actualizar `PreviewEditor` del XAML
2. Modificar `UpdatePreviewForExternalBlock()` para actualizar `PreviewEditor` del XAML

### PASO 4: Handlers deprecated (opcional - para eliminar errores)
Crear stubs vacíos o eliminar las referencias del XAML:
```csharp
private void PreviewEditTextBox_KeyDown(object sender, KeyEventArgs e) { }
private void PreviewEditTextBox_LostFocus(object sender, RoutedEventArgs e) { }
private void PreviewEditTextBox_TextChanged(object sender, TextChangedEventArgs e) { }
```

### PASO 5: Testing
1. Compilar sin errores
2. Probar Canvas → Preview (debe seguir funcionando)
3. Probar Preview → Canvas (nueva funcionalidad)
4. Verificar que no hay crashes de NullReferenceException

---

## 6. CÓDIGO CRÍTICO A REVISAR

### A) Parser NullReference Fix (ExpressionParser.cs:570-578)
Ya está implementado el fix:
```csharp
if (_parser != null)
{
    _parser.ClearCache();
    _parser = null;
}
```
✅ Mantener este fix

### B) Render() vs UpdateCurrentElementInCanvas()
- `Render()` - Completo, puede triggear parser, pesado
- `UpdateCurrentElementInCanvas()` - Ligero, solo `InvalidateVisual()`

Para sincronización en tiempo real (`finalApply=false`), usar `UpdateCurrentElementInCanvas()`
Para Enter o LostFocus (`finalApply=true`), usar `Render()`

---

## 7. RESUMEN EJECUTIVO

### PROBLEMA RAÍZ:
Hay dos instancias de AvalonEdit:
- `PreviewEditor` (XAML) - tiene event handlers definidos pero NO implementados
- `_previewEditor` (programático) - se actualiza pero no tiene event handlers

El código actualiza `_previewEditor` pero los event handlers están en `PreviewEditor`.

### SOLUCIÓN:
1. **Eliminar** `_previewEditor` completamente
2. **Usar solo** `PreviewEditor` del XAML
3. **Implementar** los 7 event handlers faltantes
4. **Actualizar** UpdatePreview() para usar `PreviewEditor` en lugar de `_previewEditor`

### RESULTADO ESPERADO:
- Canvas → Preview: ✅ Sigue funcionando
- Preview → Canvas: ✅ NUEVO - funcionará con edición en tiempo real
- Sin duplicación de controles
- Código más simple y mantenible
- Sin errores de compilación

---

## 8. SIGUIENTES PASOS

**ANTES DE IMPLEMENTAR:**
1. ✅ Revisión completa hecha (este documento)
2. ⏳ Aprobación del usuario
3. ⏳ Confirmar que OPCIÓN 1 es la correcta

**IMPLEMENTACIÓN:**
1. Hacer cambios según PLAN DE IMPLEMENTACIÓN (sección 5)
2. Compilar y verificar 0 errores
3. Probar con archivo test_code_c.cpd
4. Verificar logs en Desktop\calcpad_debug.log
5. Confirmar sincronización bidireccional

---

## NOTAS FINALES

- No crear complejidad innecesaria
- Seguir el principio: "es solo un editor debe escribir y pasarse a math editor y de math editor a textbox"
- Mantener código simple y directo
- NO usar logging exhaustivo en producción (solo durante debugging)
