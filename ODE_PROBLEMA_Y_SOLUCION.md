# Problema y Solución: Solver de ODEs

## ❌ PROBLEMA INICIAL

### Síntoma
Al generar HTML con Calcpad CLI, aparecían errores de parsing:

```
Error parsing "," as units
Assignment '=' must be the first operator
Invalid syntax: "x, y,"
```

**Cantidad de errores**: 7-17 errores por archivo

### Causa Raíz

El parser de Calcpad procesaba las líneas **ANTES** de que el bloque `@{symbolic}` las procesara:

```calcpad
@{symbolic}
sol1 = solve_ode(y' - x^2, y, x)
@{end symbolic}
```

**Flujo incorrecto:**
1. Calcpad lee: `sol1 = solve_ode(y' - x^2, y, x)`
2. **Calcpad intenta parsear esta línea PRIMERO** ❌
3. Ve las comas `,` y el `=` dentro de `solve_ode()`
4. Genera errores: "Error parsing ',' as units"
5. LUEGO el SymbolicParser procesa la línea
6. Genera el resultado correcto: `sol1 = y = x³/3 + C`
7. PERO el error ya quedó en el HTML

**Resultado**: HTML con errores + solución correcta mezclados

---

## ✅ SOLUCIÓN IMPLEMENTADA (FINAL)

### Solución Definitiva: HTML Encoding para Ecuaciones

**Archivo**: `Calcpad.Common/ExpressionParsers/SymbolicParser.cs`

**Líneas 726-735:**
```csharp
// Mostrar ecuación original Y solución (sin la llamada a solve_ode)
// Usar HTML encoding para evitar que Calcpad parsee la ecuación
string displayEquation = equation;
if (!equation.Contains("="))
    displayEquation += " = 0";

// HTML encode para evitar parsing de caracteres especiales como ', =, etc.
string safeEquation = System.Net.WebUtility.HtmlEncode(displayEquation);

return $"'<p><b>Ecuación:</b> <code>{safeEquation}</code></p>\n'<p><b>Solución:</b> {varName} = {result}</p>";
```

**Cómo funciona:**
1. `System.Net.WebUtility.HtmlEncode()` convierte:
   - `'` → `&#39;`
   - `"` → `&#34;`
   - `<` → `&lt;`
   - `>` → `&gt;`
   - `&` → `&amp;`

2. Estos caracteres codificados NO son parseados por Calcpad
3. El navegador los muestra correctamente como caracteres originales
4. Se envuelve en `<code>` para formato monoespaciado

**Resultado:**
- ✅ Ecuación visible: `y' - x^2 = 0`
- ✅ Solución visible: `sol1 = y = x³/3 + C`
- ✅ 0 errores de parsing

---

### Cambio 2: Usar un solo bloque @{symbolic}

**ANTES (múltiples bloques):**
```calcpad
'<h3>Ejemplo 1</h3>
@{symbolic}
sol1 = solve_ode(y' - x^2, y, x)
@{end symbolic}

'<h3>Ejemplo 2</h3>
@{symbolic}
sol2 = solve_ode(y' + 3*y, y, x)
@{end symbolic}
```

**DESPUÉS (un solo bloque):**
```calcpad
@{symbolic}

'<h3>Ejemplo 1</h3>
sol1 = solve_ode(y' - x^2, y, x)

'<h3>Ejemplo 2</h3>
sol2 = solve_ode(y' + 3*y, y, x)

@{end symbolic}
```

**Efecto**: Todo el contenido se procesa dentro del bloque simbólico, evitando que Calcpad lo vea primero.

---

## 📊 RESULTADOS

### Antes de la solución
```
Errores HTML: 7 class="err"
Resultados matemáticos: Correctos pero con errores visuales
```

HTML generado (fragmento):
```html
<p> sol1 = solve_ode(y <span class="err">Error in " - x^2, y, x)" ...</span></p>
<p> sol1 = y = x ^ 3 / 3 + C </p>
```

### Después de la solución (versión inicial - solo soluciones)
```
Errores HTML: 0 ✅
Resultados matemáticos: Correctos pero sin ecuaciones ⚠️
```

HTML generado (fragmento):
```html
<p> sol1 = y = x ^ 3 / 3 + C </p>
<p> sol2 = y = C*e^(-(3)*x) </p>
<p> sol3 = y = C1*e^(2.0000*x) + C2*e^(1.0000*x) </p>
```

**Problema**: Usuario reportó "Estan las soluciones no mas no sus ecuaeiones"

### Después de la solución FINAL (con HTML encoding)
```
Errores HTML: 0 ✅
Ecuaciones mostradas: SÍ ✅
Soluciones mostradas: SÍ ✅
```

HTML generado (fragmento):
```html
<p><b>Ecuación:</b> <code>y&#39; - x^2 = 0</code></p>
<p><b>Solución:</b> sol1 = y = x ^ 3 / 3 + C</p>

<p><b>Ecuación:</b> <code>y&#39; + 3*y = 0</code></p>
<p><b>Solución:</b> sol2 = y = C*e^(-(3)*x)</p>

<p><b>Ecuación:</b> <code>y&#39;&#39; - 3*y&#39; + 2*y = 0</code></p>
<p><b>Solución:</b> sol3 = y = C1*e^(2.0000*x) + C2*e^(1.0000*x)</p>
```

---

## 🎯 VERIFICACIÓN FINAL

```bash
cd Calcpad.Cli/bin/Release/net10.0
./Cli.exe "C:/Users/j-b-j/Documents/Calcpad-7.5.7/Examples/Test-ODE-Simple.cpd" \
          "C:/Users/j-b-j/Documents/Calcpad-7.5.7/Examples/test-ode-html-encoded.html" -s

grep -c 'class="err"' C:/Users/j-b-j/Documents/Calcpad-7.5.7/Examples/test-ode-html-encoded.html
# Output: 0 ✅
```

**Todas las ecuaciones Y soluciones matemáticas:**

| Ejemplo | Ecuación | Solución |
|---------|----------|----------|
| sol1 | `y' - x^2 = 0` | y = x³/3 + C |
| sol2 | `y' + 3*y = 0` | y = C*e^(-3x) |
| sol3 | `y'' - 3*y' + 2*y = 0` | y = C1*e^(2x) + C2*e^x |
| sol4 | `y'' - 4*y' + 4*y = 0` | y = (C1 + C2*x)*e^(2x) |
| sol5 | `y'' + 4*y = 0` | y = C1*cos(2x) + C2*sin(2x) |
| sol6 | `y'' + 2*y' + 5*y = 0` | y = e^(-x)*(C1*cos(2x) + C2*sin(2x)) |
| sol7 | `y' - 2*x = 0` | y = 2*x²/2 + C |
| sol8 | `y' + 5*y = 0` | y = C*e^(-5x) |

**Verificación visual en HTML:**
- ✅ 0 errores de parsing
- ✅ Ecuaciones mostradas con caracteres codificados (`y&#39;` → `y'`)
- ✅ Soluciones matemáticas formateadas correctamente
- ✅ Todas las derivadas (`'` y `''`) visibles sin errores

---

## 🔑 LECCIÓN APRENDIDA

**El contenido dentro de `@{parser}...@{end parser}` debe ser procesado EXCLUSIVAMENTE por ese parser, no por Calcpad primero.**

Esto aplica a todos los parsers:
- `@{symbolic}` → Solo SymbolicParser
- `@{typescript}` → Solo TypeScriptParser
- `@{python}` → Solo PythonParser
- etc.

**Orden de procesamiento correcto:**
1. Calcpad detecta `@{parser_name}`
2. Extrae el contenido completo del bloque
3. Pasa el contenido AL PARSER sin procesarlo
4. El parser retorna el resultado procesado
5. Calcpad inserta el resultado en el HTML

---

## 📁 Archivos Modificados

1. **`Calcpad.Common/ExpressionParsers/SymbolicParser.cs`**
   - Líneas 726-735: Cambio en retorno de `ProcessODE()`
   - **Cambio clave**: Uso de `System.Net.WebUtility.HtmlEncode()` para codificar ecuaciones
   - **Resultado**: Muestra ecuaciones Y soluciones sin errores de parsing

2. **`Examples/Test-ODE-Simple.cpd`**
   - Consolidado en un solo bloque `@{symbolic}`
   - Eliminados comentarios HTML problemáticos
   - Ejemplos cubren todos los tipos de ODE soportados

3. **`Examples/test-ode-html-encoded.html`** (generado)
   - HTML final con 0 errores
   - Ecuaciones codificadas como entidades HTML
   - Soluciones formateadas correctamente

---

## 📈 Evolución de la Solución

**Iteración 1**: Ocultar ecuaciones con `#hide/#show` → ❌ 14 errores
**Iteración 2**: Múltiples bloques `@{symbolic}` → ❌ 7 errores
**Iteración 3**: Un solo bloque `@{symbolic}` → ❌ 7 errores
**Iteración 4**: Solo mostrar soluciones → ✅ 0 errores, ❌ sin ecuaciones
**Iteración 5**: **HTML encoding de ecuaciones** → ✅ 0 errores, ✅ con ecuaciones

---

**Estado**: ✅ RESUELTO COMPLETAMENTE
**Versión**: 7.5.8-symbolic+odes
**Fecha**: 2026-01-26
