# DLL vs API - ¿Cuál es la diferencia?

## 🎯 Respuesta Directa

**NO son lo mismo, pero están relacionados.**

```
API = Application Programming Interface (INTERFAZ - concepto)
DLL = Dynamic Link Library (ARCHIVO FISICO - .dll)
```

**Una DLL puede CONTENER una API, pero no son lo mismo.**

---

## 📦 Analogías Simples

### API = Menú del Restaurante
```
┌─────────────────────────┐
│      MENU (API)         │
├─────────────────────────┤
│                         │
│ 1. Pizza                │
│ 2. Hamburguesa          │
│ 3. Ensalada             │
│ 4. Refresco             │
│                         │
│ (lista de opciones      │
│  disponibles)           │
└─────────────────────────┘
```

**API** = Lista de funciones disponibles que puedes llamar

### DLL = Cocina del Restaurante
```
┌─────────────────────────┐
│    COCINA (DLL)         │
├─────────────────────────┤
│                         │
│ [código para hacer pizza]
│ [código para hacer hamburguesa]
│ [código para hacer ensalada]
│                         │
│ (implementación real)   │
└─────────────────────────┘
```

**DLL** = Archivo que contiene el código que hace el trabajo

---

## 🔍 Definiciones Técnicas

### API (Application Programming Interface)

**¿Qué es?**
- Es un CONCEPTO, no un archivo
- Es la "interfaz" o "contrato"
- Define QUÉ funciones están disponibles
- Define CÓMO llamarlas (parámetros, retorno)

**Ejemplo de API:**
```cpp
// API de una biblioteca matemática
// (solo declaraciones - la interfaz)

double sumar(double a, double b);
double restar(double a, double b);
double multiplicar(double a, double b);
```

Esto es **la API** - te dice qué funciones existen y cómo llamarlas.

### DLL (Dynamic Link Library)

**¿Qué es?**
- Es un ARCHIVO FÍSICO (.dll en Windows)
- Contiene el CÓDIGO COMPILADO
- Implementa las funciones que la API define

**Ejemplo de DLL:**
```cpp
// Código en la DLL (implementación)

double sumar(double a, double b) {
    return a + b;  // código real que hace la suma
}

double restar(double a, double b) {
    return a - b;  // código real que hace la resta
}
```

Esto se compila y se convierte en **matematicas.dll**.

---

## 📊 Comparación Visual

```
┌─────────────────────────────────────────────────────────┐
│                    PROYECTO COMPLETO                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  API (Interfaz)                  DLL (Implementación)  │
│  ===============                 ==================     │
│                                                         │
│  matematicas.h                   matematicas.dll       │
│  ┌───────────────┐              ┌───────────────┐      │
│  │               │              │               │      │
│  │ Declaraciones │─────────────>│  Código real  │      │
│  │               │   define     │               │      │
│  │ double sumar()│              │ return a + b  │      │
│  │ double restar │              │ return a - b  │      │
│  │               │              │               │      │
│  └───────────────┘              └───────────────┘      │
│   "QUÉ hay"                      "CÓMO funciona"       │
│   (contrato)                     (código)              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 💻 Ejemplo Completo en C++

### Paso 1: Definir la API (archivo .h)

**matematicas_api.h** - Este es "la API"
```cpp
// matematicas_api.h
// Esto define la API - qué funciones están disponibles

#ifndef MATEMATICAS_API_H
#define MATEMATICAS_API_H

#ifdef _WIN32
    #ifdef BUILDING_DLL
        #define API_EXPORT __declspec(dllexport)
    #else
        #define API_EXPORT __declspec(dllimport)
    #endif
#else
    #define API_EXPORT
#endif

// ============================================================================
// API DE MATEMATICAS
// ============================================================================
// Estas son las funciones que la DLL ofrece
// (solo declaraciones - no hay implementación aquí)

extern "C" {
    // Suma dos números
    API_EXPORT double sumar(double a, double b);

    // Resta dos números
    API_EXPORT double restar(double a, double b);

    // Multiplica dos números
    API_EXPORT double multiplicar(double a, double b);

    // Divide dos números
    API_EXPORT double dividir(double a, double b);
}

#endif // MATEMATICAS_API_H
```

**Esto es LA API** - Define qué funciones existen.

### Paso 2: Implementar la API (archivo .cpp que se compila en .dll)

**matematicas.cpp** - Implementación de la API
```cpp
// matematicas.cpp
// Esto implementa la API definida en matematicas_api.h

#define BUILDING_DLL
#include "matematicas_api.h"

// ============================================================================
// IMPLEMENTACION DE LA API
// ============================================================================
// Aquí está el código REAL que hace el trabajo

extern "C" {
    API_EXPORT double sumar(double a, double b) {
        return a + b;  // Implementación real
    }

    API_EXPORT double restar(double a, double b) {
        return a - b;  // Implementación real
    }

    API_EXPORT double multiplicar(double a, double b) {
        return a * b;  // Implementación real
    }

    API_EXPORT double dividir(double a, double b) {
        if (b != 0)
            return a / b;  // Implementación real
        return 0;
    }
}
```

**Compilar esto crea matematicas.dll** - El archivo que contiene el código.

### Paso 3: Usar la API desde un programa

**programa.cpp** - Programa que usa la API
```cpp
// programa.cpp
// Este programa usa la API definida en matematicas_api.h

#include <iostream>
#include "matematicas_api.h"

int main() {
    // Usar las funciones de la API
    double resultado = sumar(10, 5);
    std::cout << "10 + 5 = " << resultado << std::endl;

    return 0;
}
```

---

## 🎯 Relación entre API y DLL

```
┌──────────────────────────────────────────────────┐
│                                                  │
│  1. Defines la API (matematicas_api.h)          │
│     ↓                                            │
│     "Declaro que existe sumar(a, b)"             │
│                                                  │
│  2. Implementas la API (matematicas.cpp)         │
│     ↓                                            │
│     "Aquí está el código real de sumar()"        │
│                                                  │
│  3. Compilas la implementación → DLL             │
│     ↓                                            │
│     matematicas.dll creada                       │
│                                                  │
│  4. Otros programas usan la API                  │
│     ↓                                            │
│     #include "matematicas_api.h"                 │
│     resultado = sumar(10, 5);                    │
│     (El programa carga matematicas.dll           │
│      en tiempo de ejecución)                     │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 📚 Ejemplos del Mundo Real

### Windows API
```cpp
// Windows proporciona una API
#include <windows.h>  // ← Archivo de cabecera (API)

// Puedes llamar a estas funciones (definidas en la API)
MessageBox(NULL, "Hola", "Título", MB_OK);
CreateFile("archivo.txt", ...);
```

**¿Dónde está el código real?**
- En **DLLs de Windows**: `kernel32.dll`, `user32.dll`, `gdi32.dll`
- Estas DLLs implementan la Windows API

```
Windows API (concepto) → Definida en archivos .h
    ↓
Implementada en → kernel32.dll, user32.dll (archivos físicos)
```

### OpenGL API
```cpp
// OpenGL API
#include <GL/gl.h>  // ← API de OpenGL

// Funciones de la API
glBegin(GL_TRIANGLES);
glVertex3f(0.0, 1.0, 0.0);
glEnd();
```

**¿Dónde está el código real?**
- En **opengl32.dll** (Windows)
- O en drivers de tu tarjeta gráfica

### Tu proyecto: Mathcad API

```cpp
// Mathcad Custom Functions API (conceptual)

// Funciones disponibles (la API)
double cantilever_defl(P, L, E, I);
double fem_beam_K(...);
double tri_area(...);
```

**¿Dónde está el código real?**
- En **mathcad_fem.dll** (archivo físico)
- En **mathcad_triangle.dll** (archivo físico)

---

## 🔍 Tipos de APIs

### 1. API Web (REST API)
```
Cliente → HTTP Request → Servidor
         (GET /api/usuarios)

Servidor → HTTP Response → Cliente
          (JSON con datos)
```

**Ejemplo:**
```javascript
// API de Twitter
fetch('https://api.twitter.com/tweets')
```

**No es una DLL** - Es una interfaz HTTP.

### 2. API de Biblioteca (Library API)
```cpp
// API de una biblioteca matemática
#include "math_api.h"

double resultado = sqrt(25);  // De math_api.h
```

**Implementado en:**
- Una DLL (Windows): `math.dll`
- O un .so (Linux): `libmath.so`
- O un .dylib (Mac): `libmath.dylib`

### 3. API del Sistema Operativo
```cpp
// Windows API
#include <windows.h>
CreateFile(...);

// POSIX API (Linux/Mac)
#include <unistd.h>
open(...);
```

**Implementado en:**
- Windows: DLLs del sistema
- Linux: archivos .so del sistema

---

## 📊 Tabla Comparativa

| Aspecto | API | DLL |
|---------|-----|-----|
| **¿Qué es?** | Interfaz/Contrato | Archivo físico |
| **Tipo de cosa** | Concepto abstracto | Archivo concreto (.dll) |
| **Puedes verlo** | En archivos .h (declaraciones) | Sí (archivo .dll en disco) |
| **Puedes ejecutarlo** | No (es solo una definición) | No directamente (necesita un EXE) |
| **Contiene** | Declaraciones de funciones | Código compilado |
| **Ejemplo** | `matematicas.h` | `matematicas.dll` |
| **Propósito** | Define QUÉ hay disponible | Implementa CÓMO funciona |
| **Documentación** | "La biblioteca tiene `sumar()`" | - |
| **Extensión** | .h, .hpp (C++) | .dll (Windows), .so (Linux) |

---

## 🎓 ¿DLLs son para APIs?

**Respuesta corta:** No exactamente.

**Respuesta completa:**

1. **API** es el CONCEPTO/INTERFAZ
   - Define qué funciones existen
   - Define cómo llamarlas

2. **DLL** es la IMPLEMENTACIÓN
   - Contiene el código que hace el trabajo
   - Implementa las funciones que la API definió

3. **Relación:**
   - Una DLL puede IMPLEMENTAR una API
   - Pero la API existe como concepto, independiente de la DLL

**Ejemplo:**
```
API de Matemáticas (concepto)
    ├── Implementación en C++ → matematicas.dll
    ├── Implementación en Python → matematicas.py
    ├── Implementación en Java → matematicas.jar
    └── Implementación en Web → REST API en servidor
```

La misma API puede tener múltiples implementaciones.

---

## 💡 Caso Práctico: SAP2000 API

En tu proyecto tienes:

### SAP2000 API (la interfaz)
```csharp
// API de SAP2000 (definiciones)
interface cSapModel {
    int InitializeNewModel();
    int File_Open(string filename);
    int FrameObj_AddByCoord(...);
}
```

### SAP2000 DLL (la implementación)
```
SAP2000v1.dll  ← Archivo que implementa la API
```

### Tu código usa la API
```csharp
// Tu programa
var SapModel = SapObject.SapModel;  // Conecta a la API
SapModel.File_Open("modelo.sdb");   // Llama función de la API
                                    // (implementada en SAP2000v1.dll)
```

**Flujo:**
```
Tu código → Llama API de SAP2000 → SAP2000v1.dll ejecuta el código
```

---

## 🔧 Otro Ejemplo: Python API

### Python tiene una API para C
```c
// Python C API
#include <Python.h>

PyObject *obj = PyList_New(5);  // Función de la API
```

### Implementada en DLL
- **Windows:** `python39.dll`, `python310.dll`
- **Linux:** `libpython3.9.so`

**La API es el concepto**, la DLL es la implementación.

---

## 📝 Resumen Final

### API (Application Programming Interface)
- ✅ Es un concepto/interfaz
- ✅ Define qué funciones hay
- ✅ Define cómo llamarlas
- ❌ NO es un archivo ejecutable
- 📄 Se documenta en archivos .h

### DLL (Dynamic Link Library)
- ✅ Es un archivo físico (.dll)
- ✅ Contiene código compilado
- ✅ Implementa funciones
- ❌ NO se ejecuta directamente
- 💾 Archivo binario en disco

### Relación
```
API define → DLL implementa

Analogía:
API = Plano de una casa (dibuja QUÉ hay)
DLL = Casa construida (implementación real)
```

### Para tu proyecto Mathcad

```
Mathcad Custom Functions API
    ↓
Implementada en:
    • mathcad_fem.dll
    • mathcad_triangle.dll
    • mathcad_plate.dll

Tu código:
    • Define la API (qué funciones existen)
    • Compila la DLL (código que las implementa)
    • Mathcad/Python carga la DLL y usa las funciones
```

---

**¿Quedó claro?**

- **API** = El "menú" (qué funciones están disponibles)
- **DLL** = La "cocina" (código que implementa esas funciones)

No son lo mismo, pero trabajan juntos.
