# Diagnóstico: Problema de Desincronización AvalonEdit

## Problema Reportado (Screenshot_18.png)

**Al cambiar de archivo C a Fortran**:
- ❌ **Editor (AvalonEdit)**: Muestra código C (viejo)
- ✅ **Output**: Muestra resultados de Fortran (correcto)

## Análisis del Código

### Flujo al Abrir Archivo (FileOpen - línea 1270)

```
1. FileOpen(fileName)
2. CurrentFileName = fileName (línea 1280)
3. GetInputTextFromFile() (línea 1282)
   ├─> GetInputTextFromFile_AvalonEdit() (línea 2217)
   │   ├─> fileContent = ReadTextFromFile(CurrentFileName) (línea 2220) ✅ Lee del disco
   │   └─> Dispatcher.InvokeAsync(() => {
   │       TextEditor.Text = fileContent;  // ASÍNCRONO
   │   }, DispatcherPriority.Render) (línea 2231)
   │
4. Si IsAutoRun o hasForm:
   └─> Dispatcher.InvokeAsync(() => CalculateAsync(), Background) (línea 1322)
```

### Problema Potencial: Condición de Carrera

Ambas operaciones usan `Dispatcher.InvokeAsync`:
1. **Actualizar editor**: `DispatcherPriority.Render`
2. **Auto-cálculo**: `DispatcherPriority.Background`

`Render` > `Background` en prioridad, pero **no hay garantía de timing**.

### ¿Por qué el Output es Correcto?

**Hipótesis 1**: CalcpadProcessor lee del archivo
- Necesito verificar si `ProcessCodeAsync` internamente vuelve a leer `CurrentFileName`

**Hipótesis 2**: TextEditor.Text se actualiza DESPUÉS del cálculo
- Cálculo lee InputText (que tiene valor viejo cacheado en memoria)
- Luego TextEditor.Text se actualiza con contenido nuevo
- Pero esta hipótesis contradice que el output sea correcto

**Hipótesis 3**: El usuario presionó F5 manualmente DESPUÉS
- No cambió con auto-run
- F5 lee del disco nuevamente y calcula bien
- Pero el editor visualmente no se refrescó

## Preguntas para el Usuario

1. ¿Tienes **AutoRun activado** (checkbox en la UI)?
2. ¿El problema ocurre **inmediatamente al abrir** el archivo o **después de presionar F5**?
3. Cuando ves el problema:
   - ¿El output ya está calculado o está en blanco?
   - ¿Qué archivo tenías abierto antes?
   - ¿Qué archivo abriste después?

## Posible Solución 1: Forzar Actualización Síncrona

Cambiar en `GetInputTextFromFile_AvalonEdit()`:

```csharp
// EN LUGAR DE:
Dispatcher.InvokeAsync(() => {
    TextEditor.Text = fileContent;
}, DispatcherPriority.Render);

// USAR:
TextEditor.Text = fileContent;  // Directo, síncrono
```

**Riesgo**: Puede bloquear UI si el archivo es muy grande.

## Posible Solución 2: Esperar a que TextEditor se Actualice

```csharp
var tcs = new TaskCompletionSource<bool>();

Dispatcher.InvokeAsync(() => {
    TextEditor.Text = fileContent;
    tcs.SetResult(true);
}, DispatcherPriority.Render);

await tcs.Task;  // Esperar a que se complete

// LUEGO ejecutar auto-cálculo
if (IsAutoRun)
    Dispatcher.InvokeAsync(() => CalculateAsync(), DispatcherPriority.Background);
```

## Posible Solución 3: Leer del Archivo en Calculate

Hacer que `CalculateAsync` siempre vuelva a leer `CurrentFileName` del disco en lugar de confiar en `InputText`:

```csharp
// En CalculateAsync (línea 1448):
string inputCode;
if (!string.IsNullOrEmpty(CurrentFileName) && File.Exists(CurrentFileName))
{
    inputCode = ReadTextFromFile(CurrentFileName);  // Leer del disco
}
else
{
    inputCode = InputText;  // Fallback
}
```

**Ventaja**: Siempre usa contenido actualizado del disco
**Desventaja**: Si usuario está editando sin guardar, pierde cambios

## Estado Actual

- ✅ Code folding para bloques externos ya implementado (líneas 314-338)
- ⚠️ Desincronización al cambiar archivo (investigando)
- ❓ Necesito más información del usuario sobre cuándo ocurre el problema

## Siguiente Paso

Esperar respuesta del usuario para entender exactamente cuándo ocurre el problema y elegir la solución apropiada.
