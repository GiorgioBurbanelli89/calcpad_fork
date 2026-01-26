# Guía: Custom Functions DLL para Mathcad Prime

## Resumen de la Sesión

Se crearon 3 DLLs de funciones personalizadas para Mathcad Prime 10:

| DLL | Funciones | Propósito |
|-----|-----------|-----------|
| `mathcad_fem.dll` | 4 funciones | Matrices de rigidez FEM para vigas y frames |
| `mathcad_triangle.dll` | 6 funciones | Generación de mallas triangulares |
| `mathcad_plate.dll` | 4 funciones | Análisis FEM de placas (shell triangular) |

---

## 1. mathcad_fem.dll - Matrices de Rigidez

### Funciones Disponibles

```
fem_beam_K(E, A, I, L)           → Matriz 6×6 rigidez viga 2D
fem_frame3d_K(E, G, A, Iy, Iz, J, L) → Matriz 12×12 rigidez frame 3D
cantilever_defl(P, L, E, I)      → Deflexión cantilever
cantilever_rot(P, L, E, I)       → Rotación cantilever
```

### Ejemplo de Uso en Mathcad Prime

```
E := 210 GPa
A := 100 cm²
I := 833.3 cm⁴
L := 3 m

K := fem_beam_K(E, A, I, L)
```

### Verificación

| Coeficiente | Fórmula | Valor Esperado |
|-------------|---------|----------------|
| K[0,0] | EA/L | 700,000,000 |
| K[1,1] | 12EI/L³ | 777,746.667 |
| K[2,2] | 4EI/L | 2,333,240 |

### Archivos

- Código fuente: `Tests/mathcad_fem/mathcad_fem.C`
- Script compilación: `Tests/mathcad_fem/build.bat`
- Verificación Python: `Tests/verify_fem_beam.py`
- Verificación C++: `Tests/verify_fem_beam.cpp`

---

## 2. mathcad_triangle.dll - Generación de Mallas

### Funciones Disponibles

```
tri_nodes(Lx, Ly, nx, ny)        → Matriz [N×2] coordenadas de nodos
tri_elements(nx, ny)             → Matriz [T×3] conectividad (base 1)
tri_rect_mesh(Lx, Ly, nx, ny)    → Matriz [T×3] conectividad
tri_area(x1, y1, x2, y2, x3, y3) → Área del triángulo
tri_quality(x1, y1, x2, y2, x3, y3) → Calidad (1=equilátero)
tri_centroid(x1, y1, x2, y2, x3, y3) → Vector [xc, yc]
```

### Ejemplo de Uso

```
Lx := 6 m
Ly := 4 m
nx := 3
ny := 2

nodes := tri_nodes(Lx, Ly, nx, ny)    // 12×2
elements := tri_elements(nx, ny)       // 12×3
```

### Verificación

| Función | Entrada | Resultado Esperado |
|---------|---------|-------------------|
| `tri_area(0,0, 2,0, 0,2)` | Triángulo rectángulo | 2.0 |
| `tri_quality(0,0, 1,0, 0.5,0.866)` | Equilátero | 1.0 |
| `tri_centroid(0,0, 3,0, 0,3)` | - | (1.0, 1.0) |

### Archivos

- Código fuente: `Tests/mathcad_triangle/mathcad_triangle.c`
- Script compilación: `Tests/mathcad_triangle/build.bat`
- Verificación Python: `Tests/verify_triangle.py`
- Verificación C++: `Tests/verify_triangle.cpp`

---

## 3. mathcad_plate.dll - Análisis de Placas

### Funciones Disponibles

```
plate_Kb(x1,y1, x2,y2, x3,y3, E, nu, t) → Matriz 9×9 rigidez flexión
plate_Ks(x1,y1, x2,y2, x3,y3, E, nu, t) → Matriz 9×9 rigidez cortante
plate_K(x1,y1, x2,y2, x3,y3, E, nu, t)  → Matriz 9×9 rigidez total
plate_defl(q, a, E, nu, t)              → Deflexión central placa empotrada
```

### DOFs por Nodo (9 DOFs total para elemento triangular)

- w (desplazamiento transversal)
- θx (rotación alrededor de X)
- θy (rotación alrededor de Y)

### Ejemplo de Uso

```
// Triángulo con vértices
x1 := 0    y1 := 0
x2 := 2 m  y2 := 0
x3 := 0    y3 := 2 m

// Material
E := 210 GPa
nu := 0.3
t := 100 mm

K := plate_K(x1, y1, x2, y2, x3, y3, E, nu, t)

// Deflexión analítica para placa cuadrada empotrada
q := 1000 N/m²
a := 4 m
w := plate_defl(q, a, E, nu, t)  // ≈ 0.0168 mm
```

### Teoría Implementada

- **Teoría de Mindlin-Reissner** (placas gruesas)
- Factor de corrección de cortante: κ = 5/6
- Matriz constitutiva de flexión: Db = D × [1, ν, 0; ν, 1, 0; 0, 0, (1-ν)/2]
- Donde D = Et³/(12(1-ν²))

### Archivos

- Código fuente: `Tests/mathcad_plate/mathcad_plate.c`
- Script compilación: `Tests/mathcad_plate/build.bat`
- Verificación Python: `Tests/plate_fem_example.py`
- Verificación C++: `Tests/plate_fem_example.cpp`

---

## Cómo Compilar una DLL

### Requisitos

1. Visual Studio 2022 (Community o superior)
2. Mathcad Prime 10 instalado
3. Headers de Mathcad en: `C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions\`

### Estructura del Código C

```c
#include "mcadincl.h"

// Definir función
LRESULT MiFuncion(LPCOMPLEXSCALAR resultado, LPCCOMPLEXSCALAR param1, ...) {
    // Verificar parámetros
    if (param1->imag != 0) return MAKELRESULT(ERROR_CODE, 1);

    // Calcular
    resultado->real = /* valor */;
    resultado->imag = 0.0;

    return 0;
}

// Registrar función
FUNCTIONINFO fi_MiFuncion = {
    "nombre_funcion",           // Nombre en Mathcad
    "param1,param2",            // Parámetros
    "Descripción",              // Tooltip
    (LPCFUNCTION)MiFuncion,     // Puntero a función
    COMPLEX_SCALAR,             // Tipo de retorno
    2,                          // Número de parámetros
    {COMPLEX_SCALAR, COMPLEX_SCALAR}  // Tipos de parámetros
};

// Entry point
BOOL WINAPI DllEntryPoint(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    if (fdwReason == DLL_PROCESS_ATTACH) {
        CreateUserFunction(hinstDLL, &fi_MiFuncion);
    }
    return TRUE;
}
```

### Comando de Compilación

```batch
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cl /I"C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions" archivo.c /LD /link /out:archivo.dll /entry:DllEntryPoint "C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions\mcaduser.lib" kernel32.lib
```

### Instalación

Copiar la DLL a:
```
C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions\
```

**IMPORTANTE**: Reiniciar Mathcad Prime después de copiar la DLL.

---

## Tipos de Datos en Mathcad Custom Functions

| Tipo | Descripción | Uso |
|------|-------------|-----|
| `COMPLEX_SCALAR` | Número complejo | Entrada/Salida escalar |
| `COMPLEX_ARRAY` | Matriz compleja | Entrada/Salida matriz |
| `LPCCOMPLEXSCALAR` | Puntero const a escalar | Parámetro de entrada |
| `LPCOMPLEXSCALAR` | Puntero a escalar | Parámetro de salida |
| `LPCOMPLEXARRAY` | Puntero a array | Parámetro de salida |

### Acceso a Matrices

```c
// Mathcad usa [columna][fila] (column-major)
result->hReal[col][row] = valor;

// Allocar matriz
MathcadArrayAllocate(result, filas, columnas, TRUE, FALSE);
```

---

## Archivos Creados en esta Sesión

```
Tests/
├── mathcad_fem/
│   ├── mathcad_fem.C
│   ├── build.bat
│   └── compile.bat
├── mathcad_triangle/
│   ├── mathcad_triangle.c
│   └── build.bat
├── mathcad_plate/
│   ├── mathcad_plate.c
│   └── build.bat
├── verify_fem_beam.py
├── verify_fem_beam.cpp
├── verify_triangle.py
├── verify_triangle.cpp
├── plate_fem_example.py
└── plate_fem_example.cpp
```

---

## Próximos Pasos Sugeridos

1. **Verificar en Mathcad Prime**: Comparar resultados de las DLLs con los scripts Python/C++
2. **Agregar más funciones**: Ensamblar matrices globales, resolver sistemas
3. **Integrar Triangle de Shewchuk**: Crear wrapper para mallado Delaunay avanzado
4. **Conectar con Awatif**: Portar más funciones del código FEM de Awatif

---

## Prompt para Continuar

```
Continúa el desarrollo de las Custom Functions DLL para Mathcad Prime.

Contexto:
- Se crearon 3 DLLs: mathcad_fem.dll, mathcad_triangle.dll, mathcad_plate.dll
- Ubicación: C:\Users\j-b-j\Documents\Calcpad-7.5.7\Tests\
- Están instaladas en: C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions\

Tareas pendientes:
1. Comparar resultados de Mathcad Prime con Python/C++ para verificar exactitud
2. Agregar funciones de ensamblaje global para el análisis FEM completo
3. Crear función que resuelva el sistema K*U=F
4. Integrar el código Triangle de Shewchuk para mallado Delaunay

Archivos de referencia:
- Código Awatif FEM: C:\Users\j-b-j\Documents\Calcpad-7.5.7\awatif-2.0.0\awatif-fem\src\cpp\
- Triangle: C:\Users\j-b-j\Documents\Calcpad-7.5.7\Triangle\
- Eigen: C:\Users\j-b-j\eigen\
```
