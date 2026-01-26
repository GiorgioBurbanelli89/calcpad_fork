# ✅ Awatif - Plataforma FEM Paramétrica Web

## 📍 ¿Qué es Awatif?

**Awatif** es una plataforma web de **ingeniería estructural paramétrica** con análisis FEM en tiempo real.

```
Ubicación: C:\Users\j-b-j\Documents\Calcpad-7.5.7\awatif-2.0.0
Website: https://awatif.co/
GitHub: https://github.com/madil4/awatif
```

## 🎯 Características Principales

### ✅ Análisis FEM
- **Elementos 1D**: Barras y vigas
- **Elementos 2D**: Placas y shells
- **Simulaciones estáticas**: Deformaciones, reacciones, esfuerzos
- **Generación de mallas**: 2D y 3D automáticas

### ✅ Interfaz de Usuario
- **Visualización 3D**: Renderizado con Three.js
- **Tablas editables**: Edición de datos estructurales
- **Dibujo interactivo**: Herramientas de dibujo
- **Reportes**: Generación de informes

### ✅ Sistemas Estructurales
- Diseño de armaduras (trusses)
- Vigas continuas
- Placas y losas
- Estructuras 3D completas

## 🏗️ Arquitectura del Proyecto

```
awatif-2.0.0/
├── awatif-fem/          → Solver FEM (TypeScript + C++/WASM)
│   ├── src/
│   │   ├── deform.ts    → Implementación TypeScript
│   │   ├── analyze.ts   → Análisis de esfuerzos
│   │   └── cpp/         → Implementación C++ optimizada
│   │       ├── deform.cpp             → Solver principal
│   │       ├── data-model.h           → Estructuras de datos
│   │       └── utils/
│   │           ├── getGlobalStiffnessMatrix.cpp
│   │           ├── getLocalStiffnessMatrix.cpp
│   │           └── getTransformationMatrix.cpp
│   └── package.json
│
├── awatif-mesh/         → Generación de mallas
│
├── awatif-ui/           → Interfaz de usuario
│   └── src/
│       ├── viewer/      → Visualización 3D con Three.js
│       ├── tables/      → Tablas editables
│       └── drawing/     → Herramientas de dibujo
│
├── examples/            → 14 ejemplos completos
│   └── src/
│       ├── plate/       → Análisis de placas
│       ├── beams/       → Análisis de vigas
│       ├── slab-designer/ → Diseñador de losas
│       ├── advanced-truss/ → Armaduras avanzadas
│       ├── 1d-mesh/     → Mallas 1D
│       ├── 2d-mesh/     → Mallas 2D
│       ├── 3d-structure/ → Estructuras 3D
│       ├── building/    → Edificios
│       └── ... (14 ejemplos en total)
│
└── website/             → Sitio web de documentación
```

## 💻 Stack Tecnológico

| Componente | Tecnología | Uso |
|------------|------------|-----|
| **Solver FEM** | C++ + Eigen | Cálculos de alto rendimiento |
| **Compilador** | Emscripten | C++ → WebAssembly |
| **Frontend** | TypeScript | Lógica de aplicación |
| **Estado Reactivo** | VanJS | Manejo de estado |
| **3D Rendering** | Three.js | Visualización 3D |
| **Templates** | Lit-html | Plantillas HTML |
| **UI Components** | W2UI | Componentes de interfaz |

## 🔬 Cómo Funciona el Solver FEM

### Implementación Dual

Awatif tiene **DOS implementaciones** del solver:

1. **TypeScript** (deform.ts)
   - Para desarrollo y debugging
   - Más fácil de modificar
   - Más lenta

2. **C++ + WebAssembly** (deform.cpp)
   - Para producción
   - Usa librería Eigen para álgebra lineal
   - 10-100x más rápida que TypeScript
   - Compilada a WASM para ejecutarse en navegador

### Proceso de Compilación C++ → WASM

```bash
emcc ./src/cpp/deform.cpp \
     ./src/cpp/utils/getGlobalStiffnessMatrix.cpp \
     ./src/cpp/utils/getLocalStiffnessMatrix.cpp \
     ./src/cpp/utils/getTransformationMatrix.cpp \
     -o ./src/cpp/built/deform.js \
     -O3 \
     -s MODULARIZE \
     -s EXPORT_ES6 \
     -s EXPORTED_FUNCTIONS=_malloc,_free,_deform \
     -I /path/to/eigen/
```

Esto genera `deform.js` (código WASM) que se ejecuta en el navegador.

### Algoritmo FEM (deform.cpp)

```cpp
extern "C" {
    void deform(
        // Geometría
        double *nodes_flat_ptr, int num_nodes,
        unsigned int *element_indices_ptr, int num_element_indices,
        unsigned int *element_sizes_ptr, int num_elements,

        // Condiciones de frontera
        int *support_keys_ptr, bool *support_values_ptr, int num_supports,
        int *load_keys_ptr, double *load_values_ptr, int num_loads,

        // Propiedades de materiales
        int *elasticity_keys_ptr, double *elasticity_values_ptr, int num_elasticities,
        // ... más propiedades ...

        // Salidas
        double **deformations_data_ptr_out, int *deformations_size_out,
        double **reactions_data_ptr_out, int *reactions_size_out
    ) {
        // 1. Parsear entradas desde memoria WASM
        std::vector<Node> nodes;
        NodeInputs nodeInputs;
        ElementInputs elementInputs;

        // 2. Construir matriz de rigidez global K usando Eigen
        Eigen::SparseMatrix<double> K_global = getGlobalStiffnessMatrix(...);

        // 3. Construir vector de fuerzas F
        Eigen::VectorXd F_global = getForces(...);

        // 4. Aplicar condiciones de frontera (reducir matriz)
        std::vector<int> freeIndices = getFreeIndices(...);
        Eigen::SparseMatrix<double> K_reduced = getReducedMatrix(...);
        Eigen::VectorXd F_reduced = getReducedVector(...);

        // 5. Resolver sistema K*U = F usando Conjugate Gradient
        Eigen::ConjugateGradient<Eigen::SparseMatrix<double>> solver;
        solver.compute(K_reduced);
        Eigen::VectorXd U_reduced = solver.solve(F_reduced);

        // 6. Reconstruir vector de deformaciones completo
        Eigen::VectorXd U_global = Eigen::VectorXd::Zero(dof);
        // Mapear U_reduced → U_global

        // 7. Calcular reacciones R = K * U
        Eigen::VectorXd R_global = K_global * U_global;

        // 8. Retornar resultados a TypeScript
        outputs.deformations = ...;
        outputs.reactions = ...;
    }
}
```

**Nota:** Este es el MISMO algoritmo que usas en tus DLLs de Mathcad!

## 📚 Ejemplos Disponibles

### 1. **Plate** (`examples/src/plate/`)
**Análisis de placas rectangulares con malla automática**

```typescript
// Parámetros editables
const parameters = {
  xPosition: { value: 15, min: 5, max: 20 },
  Ex: { value: 100, min: 50, max: 500 },
  Ey: { value: 100, min: 50, max: 500 },
  load: { value: -3, min: -10, max: 10 },
};

// Generar malla automática
const { nodes, elements } = getMesh({
  points: [[0,0,0], [15,0,0], [xPosition,10,0], [0,5,0]],
  polygon: [0, 1, 2, 3],
  maxMeshSize: 0.5,
});

// Analizar
mesh.deformOutputs = deform(nodes, elements, nodeInputs, elementInputs);
mesh.analyzeOutputs = analyze(nodes, elements, elementInputs, deformOutputs);

// Visualizar en 3D
getViewer({
  mesh,
  settingsObj: {
    deformedShape: true,
    shellResults: "displacementZ",
  },
});
```

**Características:**
- ✅ Malla automática adaptativa
- ✅ Propiedades ortótropas (Ex, Ey)
- ✅ Visualización de deformaciones
- ✅ Visualización de esfuerzos
- ✅ Parámetros interactivos en tiempo real

### 2. **Beams** (`examples/src/beams/`)
**Pórtico simple con visualización de deformaciones**

```typescript
nodes = [
  [0, 0, 0],      // Nodo 0 (apoyo izquierdo)
  [0, 0, height], // Nodo 1 (columna izquierda)
  [length, 0, height], // Nodo 2 (viga superior)
  [length, 0, 0], // Nodo 3 (apoyo derecho)
];

elements = [
  [0, 1],  // Columna izquierda
  [1, 2],  // Viga
  [2, 3],  // Columna derecha
];

nodeInputs = {
  supports: new Map([
    [0, [true, true, true, true, true, true]], // Empotramiento nodo 0
    [3, [true, true, true, true, true, true]], // Empotramiento nodo 3
  ]),
  loads: new Map([
    [2, [xLoad, 0, 0, 0, 0, 0]], // Carga horizontal en nodo 2
  ]),
};

elementInputs = {
  elasticities: new Map([[0, 10], [1, 10], [2, 10]]),
  areas: new Map([[0, 10], [1, 10], [2, 10]]),
  momentsOfInertiaY: new Map([[0, 10], [1, 10], [2, 10]]),
  momentsOfInertiaZ: new Map([[0, 10], [1, 10], [2, 10]]),
};
```

### 3. **Slab Designer** (`examples/src/slab-designer/`)
**Diseñador interactivo de losas**

- Dibujo de geometría con herramientas CAD
- Definición de cargas
- Definición de soportes
- Análisis automático
- Visualización de resultados

### 4. **Advanced Truss** (`examples/src/advanced-truss/`)
**Diseño optimizado de armaduras**

- Generación paramétrica de armaduras
- Optimización de miembros
- Análisis de esfuerzos axiales
- Diagramas de barras

### 5. **3D Structure** (`examples/src/3d-structure/`)
**Estructura 3D completa**

- Pórticos espaciales
- Múltiples niveles
- Cargas distribuidas
- Visualización 3D interactiva

## 🔗 ¿Cómo se Puede Usar con Tu Proyecto?

### Opción 1: Usar Awatif Directamente
**Ejecutar los ejemplos en tu navegador**

```bash
cd C:\Users\j-b-j\Documents\Calcpad-7.5.7\awatif-2.0.0
npm install
npm run dev:examples
```

Esto abre el navegador con ejemplos interactivos de:
- Placas
- Vigas
- Losas
- Armaduras
- Estructuras 3D

**Ventajas:**
- ✅ Ya funciona, solo ejecutar
- ✅ Interfaz moderna y profesional
- ✅ Visualización 3D excelente
- ✅ Parámetros interactivos
- ✅ Gratis y open source

**Desventajas:**
- ⚠️ Requiere Node.js y navegador
- ⚠️ No integrado con Calcpad/SMath
- ⚠️ No usa tus DLLs de Mathcad

### Opción 2: Extraer Código C++ para Tus DLLs
**Reutilizar el solver FEM de Awatif en tus DLLs**

El código C++ de Awatif (`awatif-fem/src/cpp/`) es **muy similar** a lo que tienes en tus DLLs de Mathcad.

**Lo que puedes hacer:**

1. **Estudiar el código** para mejorar tus DLLs
   - `deform.cpp` → Algoritmo completo FEM
   - `getLocalStiffnessMatrix.cpp` → Matrices de rigidez locales
   - `getGlobalStiffnessMatrix.cpp` → Ensamblaje de matriz global
   - `getTransformationMatrix.cpp` → Matrices de transformación

2. **Copiar funciones útiles**
   - Reducción de matriz para condiciones de frontera
   - Solver con Conjugate Gradient (muy rápido)
   - Manejo de elementos shell (placas)

3. **Compilar para Mathcad/SMath**
   ```bash
   # En lugar de compilar a WASM
   g++ -shared -o fem_solver.dll deform.cpp ... -lEigen
   ```

**Ventajas:**
- ✅ Código C++ bien estructurado
- ✅ Usa Eigen (muy eficiente)
- ✅ Bien probado y documentado
- ✅ Puedes adaptarlo a tus necesidades

**Desventajas:**
- ⚠️ Requiere trabajo de adaptación
- ⚠️ Necesitas instalar Eigen
- ⚠️ Debes modificar interfaces

### Opción 3: Integrar Awatif con SMath Studio
**Crear plugin SMath que use Awatif internamente**

Puedes crear un plugin SMath que:

1. **Ejecute Awatif en background** (Node.js subprocess)
2. **Pase datos** desde SMath a Awatif (JSON)
3. **Reciba resultados** de Awatif
4. **Visualice en SMath** o abra navegador

**Arquitectura:**
```
SMath Studio (C#)
    ↓ (datos de entrada)
Plugin SMath (C#)
    ↓ (ejecuta Node.js)
Awatif (TypeScript/WASM)
    ↓ (retorna resultados JSON)
Plugin SMath (C#)
    ↓ (procesa y muestra)
SMath Studio (visualización)
```

**Ventajas:**
- ✅ Mejor visualización 3D que SMath
- ✅ Interfaz moderna
- ✅ Mantiene tus workflows en SMath

**Desventajas:**
- ⚠️ Complejo de implementar
- ⚠️ Requiere Node.js instalado
- ⚠️ Comunicación entre procesos

### Opción 4: Usar Awatif como Referencia Visual
**Comparar resultados de tus DLLs con Awatif**

Puedes usar Awatif para **verificar** que tus DLLs funcionan correctamente:

1. Define el mismo problema en Awatif y en Mathcad/SMath
2. Compara resultados
3. Si difieren, debuggea tu código

**Ejemplo: Comparar viga en voladizo**

```javascript
// En Awatif
nodes = [[0,0,0], [L,0,0]];
elements = [[0,1]];
supports = Map([[0, [true,true,true,true,true,true]]]);
loads = Map([[1, [0,0,-P,0,0,0]]]);
```

```cpp
// En tu DLL Mathcad
double delta = cantilever_defl(P, L, E, I);
// Comparar con Awatif → deformOutputs[1][2] (desplazamiento Z nodo 1)
```

## 🎨 Visualización: Awatif vs SMath vs Calcpad

| Característica | Awatif | SMath Studio | Calcpad |
|----------------|--------|--------------|---------|
| **Visualización 3D** | ✅ Three.js (excelente) | ⚠️ Básica | ❌ No |
| **Interactividad** | ✅ Tiempo real | ⚠️ Manual | ⚠️ Manual |
| **Deformadas** | ✅ Animadas | ⚠️ Estáticas | ❌ No |
| **Mallas** | ✅ Auto + manual | ⚠️ Manual | ⚠️ Manual |
| **Diagramas** | ✅ Integrados | ⚠️ Plugin | ⚠️ No |
| **Tablas** | ✅ Editables | ✅ Sí | ⚠️ Limitadas |
| **Exportar** | ✅ JSON, PNG | ✅ Múltiples | ✅ HTML, PDF |

## 📖 Documentación y Recursos

**Documentación Oficial:**
- Website: https://awatif.co/
- API FEM: https://awatif.co/awatif-fem/
- GitHub: https://github.com/madil4/awatif

**Videos:**
- Visión general: https://www.youtube.com/watch?v=QkoFJGfD7rc
- Arquitectura: https://www.youtube.com/watch?v=4NdFQGouIjU

**Ejemplos en vivo:**
- Placas: https://awatif.co/examples/plate/
- Vigas: https://awatif.co/examples/beams/
- Armaduras: https://awatif.co/examples/advanced-truss/
- Mallas 2D: https://awatif.co/examples/2d-mesh/
- Estructuras 3D: https://awatif.co/examples/3d-structure/

## 🚀 Cómo Empezar

### 1. Ejecutar Ejemplos Localmente

```bash
# Navegar a la carpeta
cd C:\Users\j-b-j\Documents\Calcpad-7.5.7\awatif-2.0.0

# Instalar dependencias (solo primera vez)
npm install

# Ejecutar ejemplos
npm run dev:examples
```

Se abrirá el navegador en `http://localhost:5173/`

**Ejemplos disponibles:**
- `http://localhost:5173/plate/` → Análisis de placas
- `http://localhost:5173/beams/` → Análisis de vigas
- `http://localhost:5173/slab-designer/` → Diseñador de losas
- `http://localhost:5173/advanced-truss/` → Armaduras
- etc.

### 2. Modificar Ejemplos

Edita los archivos `.ts` en `examples/src/`:

```bash
# Ejemplo: Modificar análisis de placas
code examples/src/plate/main.ts
```

Los cambios se reflejan automáticamente en el navegador (hot reload).

### 3. Crear Tu Propia Aplicación

Copia un ejemplo y modifícalo:

```bash
cd examples/src
cp -r plate mi-aplicacion
code mi-aplicacion/main.ts
```

## 💡 Casos de Uso para Tu Proyecto

### Caso 1: Visualización Avanzada
**Problema:** SMath y Mathcad tienen visualización limitada
**Solución:** Usar Awatif para visualizar resultados de tus DLLs

**Workflow:**
1. Calcular con tus DLLs en SMath/Mathcad
2. Exportar resultados a JSON
3. Importar en Awatif para visualizar

### Caso 2: Prototipado Rápido
**Problema:** Compilar DLLs es lento para probar ideas
**Solución:** Prototipar en Awatif (TypeScript)

**Workflow:**
1. Implementar algoritmo en Awatif TypeScript
2. Probar interactivamente en navegador
3. Cuando funciona, portar a C++ DLL

### Caso 3: Interfaz Moderna
**Problema:** SMath/Mathcad no tienen interfaz moderna
**Solución:** Desarrollar aplicación web con Awatif

**Workflow:**
1. Usar solver FEM de Awatif
2. Crear interfaz personalizada
3. Publicar en web para clientes

### Caso 4: Aprendizaje y Referencia
**Problema:** Código FEM complejo de entender
**Solución:** Estudiar código bien documentado de Awatif

**Workflow:**
1. Leer código C++ de Awatif
2. Comparar con tus DLLs
3. Adoptar mejores prácticas

## ✅ Respuesta a Tu Pregunta

**Pregunta:** "Se puede usar hasta awatif-2.0.0 los examples?"

**Respuesta:** **¡SÍ, ABSOLUTAMENTE!**

### Lo que puedes hacer:

1. **✅ Ejecutar todos los ejemplos**
   ```bash
   npm install
   npm run dev:examples
   ```

2. **✅ Modificar los ejemplos** para tus necesidades específicas

3. **✅ Estudiar el código C++** para mejorar tus DLLs

4. **✅ Usar como referencia** para verificar tus cálculos

5. **✅ Integrar con SMath Studio** vía plugin

6. **✅ Crear aplicaciones web** personalizadas

### Lo que NO puedes hacer directamente:

- ❌ Usar Awatif desde dentro de Mathcad Prime
- ❌ Cargar tus DLLs en Awatif (solo TypeScript/WASM)
- ❌ Ejecutar Awatif en Calcpad

### Recomendación:

**Para tu caso específico, te recomiendo:**

1. **Corto plazo:** Ejecuta los ejemplos para ver capacidades
   ```bash
   npm run dev:examples
   ```

2. **Mediano plazo:** Estudia el código C++ para mejorar tus DLLs
   - `awatif-fem/src/cpp/deform.cpp`
   - `awatif-fem/src/cpp/utils/`

3. **Largo plazo:** Decide si quieres:
   - **Opción A:** Integrar Awatif en plugin SMath
   - **Opción B:** Portar código Awatif a tus DLLs
   - **Opción C:** Desarrollar aplicación web con Awatif

## 📊 Comparación Final

| Característica | Awatif | Tus DLLs Mathcad | SMath Studio |
|----------------|--------|------------------|--------------|
| **Lenguaje** | TypeScript/C++ | C/C++ | Usa tus DLLs |
| **Plataforma** | Web (navegador) | Windows | Windows |
| **Visualización** | ⭐⭐⭐⭐⭐ | ⭐ (N/A) | ⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ (WASM) | ⭐⭐⭐⭐⭐ (nativo) | ⭐⭐⭐⭐ |
| **Facilidad** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Costo** | Gratis | Gratis | Gratis |
| **Ecosistema** | Moderno (npm) | Clásico | Plugin system |
| **Documentación** | ⭐⭐⭐⭐ | N/A | ⭐⭐⭐ |

## 🎯 Conclusión

**Awatif es:**
- ✅ Una plataforma FEM moderna y completa
- ✅ Código abierto y bien documentado
- ✅ Con ejemplos excelentes
- ✅ Compatible con tus necesidades
- ✅ Útil para visualización y prototipado
- ✅ Referencia de código C++ FEM de calidad

**Los ejemplos SÍ se pueden usar**, y te serán muy útiles para:
1. Ver qué es posible con FEM moderno
2. Aprender de código bien estructurado
3. Verificar tus cálculos
4. Inspirarte para nuevas features

## 📝 Próximos Pasos

1. **Ejecuta los ejemplos:**
   ```bash
   cd awatif-2.0.0
   npm install
   npm run dev:examples
   ```

2. **Explora cada ejemplo:**
   - Plate → Placas
   - Beams → Vigas
   - Slab-designer → Losas

3. **Estudia el código C++:**
   - Lee `awatif-fem/src/cpp/deform.cpp`
   - Compara con tus DLLs

4. **Decide qué hacer:**
   - ¿Integrar con SMath?
   - ¿Mejorar tus DLLs?
   - ¿Crear app web?

¡Tienes un recurso valioso en tus manos!
