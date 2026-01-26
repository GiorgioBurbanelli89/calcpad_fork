# API vs DLL - En Tu Proyecto Mathcad

## 🎯 Tu Situación Específica

Tienes estas DLLs:
- `mathcad_fem.dll`
- `mathcad_triangle.dll`
- `mathcad_plate.dll`

**Pregunta:** ¿Estas DLLs son APIs?

**Respuesta:** NO. Estas DLLs **implementan** una API.

---

## 📋 En Tu Proyecto

### La API (Concepto/Interfaz)

Esto es lo que **defines** - qué funciones existen:

```cpp
// mathcad_fem_api.h - ESTO ES LA API
// Define QUE funciones están disponibles

#ifndef MATHCAD_FEM_API_H
#define MATHCAD_FEM_API_H

#ifdef _WIN32
    #define DLL_EXPORT __declspec(dllexport)
#else
    #define DLL_EXPORT
#endif

extern "C" {
    // API para voladizo
    DLL_EXPORT double cantilever_defl_export(double P, double L, double E, double I);
    DLL_EXPORT double cantilever_rot_export(double P, double L, double E, double I);

    // API para viga
    DLL_EXPORT void fem_beam_K_export(double E, double A, double I, double L, double* K);

    // API para frame 3D
    DLL_EXPORT void fem_frame3d_K_export(double E, double G, double A,
                                          double Iy, double Iz, double J,
                                          double L, double* K);
}

#endif
```

**Esto es LA API:**
- Define qué funciones existen
- Define sus parámetros
- Define qué retornan
- NO contiene implementación

### La DLL (Implementación)

Esto es lo que **compilas** - el código que hace el trabajo:

```cpp
// mathcad_fem.cpp - ESTO SE COMPILA EN LA DLL
// Implementa las funciones que la API definió

#include "mathcad_fem_api.h"

extern "C" {
    // IMPLEMENTACION de cantilever_defl_export
    DLL_EXPORT double cantilever_defl_export(double P, double L, double E, double I) {
        // CODIGO REAL que calcula la deflexión
        return (P * L * L * L) / (3.0 * E * I);
    }

    // IMPLEMENTACION de cantilever_rot_export
    DLL_EXPORT double cantilever_rot_export(double P, double L, double E, double I) {
        // CODIGO REAL que calcula la rotación
        return (P * L * L) / (2.0 * E * I);
    }

    // IMPLEMENTACION de fem_beam_K_export
    DLL_EXPORT void fem_beam_K_export(double E, double A, double I, double L, double* K) {
        // CODIGO REAL que calcula la matriz de rigidez
        double EA_L = E * A / L;
        double EI_L3 = E * I / (L * L * L);
        // ... más código
        K[0] = EA_L;
        K[7] = 12 * EI_L3;
        // ... etc
    }
}
```

**Compilar:**
```bash
g++ -shared -o mathcad_fem.dll mathcad_fem.cpp
```

**Resultado:** `mathcad_fem.dll`

---

## 🔍 Comparación

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TU PROYECTO                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  API (Interfaz)                   DLL (Implementación)              │
│  ===============                  ====================              │
│                                                                     │
│  mathcad_fem_api.h               mathcad_fem.dll                    │
│  ┌──────────────────┐            ┌──────────────────┐              │
│  │                  │            │                  │              │
│  │ Declaraciones:   │───────────>│ Código real:     │              │
│  │                  │  define    │                  │              │
│  │ double           │            │ return P*L³/3EI  │              │
│  │ cantilever_defl()│            │                  │              │
│  │                  │            │                  │              │
│  └──────────────────┘            └──────────────────┘              │
│    Archivo .h                      Archivo .dll                    │
│    Texto legible                   Binario compilado               │
│    "QUE hay"                       "COMO funciona"                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 💻 Cómo se Usa en Diferentes Lugares

### En Mathcad Prime

**Mathcad carga la DLL:**
```mathcad
CustomFunctions := [
  ["mathcad_fem.dll" "cantilever_defl_export" "Function: Invoke4"]
]

δ := cantilever_defl_export(10000, 5, 200000, 0.0001)
```

**Lo que pasa:**
1. Mathcad lee tu **API** (sabe que existe `cantilever_defl_export`)
2. Mathcad carga la **DLL** (`mathcad_fem.dll`)
3. Mathcad ejecuta el **código** dentro de la DLL

### En Python

```python
import ctypes

# Cargar la DLL
dll = ctypes.CDLL("mathcad_fem.dll")

# Configurar la API (decirle a Python qué esperar)
dll.cantilever_defl_export.argtypes = [ctypes.c_double] * 4
dll.cantilever_defl_export.restype = ctypes.c_double

# Usar la función
delta = dll.cantilever_defl_export(10000, 5, 200000, 0.0001)
```

**Lo que pasa:**
1. Python carga la **DLL** (`mathcad_fem.dll`)
2. Python necesita saber la **API** (qué parámetros, qué retorna)
3. Python llama la función, la **DLL ejecuta el código**

### En C++

```cpp
#include <windows.h>
#include "mathcad_fem_api.h"  // ← Incluye la API

int main() {
    // Cargar la DLL
    HMODULE dll = LoadLibrary("mathcad_fem.dll");

    // Obtener la función (definida en la API)
    typedef double (*CantileverDefl)(double, double, double, double);
    auto cantilever_defl = (CantileverDefl)GetProcAddress(dll, "cantilever_defl_export");

    // Usar la función
    double delta = cantilever_defl(10000, 5, 200000, 0.0001);

    FreeLibrary(dll);
    return 0;
}
```

**Lo que pasa:**
1. C++ incluye el **archivo de API** (sabe qué funciones existen)
2. C++ carga la **DLL** en memoria
3. C++ llama la función, la **DLL ejecuta el código**

---

## 🎓 Flujo Completo en Tu Proyecto

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DESARROLLO DE TU DLL                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. DISEÑAS LA API                                                  │
│     ↓                                                               │
│     "Necesito estas funciones:"                                     │
│     • cantilever_defl(P, L, E, I)                                   │
│     • fem_beam_K(E, A, I, L)                                        │
│                                                                     │
│  2. ESCRIBES EL ARCHIVO DE CABECERA (.h)                            │
│     ↓                                                               │
│     mathcad_fem_api.h                                               │
│     (declaraciones de funciones)                                    │
│                                                                     │
│  3. IMPLEMENTAS LAS FUNCIONES (.cpp)                                │
│     ↓                                                               │
│     mathcad_fem.cpp                                                 │
│     double cantilever_defl(...) {                                   │
│       return P * L³ / (3 * E * I);                                  │
│     }                                                               │
│                                                                     │
│  4. COMPILAS A DLL                                                  │
│     ↓                                                               │
│     g++ -shared -o mathcad_fem.dll mathcad_fem.cpp                  │
│                                                                     │
│  5. RESULTADO                                                       │
│     ↓                                                               │
│     mathcad_fem.dll creada                                          │
│     (archivo binario con código compilado)                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      USO DE TU DLL                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  USUARIO (Mathcad/Python/C++)                                       │
│     ↓                                                               │
│  "Quiero calcular deflexión"                                        │
│     ↓                                                               │
│  Llama: cantilever_defl(10000, 5, 200000, 0.0001)                   │
│     ↓                                                               │
│  Sistema carga mathcad_fem.dll                                      │
│     ↓                                                               │
│  DLL ejecuta el código: return P*L³/(3*E*I)                         │
│     ↓                                                               │
│  Retorna: 0.020833                                                  │
│     ↓                                                               │
│  Usuario recibe el resultado                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Ejemplo Real de Tu Código

### Archivo API (mathcad_fem_api.h)

```cpp
// mathcad_fem_api.h
// ESTO ES LA API - Define la interfaz

#ifndef MATHCAD_FEM_API_H
#define MATHCAD_FEM_API_H

#ifdef _WIN32
    #define API_EXPORT __declspec(dllexport)
#else
    #define API_EXPORT
#endif

// ============================================================================
// API DE MATHCAD FEM
// ============================================================================
// Estas son todas las funciones que la DLL ofrece
// Otros programas pueden llamar estas funciones

extern "C" {
    // Calcula deflexión de voladizo
    // Parámetros: P (carga), L (longitud), E (módulo), I (inercia)
    // Retorna: deflexión en metros
    API_EXPORT double cantilever_defl_export(double P, double L, double E, double I);

    // Calcula rotación de voladizo
    // Parámetros: P (carga), L (longitud), E (módulo), I (inercia)
    // Retorna: rotación en radianes
    API_EXPORT double cantilever_rot_export(double P, double L, double E, double I);

    // Calcula matriz de rigidez de viga 2D
    // Parámetros: E, A, I, L, K (puntero al array de salida)
    API_EXPORT void fem_beam_K_export(double E, double A, double I, double L, double* K);
}

#endif
```

**Esto es LA API:**
- NO contiene código de implementación
- Solo declara qué funciones existen
- Documenta parámetros y retornos

### Archivo Implementación (mathcad_fem.cpp)

```cpp
// mathcad_fem.cpp
// ESTO SE COMPILA EN LA DLL - Implementa la API

#include "mathcad_fem_api.h"
#include <cmath>

extern "C" {
    // IMPLEMENTACION de cantilever_defl_export
    API_EXPORT double cantilever_defl_export(double P, double L, double E, double I) {
        // Fórmula: δ = P*L³/(3*E*I)
        return (P * L * L * L) / (3.0 * E * I);
    }

    // IMPLEMENTACION de cantilever_rot_export
    API_EXPORT double cantilever_rot_export(double P, double L, double E, double I) {
        // Fórmula: θ = P*L²/(2*E*I)
        return (P * L * L) / (2.0 * E * I);
    }

    // IMPLEMENTACION de fem_beam_K_export
    API_EXPORT void fem_beam_K_export(double E, double A, double I, double L, double* K) {
        // Calcular términos comunes
        double EA_L = E * A / L;
        double EI_L3 = E * I / (L * L * L);
        double EI_L2 = E * I / (L * L);
        double EI_L = E * I / L;

        // Llenar matriz 6x6 (guardada como array 1D)
        // Rigidez axial
        K[0*6+0] = EA_L;   K[0*6+3] = -EA_L;
        K[3*6+0] = -EA_L;  K[3*6+3] = EA_L;

        // Rigidez de flexión
        K[1*6+1] = 12 * EI_L3;
        K[1*6+2] = 6 * EI_L2;
        // ... resto de la matriz
    }
}
```

**Compilar:**
```bash
g++ -shared -o mathcad_fem.dll mathcad_fem.cpp
```

**Resultado:** `mathcad_fem.dll` (archivo binario)

---

## 🔍 ¿Qué es Qué?

### En tu proyecto:

| Archivo | ¿Es API? | ¿Es DLL? | ¿Qué es? |
|---------|----------|----------|----------|
| `mathcad_fem_api.h` | ✅ Sí (define la API) | ❌ No | Archivo de cabecera con declaraciones |
| `mathcad_fem.cpp` | ❌ No | ❌ No (aún) | Código fuente con implementación |
| `mathcad_fem.dll` | ❌ No | ✅ Sí | Archivo binario compilado |

**Relación:**
```
mathcad_fem_api.h (API) + mathcad_fem.cpp (código) → compilar → mathcad_fem.dll
```

---

## 💡 Resumen para Tu Proyecto

### ¿Qué tienes ahora?

```
Tests/
├── mathcad_fem.dll          ← DLL (implementación compilada)
├── mathcad_triangle.dll     ← DLL (implementación compilada)
└── mathcad_plate.dll        ← DLL (implementación compilada)
```

### ¿Son estas DLLs APIs?

**NO.** Estas DLLs **implementan** una API.

### ¿Cuál es la API entonces?

La API es el conjunto de funciones que definiste:
- `cantilever_defl_export(P, L, E, I)`
- `cantilever_rot_export(P, L, E, I)`
- `fem_beam_K_export(E, A, I, L, K)`
- `tri_area_export(x1, y1, x2, y2, x3, y3)`
- etc.

### ¿Dónde está definida la API?

En los archivos de cabecera (si los tienes):
- `mathcad_fem_api.h`
- `mathcad_triangle_api.h`

O simplemente en la documentación/código fuente.

### Flujo completo:

```
1. Defines la API
   ↓
   "Necesito cantilever_defl(P, L, E, I)"

2. Implementas la API
   ↓
   double cantilever_defl(...) { return P*L³/(3*E*I); }

3. Compilas
   ↓
   mathcad_fem.dll

4. Otros programas usan
   ↓
   Mathcad: cantilever_defl_export(...)
   Python: dll.cantilever_defl_export(...)
   C++: cantilever_defl(...)
```

---

## 🎯 Conclusión

**Para tu proyecto:**

- **API** = Las funciones que definiste (`cantilever_defl`, `fem_beam_K`, etc.)
- **DLL** = Los archivos binarios que contienen el código (`mathcad_fem.dll`)

**Las DLLs NO SON APIs.**

**Las DLLs IMPLEMENTAN tu API.**

**Analogía:**
- API = Menú del restaurante ("Ofrecemos pizza")
- DLL = La cocina que hace la pizza

El menú y la cocina son cosas diferentes.
Pero trabajan juntos para darte la pizza.
