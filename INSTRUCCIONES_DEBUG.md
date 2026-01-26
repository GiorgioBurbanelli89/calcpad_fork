# 🔍 INSTRUCCIONES PARA DEBUG LÍNEA POR LÍNEA

## ✅ LOGGING EXHAUSTIVO ACTIVADO

He agregado logging detallado línea por línea como en MATLAB. Ahora cada función registra exactamente qué está haciendo en cada paso.

## 📋 CÓMO USAR:

### Paso 1: Monitorear el log en tiempo real

Abre PowerShell y ejecuta:
```powershell
cd "C:\Users\j-b-j\Documents\Calcpad-7.5.7"
powershell -ExecutionPolicy Bypass -File watch_log.ps1
```

Esto monitoreará el archivo `C:\Users\j-b-j\Desktop\calcpad_debug.log` en tiempo real.

### Paso 2: Ejecutar las acciones en Calcpad

Mientras el monitor está corriendo, haz lo siguiente en Calcpad:

1. **Abre o crea un archivo `.cpd` con código C**:
   ```
   Test C Language

   | C [+][-]
   #include <stdio.h>

   int main() {
       printf("Hola desde C!\n");
       return 0;
   }
   ```

2. **Navega a una línea de código** (usa las flechas ↑↓)

3. **Haz click en la barra amarilla de preview** (donde dice `@{c} Ln 4: printf...`)

4. **Observa el log** - verás exactamente qué pasa paso por paso:
   ```
   ========== PreviewTextBlock_MouseLeftButtonDown START ==========
     _currentElement type = MathExternalBlock
     -> MathExternalBlock detected for click
     lang = 'c'
     lineNum = 4
     _previewEditPrefix = '@{c} Ln 4: '
     currentLine = 'printf("Hola desde C!\n");'
     currentText = '@{c} Ln 4: printf("Hola desde C!\n");'
     cursorPosition = 14
     -> Setting PreviewEditor.Text = '...'
     -> Hiding PreviewTextBlock, showing PreviewEditorContainer
     -> Calling PreviewEditor.Focus()
     -> Setting PreviewEditor.CaretOffset = 14
     -> Click handler complete
   ========== PreviewTextBlock_MouseLeftButtonDown END ==========
   ```

5. **Escribe algo en el AvalonEdit que aparece**

6. **Observa el log nuevamente** - verás:
   ```
   ========== PreviewEditor_TextChanged START ==========
     _isApplyingPreviewEdit = False
     PreviewEditor == null? False
     PreviewEditor.IsFocused = True
     -> Calling ApplyPreviewEditFromAvalonEdit(finalApply=false)
   ========== ApplyPreviewEditFromAvalonEdit START (finalApply=False) ==========
     fullText = '@{c} Ln 4: printf("TEST");'
     cursorPos = 23
     _currentElement type = MathExternalBlock
     _previewEditPrefixLength = 14
     -> MathExternalBlock detected
     colonPos = 12
     Using colon method: newText = 'printf("TEST");', adjustedCursorPos = 9
     -> Calling externalBlock.SetCurrentLine('printf("TEST");')
     -> Setting externalBlock.CursorPosition = 9
     -> Model updated successfully
     finalApply=false -> Light update only
       -> Calling UpdateCurrentElementInCanvas()
       -> Light update complete
   ========== ApplyPreviewEditFromAvalonEdit END ==========
   ```

7. **Presiona Enter**

8. **Observa el log final**:
   ```
   ========== PreviewEditor_KeyDown (Enter) ==========
     -> Calling ApplyPreviewEditFromAvalonEdit(finalApply=true)
   ========== ApplyPreviewEditFromAvalonEdit START (finalApply=True) ==========
     [... mismo proceso ...]
     finalApply=true -> Full render sequence
       -> Calling Render()
       -> Hiding PreviewEditorContainer
       -> Calling UpdatePreview()
       -> Calling Focus()
       -> Final apply complete
   ========== ApplyPreviewEditFromAvalonEdit END ==========
   ```

## 🔍 QUÉ BUSCAR EN EL LOG:

### Si dice "ya no puedo ver en qué línea de código voy":

Busca en el log:
- ¿Se llama correctamente `PreviewTextBlock_MouseLeftButtonDown`?
- ¿Cuál es el valor de `currentText` y `cursorPosition`?
- ¿Se muestra correctamente `PreviewEditorContainer`?
- ¿Se oculta `PreviewTextBlock`?
- ¿El `CaretOffset` está en la posición correcta?

### Si no se sincroniza Canvas ↔ TextBox:

Busca en el log:
- ¿Se llama `ApplyPreviewEditFromAvalonEdit`?
- ¿Cuál es el valor de `newText` extraído?
- ¿Se llama `externalBlock.SetCurrentLine()` correctamente?
- ¿Se llama `UpdateCurrentElementInCanvas()` o `Render()`?

### Si crashea:

Busca en el log:
- ¿Dónde se detiene el flujo?
- ¿Hay algún "ERROR:" en el log?
- ¿Qué fue lo último que se ejecutó antes del crash?

## 📝 ALTERNATIVA: Ver log completo después

Si prefieres ver el log completo después de hacer las acciones:

```powershell
Get-Content "C:\Users\j-b-j\Desktop\calcpad_debug.log" -Tail 200
```

O abre el archivo en un editor de texto.

## ✅ ESTADO ACTUAL:

- ✅ Calcpad compilado con logging exhaustivo
- ✅ Calcpad ejecutándose
- ✅ Log ubicado en: `C:\Users\j-b-j\Desktop\calcpad_debug.log`
- 🔄 Esperando que hagas las pruebas

## 📊 RESUMEN:

Ahora tenemos un **depurador línea por línea** como en MATLAB:
- Cada función registra ENTRADA y SALIDA
- Cada variable importante se registra
- Cada decisión (if/else) se registra
- Cada llamada a función se registra

Con esto podemos ver **exactamente** qué está pasando en cada paso y dónde está el problema.

---

**¿Listo para probar?** Ejecuta el monitor del log y luego haz las acciones en Calcpad. Dime qué ves en el log.
