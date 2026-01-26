# ✅ IMPLEMENTACIÓN: AvalonEdit en Barra de Preview

**Fecha**: 2026-01-21 23:10
**Branch**: feature/matheditor-mejoras-v1.0.0
**Cambio Principal**: Reemplazar TextBox por AvalonEdit en la barra de preview

---

## 🎯 MOTIVACIÓN

**Sugerencia del usuario**: Usar AvalonEdit en lugar del TextBox simple para la barra de preview porque:

1. ✅ AvalonEdit tiene mejor sincronización implementada
2. ✅ Soporte nativo para syntax highlighting
3. ✅ Manejo robusto del cursor y selección
4. ✅ Ideal para edición de código complejo
5. ✅ Ya está integrado en el proyecto (usado en AvalonEdit principal)

**Problema anterior con TextBox**:
- El TextBox simple se sobrescribía durante la edición
- No tenía syntax highlighting
- Sincronización problemática con el MathEditor
- No era ideal para código complejo

---

## 📝 CAMBIOS IMPLEMENTADOS

### 1️⃣ XAML - MathEditorControl.xaml

**Namespace agregado** (línea 5):
```xml
xmlns:avalonEdit="http://icsharpcode.net/sharpdevelop/avalonedit"
```

**PreviewEditorContainer actualizado** (líneas 41-56):
```xml
<!-- AvalonEdit para edición directa con syntax highlighting (oculto por defecto) -->
<Border x:Name="PreviewEditorContainer" BorderThickness="1" BorderBrush="#1976D2"
        Background="White" Height="20" MinWidth="200" MaxWidth="600"
        VerticalAlignment="Center" Margin="0,0,0,0" Visibility="Collapsed">
    <avalonEdit:TextEditor x:Name="PreviewEditor"
                           FontFamily="Consolas" FontSize="10"
                           Background="White" Foreground="#333"
                           VerticalScrollBarVisibility="Hidden"
                           HorizontalScrollBarVisibility="Hidden"
                           ShowLineNumbers="False"
                           WordWrap="False"
                           Padding="2,0,0,0"
                           KeyDown="PreviewEditor_KeyDown"
                           LostFocus="PreviewEditor_LostFocus"
                           TextChanged="PreviewEditor_TextChanged"/>
</Border>

<!-- DEPRECATED: TextBox antiguo - mantener para referencia temporal -->
<TextBox x:Name="PreviewEditTextBox" ... Visibility="Collapsed" />
```

**Características del AvalonEdit**:
- Altura: 20px (una línea)
- Sin scroll bars (edición inline)
- Sin números de línea
- Sin word wrap
- Border azul cuando está activo
- Font: Consolas 10pt

---

### 2️⃣ CODE-BEHIND - MathEditorControl.xaml.cs

#### Event Handlers Nuevos:

**PreviewEditor_KeyDown** (línea 390-402):
```csharp
private void PreviewEditor_KeyDown(object sender, KeyEventArgs e)
{
    if (e.Key == Key.Enter)
    {
        ApplyPreviewEditFromAvalonEdit();
        e.Handled = true;
    }
    else if (e.Key == Key.Escape)
    {
        CancelPreviewEditFromAvalonEdit();
        e.Handled = true;
    }
}
```

**PreviewEditor_LostFocus** (línea 407-415):
```csharp
private void PreviewEditor_LostFocus(object sender, RoutedEventArgs e)
{
    if (_isApplyingPreviewEdit) return;

    if (PreviewEditorContainer?.Visibility == Visibility.Visible && PreviewEditor != null)
    {
        ApplyPreviewEditFromAvalonEdit(finalApply: true);
    }
}
```

**PreviewEditor_TextChanged** (línea 420-427):
```csharp
private void PreviewEditor_TextChanged(object sender, EventArgs e)
{
    if (_isApplyingPreviewEdit) return;
    if (PreviewEditor == null || !PreviewEditor.IsFocused) return;

    // Sincronización en tiempo real con AvalonEdit
    ApplyPreviewEditFromAvalonEdit(finalApply: false);
}
```

#### Funciones de Apoyo:

**ApplyPreviewEditFromAvalonEdit()** (línea 529-594):
- Extrae texto del AvalonEdit usando `PreviewEditor.Text`
- Obtiene posición del cursor con `PreviewEditor.CaretOffset`
- Quita el prefijo `@{lang} Ln X: ` para bloques externos
- Actualiza el modelo (MathExternalBlock, MathText, MathComment, etc.)
- Sincroniza cursor: `externalBlock.CursorPosition`
- Si `finalApply=true`: Cierra AvalonEdit, hace Render(), muestra TextBlock

**CancelPreviewEditFromAvalonEdit()** (línea 599-606):
- Oculta PreviewEditorContainer
- Muestra PreviewTextBlock
- Restaura foco al MathEditor

#### Click Handler Modificado:

**PreviewTextBlock_MouseLeftButtonDown** (línea 270-316):
```csharp
// ANTES:
PreviewEditTextBox.Text = currentText;
PreviewEditTextBox.Visibility = Visibility.Visible;
PreviewEditTextBox.Focus();
PreviewEditTextBox.SelectionStart = cursorPosition;

// AHORA:
PreviewEditor.Text = currentText;
PreviewEditorContainer.Visibility = Visibility.Visible;
PreviewEditor.Focus();
PreviewEditor.CaretOffset = cursorPosition;  // ← Cursor de AvalonEdit
```

#### Render() Fix Actualizado (línea 1437-1445):
```csharp
// FIX: No actualizar si el usuario está editando en preview (TextBox o AvalonEdit)
bool isEditingInTextBox = PreviewEditTextBox?.Visibility == Visibility.Visible
                          && PreviewEditTextBox.IsFocused;
bool isEditingInAvalonEdit = PreviewEditorContainer?.Visibility == Visibility.Visible
                              && PreviewEditor != null && PreviewEditor.IsFocused;

if (!isEditingInTextBox && !isEditingInAvalonEdit)
{
    UpdatePreview();
}
```

---

## 🔄 FLUJO DE SINCRONIZACIÓN

### Cuando el usuario hace click en la barra de preview:

```
Usuario click en "@{c} Ln 4: printf(...)"
  ↓
PreviewTextBlock_MouseLeftButtonDown()
  ↓
Construye texto: "@{c} Ln 4: printf("Hola desde C!\n");"
  ↓
PreviewEditor.Text = texto completo
PreviewEditor.CaretOffset = posición del cursor
  ↓
Muestra PreviewEditorContainer (AvalonEdit)
Oculta PreviewTextBlock
  ↓
AvalonEdit obtiene foco → Usuario puede editar
```

### Cuando el usuario escribe en el AvalonEdit:

```
Usuario escribe "test"
  ↓
PreviewEditor_TextChanged se dispara
  ↓
ApplyPreviewEditFromAvalonEdit(finalApply=false)
  ↓
Extrae texto sin prefijo: "test"
  ↓
externalBlock.SetCurrentLine("test")
externalBlock.CursorPosition = posición ajustada
  ↓
Modelo actualizado ✓
AvalonEdit NO se sobrescribe (porque tiene foco)
  ↓
Render() se ejecuta pero NO llama UpdatePreview()
(porque detecta que AvalonEdit tiene foco)
```

### Cuando el usuario presiona Enter o pierde foco:

```
Usuario presiona Enter
  ↓
PreviewEditor_KeyDown detecta Enter
  ↓
ApplyPreviewEditFromAvalonEdit(finalApply=true)
  ↓
Actualiza modelo (igual que antes)
  ↓
Render() → Redibuja canvas con cambios ✓
UpdatePreview() → Actualiza TextBlock
  ↓
Oculta AvalonEdit, muestra TextBlock
  ↓
Canvas actualizado con cambios aplicados
```

---

## 🎨 VENTAJAS DE AVALONEDIT

### vs TextBox simple:

| Característica | TextBox | AvalonEdit |
|----------------|---------|------------|
| Syntax highlighting | ❌ No | ✅ Sí (futuro) |
| Manejo cursor | Básico | ✅ Robusto |
| Sincronización | ❌ Problemática | ✅ Robusta |
| Código complejo | ❌ Limitado | ✅ Excelente |
| Consistencia | ❌ Diferente | ✅ Igual que editor principal |
| CaretOffset | ❌ SelectionStart | ✅ CaretOffset (más preciso) |

### Consistencia con AvalonEdit principal:

- Mismo componente usado en ambos lados
- Misma API para manipular texto y cursor
- Mismo comportamiento de edición
- Fácil sincronización bidireccional

---

## 🧪 TESTING REQUERIDO

### Casos de prueba:

1. **Click en preview → AvalonEdit aparece**:
   - ✅ Verificar que AvalonEdit se muestra
   - ✅ Cursor en posición correcta
   - ✅ Prefijo `@{c} Ln 4: ` visible

2. **Escribir en AvalonEdit**:
   - ✅ Texto aparece mientras escribes
   - ✅ NO se sobrescribe
   - ✅ Cursor se mantiene en posición

3. **Presionar Enter**:
   - ✅ AvalonEdit se cierra
   - ✅ Cambios aplicados al canvas
   - ✅ TextBlock muestra texto actualizado

4. **Presionar Escape**:
   - ✅ AvalonEdit se cierra sin aplicar cambios
   - ✅ Vuelve al estado anterior

5. **Perder foco (click fuera)**:
   - ✅ AvalonEdit se cierra
   - ✅ Cambios aplicados automáticamente

6. **Editar código complejo**:
   - ✅ Múltiples líneas (si fuera necesario en futuro)
   - ✅ Caracteres especiales
   - ✅ Syntax highlighting (futuro)

---

## 📊 IMPACTO

- **Archivos modificados**: 2
  - `MathEditorControl.xaml` (namespace + AvalonEdit control)
  - `MathEditorControl.xaml.cs` (event handlers + sync logic)

- **Líneas agregadas**: ~150 líneas
  - XAML: ~15 líneas
  - C#: ~135 líneas (handlers + apply/cancel functions)

- **Líneas modificadas**: ~20 líneas
  - Click handler
  - Render() check

- **Deprecado (no eliminado)**: TextBox antiguo (líneas 58-66)
  - Mantener para referencia temporal
  - Puede eliminarse en próxima versión

- **Compatibilidad**: 100% compatible
- **Regresiones**: Ninguna esperada
- **Performance**: Similar o mejor (AvalonEdit optimizado)

---

## 🔮 MEJORAS FUTURAS

### Syntax Highlighting:
```csharp
// Detectar lenguaje del bloque externo
if (_currentElement is MathExternalBlock externalBlock)
{
    var lang = externalBlock.Language.ToLower();

    // Aplicar syntax highlighting según lenguaje
    if (lang == "c" || lang == "cpp")
        PreviewEditor.SyntaxHighlighting = HighlightingManager.Instance.GetDefinition("C++");
    else if (lang == "html")
        PreviewEditor.SyntaxHighlighting = HighlightingManager.Instance.GetDefinition("HTML");
    // etc...
}
```

### Multi-línea:
- Ajustar altura del PreviewEditorContainer dinámicamente
- Permitir editar múltiples líneas si es necesario
- Agregar scroll vertical solo si necesario

### Auto-complete:
- Usar el sistema de auto-complete de AvalonEdit
- Sugerir funciones, keywords según el lenguaje

---

## ✅ VERIFICACIÓN

- [x] Namespace AvalonEdit agregado al XAML
- [x] PreviewEditor definido en XAML
- [x] Event handlers implementados (KeyDown, LostFocus, TextChanged)
- [x] ApplyPreviewEditFromAvalonEdit() implementada
- [x] CancelPreviewEditFromAvalonEdit() implementada
- [x] Click handler modificado para usar AvalonEdit
- [x] Render() fix actualizado para check AvalonEdit
- [x] Compilación exitosa (0 errores, 40 warnings no críticos)
- [x] Calcpad ejecutándose
- [ ] **PENDIENTE: Testing por usuario**

---

## 📝 NOTAS DE IMPLEMENTACIÓN

### Decisiones de diseño:

1. **Mantener TextBox deprecated**: Para rollback rápido si hay problemas
2. **Altura fija 20px**: Una línea de edición (puede cambiar en futuro)
3. **Sin syntax highlighting inicial**: Implementar gradualmente
4. **Mismo prefijo**: `@{lang} Ln X: ` se mantiene igual
5. **CaretOffset vs SelectionStart**: AvalonEdit usa CaretOffset (más preciso)

### Consideraciones:

- AvalonEdit es más pesado que TextBox, pero la diferencia es mínima
- El componente ya está cargado en memoria (usado en editor principal)
- Sincronización más robusta compensa el overhead mínimo

---

**Status**: ✅ IMPLEMENTADO Y COMPILADO
**Testing**: PENDIENTE DE VERIFICACIÓN POR USUARIO
**Próximo paso**: Usuario debe probar edición en barra de preview

---

**Desarrollado con** ❤️ **por el equipo Calcpad Fork**
**Sugerencia del usuario implementada exitosamente**
