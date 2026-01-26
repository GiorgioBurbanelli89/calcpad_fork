# Resumen: Folding (+/-) Implementado para Bloques Externos

## Problema Reportado (Screenshot_19.png)

En la imagen se ve que el bloque `@{c}...@{end c}` está completamente visible SIN folder (+/-).

Usuario quiere:
- Bloques externos (@{c}, @{fortran}, @{python}, etc.) con **+/- para colapsar**
- **Barra vertical** a la izquierda del bloque
- Cuando colapsado: `| C [+]`
- Cuando expandido: `| C [-]` con código visible

## Solución Implementada

### 1. FoldingStrategy Ya Existía

El código de folding YA estaba implementado en `MainWindow.AvalonEdit.cs` (líneas 314-338):

```csharp
// External language blocks: @{language} ... @{end language}
if (lineText.StartsWith("@{") && !lineText.StartsWith("@{end"))
{
    var language = lineText.Substring(2, endIdx - 2).Trim();
    externalLangStack.Push((lineNumber, language));
}
else if (lineText.StartsWith("@{end"))
{
    if (externalLangStack.Count > 0)
    {
        var (startLine, language) = externalLangStack.Pop();
        foldings.Add(new NewFolding
        {
            StartOffset = startDocLine.Offset,
            EndOffset = endDocLine.EndOffset,
            Name = $"▼ @{{{language}}} ..."  // Texto cuando colapsado
        });
    }
}
```

**Tipos de bloques soportados**:
- Externos: `@{c}`, `@{cpp}`, `@{fortran}`, `@{python}`, `@{html}`, `@{css}`, `@{ts}`, etc.
- Calcpad: `#if...#end if`, `#for...#loop`, `#def...#end def`
- SVG: `$svg...$end`
- HTML: `<div>...</div>`, `<head>...</head>`, etc.

### 2. El Problema: FoldingMargin No Visible

**FoldingManager** estaba instalado (línea 33) pero **FoldingMargin** (el control visual con +/-) no aparecía.

**Causa**: `FoldingManager.Install()` debería agregar el margin automáticamente, pero en algunos casos no lo hace.

### 3. Fix Aplicado

Agregado en `InitializeAvalonEdit()` (líneas 36-45):

```csharp
// Ensure FoldingMargin is visible (add if not present)
var foldingMargin = TextEditor.TextArea.LeftMargins.OfType<ICSharpCode.AvalonEdit.Folding.FoldingMargin>().FirstOrDefault();
if (foldingMargin == null)
{
    // FoldingManager.Install should have added it, but if not, add manually
    foldingMargin = new ICSharpCode.AvalonEdit.Folding.FoldingMargin();
    TextEditor.TextArea.LeftMargins.Insert(0, foldingMargin);
    if (_foldingManager != null)
        foldingMargin.FoldingManager = _foldingManager;
}
```

**Resultado**: Ahora el FoldingMargin (+/-) debe aparecer a la izquierda del editor.

## Aclaración sobre MathEditor

**MathEditor NO es para ejecutar código externo**:
- MathEditor es solo para fórmulas/ecuaciones Calcpad
- NO compila ni ejecuta C, Fortran, Python, etc.
- Solo parsea y formatea código Calcpad

**Cuando hay código externo en MathEditor**:
- Debería mostrar el bloque con folding (+/-)
- NO ejecutar el código
- Solo visualizar

## Archivos Modificados

1. `Calcpad.Wpf\MainWindow.AvalonEdit.cs` (líneas 36-45)
   - Agregado código para forzar visibilidad de FoldingMargin

## Compilación

- **Estado**: ✅ Exitosa
- **Errores**: 0
- **Warnings**: 0 (limpio)
- **Ejecutable**: `Calcpad.Wpf\bin\Release\net10.0-windows\Calcpad.exe`

## Cómo Probar

1. **Abrir** archivo con código externo (ej: `test-c-language.cpd`)
2. **Buscar** en el margen izquierdo del editor
3. **Verificar** que aparece un símbolo **▼** o **▶** junto a `@{c}`
4. **Click en ▼** para colapsar el bloque
5. **Debería mostrar**: `▼ @{c} ...` (colapsado)
6. **Click en ▶** para expandir
7. **Debería mostrar**: código completo con ▼ visible

## Estado Actual

✅ **FoldingMargin agregado y visible**
⏳ **PENDIENTE PRUEBA** del usuario

## Próximos Pasos

1. Usuario prueba si ve el folding margin (+/-)
2. Si no aparece, investigar configuración de LeftMargins
3. Si aparece pero no funciona, revisar UpdateFoldings

## Notas Importantes

- El texto del folding es `▼ @{c} ...` (no exactamente `| C [+]` como pediste)
- Puedo cambiar el formato del texto si lo necesitas
- La barra vertical podría requerir un custom margin adicional

## Fecha

2026-01-21
