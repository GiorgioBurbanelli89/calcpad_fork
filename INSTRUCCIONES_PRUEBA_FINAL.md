# INSTRUCCIONES PARA PRUEBA FINAL

## FECHA: 2026-01-22

---

## PROBLEMA RESUELTO: Pipe (|) Duplicado

✅ **Fix aplicado y compilado**

El bug donde cada click agregaba un `|` ha sido corregido.

---

## CÓMO PROBAR

### PASO 1: Abrir Calcpad manualmente

1. Ve a la carpeta:
   ```
   C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\bin\Debug\net10.0-windows
   ```

2. Haz doble click en `Calcpad.exe`

3. En Calcpad, abre el archivo:
   ```
   C:\Users\j-b-j\Documents\Calcpad-7.5.7\test_code_c.cpd
   ```

---

### PASO 2: Verificar el archivo

El archivo debe contener:

```calcpad
Test C Language

| C [+][-]
#include <stdio.h>

int main() {
    printf("Hola desde C!\n");
    printf("La suma de 5 + 3 = %d\n", 5 + 3);
    return 0;
}
```

**Importante**: Verifica que estés en **modo Visual (MathEditor)**, no en modo Code (editor de texto).

---

### PASO 3: Verificar que estás en el bloque de código C

1. Haz click dentro del bloque de código C (líneas 4-9)
2. Usa las flechas del teclado para moverte dentro del código
3. El preview bar arriba debe mostrar algo como:
   ```
   @{c} Ln 4: #include <stdio.h>|
   ```
   o
   ```
   @{c} Ln 7: printf("Hola desde C!\n");|
   ```

---

### PASO 4: Probar el CLICK en preview bar

**IMPORTANTE**: El click debe ser en el **TextBlock amarillo del preview bar**, NO en el canvas.

1. Localiza la barra amarilla arriba que dice:
   ```
   Calcpad: @{c} Ln X: código...
   ```

2. Haz **CLICK directamente en el texto** `@{c} Ln X: código...`

3. **Debe suceder:**
   - El TextBlock desaparece
   - Aparece un editor AvalonEdit en su lugar
   - El editor tiene el texto: `@{c} Ln X: código...`
   - Puedes escribir en el editor

---

### PASO 5: Editar en el preview editor

Si el editor se abrió:

1. Escribe algo nuevo en el editor
2. Los cambios deben verse en el canvas en tiempo real
3. Presiona ENTER para cerrar el editor
4. El canvas debe actualizarse completamente

---

## SI NO PUEDES EDITAR

### Posible Causa 1: No estás en modo MathEditor

**Síntoma**: Ves un editor de texto normal, no un canvas visual

**Solución**:
- Haz click en el botón de "Vista" y selecciona "Visual" o "MathEditor"
- O haz doble click en el bloque `| C [+][-]`

### Posible Causa 2: No estás en un bloque externo

**Síntoma**: El preview bar no muestra `@{c} Ln X: ...`

**Solución**:
- Haz click dentro del bloque de código C (entre las líneas 4-9)
- Verifica que el preview bar diga `@{c}` al principio

### Posible Causa 3: Click en el lugar equivocado

**Síntoma**: Nada pasa al hacer click

**Solución**:
- El click debe ser EXACTAMENTE en el texto amarillo del preview bar
- NO en el canvas
- NO en el "Calcpad:" label
- SÍ en el texto `@{c} Ln X: código...`

---

## DEBUGGING

### Verificar que el fix está aplicado

1. Abre el archivo:
   ```
   C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Wpf\MathEditor\MathEditorControl.xaml.cs
   ```

2. Busca la línea 1201 (aproximadamente)

3. Debe decir:
   ```csharp
   // NO actualizar PreviewEditor aquí porque el | es solo visual para TextBlock
   // PreviewEditor se actualiza solo cuando el usuario hace click en PreviewTextBlock
   ```

4. Si dice `PreviewEditor.Text = lineText;` entonces el fix NO está aplicado

---

## RESULTADO ESPERADO

### ANTES del fix (BUG):
```
Click 1: @{c} Ln 4: |printf(...);|      ← 1 pipe extra
Click 2: @{c} Ln 4: ||printf(...);|     ← 2 pipes extra
Click 3: @{c} Ln 4: |||printf(...);|    ← 3 pipes extra
```

### DESPUÉS del fix (CORRECTO):
```
Click 1: Editor abre con: @{c} Ln 4: printf(...);    ← Sin | en el editor
Click 2: Editor abre con: @{c} Ln 4: printf(...);    ← Sin | en el editor
Click 3: Editor abre con: @{c} Ln 4: printf(...);    ← Sin | en el editor
```

**Nota**: El `|` solo debe aparecer en el TextBlock amarillo (para mostrar cursor), NUNCA en el editor AvalonEdit.

---

## ARCHIVOS DE REFERENCIA

- `FIX_BUG_PIPE_DUPLICADO.md` - Explicación completa del bug y fix
- `IMPLEMENTACION_SINCRONIZACION_PREVIEW_FINAL.md` - Implementación completa
- `ANALISIS_COMPLETO_MATHEDITOR.md` - Análisis técnico

---

## REPORTAR RESULTADOS

Por favor reporta:

1. ✅ ¿Pudiste abrir Calcpad con test_code_c.cpd?
2. ✅ ¿Estás en modo Visual (MathEditor)?
3. ✅ ¿El preview bar muestra `@{c} Ln X: código|`?
4. ✅ ¿Al hacer click en el preview bar, se abre el editor?
5. ✅ ¿El editor NO tiene pipes duplicados?
6. ✅ ¿Puedes escribir en el editor?
7. ✅ ¿Los cambios se ven en el canvas?
8. ✅ ¿Al presionar Enter, el editor se cierra?

---

## ESTADO ACTUAL

```
Fix aplicado: ✅ SI
Compilación: ✅ EXITOSA (0 errores)
Bug resuelto: ✅ SI (en teoría)
Probado: ⏳ PENDIENTE (necesitas probar manualmente)
```
