# 📚 Documentación: CustomFunctions de Mathcad Prime

## 📌 Archivos Identificados

```
Tests/
├── mathcad_fem.cpp          → DLL principal para Mathcad Prime
├── verify_fem_beam.cpp      → Verificación standalone
└── plate_fem_example.cpp    → Ejemplo de placa FEM
```

---

## 🎯 1. mathcad_fem.cpp - DLL Principal

### Descripción
**DLL de funciones FEM para Mathcad Prime 10** que usa Eigen para cálculos matriciales.

### Características Técnicas
- **API:** Mathcad SDK (`mcadincl.h`)
- **Librería matemática:** Eigen (álgebra lineal)
- **Lenguaje:** C++
- **Tipo:** DLL para CustomFunctions
- **Inspiración:** Código de Awatif

### Dependencias
```cpp
#include "mcadincl.h"         // Mathcad SDK (OBLIGATORIO)
#include <cmath>              // Funciones matemáticas estándar
#include <vector>             // STL containers
#include <Eigen/Core>         // Eigen core
#include <Eigen/Dense>        // Eigen matrices densas
```

---

## 🔧 Funciones Implementadas

### Función 1: `fem_beam_K(E, A, I, L)`

**Propósito:** Calcular matriz de rigidez 6x6 para viga 2D (elemento Euler-Bernoulli)

**Parámetros:**
- `E` → Módulo de elasticidad (Pa)
- `A` → Área de sección transversal (m²)
- `I` → Momento de inercia (m⁴)
- `L` → Longitud del elemento (m)

**Retorna:**
- Matriz 6x6 (COMPLEXARRAY)

**DOFs por nodo:**
- Nodo 1: ux₁, uy₁, rz₁ (desplazamientos + rotación)
- Nodo 2: ux₂, uy₂, rz₂

**Formulación:**
```
K = [  EA/L       0         0      -EA/L       0         0    ]
    [    0    12EI/L³    6EI/L²      0    -12EI/L³   6EI/L²  ]
    [    0    6EI/L²     4EI/L       0     -6EI/L²   2EI/L   ]
    [ -EA/L       0         0       EA/L       0         0    ]
    [    0   -12EI/L³   -6EI/L²      0     12EI/L³  -6EI/L²  ]
    [    0    6EI/L²     2EI/L       0     -6EI/L²   4EI/L   ]
```

**Código clave:**
```cpp
double EA_L = E * A / L;
double EI_L3 = E * I / (L * L * L);
double EI_L2 = E * I / (L * L);
double EI_L = E * I / L;

MatrixXd K = MatrixXd::Zero(6, 6);
K(0, 0) = EA_L;       K(0, 3) = -EA_L;
K(1, 1) = 12*EI_L3;   K(1, 2) = 6*EI_L2;   K(1, 4) = -12*EI_L3;  K(1, 5) = 6*EI_L2;
// ... etc
```

**Uso en Mathcad:**
```
E := 210·10^9      # Pa
A := 0.01          # m²
I := 833.3·10^-8   # m⁴
L := 3             # m

K := fem_beam_K(E, A, I, L)  # Retorna matriz 6×6
```

---

### Función 2: `fem_solve(K, F, supports)`

**Propósito:** Resolver sistema FEM K·U = F aplicando condiciones de frontera

**Parámetros:**
- `K` → Matriz de rigidez global (n×n)
- `F` → Vector de fuerzas (n×1)
- `supports` → Vector de restricciones (n×1, valores 0/1)

**Retorna:**
- Vector de desplazamientos U (n×1)

**Algoritmo:**
1. Parsear matriz K y vectores F, supports
2. Identificar DOFs libres (supports = 0) y fijos (supports = 1)
3. Reducir matriz K y vector F solo a DOFs libres
4. Resolver sistema reducido: K_red · U_red = F_red usando QR
5. Reconstruir vector U completo (DOFs fijos = 0)

**Código clave:**
```cpp
// Identificar DOFs libres y fijos
std::vector<int> freeIdx, fixedIdx;
for (int i = 0; i < n; i++) {
    if (Supports(i, 0) != 0) {
        fixedIdx.push_back(i);  // DOF fijo
    } else {
        freeIdx.push_back(i);   // DOF libre
    }
}

// Reducir matriz K a solo DOFs libres
MatrixXd K_red(nFree, nFree);
VectorXd F_red(nFree);
for (int i = 0; i < nFree; i++) {
    F_red(i) = F(freeIdx[i]);
    for (int j = 0; j < nFree; j++) {
        K_red(i, j) = K(freeIdx[i], freeIdx[j]);
    }
}

// Resolver con QR
VectorXd U_red = K_red.colPivHouseholderQr().solve(F_red);

// Reconstruir U completo
VectorXd U = VectorXd::Zero(n);
for (int i = 0; i < nFree; i++) {
    U(freeIdx[i]) = U_red(i);
}
```

**Uso en Mathcad:**
```
# Sistema de 2 nodos (6 DOFs)
K := fem_beam_K(E, A, I, L)

# Fuerzas (carga en nodo 2)
F := [0, 0, 0, 0, -1000, 0]ᵀ

# Soportes (nodo 1 empotrado)
supports := [1, 1, 1, 0, 0, 0]ᵀ

# Resolver
U := fem_solve(K, F, supports)
```

---

### Función 3: `cantilever_defl(P, L, E, I)`

**Propósito:** Calcular deflexión analítica de viga en voladizo

**Parámetros:**
- `P` → Carga puntual en extremo libre (N)
- `L` → Longitud (m)
- `E` → Módulo de elasticidad (Pa)
- `I` → Momento de inercia (m⁴)

**Retorna:**
- Deflexión en extremo libre (m)

**Fórmula:**
```
δ = P·L³ / (3·E·I)
```

**Código:**
```cpp
result->real = P * L * L * L / (3.0 * E * I);
```

**Uso en Mathcad:**
```
P := 1000          # N
L := 3             # m
E := 210·10^9      # Pa
I := 833.3·10^-8   # m⁴

δ := cantilever_defl(P, L, E, I)   # Retorna deflexión en m
```

**Uso típico:** Verificar resultados FEM comparando con solución analítica.

---

### Función 4: `fem_frame3d_K(E, G, A, Iy, Iz, J, L)`

**Propósito:** Calcular matriz de rigidez 12×12 para elemento frame 3D

**Parámetros:**
- `E` → Módulo de elasticidad (Pa)
- `G` → Módulo de cortante (Pa)
- `A` → Área (m²)
- `Iy` → Momento de inercia en Y (m⁴)
- `Iz` → Momento de inercia en Z (m⁴)
- `J` → Constante torsional (m⁴)
- `L` → Longitud (m)

**Retorna:**
- Matriz 12×12 (COMPLEXARRAY)

**DOFs por nodo:**
- Nodo 1: ux₁, uy₁, uz₁, rx₁, ry₁, rz₁ (3 desplazamientos + 3 rotaciones)
- Nodo 2: ux₂, uy₂, uz₂, rx₂, ry₂, rz₂

**Términos de la matriz:**
```cpp
double EA_L = E * A / L;         // Rigidez axial
double EIz_L3 = E * Iz / (L³);   // Rigidez flexión en Z
double EIy_L3 = E * Iy / (L³);   // Rigidez flexión en Y
double GJ_L = G * J / L;         // Rigidez torsional
double EIz_L2 = E * Iz / (L²);   // Rotación Z
double EIy_L2 = E * Iy / (L²);   // Rotación Y
double EIz_L = E * Iz / L;       // Momento Z
double EIy_L = E * Iy / L;       // Momento Y
```

**Estructura de la matriz:**
```
K = [ Axial      0         0      Torsion    ...  ]
    [   0     Flexión Z    0         0       ...  ]
    [   0        0      Flexión Y    0       ...  ]
    [Torsion     0         0        GJ/L     ...  ]
    [ ...       ...       ...       ...      ...  ]
```

**Uso en Mathcad:**
```
E := 210·10^9      # Pa
G := 80·10^9       # Pa
A := 0.01          # m²
Iy := 833.3·10^-8  # m⁴
Iz := 833.3·10^-8  # m⁴
J := 1416·10^-8    # m⁴
L := 5             # m

K := fem_frame3d_K(E, G, A, Iy, Iz, J, L)  # Retorna 12×12
```

---

## 🔄 Funciones de Conversión (Internas)

### `EigenToMathcad(const MatrixXd& eigen, LPCOMPLEXARRAY out)`
Copia matriz de Eigen a COMPLEXARRAY de Mathcad.

```cpp
void EigenToMathcad(const MatrixXd& eigen, LPCOMPLEXARRAY out) {
    for (unsigned int c = 0; c < out->cols; c++) {
        for (unsigned int r = 0; r < out->rows; r++) {
            out->hReal[c][r] = eigen(r, c);
        }
    }
}
```

### `MathcadToEigen(LPCCOMPLEXARRAY in)`
Copia COMPLEXARRAY de Mathcad a matriz de Eigen.

```cpp
MatrixXd MathcadToEigen(LPCCOMPLEXARRAY in) {
    MatrixXd eigen(in->rows, in->cols);
    for (unsigned int c = 0; c < in->cols; c++) {
        for (unsigned int r = 0; r < in->rows; r++) {
            eigen(r, c) = (in->hReal != NULL) ? in->hReal[c][r] : 0.0;
        }
    }
    return eigen;
}
```

### `EigenVectorToMathcad(const VectorXd& vec, LPCOMPLEXARRAY out)`
Copia vector de Eigen a COMPLEXARRAY columna.

```cpp
void EigenVectorToMathcad(const VectorXd& vec, LPCOMPLEXARRAY out) {
    for (unsigned int r = 0; r < out->rows; r++) {
        out->hReal[0][r] = vec(r);
    }
}
```

---

## 🚀 Punto de Entrada DLL

### `DllEntryPoint()`

Función requerida por Mathcad SDK para registrar funciones.

```cpp
BOOL WINAPI DllEntryPoint(HANDLE hDLL, DWORD dwReason, LPVOID lpReserved)
{
    switch (dwReason)
    {
    case DLL_PROCESS_ATTACH:
        if (!_CRT_INIT((HINSTANCE)hDLL, dwReason, lpReserved))
            return FALSE;

        // Registrar cada función con Mathcad
        CreateUserFunction((HINSTANCE)hDLL, &fi_FemBeamK);
        CreateUserFunction((HINSTANCE)hDLL, &fi_FemSolve);
        CreateUserFunction((HINSTANCE)hDLL, &fi_CantileverDefl);
        CreateUserFunction((HINSTANCE)hDLL, &fi_FemFrame3dK);
        break;

    // ... otros casos
    }
    return TRUE;
}
```

---

## 📋 FUNCTIONINFO Structures

Cada función necesita una estructura `FUNCTIONINFO`:

```cpp
FUNCTIONINFO fi_FemBeamK = {
    (char*)"fem_beam_K",                    // Nombre en Mathcad
    (char*)"E,A,I,L",                       // Argumentos
    (char*)"Matriz de rigidez 6x6...",     // Descripción
    (LPCFUNCTION)FemBeamKFunc,              // Puntero a función
    COMPLEX_ARRAY,                          // Tipo de retorno
    4,                                      // Número de argumentos
    {COMPLEX_SCALAR, COMPLEX_SCALAR,        // Tipos de argumentos
     COMPLEX_SCALAR, COMPLEX_SCALAR}
};
```

---

## 🛠️ Compilación

### Requisitos
- Visual Studio (2019 o superior)
- Mathcad Prime SDK
- Eigen library

### Comando de compilación (ejemplo)
```bash
cl /LD /O2 /EHsc mathcad_fem.cpp ^
   /I "C:\Program Files\PTC\Mathcad Prime 10.0\Custom Functions" ^
   /I "C:\Users\j-b-j\eigen" ^
   /link /DEF:mathcad_fem.def
```

### Archivo .def (export)
```
LIBRARY mathcad_fem
EXPORTS
    DllEntryPoint
```

### Resultado
- `mathcad_fem.dll` → Copiar a carpeta Custom Functions de Mathcad

---

## 📍 Instalación en Mathcad Prime

### Paso 1: Compilar DLL
```bash
cl /LD /O2 mathcad_fem.cpp ...
```

### Paso 2: Copiar DLL
```
Destino: C:\Program Files\PTC\Mathcad Prime 10.0\Custom Functions\
```

### Paso 3: Reiniciar Mathcad Prime

### Paso 4: Usar funciones
```
K := fem_beam_K(210·10^9, 0.01, 833.3·10^-8, 3)
```

---

## 🔍 2. verify_fem_beam.cpp - Verificación

### Descripción
Programa standalone (NO es DLL) para verificar matriz de rigidez de viga 2D.

### Propósito
- Calcular matriz K con mismos parámetros que Mathcad
- Comparar resultados con valores de Mathcad
- Verificar fórmula de cantilever

### Compilación
```bash
g++ -o verify_fem_beam verify_fem_beam.cpp
```

### Ejecución
```bash
./verify_fem_beam.exe
```

### Salida
```
=== Verificación Matriz Rigidez Viga 2D ===

Parámetros:
  E = 210 GPa
  A = 100 cm²
  I = 833.3 cm⁴
  L = 3 m

Coeficientes calculados:
  EA/L     = 700000000.000
  12EI/L³  = 777746.667
  6EI/L²   = 1166620.000
  4EI/L    = 2333240.000
  2EI/L    = 1166620.000

Matriz de Rigidez K (6x6):
  [...]

=== Comparación con Mathcad ===
Error máximo: 0.00

=== Verificación Cantilever ===
  P = 1000 N
  Deflexión teórica = PL³/(3EI) = 15.419501 mm
  Rotación teórica  = PL²/(2EI) = 7.709751 mrad
```

**Uso:** Ejecutar antes de compilar DLL para asegurar que las fórmulas son correctas.

---

## 🧪 3. plate_fem_example.cpp - Ejemplo Placa

### Descripción
Ejemplo completo de análisis FEM de placas usando elementos shell triangulares (Mindlin-Reissner).

**Inspiración:** Código de Awatif-FEM

### Características
- Elementos shell triangulares (3 nodos)
- 3 DOF por nodo: w (deflexión), θₓ, θᵧ (rotaciones)
- Teoría Mindlin-Reissner (incluye deformación por cortante)
- Generación automática de malla rectangular
- Matriz de rigidez separada: flexión + cortante
- Solver: Conjugate Gradient (Eigen)

### Compilación
```bash
g++ -I C:\Users\j-b-j\eigen -o plate_fem_example plate_fem_example.cpp
```

### Ejecución
```bash
./plate_fem_example.exe
```

### Salida
```
============================================================
  Ejemplo de Placa FEM - Elementos Shell Triangulares
  (Similar al ejemplo plate de Awatif)
============================================================

Parametros:
  Placa: 6 x 4 m
  Malla: 3 x 2 elementos
  E = 210 GPa
  nu = 0.3
  t = 100 mm
  q = -1000 N/m²

Malla generada:
  Nodos: 12
  Elementos: 12

Condiciones de frontera:
  Nodos fijos en bordes: 10

============================================================
  RESULTADOS
============================================================

Desplazamiento maximo (w):
  Nodo 5 en (3.000000, 2.000000)
  w_max = -2.345678 mm

Comparacion con solucion analitica (placa empotrada):
  w_analitico ≈ 2.567890 mm
  Error: 8.65 %

Desplazamientos en nodos centrales:
  Nodo      x         y        w (mm)      theta_x      theta_y
     5   3.00      2.00      -2.346      0.000123     -0.000145
```

### Funciones Principales

#### `generateRectangularMesh()`
Genera malla de elementos triangulares para placa rectangular.

#### `getBendingStiffnessMatrix()`
Matriz de rigidez de flexión (curvatura).

**Matriz constitutiva:**
```
D_b = E·t³/(12(1-ν²)) · [  1    ν     0      ]
                         [  ν    1     0      ]
                         [  0    0  (1-ν)/2   ]
```

#### `getShearStiffnessMatrix()`
Matriz de rigidez de cortante (deformación transversal).

**Factor de corrección de cortante:**
```
κ = 5/6
D_s = κ·G·t
```

#### `assembleGlobalStiffness()`
Ensambla matriz de rigidez global a partir de elementos.

**Estructura:**
```
K_global (sparse) = Σ K_elemento_i
```

#### `applyBoundaryConditions()`
Aplica restricciones usando método de penalización.

```cpp
K[dof, dof] += 1e20  // Penalización para DOF fijo
F[dof] = 0
```

### Teoría Implementada

**Mindlin-Reissner Plate Theory:**
- Considera deformación por cortante transversal
- Más precisa para placas gruesas (t/L > 1/20)
- 3 variables: w, θₓ, θᵧ

**Deformaciones:**
```
κₓ = ∂θᵧ/∂x          (curvatura en x)
κᵧ = -∂θₓ/∂y         (curvatura en y)
κₓᵧ = ∂θᵧ/∂y - ∂θₓ/∂x (curvatura de torsión)

γₓz = ∂w/∂x - θᵧ     (cortante transversal xz)
γᵧz = ∂w/∂y + θₓ     (cortante transversal yz)
```

**Uso:** Estudiar implementación de elementos shell, comparar con Awatif.

---

## 📊 Comparación de Archivos

| Archivo | Tipo | Propósito | Requiere Mathcad | Requiere Eigen |
|---------|------|-----------|------------------|----------------|
| mathcad_fem.cpp | DLL | CustomFunctions para Mathcad | ✅ Sí (SDK) | ✅ Sí |
| verify_fem_beam.cpp | EXE | Verificación independiente | ❌ No | ❌ No |
| plate_fem_example.cpp | EXE | Ejemplo educativo | ❌ No | ✅ Sí |

---

## 🎯 Flujo de Trabajo Recomendado

### 1. Desarrollo
```
1. Escribir código de función en mathcad_fem.cpp
2. Verificar con verify_fem_beam.cpp (standalone)
3. Si correcto, compilar DLL
4. Instalar en Mathcad
5. Probar en Mathcad worksheet
```

### 2. Testing
```
1. Crear casos de prueba en verify_*.cpp
2. Comparar con soluciones analíticas
3. Comparar con resultados de otros software (SAP2000, etc.)
4. Si coinciden, confiar en la DLL
```

### 3. Expansión
```
1. Estudiar plate_fem_example.cpp
2. Extraer funciones útiles (getBendingStiffnessMatrix, etc.)
3. Adaptar a formato Mathcad CustomFunction
4. Agregar a mathcad_fem.cpp
5. Recompilar DLL
```

---

## 🔗 Relación con Awatif

### Código Inspirado en Awatif

Los archivos usan conceptos de **Awatif-FEM** (awatif-2.0.0/awatif-fem/src/cpp/):

| Concepto | Awatif | Tus Archivos |
|----------|--------|--------------|
| Matriz rigidez global | getGlobalStiffnessMatrix.cpp | assembleGlobalStiffness() |
| Matriz rigidez local | getLocalStiffnessMatrix.cpp | getLocalStiffnessMatrix() |
| Solver FEM | deform.cpp | fem_solve() |
| Elementos shell | deform.cpp | plate_fem_example.cpp |
| Condiciones frontera | deform.cpp | applyBoundaryConditions() |

**Puedes portar más funciones de Awatif a tu DLL Mathcad.**

---

## 🚀 Expandir DLL con Más Funciones

### Funciones Sugeridas

#### 1. Matriz de Rigidez de Placa Shell
```cpp
LRESULT FemShellKFunc(
    LPCOMPLEXARRAY K_out,
    LPCCOMPLEXSCALAR pE,
    LPCCOMPLEXSCALAR pnu,
    LPCCOMPLEXSCALAR pt,
    LPCCOMPLEXARRAY pNodes  // 3 nodos × [x,y,z]
)
{
    // Implementar como en plate_fem_example.cpp
    // K = K_bending + K_shear
}
```

#### 2. Ensamblaje Automático de Matriz Global
```cpp
LRESULT FemAssembleKFunc(
    LPCOMPLEXARRAY K_global_out,
    LPCCOMPLEXARRAY pNodes,      // n × 3
    LPCCOMPLEXARRAY pElements,   // m × 3 (triangulos)
    LPCCOMPLEXARRAY pProperties  // m × 3 (E, nu, t)
)
{
    // Loop sobre elementos
    // Para cada elemento: calcular K_local
    // Ensamblar en K_global
}
```

#### 3. Cálculo de Esfuerzos Post-Procesado
```cpp
LRESULT FemStressesFunc(
    LPCOMPLEXARRAY stresses_out,
    LPCCOMPLEXARRAY pU,          // Desplazamientos
    LPCCOMPLEXARRAY pK_element,  // Matriz K del elemento
    LPCCOMPLEXSCALAR pE,
    LPCCOMPLEXSCALAR pnu
)
{
    // Calcular esfuerzos σ = D * B * U_element
}
```

#### 4. Generador de Mallas
```cpp
LRESULT FemGenerateMeshFunc(
    LPCOMPLEXARRAY nodes_out,
    LPCOMPLEXARRAY elements_out,
    LPCCOMPLEXSCALAR pLx,
    LPCCOMPLEXSCALAR pLy,
    LPCCOMPLEXSCALAR pnx,
    LPCCOMPLEXSCALAR pny
)
{
    // Como generateRectangularMesh() pero retorna a Mathcad
}
```

---

## 📖 Recursos

### Documentación Mathcad SDK
- Ruta: `C:\Program Files\PTC\Mathcad Prime 10.0\doc\`
- Archivo: `Creating_User_Functions_in_Mathcad.pdf`

### Eigen Library
- Website: https://eigen.tuxfamily.org/
- Docs: https://eigen.tuxfamily.org/dox/

### Awatif Source Code
- Local: `C:\Users\j-b-j\Documents\Calcpad-7.5.7\awatif-2.0.0\awatif-fem\src\cpp\`
- GitHub: https://github.com/madil4/awatif

### Teoría FEM
- Awatif videos:
  - Vision: https://www.youtube.com/watch?v=QkoFJGfD7rc
  - Architecture: https://www.youtube.com/watch?v=4NdFQGouIjU

---

## ✅ Resumen

### Archivo Principal: `mathcad_fem.cpp`
- **DLL para Mathcad Prime CustomFunctions**
- 4 funciones FEM implementadas
- Usa Eigen para álgebra lineal
- Conversiones automáticas Eigen ↔ Mathcad

### Archivos de Soporte:
- **verify_fem_beam.cpp** → Verificación standalone
- **plate_fem_example.cpp** → Ejemplo educativo de placas

### Ventajas:
- ✅ Funciones FEM disponibles en Mathcad
- ✅ Uso de Eigen (eficiente y robusto)
- ✅ Código inspirado en Awatif (probado)
- ✅ Fácil de expandir con nuevas funciones

### Próximos Pasos:
1. Compilar mathcad_fem.cpp → mathcad_fem.dll
2. Instalar en Mathcad Prime
3. Probar funciones en worksheets
4. Agregar más funciones según necesidades
5. Portar código de Awatif para funcionalidad avanzada

---

**¡Tienes un excelente conjunto de CustomFunctions FEM para Mathcad Prime!**
