# 🎨 Propuesta: Función svg{} Simplificada para Calcpad

## 📊 Problema Actual

En el ejemplo **Rectangular Slab FEA**, dibujar el mesh de elementos finitos requiere **34 líneas de código SVG complejo**:

```calcpad
'<svg viewbox="'-d' '-d' 'w + 2*d' 'h + 2*d'" xmlns="http://www.w3.org/2000/svg" version="1.1" style="...">
'<style>.joint{fill:orangeRed;} .support{stroke:red; stroke-width:1; fill:lightpink;} ...</style>
'<rect x="'0'" y="'0'" width="'w'" height="'h'" style="fill:yellow; fill-opacity:0.2" />
#for e = 1 : n_e
    #hide
    x = x_c(e)*k
    y = y_c(e)*k
    #show
    '<text x="'x'" y="'h - y'" text-anchor="middle">'e'</text>
    '<rect x="'x - a_1/2*k'" y="'h - y - b_1/2*k'" width="'a_1*k'" height="'b_1*k'" class="element" />
#loop
#for i = 1 : n_s
    ... (más loops para apoyos y juntas)
#loop
'</svg>
```

**Problemas:**
- ❌ **Complejo**: 34+ líneas para un gráfico simple
- ❌ **Repetitivo**: Muchos loops y transformaciones manuales
- ❌ **Propenso a errores**: Fácil equivocarse en coordenadas
- ❌ **Difícil de mantener**: CSS inline mezclado con lógica
- ❌ **No reutilizable**: Cada gráfico requiere reescribir todo

---

## ✨ Solución Propuesta: Función `svg{}`

### 🎯 Objetivo

Crear una función declarativa y simple que permita:
1. Definir canvas SVG con pocas líneas
2. Dibujar elementos estructurales fácilmente
3. Graficar mallas FEA automáticamente
4. Personalizar estilos sin mezclar con lógica

---

## 📐 Propuesta 1: Sintaxis Declarativa Simple

### Ejemplo de Uso

```calcpad
"Parámetros del mesh FEA
a = 6'm, b = 4'm
n_a = 6, n_b = 4

@{svg width="400" height="267" title="Mesh de Elementos Finitos"}
    # Canvas base con grid opcional
    canvas(color: "lightyellow", opacity: 0.2)
    grid(nx: n_a, ny: n_b, color: "lightgray")

    # Dibujar malla de elementos
    fem_mesh(
        nx: n_a,
        ny: n_b,
        width: a,
        height: b,
        element_color: "lime",
        element_opacity: 0.1,
        border_color: "seaGreen",
        show_numbers: true
    )

    # Dibujar apoyos en bordes
    supports(
        edges: "all",
        type: "fixed",
        color: "red",
        size: 8
    )

    # Dibujar juntas/nodos
    nodes(
        radius: 4,
        color: "orangeRed",
        show_numbers: true,
        font_size: 10
    )
@{/svg}
```

**Resultado**: El mismo gráfico en **~15 líneas** vs 34+ líneas actuales

---

## 📐 Propuesta 2: API de Funciones Específicas

### Ejemplo de Uso

```calcpad
"Inicializar SVG
svg_init(width: 400, height: 267)

"Dibujar fondo
svg_rect(0, 0, 400, 267, fill: "lightyellow", opacity: 0.2)

"Dibujar malla FEA automáticamente
svg_fem_mesh(
    elements_x: n_a,
    elements_y: n_b,
    domain_width: a,
    domain_height: b,
    style: "green_lime"  # Preset de colores
)

"Dibujar apoyos
#for i = 1 : n_s
    j = s_j.i
    svg_support(x_j.j, y_j.j, type: "pin", color: "red")
#loop

"Dibujar nodos
#for j = 1 : n_j
    svg_node(x_j.j, y_j.j, radius: 4, label: j)
#loop

"Finalizar y renderizar
svg_render()
```

**Ventajas**:
- ✅ Más control granular
- ✅ Funciones reutilizables
- ✅ Fácil de debuguear

---

## 📐 Propuesta 3: Generadores de Alto Nivel

### Ejemplo de Uso

```calcpad
"Definir geometría
geom = fem_geometry(
    type: "rectangular",
    width: a,
    height: b,
    mesh_x: n_a,
    mesh_y: n_b
)

"Definir apoyos (vector de índices)
supports_vec = [1; 2; 3; ...] # Automático desde bordes

"Generar gráfico completo
svg_plot_fem(
    geometry: geom,
    supports: supports_vec,
    theme: "engineering",  # Preset completo de estilos
    show_element_numbers: true,
    show_node_numbers: true,
    width: 400
)
```

**Ventajas**:
- ✅ Máxima simplicidad (5-10 líneas)
- ✅ Presets profesionales
- ✅ Ideal para usuarios no expertos

---

## 🎨 Componentes SVG Sugeridos

### 1. **Elementos Básicos**
```calcpad
svg_line(x1, y1, x2, y2, style)
svg_rect(x, y, width, height, style)
svg_circle(cx, cy, r, style)
svg_polygon(points_vector, style)
svg_text(x, y, text, style)
svg_path(d_string, style)
```

### 2. **Elementos Estructurales**
```calcpad
svg_beam(x1, y1, x2, y2, height, color)
svg_support(x, y, type: "pin|roller|fixed", rotation)
svg_load(x, y, magnitude, direction, type: "point|distributed")
svg_moment(x, y, magnitude, rotation)
svg_dimension(x1, y1, x2, y2, offset, text)
```

### 3. **Mallas y Grids**
```calcpad
svg_grid(nx, ny, width, height, style)
svg_fem_mesh(elements_x, elements_y, width, height, style)
svg_triangular_mesh(nodes_matrix, elements_matrix, style)
svg_deformed_mesh(nodes_original, nodes_deformed, scale, style)
```

### 4. **Visualización de Resultados**
```calcpad
svg_contour_plot(values_matrix, colormap: "rainbow|thermal|grayscale")
svg_vector_field(x_vectors, y_vectors, scale, style)
svg_stress_diagram(elements, stress_values, colormap)
svg_displacement_plot(nodes, displacements, scale, style)
```

### 5. **Herramientas de Composición**
```calcpad
svg_layer(name, visible: true|false)  # Capas tipo Photoshop
svg_group(id, transform)              # Agrupar elementos
svg_clip(region)                      # Recortar área
svg_animate(property, from, to, duration)
```

---

## 🎯 Propuesta de Implementación

### Opción A: **Parser Nativo en C#** (Recomendado)
**Ubicación**: `Calcpad.Core/Parsers/SvgParser/`

**Ventajas**:
- ⭐ Máximo rendimiento
- ⭐ Integración perfecta con ExpressionParser
- ⭐ Validación de tipos en tiempo de compilación
- ⭐ Intellisense/autocomplete posible

**Implementación**:
```csharp
// Calcpad.Core/Parsers/SvgParser/SvgParser.cs
public class SvgParser
{
    private StringBuilder _svgBuilder;
    private SvgConfig _config;

    public string Parse(string svgCode, MathParser mathParser)
    {
        // 1. Parsear bloques @{svg}...@{/svg}
        // 2. Interpretar comandos (fem_mesh, nodes, supports, etc.)
        // 3. Generar SVG optimizado
        // 4. Retornar string SVG completo
    }

    private string ParseFemMesh(Dictionary<string, object> parameters)
    {
        // Generar automáticamente el mesh con loops
        // Aplicar estilos predefinidos
        // Retornar fragmento SVG
    }
}
```

**Integración en ExpressionParser.cs**:
```csharp
// En ParseKeyword() agregar:
case "@{svg}":
    var svgParser = new SvgParser();
    var svgCode = ExtractBlockUntil("@{/svg}");
    var svgResult = svgParser.Parse(svgCode, _parser);
    _sb.AppendLine(svgResult);
    break;
```

---

### Opción B: **Librería Python** (Más Rápido de Implementar)

**Ventajas**:
- ⚡ Desarrollo rápido
- ⚡ Usar librerías existentes (matplotlib, plotly, etc.)
- ⚡ Prototipo funcional en horas

**Implementación**:
```calcpad
@{py}
import calcpad_svg as svg

# Crear canvas
canvas = svg.Canvas(width=400, height=267)

# Dibujar mesh FEA
canvas.fem_mesh(
    elements_x=6,
    elements_y=4,
    width=6.0,
    height=4.0,
    style="engineering"
)

# Renderizar
print(canvas.to_svg())
@{/py}
```

---

### Opción C: **Macros de Calcpad** (Sin Modificar Core)

**Ventajas**:
- ✅ No requiere modificar Calcpad.Core
- ✅ Usuarios pueden extender fácilmente
- ✅ Portable (archivo .cpd)

**Implementación**:
```calcpad
"Archivo: svg_library.cpd
#def svg_fem_mesh(nx$; ny$; w$; h$; style$)
    #hide
    "Generar coordenadas de nodos
    ... (lógica de generación)
    #show

    '<svg ...>
    #for e = 1 : nx$*ny$
        ... (dibujar elementos)
    #loop
    '</svg>
#end def

"Uso en archivo principal:
#include "svg_library.cpd"
svg_fem_mesh(6; 4; 6; 4; "green")
```

---

## 🎨 Presets de Estilos Sugeridos

### 1. **Engineering Theme**
```css
.element { stroke: #2E7D32; fill: #81C784; opacity: 0.3; }
.node { fill: #FF5722; }
.support { stroke: #D32F2F; fill: #FFCDD2; }
```

### 2. **Blueprint Theme**
```css
.element { stroke: #1976D2; fill: #64B5F6; opacity: 0.2; }
.node { fill: #FFF; }
.support { stroke: #FFF; }
background: #0D47A1;
```

### 3. **Grayscale Theme**
```css
.element { stroke: #424242; fill: #BDBDBD; opacity: 0.5; }
.node { fill: #212121; }
.support { stroke: #757575; }
```

### 4. **Thermal Colormap**
```css
/* Para mapas de esfuerzos */
low: #0000FF (azul)
medium: #00FF00 (verde)
high: #FFFF00 (amarillo)
critical: #FF0000 (rojo)
```

---

## 📊 Comparación de Código

### Código Actual (Rectangular Slab FEA)
```calcpad
# 34+ líneas de código SVG
'<svg viewbox="..." xmlns="..." ...>
'<style>...</style>
#for e = 1 : n_e
    #hide
    x = x_c(e)*k
    y = y_c(e)*k
    #show
    '<text ...>'e'</text>
    '<rect .../>
#loop
... (3 loops más)
'</svg>
```

### Con Función svg{} Propuesta
```calcpad
# ~10 líneas de código declarativo
@{svg width="400" height="267"}
    fem_mesh(nx: n_a, ny: n_b, width: a, height: b)
    supports(edges: "all", type: "fixed")
    nodes(show_numbers: true)
@{/svg}
```

**Reducción**: 70% menos código

---

## 🚀 Roadmap de Implementación

### Fase 1: **MVP - Comandos Básicos** (1-2 semanas)
- [ ] Parser básico de bloques `@{svg}...@{/svg}`
- [ ] Comandos: `canvas`, `rect`, `circle`, `line`, `text`
- [ ] Sistema de estilos básico
- [ ] Integración con ExpressionParser

### Fase 2: **Elementos Estructurales** (2-3 semanas)
- [ ] `fem_mesh` - Malla rectangular automática
- [ ] `nodes` - Nodos con etiquetas
- [ ] `supports` - Apoyos con tipos (pin, roller, fixed)
- [ ] `beam` - Vigas con dimensiones

### Fase 3: **Visualización Avanzada** (3-4 semanas)
- [ ] `contour_plot` - Mapas de contorno
- [ ] `vector_field` - Campo de vectores (fuerzas, desplazamientos)
- [ ] `deformed_mesh` - Malla deformada con escala
- [ ] `stress_diagram` - Diagrama de esfuerzos con colormaps

### Fase 4: **Herramientas Avanzadas** (2-3 semanas)
- [ ] Capas y grupos
- [ ] Animaciones
- [ ] Exportación SVG standalone
- [ ] Temas/presets personalizables

---

## 💡 Recomendación Final

**Mejor enfoque**: **Opción A (Parser Nativo en C#)** combinado con **Opción C (Macros)**

**Estrategia**:
1. **Corto plazo**: Crear macros `.cpd` reutilizables (sin modificar core)
2. **Mediano plazo**: Implementar parser nativo en C# para mejor performance
3. **Largo plazo**: Expandir con visualizaciones avanzadas

**Primer paso inmediato**:
Crear `svg_fem_library.cpd` con macros para:
- `svg_fem_mesh()`
- `svg_nodes()`
- `svg_supports()`
- `svg_loads()`

---

## 📝 Siguiente Acción

¿Quieres que:

1. **📦 Cree macros `.cpd` reutilizables** (solución inmediata, sin modificar core)
2. **🔧 Implemente parser nativo en C#** (solución robusta, requiere modificar core)
3. **🎨 Cree ejemplo mejorado de Rectangular Slab FEA** usando macros
4. **📚 Documente API completa** de funciones svg{} propuestas

**Mi recomendación**: Empezar con **opción 1** (macros) para tener algo funcional hoy mismo, luego migrar a parser nativo.

¿Qué prefieres?
