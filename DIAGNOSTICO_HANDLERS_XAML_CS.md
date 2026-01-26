# DIAGNÓSTICO: Event Handlers XAML vs C#

## FECHA: 2026-01-22

---

## PROBLEMA: Handlers definidos en XAML pero NO implementados en C#

### Event Handlers en XAML (MathEditorControl.xaml)

```xml
Línea 38:  MouseLeftButtonDown="PreviewTextBlock_MouseLeftButtonDown"
Línea 54:  KeyDown="PreviewEditor_KeyDown"
Línea 55:  LostFocus="PreviewEditor_LostFocus"
Línea 56:  TextChanged="PreviewEditor_TextChanged"
Línea 64:  KeyDown="PreviewEditTextBox_KeyDown"
Línea 65:  LostFocus="PreviewEditTextBox_LostFocus"
Línea 66:  TextChanged="PreviewEditTextBox_TextChanged"
```

### Event Handlers en C# (MathEditorControl.xaml.cs)

```
RESULTADO: ❌ NINGUNO ENCONTRADO
```

**CONCLUSIÓN**: El XAML define 7 event handlers que NO EXISTEN en el C#.

---

## FLUJO DE MATHEDITOR: Texto Plano ↔ Canvas/HTML

### Texto Plano (Formato Calcpad)

```calcpad
x^2 + sqrt(y) + 'comentario
"Título en negrita"
a = 5
b_1 = 3.14
```

### Flujo: Texto → Canvas

```
1. Texto Plano Calcpad
   ↓
2. FromCalcpad(string code)  [línea 589]
   ↓
3. ParseCalcpad(string code)  [línea 700]
   - Detecta: ", ', /, ^, _, sqrt, etc.
   - Crea MathElements apropiados
   ↓
4. Lista de MathElements
   - MathText("x")
   - MathPower(base, exponent)
   - MathComment("comentario")
   - MathTitle("Título")
   - MathExternalBlock con Code
   ↓
5. Render()  [ejecuta al final de FromCalcpad]
   - Cada MathElement se dibuja en Canvas
   - Cada MathElement genera su forma visual
   ↓
6. Canvas Visual renderizado
```

### Flujo: Canvas → Texto

```
1. Canvas Visual (usuario edita)
   ↓
2. MathElements se actualizan internamente
   ↓
3. ToCalcpad()  [línea 571]
   - Recorre todas las líneas
   - Cada elemento llama su ToCalcpad()
   ↓
4. Texto Plano Calcpad
```

---

## PARA BLOQUES EXTERNOS (MathExternalBlock)

### Estructura de MathExternalBlock

```csharp
public class MathExternalBlock : MathElement
{
    public string Language { get; set; }      // "c", "html", etc.
    public string Code { get; set; }          // Código completo (multilínea)
    public int CursorLine { get; set; } = 0;  // Línea actual (0-based)
    public int CursorPosition { get; set; } = 0;  // Posición en línea

    public string[] GetCodeLines()  // Split por \n
    public string GetCurrentLine()  // Línea en CursorLine
    public void SetCurrentLine(string newContent)  // Actualiza línea
}
```

### Formato en Texto Plano Calcpad

```calcpad
| C [+]
#include <stdio.h>
int main() {
    printf("Hello\n");
    return 0;
}
@{end c}
```

### Formato en Preview Bar (lo que se debe mostrar en TextBox)

```
@{c} Ln 3:     printf("Hello\n");|
```

Donde:
- `@{c}` = lenguaje
- `Ln 3` = número de línea (1-based)
- `printf("Hello\n");` = código de la línea actual
- `|` = cursor (posición visual)

---

## SOLUCIÓN: Implementar los Event Handlers

### 1. PreviewTextBlock_MouseLeftButtonDown

**Propósito**: Cuando usuario hace click en preview bar, abrir el editor

**Flujo**:
```
Click en PreviewTextBlock
    ↓
Obtener externalBlock._currentElement
    ↓
Obtener línea actual: GetCodeLines()[CursorLine]
    ↓
Construir texto con prefijo: "@{c} Ln 3: printf(...);"
    ↓
Mostrar PreviewEditor
Ocultar PreviewTextBlock
    ↓
PreviewEditor.Text = texto con prefijo
PreviewEditor.CaretOffset = posición después del prefijo
PreviewEditor.Focus()
```

### 2. PreviewEditor_TextChanged

**Propósito**: Sincronizar en tiempo real mientras usuario escribe

**Flujo**:
```
Usuario escribe en PreviewEditor
    ↓
PreviewEditor_TextChanged se dispara
    ↓
Si no está aplicando ya (evitar recursión)
    ↓
Extraer texto sin prefijo usando Regex
    ↓
externalBlock.SetCurrentLine(nuevoTexto)
    ↓
Actualizar cursor: externalBlock.CursorPosition
    ↓
UpdateCurrentElementInCanvas() [ligero, sin parseo]
    ↓
Canvas se repinta (InvalidateVisual)
```

### 3. PreviewEditor_KeyDown

**Propósito**: Detectar Enter para cerrar el editor

**Flujo**:
```
Usuario presiona Enter
    ↓
ApplyPreviewEditFromAvalonEdit(finalApply: true)
    ↓
Render() completo (con parseo)
    ↓
Cerrar editor:
    PreviewEditor.Visibility = Collapsed
    PreviewTextBlock.Visibility = Visible
    ↓
EditorCanvas.Focus()
```

### 4. PreviewEditor_LostFocus

**Propósito**: Cerrar editor cuando pierde foco

**Flujo**:
```
Usuario hace click fuera del editor
    ↓
ApplyPreviewEditFromAvalonEdit(finalApply: true)
    ↓
Mismo flujo que Enter
```

---

## CÓDIGO A IMPLEMENTAR

```csharp
// Campo para evitar recursión
private bool _isApplyingPreviewEdit = false;

// 1. Click para abrir editor
private void PreviewTextBlock_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
{
    if (_currentElement is MathExternalBlock externalBlock)
    {
        var lines = externalBlock.GetCodeLines();
        if (externalBlock.CursorLine >= 0 && externalBlock.CursorLine < lines.Length)
        {
            string currentLine = lines[externalBlock.CursorLine];
            string prefix = $"@{{{externalBlock.Language.ToLower()}}} Ln {externalBlock.CursorLine + 1}: ";
            string fullText = prefix + currentLine;

            PreviewTextBlock.Visibility = Visibility.Collapsed;
            PreviewEditorContainer.Visibility = Visibility.Visible;
            PreviewEditor.Text = fullText;
            PreviewEditor.CaretOffset = prefix.Length + externalBlock.CursorPosition;
            PreviewEditor.Focus();
        }
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
private void ApplyPreviewEditFromAvalonEdit(bool finalApply = true)
{
    if (_isApplyingPreviewEdit) return;
    if (_currentElement is not MathExternalBlock externalBlock) return;

    _isApplyingPreviewEdit = true;

    try
    {
        // Extraer texto sin prefijo "@{lang} Ln X: "
        string fullText = PreviewEditor.Text;
        string pattern = @"^@\{[^\}]+\}\s+Ln\s+\d+:\s*";
        string newText = System.Text.RegularExpressions.Regex.Replace(fullText, pattern, "");

        // Actualizar modelo
        externalBlock.SetCurrentLine(newText);

        // Actualizar posición del cursor
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
            // Actualización ligera sin parseo completo
            UpdateCurrentElementInCanvas();
        }
    }
    finally
    {
        _isApplyingPreviewEdit = false;
    }
}

// 6. Actualización ligera del canvas (sin Render completo)
private void UpdateCurrentElementInCanvas()
{
    if (_currentElement != null)
    {
        EditorCanvas.InvalidateVisual();
    }
}

// 7-9. Stubs para TextBox deprecated (evitar errores de compilación)
private void PreviewEditTextBox_KeyDown(object sender, KeyEventArgs e) { }
private void PreviewEditTextBox_LostFocus(object sender, RoutedEventArgs e) { }
private void PreviewEditTextBox_TextChanged(object sender, TextChangedEventArgs e) { }
```

---

## CAMBIOS ADICIONALES REQUERIDOS

### Eliminar duplicación de AvalonEdit

**EN C# - ELIMINAR:**
```csharp
// Línea 87
private TextEditor _previewEditor;

// Líneas 155-194
private void InitializePreviewEditor() { ... }
```

**EN UpdatePreview() - CAMBIAR:**
```csharp
// ANTES (líneas 1161-1164):
if (_previewEditor != null)
{
    _previewEditor.Text = lineText;
}

// DESPUÉS:
if (PreviewEditor != null)
{
    PreviewEditor.Text = lineText;
}
```

**EN UpdatePreviewForExternalBlock() - CAMBIAR:**
```csharp
// ANTES (líneas 1196-1199):
if (_previewEditor != null)
{
    _previewEditor.Text = lineText;
}

// DESPUÉS:
if (PreviewEditor != null)
{
    PreviewEditor.Text = lineText;
}
```

---

## RESULTADO ESPERADO

Después de implementar estos cambios:

1. ✅ Compilación sin errores
2. ✅ Canvas → Preview: Sigue funcionando (UpdatePreview se ejecuta)
3. ✅ Preview → Canvas: NUEVO - funciona con edición en tiempo real
4. ✅ Click en preview bar → Abre editor
5. ✅ Escribir en editor → Se ve en canvas en tiempo real
6. ✅ Enter o click fuera → Cierra editor y hace Render completo
7. ✅ Sin duplicación de controles
8. ✅ Código simple y directo

---

## PRINCIPIO RECTOR

> "es solo un editor debe escribir y pasarse a math editor y de math editor a textbox"

La solución sigue este principio:
- Texto Plano Calcpad ↔ MathElements ↔ Canvas Visual
- Para bloques externos: código de línea actual ↔ PreviewEditor ↔ Canvas
- Sin complejidad innecesaria
- Sincronización directa y en tiempo real
