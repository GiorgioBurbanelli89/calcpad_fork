# Prompt para Continuar: Sistema de Parsers Externos y Plugins para Calcpad

## Contexto del Proyecto

Calcpad es una calculadora científica con formato de documento (similar a Mathcad) escrita en C# (.NET 10). Estoy extendiendo el sistema para soportar:

1. **Motores de evaluación intercambiables** - el usuario elige qué motor usa (Calcpad, AngouriMath, custom)
2. **Sintaxis configurable via JSON** - define tus propios delimitadores (`'`, `"`, `'<>`, etc.)
3. **Sistema de plugins/DLLs** - carga funciones personalizadas desde DLLs externas
4. **Parsers de traducción** - convierte LaTeX, Mathcad, Python math a sintaxis Calcpad
5. **Selección de parser por sección** - usa `@{parser:nombre}` para cambiar parser dinámicamente

## Archivos Clave del Sistema Actual

### Configuración de Lenguajes Externos
- `Calcpad.Common/MultLangCode/MultLangConfig.json` - Define 30+ lenguajes (Python, Octave, TypeScript, Rust, etc.)
- `Calcpad.Common/MultLangCode/MultLangProcessor.cs` - Procesa bloques @{lenguaje}...@{end lenguaje}
- `Calcpad.Common/MultLangCode/LanguageExecutor.cs` - Ejecuta código externo y captura output
- `Calcpad.Common/MultLangCode/LanguageHtmlGenerator.cs` - Genera HTML con syntax highlighting

### Sistema de Plugins y Motores (Nuevo)
- `Calcpad.Common/Plugins/PluginConfig.json` - Configuración maestra:
  - `engines` - Define motores de evaluación (calcpad, angourimath, latex, mathcad, custom)
  - `plugins` - Define DLLs a cargar (AngouriMath, MathNet, UnitsNet)
  - `parserSyntax` - Define sintaxis configurable (delimitadores, operadores)
  - `parserSelection` - Permite al usuario elegir parser por sección
  - `userDefinedExpressions` - Expresiones predefinidas del usuario
- `Calcpad.Common/Plugins/PluginManager.cs` - Carga DLLs dinámicamente
- `Calcpad.Common/Plugins/EngineManager.cs` - Gestiona motores de evaluación
- `Calcpad.Common/Plugins/ICalcpadEngine.cs` - Interfaces para motores y plugins

### Parser Principal
- `Calcpad.Core/Parsers/ExpressionParser/ExpressionParser.cs` - Parser principal de Calcpad
- `Calcpad.Core/Parsers/MathParser/MathParser.cs` - Evaluador de expresiones matemáticas
- `Calcpad.Core/Parsers/MathParser/MathParser.CustomFunction.cs` - Funciones personalizadas

## Lo Que Ya Se Implementó (Esta Sesión)

### 1. PluginConfig.json Completo
- Sección `engines` con motores: calcpad, angourimath, latex, mathcad, python, custom
- Sección `parserSyntax` con presets: calcpad, mathcad, latex, custom
- Sección `parserSelection` para elegir parser por sección con `@{parser:nombre}`
- Sección `userDefinedExpressions` para expresiones predefinidas
- Sección `customSymbols` para operadores y funciones en otros idiomas (sen→sin, tg→tan)

### 2. ParserDefinition.json - TODAS las expresiones en JSON
- Define TODOS los operadores (+, -, *, /, ^, etc.) con precedencia y asociatividad
- Define TODAS las funciones (sin, cos, sqrt, etc.) con número de argumentos
- Define TODAS las keywords (#if, #for, $Root, etc.)
- Define TODOS los delimitadores (', ", '<, '>", etc.)
- Define constantes (π, e, ∞)
- Define aliases por idioma (sen→sin, tg→tan en español)
- Parsers: calcpad, symbolic, latex, custom

### 3. ParserLoader.cs
- Carga ParserDefinition.json
- Proporciona métodos: GetOperator(), GetFunction(), GetKeyword(), GetDelimiter()
- Traduce expresiones entre parsers
- Aplica aliases de idioma

### 4. EngineManager.cs
- Carga configuración de motores desde JSON
- Crea instancias de motores según tipo (builtin, plugin, translator, custom)
- Permite evaluar con motor específico o default
- Variables compartidas entre motores

### 5. ICalcpadEngine.cs
- Interface base `ICalcpadEngine` para todos los motores
- Interface `ISymbolicEngine` para motores simbólicos (derivadas, integrales)
- Interface `ITranslatorEngine` para traductores de sintaxis
- Implementación `AngouriMathEngine` con reflexión

### 6. Test de AngouriMath
- Proyecto en `Tests/AngouriMathTest/`
- Demuestra derivadas, integrales, resolver ecuaciones, matrices, LaTeX output

## Lo Que Falta Implementar

### 1. Sistema de Sintaxis Múltiples

Ya está configurado en JSON, ahora falta integrar con el parser. Ejemplo de uso:

```
' Sintaxis Calcpad nativa
a = 5
b = sqrt(a^2 + 3)

' Sintaxis LaTeX (nuevo)
@{latex}
c = \frac{a + b}{2}
d = \sqrt{a^2 + b^2}
@{end latex}

' Sintaxis Mathcad-style (nuevo)
@{mathcad}
e := a + b
f := e · 2
@{end mathcad}

' Sintaxis Python-style (nuevo)
@{pymath}
g = a**2 + b**2
h = math.sin(g)
@{end pymath}
```

### 2. Registrar Parsers Externos via JSON

Agregar una sección al JSON para definir parsers de expresiones:

```json
{
  "expressionParsers": {
    "latex": {
      "name": "LaTeX Math Parser",
      "directive": "@{latex}",
      "endDirective": "@{end latex}",
      "operators": {
        "\\frac{a}{b}": "a/b",
        "\\sqrt{x}": "sqrt(x)",
        "\\cdot": "*",
        "^": "^"
      },
      "functions": {
        "\\sin": "sin",
        "\\cos": "cos",
        "\\tan": "tan",
        "\\ln": "ln",
        "\\log": "log"
      },
      "assignment": "=",
      "processMode": "translate"  // translate to Calcpad syntax
    },
    "mathcad": {
      "name": "Mathcad Prime Style",
      "directive": "@{mathcad}",
      "endDirective": "@{end mathcad}",
      "operators": {
        ":=": "=",
        "·": "*",
        "×": "*"
      },
      "processMode": "translate"
    },
    "symbolic": {
      "name": "AngouriMath Symbolic",
      "directive": "@{symbolic}",
      "endDirective": "@{end symbolic}",
      "pluginRef": "angourimath",
      "processMode": "plugin"  // execute via plugin
    }
  }
}
```

### 3. Integración con MathParser

El flujo sería:
1. MultLangProcessor detecta directiva @{latex}
2. Busca en "expressionParsers" si hay un parser definido
3. Si `processMode = "translate"`: convierte a sintaxis Calcpad y pasa a MathParser
4. Si `processMode = "plugin"`: llama al PluginManager para ejecutar

### 4. Interfaces que Necesito

```csharp
/// <summary>
/// Interface para parsers de expresiones externos
/// </summary>
public interface IExpressionParser
{
    string Name { get; }
    string Directive { get; }

    /// <summary>Traduce expresión externa a sintaxis Calcpad</summary>
    string Translate(string expression);

    /// <summary>Evalúa directamente y devuelve resultado</summary>
    object Evaluate(string expression, IDictionary<string, double> variables);

    /// <summary>Valida sintaxis sin evaluar</summary>
    bool Validate(string expression, out string error);
}

/// <summary>
/// Interface para operadores personalizados
/// </summary>
public interface ICustomOperator
{
    string Symbol { get; }
    int Precedence { get; }
    bool IsRightAssociative { get; }
    double Evaluate(double left, double right);
}
```

## Tareas Pendientes

1. [ ] Crear `ExpressionParserConfig` clase para deserializar la sección de parsers
2. [ ] Implementar `LaTeXParser` que traduzca LaTeX a Calcpad
3. [ ] Implementar `MathcadParser` que traduzca sintaxis Mathcad
4. [ ] Modificar `MultLangProcessor` para detectar y usar parsers de expresiones
5. [ ] Integrar `PluginManager` con el sistema de parsers
6. [ ] Crear ejemplos de uso y tests

## Ejemplo de Uso Final Esperado

```calcpad
"Cálculo de Viga Simple"

' Variables en Calcpad nativo
L = 6m
q = 10kN/m

' Momento máximo con LaTeX
@{latex}
M_{max} = \frac{q \cdot L^2}{8}
@{end latex}

' Operaciones simbólicas con AngouriMath
@{symbolic}
M(x) = q*x*(L-x)/2
M'(x) = diff(M(x), x)
x_max = solve(M'(x) = 0, x)
@{end symbolic}

' Visualización con Python
@{python}
import matplotlib.pyplot as plt
x = np.linspace(0, $L, 100)
M = $q * x * ($L - x) / 2
plt.plot(x, M)
plt.savefig('momento.png')
@{end python}

@{image}momento.png@{end image}
```

## Archivos a Revisar/Modificar

1. `Calcpad.Common/MultLangCode/MultLangConfig.json` - Agregar sección expressionParsers
2. `Calcpad.Common/MultLangCode/MultLangProcessor.cs` - Integrar detección de parsers
3. `Calcpad.Common/Plugins/PluginManager.cs` - Ya creado, expandir
4. `Calcpad.Core/Parsers/MathParser/MathParser.cs` - Hooks para funciones de plugins
5. Nuevo: `Calcpad.Common/ExpressionParsers/` - Carpeta para parsers externos

## Tests de AngouriMath Exitosos

El test en `Tests/AngouriMathTest/Program.cs` demostró que AngouriMath funciona con .NET 10:
- ✅ Simplificación: `sin(x)^2 + cos(x)^2 = 1`
- ✅ Derivadas: `f'(x) = 3*x^2 + 4*x - 5`
- ✅ Integrales: `∫ x^2 dx = x^3/3`
- ✅ Resolver ecuaciones: `x^2 - 5x + 6 = 0 → {2, 3}`
- ✅ Sistemas: `2x + y = 5, x - y = 1 → [[2, 1]]`
- ✅ Matrices: determinante, inversa
- ✅ Salida LaTeX

## Comando para Continuar

Usa este prompt para continuar la implementación:

```
Continúa implementando el sistema de parsers externos para Calcpad.

## Archivos ya creados (leer primero):
- Calcpad.Common/Plugins/ParserDefinition.json (TODAS las expresiones en JSON)
- Calcpad.Common/Plugins/ParserLoader.cs (carga definiciones del JSON)
- Calcpad.Common/Plugins/PluginConfig.json (configuración de motores y sintaxis)
- Calcpad.Common/Plugins/EngineManager.cs (gestión de motores)
- Calcpad.Common/Plugins/ICalcpadEngine.cs (interfaces)
- Calcpad.Common/Plugins/PluginManager.cs (carga de DLLs)
- Tests/AngouriMathTest/Program.cs (test funcional)

## Arquitectura del sistema:

```
┌─────────────────────────────────────────────────────────┐
│                   ParserDefinition.json                  │
│  (Define TODAS las expresiones, operadores, funciones)  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                     ParserLoader.cs                      │
│  (Carga JSON, proporciona GetOperator, GetFunction...)  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│           ExpressionParser.cs / MathParser.cs           │
│  (SOLO llama a ParserLoader - no hardcodea nada)        │
└─────────────────────────────────────────────────────────┘
```

## Tareas pendientes:

1. Modificar MathParser.cs para usar ParserLoader:
   - Reemplazar hardcoded operators con ParserLoader.GetOperator()
   - Reemplazar hardcoded functions con ParserLoader.GetFunction()
   - Usar precedence y associativity del JSON

2. Modificar ExpressionParser.cs para usar ParserLoader:
   - Reemplazar hardcoded keywords con ParserLoader.GetKeyword()
   - Usar delimiters del JSON en lugar de caracteres fijos

3. Implementar detección de @{parser:nombre}:
   - En MultLangProcessor detectar directiva
   - Cambiar parser activo con ParserLoader.SetActiveParser()
   - Traducir si es necesario

4. Crear test que demuestre:
   - Agregar nueva función al JSON y usarla sin tocar C#
   - Cambiar delimitadores y que funcione
   - Usar aliases en español (sen, tg, raiz)
```

---
Generado: 2026-01-25
Proyecto: Calcpad v7.5.8
Autor: Claude (asistido por usuario j-b-j)
