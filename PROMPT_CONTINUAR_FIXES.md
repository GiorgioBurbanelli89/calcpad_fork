# PROMPT PARA CONTINUAR - Fixes Pendientes Calcpad v1.0.4

## ACTUALIZACIÓN: Fix de versión Mathcad APLICADO

Se corrigió `McdxConverter.cs` para leer correctamente `docProps/app.xml`:
- Namespace correcto: `http://schemas.mathsoft.com/extended-properties`
- Lee `appVersion`, `engineVersion`, `build`
- Muestra "Prime 10.0 (Build 2024.03.25.002)" en lugar de "Prime 1.0 - 4.0"

**Nota**: Archivos .mcdx antiguos NO tienen `docProps/app.xml`, solo los de Prime 7.0+

---

## Contexto del Proyecto

**Ubicación**: `C:\Users\j-b-j\Documents\Calcpad-7.5.7`
**Versión**: 1.0.4
**Instalador**: `Installer/CalcpadFork-Setup-1.0.4.exe`

---

## PROBLEMAS PENDIENTES

### 1. Vector/Matriz duplicado en output

**Problema**: Cuando escribes `A=[x;y;x]` con variables, el resultado se muestra duplicado:
```
Ā = [x y x] = [2 3 2] = [2 3 2]  ← MAL (duplicado al final)
```

**Debería ser**:
```
Ā = [x y x] = [2 3 2]  ← CORRECTO
```

**Archivo a modificar**: `Calcpad.Core/Parsers/MathParser/MathParser.Output.cs`

**Lógica actual** (líneas 121-144):
- Se detecta si es vector/matriz literal sin variables → funciona
- Pero cuando HAY variables y el resultado formateado es igual al subst, se duplica

**Fix intentado** (no funcionó completamente):
```csharp
var wouldDuplicate = isVectorOrMatrix && !string.IsNullOrEmpty(subst) &&
    _stringBuilder.ToString().EndsWith(subst);
```

---

### 2. Versión de Mathcad incorrecta

**Problema**: Al importar .mcdx muestra "Prime 1.0 - 4.0" basado en schema v50, pero debería mostrar la versión real.

**Archivo**: `Calcpad.Common/McdxConverter.cs`

**El usuario menciona** que existe `<appVersion>10.0.0.0</appVersion>` en algún XML pero no lo encontré en:
- `docProps/app.xml` (no existe en los archivos probados)
- `mathcad/worksheet.xml` (no contiene appVersion)
- `_rels/.rels` (no contiene versión)

**Archivos de prueba extraídos**:
- `/c/Users/j-b-j/Downloads/mcdx_temp/` - Clase 06_Ensamblaje_Placas_gruesas
- `/c/Users/j-b-j/Downloads/mcdx_temp2/` - Clase 06 Circulo_de_Mohr

**TAREA**: Pedirle al usuario que indique DÓNDE encontró `<appVersion>10.0.0.0</appVersion>` para poder leerlo correctamente.

---

## Archivos clave modificados recientemente

### MathParser.Output.cs (formateo vectores/matrices)
```
Calcpad.Core/Parsers/MathParser/MathParser.Output.cs
```
- Líneas 67-150: Lógica de renderizado de ecuaciones
- `RenderVectorToken` y `RenderMatrixToken`: líneas 729-751
- Nuevos métodos `FormatVectorExpression` y `FormatMatrixExpression`

### McdxConverter.cs (versión Mathcad)
```
Calcpad.Common/McdxConverter.cs
```
- `ExtractMathcadVersion()`: líneas 141-244
- Mapeo schema → versión: líneas 213-224

### OutputWriter.cs, HtmlWriter.cs, TextWriter.cs, XmlWriter.cs
- Métodos abstractos e implementaciones de FormatVectorExpression/FormatMatrixExpression

---

## Cómo reproducir los problemas

### Problema 1 - Duplicación:
```
x = 2
y = 3
A = [x; y; x]
```
Output actual: `Ā = [x y x] = [2 3 2] = [2 3 2]` (duplicado)

### Problema 2 - Versión:
Importar cualquier archivo .mcdx y ver el header:
```
' Versión Mathcad: Prime 1.0 - 4.0
```
En lugar de la versión específica como "Prime 10.0" si existe `<appVersion>10.0.0.0</appVersion>`

---

## Archivos C++ CustomFunctions (referencia)

**Ubicación**: `C:\Users\j-b-j\Documents\Calcpad-7.5.7\Tests\`
- `mathcad_fem.cpp`, `verify_fem_beam.cpp`, `plate_fem_example.cpp`
- DLL: `Tests/mathcad_fem.dll`

---

## Commits recientes

```
c058f0a build: Update to v1.0.4 with vector/matrix formatting
8050db4 feat: Format vectors/matrices with matrix style in all output modes
```

---

## Próximos pasos sugeridos

1. **Preguntar al usuario**: ¿Dónde exactamente vio `<appVersion>10.0.0.0</appVersion>`?
2. **Debug del duplicado**: Agregar logging temporal para ver qué valores tienen `res`, `subst`, y `_stringBuilder`
3. **Probar con archivo mcdx más reciente**: Crear uno nuevo en Mathcad Prime 10 y ver su estructura
