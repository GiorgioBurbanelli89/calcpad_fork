# Snippets HTML/CSS/TypeScript Implementados

## Fecha: 2026-01-21

## Estado: ✅ COMPILADO Y LISTO PARA PROBAR

## Descripción

Se implementó sistema de snippets tipo Emmet para bloques de lenguajes externos en AvalonEdit, similar a VSCode.

## Características

### 1. Detección Automática de Contexto

El sistema detecta automáticamente en qué bloque estás escribiendo:
- `@{html}` → Muestra snippets HTML
- `@{css}` → Muestra snippets CSS
- `@{ts}` / `@{js}` → Muestra snippets TypeScript/JavaScript
- Bloques normales Calcpad → Muestra autocompletado normal

### 2. Preview del Template

Cuando escribes un trigger (ej: "html"), aparece el autocompletado con:
- **Nombre del snippet** (ej: "html:5")
- **Descripción** (ej: "HTML5 boilerplate")
- **Preview completo del template** antes de insertarlo

### 3. Inserción con Cursor Posicionado

Al seleccionar un snippet:
- Inserta el template completo
- Posiciona el cursor en el lugar correcto para empezar a escribir
- No necesitas borrar ni navegar manualmente

## Snippets Disponibles

### HTML (dentro de @{html})

| Trigger | Descripción | Template |
|---------|-------------|----------|
| `html` o `html:5` | HTML5 boilerplate completo | `<!DOCTYPE html>...` |
| `div` | Div element | `<div>\n    \n</div>` |
| `p` | Paragraph | `<p></p>` |
| `h1`, `h2`, `h3` | Headings | `<h1></h1>` |
| `a` | Anchor link | `<a href=""></a>` |
| `link` | Link stylesheet | `<link rel="stylesheet" href="">` |
| `script` | Script tag | `<script src=""></script>` |
| `style` | Style tag | `<style>\n    \n</style>` |
| `button` | Button element | `<button></button>` |
| `input` | Input field | `<input type="text">` |
| `form` | Form element | `<form action="">\n    \n</form>` |
| `table` | Table element | Tabla completa con thead/tbody |
| `ul` | Unordered list | `<ul>\n    <li></li>\n</ul>` |
| `ol` | Ordered list | `<ol>\n    <li></li>\n</ol>` |

### CSS (dentro de @{css})

| Trigger | Descripción | Template |
|---------|-------------|----------|
| `flex` | Flexbox container | `display: flex;\njustify-content: center;\nalign-items: center;` |
| `grid` | Grid container | `display: grid;\ngrid-template-columns: repeat(3, 1fr);\ngap: 10px;` |
| `center` | Center element | `margin: 0 auto;\ntext-align: center;` |

### TypeScript/JavaScript (dentro de @{ts} o @{js})

| Trigger | Descripción | Template |
|---------|-------------|----------|
| `function` | Function declaration | `function functionName() {\n\n}` |
| `arrow` | Arrow function | `const functionName = () => {\n    \n}` |
| `class` | Class declaration | `class ClassName {\n    constructor() {\n\n    }\n}` |
| `interface` | TypeScript interface | `interface InterfaceName {\n\n}` |
| `log` | Console log | `console.log();` |

## Cómo Probar

### Método 1: Archivo de Prueba

1. Abre `test_snippets.cpd` en Calcpad
2. Posiciónate dentro de un bloque (ej: entre `@{html}` y `@{end html}`)
3. Escribe un trigger (ej: "html")
4. Aparecerá el autocompletado con preview del template
5. Presiona Tab o Enter para insertar
6. El cursor se posicionará automáticamente donde debes escribir

### Método 2: Crear Nuevo Archivo

```calcpad
'Mi página web
@{html}

@{end html}
```

Dentro del bloque `@{html}`, escribe:
- `html` → Ver el HTML5 boilerplate completo
- `div` → Insertar `<div></div>`
- `table` → Insertar tabla completa
- etc.

## Archivos Modificados

1. **HtmlSnippets.cs** (NUEVO)
   - Define todos los snippets HTML/CSS/TS
   - Clase `HtmlSnippet` con Trigger, Description, Template, CursorOffset
   - Clase estática `HtmlSnippets` con diccionarios de snippets
   - Método `GetSnippetsForContext()` para obtener snippets según contexto

2. **MainWindow.AvalonEdit.cs**
   - Método `GetCurrentBlockContext()` - Detecta el bloque actual (@{html}, @{css}, etc.)
   - Método `ShowSnippetAutocomplete()` - Filtra y muestra snippets
   - Clase `SnippetCompletionData` - Implementa `ICompletionData` para mostrar snippets con preview
   - Modificado `TextEditor_TextEntered` - Detecta contexto y muestra snippets apropiados

## Arquitectura

### Flujo de Trabajo

```
Usuario escribe "html" dentro de @{html}
    ↓
TextEditor_TextEntered evento
    ↓
GetCurrentBlockContext() → Retorna "html"
    ↓
GetWordBeforeCursor() → Retorna "html"
    ↓
ShowSnippetAutocomplete("html", "html")
    ↓
HtmlSnippets.GetSnippetsForContext("html") → Retorna diccionario de snippets HTML
    ↓
Filtra snippets que empiezan con "html"
    ↓
Crea CompletionWindow con SnippetCompletionData
    ↓
Muestra preview: "HTML5 boilerplate\n\n<!DOCTYPE html>..."
    ↓
Usuario presiona Tab/Enter
    ↓
SnippetCompletionData.Complete() inserta template y posiciona cursor
```

### Detección de Contexto (Stack-Based)

El método `GetCurrentBlockContext()` usa un stack para rastrear bloques anidados:

```csharp
var blockStack = new Stack<string>();

foreach (var line in lines)
{
    if (line.StartsWith("@{"))
    {
        if (line.StartsWith("@{end"))
            blockStack.Pop();  // Cerrar bloque
        else
            blockStack.Push(language);  // Abrir bloque
    }
}

return blockStack.Count > 0 ? blockStack.Peek() : "calcpad";
```

Esto permite detectar correctamente el contexto incluso con bloques anidados.

## Pendiente

1. **Implementar snippets en MathEditor** - Usuario solicitó que funcione también en MathEditor
2. **Folding para bloques externos** - Ya implementado, pendiente de prueba
3. **Mensajes dinámicos de compilación** - "Compiling... Xs"

## Problemas Conocidos

Ninguno hasta el momento. La compilación fue exitosa sin errores.

## Compilación

```
Estado: ✅ Exitosa
Errores: 0
Warnings: 38 (nullable annotations - no críticos)
Ejecutable: Calcpad.Wpf\bin\Release\net10.0-windows\Calcpad.exe
```

## Próximos Pasos

1. Usuario prueba snippets en AvalonEdit dentro de bloques @{html}, @{css}, @{ts}
2. Verificar que el preview aparece correctamente
3. Verificar que el cursor se posiciona correctamente después de insertar
4. Si funciona, implementar lo mismo en MathEditor

## Notas

- Los bloques `@{css}` y `@{js}` son bloques SEPARADOS en Calcpad, no van dentro de `@{html}`
- Dentro de `@{html}` solo aparecen snippets HTML
- Dentro de `@{css}` solo aparecen snippets CSS
- Dentro de `@{ts}` o `@{js}` solo aparecen snippets TypeScript/JavaScript
