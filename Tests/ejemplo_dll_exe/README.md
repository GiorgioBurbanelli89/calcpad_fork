# Ejemplo Práctico: DLL vs EXE

## 🎯 ¿Qué es este ejemplo?

Un ejemplo simple y completo para entender la diferencia entre DLL y EXE usando C++.

---

## 📁 Archivos

```
ejemplo_dll_exe/
├── matematicas.cpp      → Código fuente de la DLL
├── calculadora.cpp      → Código fuente del EXE
├── compilar.bat         → Script para compilar
├── ejecutar.bat         → Script para ejecutar
├── paso_a_paso.txt      → Guía paso a paso
└── README.md            → Este archivo
```

---

## 🚀 Uso Rápido (3 pasos)

### 1. Compila
```bash
compilar.bat
```

Esto crea:
- `matematicas.dll` (biblioteca)
- `calculadora.exe` (ejecutable)

### 2. Ejecuta
```bash
ejecutar.bat
```

o

```bash
calculadora.exe
```

### 3. Experimenta

**Intenta hacer doble clic en `matematicas.dll`**
- ❌ No pasa nada
- Por qué: No es ejecutable, es solo una biblioteca

**Intenta hacer doble clic en `calculadora.exe`**
- ✅ Se ejecuta
- Por qué: Es un programa completo

**Borra `matematicas.dll` y ejecuta `calculadora.exe`**
- ❌ Error: "No se pudo cargar matematicas.dll"
- Por qué: El EXE necesita la DLL para funcionar

---

## 📖 Lee el Código

### matematicas.cpp (DLL)

```cpp
// NO tiene main()
// Solo funciones exportadas

extern "C" {
    DLL_EXPORT double sumar(double a, double b) {
        return a + b;
    }
    // ... más funciones
}
```

**Características:**
- ❌ NO tiene `main()`
- ✅ Tiene funciones exportadas
- ❌ NO se puede ejecutar directamente
- ✅ Otros programas pueden usar sus funciones

### calculadora.cpp (EXE)

```cpp
// SI tiene main()
int main() {
    // 1. Cargar DLL
    HMODULE dll = LoadLibrary("matematicas.dll");

    // 2. Obtener funciones
    auto sumar = (FuncDosDoblesRetornaDoble)GetProcAddress(dll, "sumar");

    // 3. Usar funciones
    double resultado = sumar(10, 5);

    // 4. Liberar DLL
    FreeLibrary(dll);

    return 0;
}
```

**Características:**
- ✅ SI tiene `main()`
- ✅ Carga la DLL
- ✅ Usa las funciones de la DLL
- ✅ Se puede ejecutar directamente

---

## 🔍 Diferencias Visuales

### Compilar la DLL
```bash
g++ -shared -o matematicas.dll matematicas.cpp
         ↑
    importante: -shared hace que sea DLL
```

### Compilar el EXE
```bash
g++ -o calculadora.exe calculadora.cpp
       ↑
   sin -shared, es un EXE normal
```

---

## 📊 Comparación Lado a Lado

| Aspecto | matematicas.dll | calculadora.exe |
|---------|-----------------|-----------------|
| **Tiene main()** | ❌ No | ✅ Sí |
| **Se ejecuta directamente** | ❌ No | ✅ Sí |
| **Puede funcionar solo** | ❌ No | ✅ Sí (pero necesita la DLL) |
| **Contiene** | Funciones | Programa completo |
| **Tamaño** | ~50 KB | ~150 KB |

---

## 🎓 Flujo de Ejecución

```
Usuario hace doble clic en calculadora.exe
            ↓
    calculadora.exe se ejecuta
            ↓
    main() se llama
            ↓
    LoadLibrary("matematicas.dll")
            ↓
    matematicas.dll se carga en memoria
            ↓
    GetProcAddress(dll, "sumar")
            ↓
    Ahora puede llamar a sumar()
            ↓
    resultado = sumar(10, 5)
            ↓
    Muestra resultado: 15
            ↓
    FreeLibrary(dll)
            ↓
    matematicas.dll se descarga de memoria
            ↓
    Programa termina
```

---

## 💡 Analogía

### DLL = Caja de Herramientas
```
┌─────────────────────┐
│  matematicas.dll    │
├─────────────────────┤
│  🔨 sumar()         │
│  🔧 restar()        │
│  🪛 multiplicar()   │
│  ✂️  dividir()       │
│  📐 raiz_cuadrada() │
└─────────────────────┘
```

No puedes usar la caja sola. Necesitas a alguien (un carpintero) que tome las herramientas.

### EXE = Carpintero
```
┌─────────────────────┐
│  calculadora.exe    │
├─────────────────────┤
│                     │
│  1. Abre la caja    │◄── LoadLibrary()
│  2. Toma martillo   │◄── GetProcAddress()
│  3. Usa martillo    │◄── sumar()
│  4. Cierra la caja  │◄── FreeLibrary()
│                     │
└─────────────────────┘
```

El carpintero (EXE) toma las herramientas (funciones de DLL) y las usa.

---

## 🔧 Modifica y Experimenta

### Agregar una función nueva a la DLL

1. Abre `matematicas.cpp`
2. Agrega una nueva función:

```cpp
extern "C" {
    // ... funciones existentes

    // Nueva función
    DLL_EXPORT double cubo(double x) {
        return x * x * x;
    }
}
```

3. Recompila:
```bash
compilar.bat
```

4. Modifica `calculadora.cpp` para usar la nueva función:

```cpp
// Después de GetProcAddress de las otras funciones
auto cubo = (FuncUnDobleRetornaDoble)GetProcAddress(dll, "cubo");

// Usar la función
cout << "  5³ = " << cubo(5) << endl;
```

5. Recompila y ejecuta:
```bash
compilar.bat
ejecutar.bat
```

---

## 🎯 Para Entender el Proyecto Mathcad

### mathcad_fem.dll (Tu DLL)

Igual que `matematicas.dll`, pero en lugar de `sumar()` tiene:
- `cantilever_defl()` - Calcula deflexión
- `fem_beam_K()` - Matriz de rigidez
- etc.

### ¿Cómo se usa?

**En Mathcad Prime:**
```mathcad
CustomFunctions := [
  ["mathcad_fem.dll" "cantilever_defl" "Function: Invoke4"]
]

δ := cantilever_defl(P, L, E, I)
```

**En Python:**
```python
import ctypes
dll = ctypes.CDLL("mathcad_fem.dll")
delta = dll.cantilever_defl_export(P, L, E, I)
```

**En C++ (como este ejemplo):**
```cpp
HMODULE dll = LoadLibrary("mathcad_fem.dll");
auto cantilever_defl = (Func4)GetProcAddress(dll, "cantilever_defl_export");
double delta = cantilever_defl(P, L, E, I);
FreeLibrary(dll);
```

---

## 📚 Siguiente Paso

Lee: `../QUE_SON_DLL_Y_EXE.md` para más información detallada.

---

**¡Ahora compila y prueba este ejemplo para entender la diferencia!**
