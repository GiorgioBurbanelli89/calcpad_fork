# DIAGNÓSTICO: CSS Linking No Funciona en Calcpad WPF

## FECHA: 2026-01-22
## ESTADO: 🔴 PROBLEMA IDENTIFICADO

---

## RESUMEN EJECUTIVO

**Problema:** Los bloques `@{css}` y `@{html}` NO se ejecutan en Calcpad WPF, causando error de sintaxis.

**Causa Raíz:** El archivo test_css_linking.cpd contiene TANTO código externo COMO código Calcpad (líneas con `"` y `'`), lo que activa el modo MIXED. En modo MIXED, GlobalParser cambia `hasExternalCode` a `false` y el código externo no se ejecuta correctamente.

**Impacto:** ALTO - Funcionalidad de CSS linking completamente no funcional en WPF.

---

## ANÁLISIS DETALLADO

### Flujo del Problema

1. **Entrada:** test_css_linking.cpd contiene:
   - Bloques `@{css}` (código externo)
   - Bloques `@{html}` (código externo)
   - Líneas con `"` para headings (código Calcpad)
   - Líneas con `'` para comentarios (código Calcpad)

2. **GlobalParser.Process()** (línea 30-91):
   ```
   hasExternalCode = MultLangManager.HasLanguageCode(code);
   // Retorna: TRUE (encuentra @{css} y @{html})
   ```

3. **HasCalcpadCode()** (línea 96-139):
   ```
   return true; // Encuentra líneas con " y '
   ```

4. **Modo MIXED detectado** (línea 51):
   ```csharp
   if (hasMixedCode) {
       hasExternalCode = false; // ← PROBLEMA AQUÍ
       return PreprocessMixedCode(...);
   }
   ```

5. **Resultado:**
   - `hasExternalCode` cambia a `FALSE`
   - Código se envía a ExpressionParser (Calcpad normal)
   - ExpressionParser lanza error: `Error in "@{css}": Invalid symbol: "@"`

### Logs de Debug

**calcpad_haslangcode_debug.txt:**
```
[09:02:03] Checking directive: '@{html}'
[09:02:03] FOUND: '@{html}' in code! Returning TRUE
```
✅ HasLanguageCode() funciona correctamente

**calcpad-debug.txt:**
```
[09:02:03] GlobalParser ASYNC: HasExternalCode=False
[09:02:03] MainWindow: ELSE block - calling ExpressionParser
[09:02:03] Error in "@{css}" on line [7]: Invalid symbol: "@".
```
❌ hasExternalCode fue cambiado a FALSE en modo MIXED

---

## CÓDIGO RELEVANTE

### GlobalParser.cs (línea 51-67)

```csharp
if (hasMixedCode)
{
    // PATH 1A: MIXED MODE - Has external code AND Calcpad code
    // Preprocess: Replace external code blocks with Calcpad HTML comments
    // Then return for ExpressionParser to process Calcpad code
    hasExternalCode = false; // ← Cambia a FALSE

    try
    {
        var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
        System.IO.File.AppendAllText(debugPath,
            $"[{DateTime.Now:HH:mm:ss}] PATH 1A: MIXED MODE - Setting hasExternalCode=false\n");
    }
    catch { }

    return PreprocessMixedCode(code, progressCallback, partialResultCallback);
}
```

### HasCalcpadCode() (línea 96-139)

```csharp
private bool HasCalcpadCode(string code)
{
    var lines = code.Split('\n');
    bool inExternalBlock = false;

    foreach (var line in lines)
    {
        var trimmed = line.Trim();

        // Track external code blocks
        if (trimmed.StartsWith("@{") && !trimmed.StartsWith("@{end"))
        {
            inExternalBlock = true;
            continue;
        }
        else if (trimmed.StartsWith("@{end"))
        {
            inExternalBlock = false;
            continue;
        }

        // Skip lines inside external blocks
        if (inExternalBlock)
            continue;

        // Skip only empty lines
        if (string.IsNullOrWhiteSpace(trimmed))
            continue;

        // Lines starting with ' or " are Calcpad text/headings
        if (trimmed.StartsWith("'") || trimmed.StartsWith("\""))
            return true; // ← Retorna TRUE porque encuentra " y '

        // ... más comprobaciones ...
    }

    return false;
}
```

---

## ANÁLISIS DEL PROBLEMA

### ¿Por Qué Falla?

1. **Detección correcta:** HasLanguageCode() SÍ detecta bloques externos
2. **Detección de modo MIXED:** HasCalcpadCode() SÍ detecta código Calcpad (las líneas con `"` y `'`)
3. **Cambio de comportamiento:** En modo MIXED, se cambia `hasExternalCode = false`
4. **PreprocessMixedCode() no funciona:** El método que debería ejecutar los bloques externos no lo está haciendo correctamente

### ¿Qué Debería Pasar?

En modo MIXED, `PreprocessMixedCode()` debería:
1. Ejecutar bloques `@{css}` → generar styles.css
2. Ejecutar bloques `@{html}` → generar index.html con <link>
3. Reemplazar esos bloques con comentarios HTML para ExpressionParser
4. Retornar código Calcpad con comentarios HTML insertados

**Pero NO está pasando.**

---

## VERIFICACIÓN

### Archivos Generados
```
temp_multilang/
  ├── test_ts.ts (71 bytes) ← De pruebas anteriores
  ├── tsconfig.json (330 bytes) ← De pruebas anteriores
  ├── ❌ styles.css (NO generado)
  └── ❌ index.html (NO generado)
```

### Error en Output
```html
<p id="line-7" class="line">
  <span class="err" id="line-7">
    Error in "@{css}" on line [7]: Invalid symbol: "@".
  </span>
</p>
```

---

## SOLUCIONES POSIBLES

### Opción 1: Código Externo PURO (Sin Calcpad)

**Crear un archivo sin líneas con `"` y `'`:**

```
@{css}
body {
    /* CSS aquí */
}
@{end css}

@{html}
<!DOCTYPE html>
<html>
<!-- HTML aquí -->
</html>
@{end html}
```

**Ventaja:** Evita modo MIXED, ejecuta código externo directamente
**Desventaja:** No puedes mezclar con Calcpad

### Opción 2: Arreglar PreprocessMixedCode()

**Modificar GlobalParser.cs para que PreprocessMixedCode() ejecute correctamente los bloques externos.**

**Archivo a modificar:**
- `Calcpad.Common/GlobalParser.cs` línea 144-149

**Cambio necesario:**
- Verificar que MultLangProcessor.Process() con `returnHtml=false` funcione
- Asegurar que los archivos se generen (styles.css, index.html)
- Retornar comentarios HTML correctos

### Opción 3: Usar Modo PURE EXTERNAL

**Cambiar la detección para que no considere `"` y `'` como Calcpad code cuando hay bloques externos.**

**Archivo a modificar:**
- `Calcpad.Common/GlobalParser.cs` línea 96-139 (HasCalcpadCode)

**Cambio:**
```csharp
// Solo retornar true si hay VERDADERO código Calcpad (no solo comentarios)
if (trimmed.StartsWith("'") || trimmed.StartsWith("\""))
    continue; // ← Cambiar a 'continue' en lugar de 'return true'
```

---

## PRUEBA RÁPIDA

### Test 1: Archivo Externo Puro

```cpd
@{css}
body { background: red; }
@{end css}

@{html}
<!DOCTYPE html>
<html>
<head></head>
<body>Test</body>
</html>
@{end html}
```

**Resultado esperado:** Modo PURE EXTERNAL, genera archivos

### Test 2: Archivo Mixto (Actual)

```cpd
"Heading
'Comment

@{css}
body { background: red; }
@{end css}

@{html}
<!DOCTYPE html>
</html>
@{end html}
```

**Resultado actual:** Modo MIXED, ERROR
**Resultado esperado:** Modo MIXED, ejecuta bloques y retorna comentarios

---

## RECOMENDACIÓN

**CORTO PLAZO:**
1. Usar archivos PURE EXTERNAL (sin `"` ni `'`)
2. Probar si genera archivos correctamente

**MEDIANO PLAZO:**
1. Investigar PreprocessMixedCode() para ver por qué no ejecuta bloques
2. Arreglar MultLangProcessor.Process() con `returnHtml=false`

**LARGO PLAZO:**
1. Refactorizar detección de modo MIXED
2. Permitir verdadera mezcla de Calcpad + lenguajes externos

---

## ARCHIVOS AFECTADOS

1. **Calcpad.Common/GlobalParser.cs** - Lógica de decisión MIXED/PURE
2. **Calcpad.Common/MultLangCode/MultLangProcessor.cs** - Procesamiento de lenguajes
3. **Calcpad.Common/MultLangCode/LanguageExecutor.cs** - Ejecución y generación de archivos
4. **test_css_linking.cpd** - Archivo de prueba (necesita modificación)

---

## PRÓXIMOS PASOS

1. ✅ Diagnóstico completado
2. ⏳ Crear test_css_linking_PURE.cpd (sin Calcpad)
3. ⏳ Probar en modo PURE EXTERNAL
4. ⏳ Verificar generación de archivos
5. ⏳ Investigar fix de PreprocessMixedCode() si es necesario

---

**Generado:** 2026-01-22
**Estado:** ✅ DIAGNÓSTICO COMPLETO
**Siguiente acción:** Crear archivo PURE para testing
