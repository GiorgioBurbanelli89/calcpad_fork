# ¿Qué son DLL y EXE? - Explicación con C++

## 🎯 Definiciones Simples

### EXE (Ejecutable)
**Un programa completo que puedes ejecutar directamente.**

- Tiene un punto de entrada `main()`
- Se ejecuta haciendo doble clic
- Es independiente (standalone)

### DLL (Dynamic Link Library)
**Una biblioteca de funciones que otros programas pueden usar.**

- NO se puede ejecutar directamente
- NO tiene `main()`
- Contiene funciones que otros programas llaman

---

## 📦 Analogía del Mundo Real

### EXE = Calculadora Completa
```
┌─────────────────────┐
│   CALCULADORA.EXE   │
│                     │
│  ┌───────────────┐  │
│  │   Pantalla    │  │
│  ├───────────────┤  │
│  │ Botones       │  │
│  │ Memoria       │  │
│  │ Funciones     │  │
│  └───────────────┘  │
└─────────────────────┘

Doble clic → Se abre y funciona
```

### DLL = Caja de Herramientas
```
┌─────────────────────┐
│   MATEMATICAS.DLL   │
│                     │
│  • sumar()          │
│  • restar()         │
│  • multiplicar()    │
│  • dividir()        │
│  • raiz_cuadrada()  │
└─────────────────────┘

Doble clic → ❌ No pasa nada
Pero otros programas pueden usarla
```

---

## 💻 Ejemplo Práctico en C++

### Ejemplo 1: Crear una DLL

**Archivo: `matematicas.cpp`** (código de la DLL)

```cpp
// matematicas.cpp - Código de la DLL

#include <cmath>

// En Windows, necesitamos exportar las funciones
#ifdef _WIN32
    #define DLL_EXPORT __declspec(dllexport)
#else
    #define DLL_EXPORT
#endif

// Funciones que exportamos para que otros programas las usen
extern "C" {
    // Suma dos números
    DLL_EXPORT double sumar(double a, double b) {
        return a + b;
    }

    // Resta dos números
    DLL_EXPORT double restar(double a, double b) {
        return a - b;
    }

    // Multiplica dos números
    DLL_EXPORT double multiplicar(double a, double b) {
        return a * b;
    }

    // Divide dos números
    DLL_EXPORT double dividir(double a, double b) {
        if (b == 0) return 0;  // Evitar división por cero
        return a / b;
    }

    // Raíz cuadrada
    DLL_EXPORT double raiz_cuadrada(double x) {
        return std::sqrt(x);
    }
}
```

**Compilar la DLL:**
```bash
# Con g++ (MinGW en Windows)
g++ -shared -o matematicas.dll matematicas.cpp

# Con MSVC (Visual Studio)
cl /LD matematicas.cpp
```

**Resultado:** `matematicas.dll` (¡pero NO puedes ejecutarla directamente!)

---

### Ejemplo 2: Crear un EXE que use la DLL

**Archivo: `calculadora.cpp`** (código del EXE)

```cpp
// calculadora.cpp - Programa ejecutable que usa la DLL

#include <iostream>
#include <windows.h>

using namespace std;

// Tipos de las funciones que vamos a cargar desde la DLL
typedef double (*FuncDosDoblesRetornaDoble)(double, double);
typedef double (*FuncUnDobleRetornaDoble)(double);

int main() {
    cout << "==================================" << endl;
    cout << "  CALCULADORA (usando DLL)" << endl;
    cout << "==================================" << endl;
    cout << endl;

    // 1. CARGAR LA DLL
    HMODULE dll = LoadLibrary("matematicas.dll");

    if (!dll) {
        cout << "ERROR: No se pudo cargar matematicas.dll" << endl;
        return 1;
    }

    cout << "✓ DLL cargada exitosamente" << endl;
    cout << endl;

    // 2. OBTENER LAS FUNCIONES DE LA DLL
    auto sumar = (FuncDosDoblesRetornaDoble)GetProcAddress(dll, "sumar");
    auto restar = (FuncDosDoblesRetornaDoble)GetProcAddress(dll, "restar");
    auto multiplicar = (FuncDosDoblesRetornaDoble)GetProcAddress(dll, "multiplicar");
    auto dividir = (FuncDosDoblesRetornaDoble)GetProcAddress(dll, "dividir");
    auto raiz_cuadrada = (FuncUnDobleRetornaDoble)GetProcAddress(dll, "raiz_cuadrada");

    if (!sumar || !restar || !multiplicar || !dividir || !raiz_cuadrada) {
        cout << "ERROR: No se pudieron encontrar las funciones" << endl;
        FreeLibrary(dll);
        return 1;
    }

    cout << "✓ Funciones cargadas" << endl;
    cout << endl;

    // 3. USAR LAS FUNCIONES DE LA DLL
    double a = 10.0;
    double b = 5.0;

    cout << "Números: a = " << a << ", b = " << b << endl;
    cout << endl;

    cout << "Resultados:" << endl;
    cout << "  a + b = " << sumar(a, b) << endl;
    cout << "  a - b = " << restar(a, b) << endl;
    cout << "  a * b = " << multiplicar(a, b) << endl;
    cout << "  a / b = " << dividir(a, b) << endl;
    cout << "  √a    = " << raiz_cuadrada(a) << endl;
    cout << endl;

    // 4. LIBERAR LA DLL
    FreeLibrary(dll);

    cout << "✓ DLL liberada" << endl;

    return 0;
}
```

**Compilar el EXE:**
```bash
# Con g++
g++ -o calculadora.exe calculadora.cpp

# Con MSVC
cl calculadora.cpp
```

**Ejecutar:**
```bash
calculadora.exe
```

**Salida:**
```
==================================
  CALCULADORA (usando DLL)
==================================

✓ DLL cargada exitosamente
✓ Funciones cargadas

Números: a = 10, b = 5

Resultados:
  a + b = 15
  a - b = 5
  a * b = 50
  a / b = 2
  √a    = 3.16228

✓ DLL liberada
```

---

## 🔍 Diferencias Clave

### EXE (Ejecutable)
```cpp
// programa.cpp

#include <iostream>
using namespace std;

// ✅ TIENE main()
int main() {
    cout << "¡Hola Mundo!" << endl;
    return 0;
}
```

**Características:**
- ✅ Tiene función `main()`
- ✅ Se puede ejecutar directamente
- ✅ Es un programa completo
- ✅ Independiente

**Compilar:**
```bash
g++ -o programa.exe programa.cpp
```

**Usar:**
```bash
programa.exe    # ✅ Funciona
```

---

### DLL (Biblioteca)
```cpp
// biblioteca.cpp

#include <iostream>
using namespace std;

#ifdef _WIN32
    #define DLL_EXPORT __declspec(dllexport)
#else
    #define DLL_EXPORT
#endif

// ❌ NO TIENE main()

// Funciones exportadas
extern "C" {
    DLL_EXPORT void saludar() {
        cout << "¡Hola desde la DLL!" << endl;
    }
}
```

**Características:**
- ❌ NO tiene función `main()`
- ❌ NO se puede ejecutar directamente
- ✅ Contiene funciones para otros programas
- ✅ Reutilizable

**Compilar:**
```bash
g++ -shared -o biblioteca.dll biblioteca.cpp
```

**Usar:**
```bash
biblioteca.dll    # ❌ No pasa nada (no es ejecutable)
```

Necesitas un EXE que la cargue:
```bash
otro_programa.exe  # Este EXE carga la DLL
```

---

## 📊 Tabla Comparativa

| Aspecto | EXE | DLL |
|---------|-----|-----|
| **¿Tiene main()?** | ✅ Sí | ❌ No |
| **¿Se ejecuta directamente?** | ✅ Sí | ❌ No |
| **¿Puede funcionar solo?** | ✅ Sí | ❌ No (necesita un EXE que la use) |
| **Extensión en Windows** | `.exe` | `.dll` |
| **Punto de entrada** | `main()` | Funciones exportadas |
| **Doble clic** | Se ejecuta | No pasa nada |
| **Compilación** | `g++ -o programa.exe` | `g++ -shared -o biblioteca.dll` |

---

## 🎯 En el Contexto de Mathcad/Calcpad

### Las DLLs de Mathcad

```
mathcad_fem.dll
├── cantilever_defl()     → Calcula deflexión
├── cantilever_rot()      → Calcula rotación
├── fem_beam_K()          → Matriz de rigidez viga
└── fem_frame3d_K()       → Matriz de rigidez frame 3D

mathcad_triangle.dll
├── tri_area()            → Área del triángulo
├── tri_centroid()        → Centroide
└── tri_quality()         → Calidad del elemento
```

**Estas DLLs:**
- ❌ NO se pueden ejecutar directamente
- ✅ Contienen funciones matemáticas
- ✅ Mathcad Prime puede cargarlas con `CustomFunctions`
- ✅ Calcpad puede usarlas mediante Python/C++

---

### Estructura de una DLL de Mathcad (C++)

**Archivo: `mathcad_fem.cpp`**

```cpp
#include <cmath>

#ifdef _WIN32
    #define DLL_EXPORT __declspec(dllexport)
#else
    #define DLL_EXPORT
#endif

extern "C" {
    // Deflexión de viga en voladizo
    // Formula: δ = P*L³ / (3*E*I)
    DLL_EXPORT double cantilever_defl_export(double P, double L, double E, double I) {
        return (P * L * L * L) / (3.0 * E * I);
    }

    // Rotación de viga en voladizo
    // Formula: θ = P*L² / (2*E*I)
    DLL_EXPORT double cantilever_rot_export(double P, double L, double E, double I) {
        return (P * L * L) / (2.0 * E * I);
    }

    // Elemento [0,0] de matriz de rigidez de viga
    // Formula: k = E*A/L (rigidez axial)
    DLL_EXPORT double beam_k00(double E, double A, double I, double L) {
        return E * A / L;
    }

    // Y más funciones...
}
```

**Compilar:**
```bash
g++ -shared -o mathcad_fem.dll mathcad_fem.cpp
```

**Resultado:** `mathcad_fem.dll`

---

## 🔧 Cómo se Usa desde Diferentes Lenguajes

### Desde C++

```cpp
#include <windows.h>

typedef double (*Func4Args)(double, double, double, double);

int main() {
    // Cargar DLL
    HMODULE dll = LoadLibrary("mathcad_fem.dll");

    // Obtener función
    auto cantilever_defl = (Func4Args)GetProcAddress(dll, "cantilever_defl_export");

    // Usar función
    double delta = cantilever_defl(10000, 5, 200000, 0.0001);

    // Liberar DLL
    FreeLibrary(dll);

    return 0;
}
```

### Desde Python

```python
import ctypes

# Cargar DLL
dll = ctypes.CDLL("mathcad_fem.dll")

# Configurar tipos
dll.cantilever_defl_export.argtypes = [ctypes.c_double] * 4
dll.cantilever_defl_export.restype = ctypes.c_double

# Usar función
delta = dll.cantilever_defl_export(10000, 5, 200000, 0.0001)
```

### Desde C#

```csharp
using System.Runtime.InteropServices;

class Program {
    [DllImport("mathcad_fem.dll")]
    static extern double cantilever_defl_export(double P, double L, double E, double I);

    static void Main() {
        double delta = cantilever_defl_export(10000, 5, 200000, 0.0001);
    }
}
```

### Desde Mathcad Prime

```mathcad
CustomFunctions := [
  ["mathcad_fem.dll" "cantilever_defl_export" "Function: Invoke4"]
]

δ := cantilever_defl_export(10000, 5, 200000, 0.0001)
```

---

## 📁 Ejemplo Completo del Proyecto

```
MiProyecto/
│
├── matematicas.cpp          → Código fuente de la DLL
├── matematicas.dll          → DLL compilada
│
├── calculadora.cpp          → Código fuente del EXE
├── calculadora.exe          → EXE compilado
│
└── compilar.bat             → Script para compilar todo
```

**compilar.bat:**
```batch
@echo off
echo Compilando DLL...
g++ -shared -o matematicas.dll matematicas.cpp

echo Compilando EXE...
g++ -o calculadora.exe calculadora.cpp

echo Listo!
pause
```

---

## 🎓 Resumen Final

### EXE = Programa Completo
- Se puede ejecutar directamente
- Tiene `main()`
- Ejemplo: `calculadora.exe`, `notepad.exe`, `chrome.exe`

### DLL = Biblioteca de Funciones
- NO se ejecuta directamente
- NO tiene `main()`
- Contiene funciones que otros programas usan
- Ejemplo: `matematicas.dll`, `mathcad_fem.dll`

### Analogía
```
EXE = Coche completo
    ✅ Puedes conducirlo
    ✅ Tiene todo lo necesario (motor, ruedas, volante)

DLL = Motor suelto
    ❌ No puedes conducirlo (es solo una pieza)
    ✅ Pero puedes instalarlo en diferentes coches
```

---

## 🔍 Ventajas de Usar DLLs

### 1. Reutilización
```
matematicas.dll puede ser usada por:
  → calculadora.exe
  → graficadora.exe
  → analizador.exe
  → python script.py
  → Mathcad Prime
  → Calcpad (via Python/C++)
```

### 2. Actualización Fácil
```
Si actualizas matematicas.dll
  → Todos los programas que la usan
    obtienen la actualización automáticamente
```

### 3. Ahorro de Memoria
```
Si 10 programas usan matematicas.dll:
  → Windows solo carga 1 copia en memoria
  → Todos comparten la misma DLL
```

---

## 💡 Para Tu Proyecto (Mathcad/Calcpad)

### Tienes DLLs:
```
mathcad_fem.dll          → Funciones de vigas/frames
mathcad_triangle.dll     → Funciones de triángulos
mathcad_plate.dll        → Funciones de placas
```

### NO son programas ejecutables
❌ No puedes hacer doble clic para ejecutarlas

### Son bibliotecas que:
✅ Mathcad Prime puede cargar con `CustomFunctions`
✅ Python puede cargar con `ctypes`
✅ C++ puede cargar con `LoadLibrary()`
✅ C# puede cargar con `DllImport`

### En Calcpad:
- Calcpad NO puede cargarlas directamente
- PERO Calcpad puede ejecutar Python
- Python puede cargar las DLLs
- Resultado: Calcpad → Python → DLL → Resultado

---

**¿Quedó claro?** Las DLLs son "cajas de herramientas" que otros programas (EXEs) pueden usar, pero no se ejecutan solas.
