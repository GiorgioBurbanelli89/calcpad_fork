# 🔷 Cómo Funciona awatif-ui

## Análisis completo de la arquitectura awatif-ui y cómo replicarla en Calcpad

---

## 1. Estructura de awatif-ui

```
awatif-2.0.0/awatif-ui/
├── package.json          ← Dependencias y scripts
├── vite.config.ts        ← Configuración de Vite
├── tsconfig.json         ← Configuración TypeScript
└── src/
    ├── color-map/        ← Ejemplo que analizamos
    │   ├── index.html
    │   ├── main.ts
    │   ├── getColorMap.ts
    │   └── getLegend.ts
    ├── viewer/
    ├── dialog/
    ├── parameters/
    └── ...
```

---

## 2. Flujo de Ejecución en awatif-ui

### Paso 1: Iniciar Vite Dev Server

```bash
npm run dev
# → Ejecuta: vite
# → Inicia servidor en localhost:4600
# → Abre: tables/index.html
```

### Paso 2: Cargar HTML

**`src/color-map/index.html`:**
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Awatif UI - Color Map</title>
  </head>
  <body>
    <script type="module" src="./main.ts"></script>
    <!--                 ⬆️ Vite compila TypeScript -->
  </body>
</html>
```

### Paso 3: Vite Compila TypeScript

Cuando el navegador pide `main.ts`:
1. Vite intercepta la petición
2. Compila TypeScript → JavaScript
3. Resuelve imports (van, three, awatif-fem)
4. Sirve el código compilado
5. Hot reload si hay cambios

### Paso 4: Ejecutar main.ts

**`src/color-map/main.ts`:**
```typescript
import van from "vanjs-core";           // ← Estado reactivo
import { Node } from "awatif-fem";      // ← Tipos de FEM
import { getViewer } from "../viewer/getViewer";
import { getColorMap } from "./getColorMap";
import { getLegend } from "./getLegend";

// 1. Crear estados reactivos
const nodes = van.state([
  [0, 0, 0],
  [5, 0, 0],
  [5, 0, 5],
  [0, 0, 5],
] as Node[]);

const elements = van.state([
  [0, 1, 2],
  [0, 2, 3],
]);

const values = van.state([0, 0, 10, 0]);

// 2. Crear objeto 3D con color map
const objects3D = van.state([
  getColorMap(nodes, elements, values)
]);

// 3. Actualizar valores después de 1 segundo
setTimeout(() => {
  values.val = [1, 5, 0, 0];  // ← Cambiar estado
  objects3D.val = [...objects3D.rawVal]; // ← Trigger re-render
}, 1000);

// 4. Agregar componentes al DOM
document.body.append(
  getLegend(values),
  getViewer({
    mesh: { nodes, elements },
    objects3D,
  })
);
```

### Paso 5: getColorMap Genera Mesh 3D

**`src/color-map/getColorMap.ts`:**
```typescript
import * as THREE from "three";
import { Lut } from "three/addons/math/Lut.js";
import van from "vanjs-core";

export function getColorMap(
  nodes: State<Node[]>,
  elements: State<Element[]>,
  values: State<number[]>
): THREE.Mesh {

  const lut = new Lut();  // ← Look-Up Table para colores
  const color = new THREE.Color();

  // Crear mesh Three.js
  const colorMap = new THREE.Mesh(
    new THREE.BufferGeometry(),
    new THREE.MeshBasicMaterial({
      side: THREE.DoubleSide,
      vertexColors: true,
    })
  );

  lut.setColorMap("rainbow");

  // ⭐ REACTIVIDAD: Cuando nodes/elements/values cambien
  van.derive(() => {
    // Actualizar geometría
    colorMap.geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(nodes.val.flat(), 3)
    );

    colorMap.geometry.setIndex(
      new THREE.Uint16BufferAttribute(
        elements.val.filter((e) => e.length != 2).flat(),
        1
      )
    );

    // Actualizar colores según valores
    lut.setMax(Math.max(...values.val));
    lut.setMin(Math.min(...values.val));

    for (let i = 0; i < values.val.length; i++) {
      const lutColor = lut.getColor(values.val[i]);
      color.copy(lutColor).convertSRGBToLinear();
      color.multiplyScalar(0.6);

      colorMap.geometry.attributes.color.setXYZ(
        i, color.r, color.g, color.b
      );
    }
  });

  return colorMap;
}
```

---

## 3. Conceptos Clave de awatif-ui

### A. Estado Reactivo con van.js

**van.state()** crea estado observable:

```typescript
const nodes = van.state([...]);

// Leer valor
console.log(nodes.val);

// Cambiar valor (trigger reactivity)
nodes.val = [...nuevosNodos];
```

**van.derive()** crea efecto reactivo:

```typescript
van.derive(() => {
  // Este código se ejecuta automáticamente
  // cada vez que nodes.val cambia
  console.log(nodes.val);
});
```

### B. Vite: Build Tool Moderno

**¿Qué hace Vite?**

1. **Dev Server con HMR** (Hot Module Replacement)
   - Compilación instantánea
   - Recarga solo lo que cambió
   - Sin recargar toda la página

2. **Resolución de Imports**
   ```typescript
   import van from "vanjs-core";        // ← node_modules
   import { getViewer } from "../viewer"; // ← Relativo
   ```

3. **Compilación TypeScript en Tiempo Real**
   - `.ts` → `.js` al vuelo
   - Sin paso de build previo en desarrollo

4. **Optimización para Producción**
   ```bash
   npm run build
   # → Bundling, minificación, tree-shaking
   ```

### C. Arquitectura Modular

Cada componente de UI es una carpeta con:

```
component/
├── index.html     ← Entry point
├── main.ts        ← Lógica principal
├── helper1.ts     ← Funciones auxiliares
└── helper2.ts
```

**Beneficios:**
- Separación de responsabilidades
- Código reutilizable
- Fácil de mantener

---

## 4. Diferencias: awatif-ui vs Calcpad

| Aspecto | awatif-ui | Calcpad |
|---------|-----------|---------|
| **Runtime** | Navegador + Vite | ts-node |
| **Entry Point** | `index.html` con `<script type="module">` | `.cpd` con `@{html}` `@{ts}` |
| **Estado Reactivo** | van.js (`van.state()`) | Manual (clase ReactiveState) |
| **Imports** | ✅ Soportado (vite resuelve) | ❌ Limitado (un solo archivo) |
| **3D Graphics** | ✅ Three.js | ⚠️ Posible pero complicado |
| **Hot Reload** | ✅ Automático | ❌ Manual (F5) |
| **Dependencias** | npm packages | Solo globales |
| **Uso Ideal** | Apps web complejas | Cálculos + visualización |

---

## 5. Replicar awatif-ui en Calcpad

### ✅ Lo que SÍ puedes replicar:

1. **Patrón Reactivo:**
   ```typescript
   class ReactiveState<T> {
     private _value: T;
     private observers = [];

     set value(newValue: T) {
       this._value = newValue;
       this.notify(); // trigger re-render
     }
   }
   ```

2. **Estructura HTML + CSS + TS:**
   ```calcpad
   @{css}
   /* estilos */
   @{end css}

   @{html}
   <!-- estructura -->
   @{end html}

   @{ts}
   // lógica
   @{end ts}
   ```

3. **Manipulación del DOM:**
   ```typescript
   const el = document.getElementById('id');
   if (el) {
     el.textContent = 'nuevo texto';
   }
   ```

4. **Event Handlers:**
   ```html
   <button onclick="myFunction()">Click</button>
   ```

5. **Animaciones y Transiciones CSS**

### ❌ Lo que NO puedes replicar fácilmente:

1. **Imports de librerías externas:**
   ```typescript
   import * as THREE from "three"; // ❌ No funciona en Calcpad
   ```

2. **Hot Module Replacement**

3. **npm packages** (van, lit-html, three)

4. **Módulos TypeScript separados**

### ⚠️ Workarounds en Calcpad:

**Para usar librerías externas:**

```html
@{html}
<!DOCTYPE html>
<html>
<head>
  <!-- Cargar desde CDN -->
  <script src="https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/vanjs-core@1.5.2/dist/van.min.js"></script>
</head>
<body>
  <div id="app"></div>
</body>
</html>
@{end html}

@{ts}
// Ahora puedes usar THREE y van desde window
const scene = new (window as any).THREE.Scene();
const van = (window as any).van;
@{end ts}
```

---

## 6. Ejemplo Completo: Replicar color-map en Calcpad

### awatif-ui original:

```typescript
// main.ts
import van from "vanjs-core";
import { getColorMap } from "./getColorMap";

const nodes = van.state([...]);
const values = van.state([0, 0, 10, 0]);

setTimeout(() => {
  values.val = [1, 5, 0, 0];
}, 1000);
```

### Equivalente en Calcpad:

```calcpad
"Replica de awatif-ui color-map

#hide

@{css}
/* estilos */
@{end css}

@{html}
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/vanjs-core@1.5.2/dist/van.min.js"></script>
</head>
<body>
  <div id="nodes-container"></div>
</body>
</html>
@{end html}

@{ts}
const van = (window as any).van;

// Estado reactivo (como awatif-ui)
const nodes = van.state([
  [0, 0, 0],
  [5, 0, 0],
  [5, 0, 5],
  [0, 0, 5]
]);

const values = van.state([0, 0, 10, 0]);

// Render reactivo
van.derive(() => {
  const container = document.getElementById('nodes-container');
  if (!container) return;

  container.innerHTML = '';
  nodes.val.forEach((node: number[], idx: number) => {
    const div = document.createElement('div');
    div.textContent = `Nodo ${idx}: ${node.join(', ')} - Valor: ${values.val[idx]}`;
    container.appendChild(div);
  });
});

// Actualizar después de 1 segundo (como awatif-ui)
setTimeout(() => {
  values.val = [1, 5, 0, 0];
}, 1000);

console.log('✅ Color map replica funcionando');
@{end ts}

#show
```

---

## 7. Conceptos Avanzados de awatif-ui

### A. Lut (Look-Up Table)

Mapea valores numéricos a colores:

```typescript
const lut = new Lut();
lut.setColorMap("rainbow"); // azul → verde → rojo
lut.setMin(0);
lut.setMax(10);

const color = lut.getColor(5); // → color en medio del rango
```

**Mapeado:**
- 0 → Azul (#0000FF)
- 2.5 → Cyan (#00FFFF)
- 5 → Verde (#00FF00)
- 7.5 → Amarillo (#FFFF00)
- 10 → Rojo (#FF0000)

### B. BufferGeometry de Three.js

Geometría de alto rendimiento:

```typescript
const geometry = new THREE.BufferGeometry();

// Posiciones de vértices
geometry.setAttribute(
  "position",
  new THREE.Float32BufferAttribute([
    0, 0, 0,  // vértice 0
    5, 0, 0,  // vértice 1
    5, 0, 5,  // vértice 2
  ], 3)  // 3 valores por vértice (x, y, z)
);

// Índices para formar triángulos
geometry.setIndex(
  new THREE.Uint16BufferAttribute([
    0, 1, 2,  // triángulo con vértices 0-1-2
  ], 1)
);

// Colores por vértice
geometry.setAttribute(
  "color",
  new THREE.Float32BufferAttribute([
    1, 0, 0,  // rojo para vértice 0
    0, 1, 0,  // verde para vértice 1
    0, 0, 1,  // azul para vértice 2
  ], 3)
);
```

### C. van.derive() Profundo

**¿Cómo funciona internamente?**

```typescript
// Simplificado
class VanState<T> {
  private _val: T;
  private listeners = new Set<Function>();

  get val(): T {
    // Registrar listener actual si existe
    if (currentListener) {
      this.listeners.add(currentListener);
    }
    return this._val;
  }

  set val(newVal: T) {
    this._val = newVal;
    // Notificar a todos los listeners
    this.listeners.forEach(fn => fn());
  }
}

function derive(fn: Function) {
  currentListener = fn;
  fn(); // Ejecutar una vez
  currentListener = null;
}
```

**Resultado:**
- Acceder a `state.val` dentro de `derive()` auto-subscribe
- Cambiar `state.val` auto-trigger re-ejecución

---

## 8. Arquitectura de Producción en awatif-ui

### Build Process:

```bash
npm run build
# → Vite bundlea todo
# → TypeScript → JavaScript
# → Minificación
# → Tree-shaking (elimina código no usado)
# → Output: dist/
```

### Estructura Final:

```
dist/
├── index.html
├── assets/
│   ├── index-abc123.js    ← Bundle principal
│   ├── vendor-def456.js   ← Librerías (three, van)
│   └── style-ghi789.css   ← Estilos combinados
└── img/
    └── favicon.ico
```

### Optimizaciones:

- **Code Splitting:** Carga solo lo necesario
- **Lazy Loading:** Componentes bajo demanda
- **Minificación:** Reduce tamaño
- **Compression:** Gzip/Brotli

---

## 9. Resumen Ejecutivo

### awatif-ui ES:

✅ Framework moderno para apps FEM
✅ Vite + TypeScript + van.js + Three.js
✅ Estado reactivo automático
✅ Visualización 3D de mallas
✅ Hot reload en desarrollo
✅ Optimizado para producción

### Calcpad PUEDE:

✅ Replicar patrón HTML + CSS + TS
✅ Usar estado reactivo manual
✅ Manipular DOM
✅ Cargar libs desde CDN
⚠️ Sin hot reload
⚠️ Sin imports nativos
⚠️ Limitado a un archivo

### MEJOR USO:

**awatif-ui:** Apps web complejas con FEM
**Calcpad:** Cálculos + visualizaciones simples

---

## 10. Próximos Pasos

### Para Aprender awatif-ui:

1. **Explora el código:**
   ```bash
   cd awatif-2.0.0/awatif-ui
   npm install
   npm run dev
   ```

2. **Modifica ejemplos:**
   - Cambia valores en `main.ts`
   - Ve el hot reload en acción
   - Experimenta con colores

3. **Lee la documentación:**
   - [van.js docs](https://vanjs.org/)
   - [Three.js docs](https://threejs.org/)
   - [Vite docs](https://vitejs.dev/)

### Para Practicar en Calcpad:

1. **Abre los ejemplos:**
   - `Practica_Simple_HTML_CSS_TS.cpd`
   - `Practica_HTML_CSS_TS_Combinado.cpd`
   - `Practica_Avanzada_Reactive_HTML_CSS_TS.cpd`

2. **Modifica y experimenta:**
   - Cambia colores CSS
   - Agrega nuevos elementos HTML
   - Implementa nueva lógica TypeScript

3. **Crea tus propios proyectos:**
   - Calculadoras estructurales
   - Visualizadores de datos
   - Dashboards interactivos

---

## Conclusión

**awatif-ui** es una arquitectura profesional para aplicaciones web FEM con:
- Estado reactivo automático
- Build tooling moderno
- Visualización 3D potente

**Calcpad** puede replicar estos patrones a menor escala, perfecto para:
- Prototipos rápidos
- Cálculos con visualización
- Herramientas educativas

¡Ahora entiendes cómo funciona awatif-ui y cómo aplicar sus conceptos en Calcpad! 🚀
