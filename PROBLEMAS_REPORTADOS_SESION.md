# Problemas Reportados - Sesión Actual

## 1. AvalonEdit No Muestra Contenido al Abrir Archivo

**Síntoma**:
- Al abrir un archivo nuevo (File → Open)
- AvalonEdit queda vacío (no muestra código)
- Pero Output SÍ ejecuta correctamente
- F5 funciona, solo que el editor está vacío visualmente

**Estado**: ⏳ PENDIENTE INVESTIGAR
**Prioridad**: 🔴 ALTA

## 2. Cambio MathEditor → AvalonEdit No Muestra Contenido

**Síntoma**:
- Cuando cambias de modo MathEditor a AvalonEdit (Code button)
- AvalonEdit aparece vacío
- Pero Output sí ejecuta al presionar F5

**Estado**: ⏳ PENDIENTE INVESTIGAR
**Prioridad**: 🔴 ALTA

## 3. AutoRun No Responde a Cambios en Lenguajes Externos

**Síntoma**:
- Checkbox AutoRun está activado
- Al abrir archivo con código externo (@{c}, @{fortran}, etc.) SÍ ejecuta
- Pero cuando editas el código en el editor, NO vuelve a ejecutar
- Tienes que presionar F5 o el botón Calculate manualmente

**Estado**: ⏳ PENDIENTE INVESTIGAR
**Prioridad**: 🟡 MEDIA

## 4. Mensajes "Compilando..." Deben Ser Dinámicos

**Síntoma**:
- Al compilar lenguajes externos (C, C++, Fortran, etc.)
- Solo muestra "Compilando..." estático
- Debería mostrar "Compilando... 1.2s", "Compilando... 2.5s" dinámicamente

**Estado**: ⏳ PENDIENTE IMPLEMENTAR
**Prioridad**: 🟢 BAJA

---

## Acciones Tomadas Hasta Ahora

### ✅ Completado
1. Fix sincronización MathEditor con AvalonEdit (líneas 4942-5093)
2. Compilación exitosa (0 errores, 36 warnings)

### ❌ Revertido
1. Fix síncrono para GetInputTextFromFile_AvalonEdit
   - Causa: Generaba más problemas (AvalonEdit vacío)
   - Reverted a versión asíncrona original

---

## Plan de Acción Sugerido

### Fase 1: Diagnóstico (Prioridad ALTA)

1. **Capturar UI Automation** cuando:
   - Abres un archivo nuevo
   - Cambias de MathEditor a AvalonEdit
   - Ver estado de TextEditor.Text vs Output

2. **Verificar**:
   - ¿TextEditor.Visibility está en Visible?
   - ¿TextEditor.Text tiene contenido?
   - ¿Hay algún layer tapando el editor?

### Fase 2: Fix AvalonEdit Vacío (Prioridad ALTA)

**Hipótesis 1**: Dispatcher.InvokeAsync no se ejecuta
- Solución: Usar priority más alta o hacer síncrono con try-catch

**Hipótesis 2**: TextEditor se oculta por alguna razón
- Solución: Forzar Visibility = Visible después de cargar

**Hipótesis 3**: Conflicto con RichTextBox
- Solución: Asegurar que RichTextBox esté oculto cuando AvalonEdit activo

### Fase 3: Fix AutoRun (Prioridad MEDIA)

1. Buscar evento TextChanged de AvalonEdit
2. Verificar que dispare CalculateAsync cuando AutoRun activo
3. Verificar que no esté bloqueado por algún flag (_isTextChangedEnabled, etc.)

### Fase 4: Mensajes Dinámicos (Prioridad BAJA)

1. Crear timer que actualice mensaje cada 100ms
2. Calcular tiempo transcurrido desde inicio de compilación
3. Actualizar Output con "Compilando... Xs"

---

## Estado Actual

- ✅ Calcpad compilado y lanzado
- ⏳ Versión revertida (asíncrona) activa
- 🔍 Esperando pruebas del usuario

## Próximo Paso

Usuario debe probar:
1. Abrir un archivo → Ver si AvalonEdit muestra contenido
2. Cambiar de MathEditor a Code → Ver si muestra contenido
3. Reportar resultados para continuar diagnóstico
