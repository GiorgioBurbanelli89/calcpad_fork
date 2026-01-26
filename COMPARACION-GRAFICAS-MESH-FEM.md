# 🎨 Comparación: Gráficas del Mallado FEM
## Rectangular Slab FEA - Solo Parte Gráfica del Mesh

---

## 📊 Métodos de Graficación en Calcpad

### 1. **SVG Manual** (Método Actual en Rectangular Slab FEA)

**Ubicación**: Líneas 83-116 del archivo original

**Características**:
- ✅ Control total sobre elementos gráficos
- ✅ Genera SVG estándar embebido en HTML
- ❌ Código muy extenso (34+ líneas)
- ❌ Requiere cálculos manuales de coordenadas
- ❌ Difícil de mantener

**Código**:
```calcpad
#hide
w = 400
k = w/a
d = 20
h = b/a*w
r = 0.04*k
#show

'<svg viewbox="'-d' '-d' 'w + 2*d' 'h + 2*d'" xmlns="http://www.w3.org/2000/svg" version="1.1" style=" font-family: Segoe UI; font-size:10px; width:'w'pt; height:'h'pt">
'<style>.joint{fill:orangeRed;} .support{stroke:red; stroke-width:1; fill:lightpink;} .element{stroke:seaGreen; stroke-width:1; fill:lime; fill-opacity:0.1; stroke-opacity:0.5}</style>
'<rect x="'0'" y="'0'" width="'w'" height="'h'" style="fill:yellow; fill-opacity:0.2" />

# Loop para dibujar elementos
#for e = 1 : n_e
	#hide
	x = x_c(e)*k
	y = y_c(e)*k
	#show
	'<text x="'x'" y="'h - y'" text-anchor="middle">'e'</text>
	'<rect x="'x - a_1/2*k'" y="'h - y - b_1/2*k'" width="'a_1*k'" height="'b_1*k'" class="element" />
#loop

# Loop para dibujar apoyos
#for i = 1 : n_s
	j = s_j.i
	#hide
	x = x_j.j*k
	y = h - y_j.j*k
	#show
	#if y_j.j ≡ 0 ∨ y_j.j ≡ b
		'<line x1="'x - 4*r'" y1="'y'" x2="'x + 4*r'" y2="'y'" class="support"/>
	#end if
	#if x_j.j ≡ 0 ∨ x_j.j ≡ a
		'<line x1="'x'" y1="'y - 4*r'" x2="'x'" y2="'y + 4*r'" class="support"/>
	#end if
	'<circle cx="'x'" cy="'y'" r="'2*r'" class="support"/>
#loop

# Loop para dibujar nodos
#for j = 1 : n_j
	#hide
	x = x_j.j*k
	y = h - y_j.j*k
	#show
	'<circle cx="'x'" cy="'y'" r="'r'" class="joint" />
	'<text x="'x + 2*r'" y="'y - r'" text-anchor="start">'j'</text>
#loop

'</svg>
```

**Total**: ~34 líneas de código complejo

---

### 2. **$Plot** (Sistema Nativo de Calcpad)

**Características**:
- ✅ Sistema integrado de Calcpad
- ✅ Sintaxis simple para funciones y puntos
- ⚠️ **Limitado para meshes FEM** (diseñado para gráficas de funciones)
- ❌ No es ideal para topología de elementos

**Sintaxis General**:
```calcpad
PlotWidth = 400
PlotHeight = 300
PlotSVG = 1

$Plot{f(x) & x|g(x) @ x = 0 : 10}
```

**Intento de Mesh FEM con $Plot** (NO RECOMENDADO):
```calcpad
# Graficar solo nodos como puntos dispersos
PlotWidth = 400
PlotHeight = 267

# Crear serie de puntos (x|y)
#hide
node_series = ""
#for j = 1 : n_j
    node_series = node_series & " & " & x_j.j & "|" & y_j.j
#loop
#show

$Plot{node_series @ x = 0 : a}
```

**Problemas**:
- ❌ No puede dibujar rectángulos de elementos
- ❌ No puede dibujar apoyos
- ❌ No puede mostrar topología de conectividad
- ❌ Solo muestra puntos dispersos

**Conclusión**: `$Plot` NO es adecuado para visualizar meshes FEM estructurados.

---

## 🐙 Método 3: Octave/MATLAB

**Características**:
- ✅ Herramientas especializadas para FEM (`patch`, `trisurf`)
- ✅ Sintaxis compacta y expresiva
- ✅ Renderizado de alta calidad
- ✅ Interactivo (zoom, pan, rotate)

**Código Octave**:
```octave
% Datos del mesh (desde Calcpad)
a = 6; b = 4;
n_a = 6; n_b = 4;

% Generar coordenadas de nodos
[X, Y] = meshgrid(linspace(0, a, n_a+1), linspace(0, b, n_b+1));
x_nodes = X(:);
y_nodes = Y(:);
n_nodes = length(x_nodes);

% Generar conectividad de elementos (cuadriláteros)
elements = [];
for i = 1:n_a
    for j = 1:n_b
        n1 = (i-1)*(n_b+1) + j;
        n2 = n1 + (n_b+1);
        n3 = n2 + 1;
        n4 = n1 + 1;
        elements = [elements; n1 n2 n3 n4];
    end
end

% Graficar mesh
figure('Position', [100 100 600 400]);
hold on;

% Dibujar elementos como patches
for e = 1:size(elements, 1)
    nodes = elements(e, :);
    x_elem = x_nodes(nodes);
    y_elem = y_nodes(nodes);

    % Dibujar elemento
    patch(x_elem, y_elem, 'g', ...
          'FaceAlpha', 0.1, ...
          'EdgeColor', [0 0.5 0], ...
          'LineWidth', 1);

    % Etiqueta del elemento
    x_center = mean(x_elem);
    y_center = mean(y_elem);
    text(x_center, y_center, num2str(e), ...
         'HorizontalAlignment', 'center', ...
         'FontSize', 8);
end

% Dibujar nodos
plot(x_nodes, y_nodes, 'o', ...
     'MarkerSize', 6, ...
     'MarkerFaceColor', [1 0.27 0], ...
     'MarkerEdgeColor', [1 0.27 0]);

% Etiquetas de nodos
for j = 1:n_nodes
    text(x_nodes(j), y_nodes(j), ['  ' num2str(j)], ...
         'FontSize', 8, ...
         'VerticalAlignment', 'bottom');
end

% Dibujar apoyos en bordes
% Identificar nodos del borde
border_nodes = unique([find(x_nodes == 0); ...
                       find(x_nodes == a); ...
                       find(y_nodes == 0); ...
                       find(y_nodes == b)]);

% Dibujar símbolos de apoyo
for i = 1:length(border_nodes)
    n = border_nodes(i);
    x = x_nodes(n);
    y = y_nodes(n);

    % Líneas de apoyo
    if y == 0 || y == b
        plot([x-0.2 x+0.2], [y y], 'r-', 'LineWidth', 2);
    end
    if x == 0 || x == a
        plot([x x], [y-0.2 y+0.2], 'r-', 'LineWidth', 2);
    end

    % Círculo de apoyo
    plot(x, y, 'o', ...
         'MarkerSize', 8, ...
         'MarkerFaceColor', [1 0.8 0.8], ...
         'MarkerEdgeColor', 'r', ...
         'LineWidth', 1.5);
end

% Configuración de gráfico
axis equal;
xlim([-0.5 a+0.5]);
ylim([-0.5 b+0.5]);
xlabel('X (m)');
ylabel('Y (m)');
title('Mesh de Elementos Finitos - Losa Rectangular');
grid on;
box on;

% Guardar como imagen
print('fem_mesh_octave.png', '-dpng', '-r150');
```

**Total**: ~80 líneas (con comentarios y formateo completo)
**Líneas efectivas**: ~40 líneas

---

## 🐍 Método 4: Python (Matplotlib)

**Características**:
- ✅ Librería estándar de visualización científica
- ✅ Control fino sobre estilos
- ✅ Exportación a múltiples formatos (PNG, SVG, PDF)
- ✅ Integrable con Calcpad vía @{py}

**Código Python**:
```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.collections import PatchCollection

# Datos del mesh
a = 6.0  # m
b = 4.0  # m
n_a = 6
n_b = 4

# Generar coordenadas de nodos
x = np.linspace(0, a, n_a + 1)
y = np.linspace(0, b, n_b + 1)
X, Y = np.meshgrid(x, y)
x_nodes = X.flatten()
y_nodes = Y.flatten()
n_nodes = len(x_nodes)

# Generar conectividad de elementos
elements = []
for i in range(n_a):
    for j in range(n_b):
        n1 = i * (n_b + 1) + j
        n2 = n1 + (n_b + 1)
        n3 = n2 + 1
        n4 = n1 + 1
        elements.append([n1, n2, n3, n4])
elements = np.array(elements)

# Crear figura
fig, ax = plt.subplots(figsize=(8, 5.5))

# Dibujar fondo
ax.add_patch(Rectangle((0, 0), a, b,
                       facecolor='lightyellow',
                       alpha=0.2,
                       zorder=0))

# Dibujar elementos
element_patches = []
for e, elem_nodes in enumerate(elements):
    x_elem = x_nodes[elem_nodes]
    y_elem = y_nodes[elem_nodes]

    # Calcular dimensiones del elemento
    x_min, x_max = x_elem.min(), x_elem.max()
    y_min, y_max = y_elem.min(), y_elem.max()
    width = x_max - x_min
    height = y_max - y_min

    # Crear rectángulo
    rect = Rectangle((x_min, y_min), width, height,
                     facecolor='lime',
                     edgecolor='seagreen',
                     alpha=0.1,
                     linewidth=1)
    ax.add_patch(rect)

    # Etiqueta del elemento
    x_center = x_elem.mean()
    y_center = y_elem.mean()
    ax.text(x_center, y_center, str(e+1),
           ha='center', va='center',
           fontsize=8, zorder=10)

# Identificar nodos de borde (apoyos)
border_mask = ((x_nodes == 0) | (x_nodes == a) |
               (y_nodes == 0) | (y_nodes == b))
border_indices = np.where(border_mask)[0]

# Dibujar apoyos
for idx in border_indices:
    x_node = x_nodes[idx]
    y_node = y_nodes[idx]

    # Líneas de apoyo
    line_length = 0.15
    if y_node == 0 or y_node == b:
        ax.plot([x_node - line_length, x_node + line_length],
               [y_node, y_node],
               'r-', linewidth=1.5, zorder=5)

    if x_node == 0 or x_node == a:
        ax.plot([x_node, x_node],
               [y_node - line_length, y_node + line_length],
               'r-', linewidth=1.5, zorder=5)

    # Círculo de apoyo
    circle = Circle((x_node, y_node), 0.08,
                   facecolor='lightpink',
                   edgecolor='red',
                   linewidth=1,
                   zorder=6)
    ax.add_patch(circle)

# Dibujar todos los nodos
ax.plot(x_nodes, y_nodes, 'o',
       markersize=6,
       markerfacecolor='orangered',
       markeredgecolor='orangered',
       zorder=8)

# Etiquetas de nodos
for j in range(n_nodes):
    ax.text(x_nodes[j] + 0.08, y_nodes[j] - 0.08,
           str(j+1),
           fontsize=7,
           ha='left',
           va='top',
           zorder=9)

# Configuración del gráfico
ax.set_xlim(-0.4, a + 0.4)
ax.set_ylim(-0.4, b + 0.4)
ax.set_aspect('equal')
ax.set_xlabel('X (m)', fontsize=10)
ax.set_ylabel('Y (m)', fontsize=10)
ax.set_title('Mesh de Elementos Finitos - Losa Rectangular',
            fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

plt.tight_layout()

# Guardar como PNG y SVG
plt.savefig('fem_mesh_python.png', dpi=150, bbox_inches='tight')
plt.savefig('fem_mesh_python.svg', bbox_inches='tight')

plt.show()

# Para embeber en Calcpad, retornar SVG como string
# import io
# buf = io.StringIO()
# plt.savefig(buf, format='svg')
# svg_str = buf.getvalue()
# print(svg_str)
```

**Total**: ~110 líneas (con comentarios completos)
**Líneas efectivas**: ~50 líneas

---

## 🐍 Método 5: Python Optimizado (usando bibliotecas especializadas)

**Usando meshio + pyvista para FEM**:

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

def plot_fem_mesh_optimized(a, b, n_a, n_b):
    """
    Función optimizada para graficar mesh FEM rectangular
    """
    # Generar mesh
    x = np.linspace(0, a, n_a + 1)
    y = np.linspace(0, b, n_b + 1)
    X, Y = np.meshgrid(x, y)

    # Coordenadas de nodos
    nodes = np.column_stack([X.flatten(), Y.flatten()])

    # Conectividad (automática para grid rectangular)
    n_b1 = n_b + 1
    elements = []
    for i in range(n_a):
        for j in range(n_b):
            n1 = i * n_b1 + j
            elements.append([n1, n1 + n_b1, n1 + n_b1 + 1, n1 + 1])
    elements = np.array(elements)

    # Crear polígonos para elementos
    element_coords = nodes[elements]

    # Graficar
    fig, ax = plt.subplots(figsize=(8, 5.5))

    # Colección de polígonos (más eficiente que patches individuales)
    coll = PolyCollection(element_coords,
                          facecolors='lime',
                          edgecolors='seagreen',
                          alpha=0.1,
                          linewidths=1)
    ax.add_collection(coll)

    # Nodos
    ax.plot(nodes[:, 0], nodes[:, 1], 'o',
           markersize=6,
           color='orangered')

    # Identificar bordes
    border = ((nodes[:, 0] == 0) | (nodes[:, 0] == a) |
              (nodes[:, 1] == 0) | (nodes[:, 1] == b))

    # Apoyos
    ax.plot(nodes[border, 0], nodes[border, 1], 'o',
           markersize=10,
           markerfacecolor='lightpink',
           markeredgecolor='red',
           linewidth=1.5)

    ax.set_aspect('equal')
    ax.set_xlim(-0.4, a + 0.4)
    ax.set_ylim(-0.4, b + 0.4)
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_title('FEM Mesh')
    ax.grid(True, alpha=0.3)

    return fig, ax

# Usar
fig, ax = plot_fem_mesh_optimized(6, 4, 6, 4)
plt.savefig('fem_mesh_optimized.png', dpi=150)
plt.show()
```

**Total**: ~60 líneas (mucho más compacto)

---

## 📊 Comparación Resumida

| Método | Líneas Código | Complejidad | Calidad Visual | Interactividad | Velocidad | Integración Calcpad |
|--------|---------------|-------------|----------------|----------------|-----------|---------------------|
| **SVG Manual** | ~34 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐⭐ | ✅ Nativo |
| **$Plot** | N/A | ❌ | ❌ | ❌ | ⭐⭐⭐⭐⭐ | ✅ Nativo |
| **Octave** | ~40 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐ | ⚠️ Vía @{octave} |
| **Python std** | ~50 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⚠️ | ⭐⭐⭐⭐ | ✅ Vía @{py} |
| **Python opt** | ~25 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⚠️ | ⭐⭐⭐⭐⭐ | ✅ Vía @{py} |

---

## 🎯 Recomendaciones

### Para Calcpad Puro
1. **Crear macro SVG reutilizable** → Reduce de 34 líneas a 1 línea
2. **NO usar $Plot para meshes FEM** → No es apropiado

### Para Integración con Lenguajes Externos
1. **Python optimizado** → Mejor balance calidad/complejidad
2. **Octave** → Si ya lo usas para cálculos FEM
3. **Embeber SVG generado** → Usar Python para generar, retornar SVG string

### Código Híbrido Recomendado
```calcpad
@{py}
import matplotlib.pyplot as plt
import numpy as np
# ... (código Python optimizado)
# Generar SVG como string
import io
buf = io.StringIO()
plt.savefig(buf, format='svg')
print(buf.getvalue())
@{/py}
```

Esto te da:
- ✅ Código compacto (~30 líneas Python)
- ✅ Calidad profesional
- ✅ Embebido directamente en Output de Calcpad
- ✅ Sin archivos externos

---

## 💡 Conclusión

**Mejor opción actual**: Macro SVG en Calcpad (reduce 34→1 línea)
**Mejor opción futura**: Python optimizado embebido vía @{py}
**NO usar**: $Plot (no diseñado para meshes FEM)
