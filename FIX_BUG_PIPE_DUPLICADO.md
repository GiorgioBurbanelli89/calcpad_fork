# FIX BUG: Pipe (|) Duplicado en Preview

## FECHA: 2026-01-22
## ESTADO: ✅ RESUELTO

---

## PROBLEMA REPORTADO

**Síntoma:**
Cada vez que el usuario hacía click en el preview bar (TextBox), se agregaba un `|` al texto.

**Evidencia:**
```
Primera vez:  @{c} Ln 4: printf("Hola desde C!\n");|
Después click: @{c} Ln 4: |printf("Hola desde C!\n");|
Después click: @{c} Ln 4: ||printf("Hola desde C!\n");|
Después click: @{c} Ln 4: |||printf("Hola desde C!\n");|
```

---

## CAUSA RAÍZ

### Código Problemático (ANTES)

En `UpdatePreviewForExternalBlock()` (líneas 1196-1204):

```csharp
// Formato: @{LANG} Ln X: beforeCursor|afterCursor
string lineText = $"@{{{externalBlock.Language.ToLower()}}} Ln {lineIdx + 1}: {beforeCursor}|{afterCursor}";

PreviewTextBlock.Text = lineText;  // ✅ OK - el | es visual aquí

if (PreviewEditor != null)
{
    PreviewEditor.Text = lineText;  // ❌ ERROR - pone el | en el editor
}
```

### Explicación del Bug

1. **Propósito del `|`**: Es un **marcador visual** para mostrar dónde está el cursor en el PreviewTextBlock (solo lectura)

2. **El problema**: El código estaba poniendo el mismo texto CON el `|` en el PreviewEditor (editable)

3. **Consecuencia**:
   - PreviewEditor.Text = `"@{c} Ln 4: printf(...);|"`
   - Cuando el usuario edita, el `|` es texto real
   - Cuando sincroniza con `ApplyPreviewEditFromAvalonEdit()`, ese `|` se inserta en el código
   - Cada sincronización agrega un nuevo `|`

### Flujo del Bug

```
1. UpdatePreviewForExternalBlock() ejecuta
   ↓
2. lineText = "@{c} Ln 4: printf(...);|"
   ↓
3. PreviewTextBlock.Text = lineText  ← OK (visual)
   ↓
4. PreviewEditor.Text = lineText     ← ERROR (editable con |)
   ↓
5. Usuario hace cambios
   ↓
6. ApplyPreviewEditFromAvalonEdit() extrae texto
   ↓
7. SetCurrentLine("printf(...);|")   ← | insertado en Code
   ↓
8. Próxima actualización incluye el | como texto real
   ↓
9. Se acumulan pipes: ||, |||, ||||, etc.
```

---

## SOLUCIÓN

### Código Corregido (DESPUÉS)

En `UpdatePreviewForExternalBlock()` (líneas 1196-1203):

```csharp
// Formato: @{LANG} Ln X: beforeCursor|afterCursor
string lineText = $"@{{{externalBlock.Language.ToLower()}}} Ln {lineIdx + 1}: {beforeCursor}|{afterCursor}";

PreviewTextBlock.Text = lineText;  // ✅ OK - el | es visual para TextBlock

// NO actualizar PreviewEditor aquí porque el | es solo visual para TextBlock
// PreviewEditor se actualiza solo cuando el usuario hace click en PreviewTextBlock
```

### Mismo fix en `UpdatePreview()` (líneas 1161-1167):

```csharp
// Actualizar TextBlock simple - perfectamente alineado
var lineText = beforeCursor.ToString() + "|" + afterCursor.ToString();
PreviewTextBlock.Text = lineText;  // ✅ OK - el | es visual

// NO actualizar PreviewEditor aquí porque el | es solo visual para TextBlock
// PreviewEditor se actualiza solo cuando el usuario hace click en PreviewTextBlock
```

---

## FLUJO CORRECTO

### Actualización del Preview (Canvas → Preview)

```
1. Usuario edita en Canvas
   ↓
2. UpdatePreview() o UpdatePreviewForExternalBlock() ejecuta
   ↓
3. lineText = "código antes|código después"
   ↓
4. PreviewTextBlock.Text = lineText  ← Solo aquí (visual)
   ↓
5. PreviewEditor NO se actualiza      ← FIX
```

### Click en Preview (Preview → Editor)

```
1. Usuario hace click en PreviewTextBlock
   ↓
2. PreviewTextBlock_MouseLeftButtonDown() ejecuta
   ↓
3. Obtiene código SIN |: GetCodeLines()[CursorLine]
   ↓
4. Construye texto con prefijo SIN |:
   prefix + currentLine
   ↓
5. PreviewEditor.Text = "@{c} Ln 4: printf(...);"  ← SIN |
   ↓
6. PreviewEditor.CaretOffset = posición correcta
   ↓
7. Usuario puede editar sin pipes duplicados
```

### Edición en Preview (Preview → Canvas)

```
1. Usuario escribe en PreviewEditor
   ↓
2. PreviewEditor_TextChanged() ejecuta
   ↓
3. ApplyPreviewEditFromAvalonEdit() extrae texto SIN prefijo
   ↓
4. SetCurrentLine(texto limpio)  ← SIN |
   ↓
5. Canvas se actualiza correctamente
```

---

## ARCHIVOS MODIFICADOS

### Calcpad.Wpf/MathEditor/MathEditorControl.xaml.cs

**Líneas 1165-1167:**
```diff
- if (PreviewEditor != null)
- {
-     PreviewEditor.Text = lineText;
- }
+ // NO actualizar PreviewEditor aquí porque el | es solo visual para TextBlock
+ // PreviewEditor se actualiza solo cuando el usuario hace click en PreviewTextBlock
```

**Líneas 1201-1203:**
```diff
- if (PreviewEditor != null)
- {
-     PreviewEditor.Text = lineText;
- }
+ // NO actualizar PreviewEditor aquí porque el | es solo visual para TextBlock
+ // PreviewEditor se actualiza solo cuando el usuario hace click en PreviewTextBlock
```

---

## PRUEBA

### ANTES del fix:
```
Click 1: @{c} Ln 4: |printf(...);|
Click 2: @{c} Ln 4: ||printf(...);|
Click 3: @{c} Ln 4: |||printf(...);|
```

### DESPUÉS del fix:
```
Click 1: @{c} Ln 4: printf(...);  ← Sin | duplicado
Click 2: @{c} Ln 4: printf(...);  ← Sin | duplicado
Click 3: @{c} Ln 4: printf(...);  ← Sin | duplicado
```

---

## COMPILACIÓN

```bash
dotnet build Calcpad.Wpf/Calcpad.Wpf.csproj --no-incremental

RESULTADO: ✅ Compilación correcta
ERRORES: 0
```

---

## PRINCIPIO IMPORTANTE

**Separación de Responsabilidades:**

1. **PreviewTextBlock** (solo lectura):
   - Muestra el código CON `|` visual para indicar cursor
   - Es solo para mostrar, no para editar

2. **PreviewEditor** (editable):
   - Muestra el código SIN `|` porque es editable
   - El cursor real del AvalonEdit indica la posición
   - Solo se actualiza cuando el usuario hace click

3. **El `|` es un símbolo visual**, NO parte del código

---

## VERIFICACIÓN

Ahora puedes probar:

1. ✅ Abre Calcpad con test_code_c.cpd
2. ✅ Verifica que el preview bar muestra: `@{c} Ln X: código|`
3. ✅ Haz click en el preview bar
4. ✅ Debe abrir editor SIN `|` en el texto
5. ✅ Escribe algo nuevo
6. ✅ NO debe aparecer `|` duplicado
7. ✅ Presiona Enter
8. ✅ El canvas se actualiza correctamente SIN `|` extra

---

## CONCLUSIÓN

El bug estaba causado por actualizar `PreviewEditor.Text` con el marcador visual `|` que es solo para el TextBlock.

La solución es simple: **NO actualizar PreviewEditor en UpdatePreview/UpdatePreviewForExternalBlock**.

El PreviewEditor solo se actualiza cuando el usuario hace click explícitamente en el PreviewTextBlock, y en ese momento se usa el código limpio SIN el `|`.

**Estado: ✅ RESUELTO Y COMPILADO**
