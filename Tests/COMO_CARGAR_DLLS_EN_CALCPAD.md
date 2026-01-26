# Cómo Cargar DLLs en Calcpad - Guía Completa

## Resumen Ejecutivo

**Calcpad NO puede cargar DLLs externas directamente** como lo hace Mathcad Prime con `CustomFunctions`.

Sin embargo, **SÍ hay formas de usar las DLLs** mediante código intermedio.

---

## ❌ Lo que NO existe en Calcpad

### CustomFunctions para DLLs (como en Mathcad Prime)

```calcpad
# ❌ ESTO NO FUNCIONA EN CALCPAD
CustomFunctions = [
  ["mathcad_fem.dll" "fem_beam_K" "Function: Invoke4"]
]

K_beam = fem_beam_K(E, A, I, L)  # ❌ ERROR
```

**Por qué no funciona:**
- La sintaxis `CustomFunctions` es exclusiva de **Mathcad Prime**
- Calcpad tiene su propia clase `CustomFunction` pero es solo para funciones definidas en sintaxis Calcpad
- No hay mecanismo de carga de DLLs directa en Calcpad

---

## ✅ Lo que SÍ existe en Calcpad

### 1. MultLangCode - Ejecutar Código Externo

Calcpad puede ejecutar código en otros lenguajes mediante directivas `@{lenguaje}`:

```calcpad
# Lenguajes soportados:
@{python}    ... @{end python}
@{cpp}       ... @{end cpp}
@{csharp}    ... @{end csharp}
@{octave}    ... @{end octave}
@{julia}     ... @{end julia}
@{fortran}   ... @{end fortran}
@{r}         ... @{end r}
@{bash}      ... @{end bash}
@{powershell} ... @{end powershell}
```

**Ubicación en código:**
- `Calcpad.Common/MultLangCode/MultLangManager.cs`
- `Calcpad.Common/MultLangCode/LanguageExecutor.cs`
- `MultLangConfig.json` (configuración de lenguajes)

---

## 🔧 Métodos para Usar DLLs desde Calcpad

### Método 1: Usar C# con DllImport

**Paso 1:** Crear wrapper en C# dentro de Calcpad

```calcpad
# Parámetros
E = 200000'MPa
A = 0.01'm^2
I = 0.0001'm^4
L = 5'm

@{csharp}
using System;
using System.Runtime.InteropServices;

public class FEMWrapper
{
    [DllImport("mathcad_fem.dll", CallingConvention = CallingConvention.Cdecl)]
    public static extern double cantilever_defl_export(double P, double L, double E, double I);

    public static void Main()
    {
        double P = 10000;
        double L = 5;
        double E = 200000;
        double I = 0.0001;

        double delta = cantilever_defl_export(P, L, E, I);
        Console.WriteLine($"Deflexion: {delta}");
    }
}
@{end csharp}
```

**Limitación:** Calcpad ejecuta esto como un proceso externo, no puede recibir el resultado directamente en variables de Calcpad.

---

### Método 2: Usar Python con ctypes

```calcpad
# Parámetros
E = 200000'MPa
A = 0.01'm^2
I = 0.0001'm^4
L = 5'm
P = 10000'N

@{python}
import ctypes
import os

# Cargar DLL
dll_path = os.path.join(os.getcwd(), "mathcad_fem.dll")
fem_dll = ctypes.CDLL(dll_path)

# Configurar tipos
fem_dll.cantilever_defl_export.argtypes = [ctypes.c_double] * 4
fem_dll.cantilever_defl_export.restype = ctypes.c_double

# Llamar función
P = 10000.0
L = 5.0
E = 200000.0
I = 0.0001

delta = fem_dll.cantilever_defl_export(P, L, E, I)
print(f"Deflexion desde DLL: {delta} m")

# Calcular analíticamente
delta_calc = P * L**3 / (3 * E * I)
print(f"Deflexion analítica: {delta_calc} m")
print(f"Diferencia: {abs(delta - delta_calc)} m")
@{end python}
```

**Ventaja:** Python puede cargar DLLs fácilmente con `ctypes`.

---

### Método 3: Usar aplicación .NET externa

**Paso 1:** Crear aplicación C# que use las DLLs

Ya existe en: `Tests/MathcadFEM.NET/MathcadFEMWrapper.cs`

**Paso 2:** Compilar la aplicación

```bash
cd Tests/MathcadFEM.NET
dotnet build -c Release
```

**Paso 3:** Llamarla desde Calcpad con bash/powershell

```calcpad
@{powershell}
# Ejecutar wrapper .NET
$result = & "MathcadFEM.NET\bin\Release\net8.0\MathcadFEM.NET.exe"
Write-Output $result
@{end powershell}
```

---

### Método 4: Wrapper C++ ejecutable

```calcpad
@{cpp}
#include <iostream>
#include <windows.h>

typedef double (*CantileverDeflFunc)(double, double, double, double);

int main() {
    // Cargar DLL
    HMODULE dll = LoadLibrary("mathcad_fem.dll");
    if (!dll) {
        std::cerr << "Error loading DLL" << std::endl;
        return 1;
    }

    // Obtener función
    auto cantilever_defl = (CantileverDeflFunc)GetProcAddress(dll, "cantilever_defl_export");
    if (!cantilever_defl) {
        std::cerr << "Function not found" << std::endl;
        return 1;
    }

    // Llamar función
    double P = 10000.0;
    double L = 5.0;
    double E = 200000.0;
    double I = 0.0001;

    double delta = cantilever_defl(P, L, E, I);
    std::cout << "Deflexion: " << delta << " m" << std::endl;

    FreeLibrary(dll);
    return 0;
}
@{end cpp}
```

---

## 📊 Comparación de Métodos

| Método | Complejidad | Velocidad | Integración con Calcpad |
|--------|-------------|-----------|-------------------------|
| **C# DllImport** | Media | Alta | Baja (salida solo a consola) |
| **Python ctypes** | Baja | Media | Media (puede generar archivos) |
| **App .NET externa** | Alta | Alta | Baja (ejecutable separado) |
| **C++ wrapper** | Alta | Muy Alta | Baja (ejecutable separado) |
| **Cálculo directo en Calcpad** | Muy Baja | Alta | Muy Alta (nativo) |

---

## 🎯 Recomendación para Comparación con Mathcad

### Opción A: Comparación Manual (Más Simple)

1. **Calcpad:** Calcula resultados analíticos y genera HTML
2. **Mathcad Prime:** Usa CustomFunctions para cargar DLLs
3. **Usuario:** Compara resultados manualmente

**Archivos:**
```
Tests/
├── mathcad_fem_comparison.cpd    # Cálculos analíticos en Calcpad
├── run_comparison.bat             # Genera HTML
└── COMPARACION_RESULTADOS.md     # Template para comparación
```

**Comando:**
```bash
cd Tests
run_comparison.bat
```

---

### Opción B: Uso de Python ctypes (Automatizada)

```calcpad
# mathcad_dll_python_test.cpd

"================================================================"
"PRUEBA: Comparar DLLs de Mathcad usando Python desde Calcpad"
"================================================================"
''
# Parámetros
E = 200000'MPa
A = 0.01'm^2
I = 0.0001'm^4
L = 5'm
P = 10000'N
''
"Resultados analíticos (Calcpad):"
δ_calc = P*L^3/(3*E*I)'m
θ_calc = P*L^2/(2*E*I)'rad
k_EA_L = E*A/L'N/m
''
"Llamando a DLLs mediante Python:"
''
@{python}
import ctypes
import os

# Cargar DLL
dll = ctypes.CDLL("mathcad_fem.dll")

# Configurar funciones
dll.cantilever_defl_export.argtypes = [ctypes.c_double] * 4
dll.cantilever_defl_export.restype = ctypes.c_double
dll.cantilever_rot_export.argtypes = [ctypes.c_double] * 4
dll.cantilever_rot_export.restype = ctypes.c_double

# Parámetros
P, L, E, I = 10000.0, 5.0, 200000.0, 0.0001

# Llamar DLLs
delta_dll = dll.cantilever_defl_export(P, L, E, I)
theta_dll = dll.cantilever_rot_export(P, L, E, I)

# Calcular analíticamente
delta_calc = P * L**3 / (3 * E * I)
theta_calc = P * L**2 / (2 * E * I)

# Comparar
print(f"DEFLEXION:")
print(f"  DLL:       {delta_dll:.6f} m")
print(f"  Calcpad:   {delta_calc:.6f} m")
print(f"  Diferencia: {abs(delta_dll - delta_calc):.9f} m")
print(f"  Estado: {'PASS' if abs(delta_dll - delta_calc) < 0.001 else 'FAIL'}")
print()
print(f"ROTACION:")
print(f"  DLL:       {theta_dll:.6f} rad")
print(f"  Calcpad:   {theta_calc:.6f} rad")
print(f"  Diferencia: {abs(theta_dll - theta_calc):.9f} rad")
print(f"  Estado: {'PASS' if abs(theta_dll - theta_calc) < 0.001 else 'FAIL'}")
@{end python}
''
"================================================================"
"FIN DE LA PRUEBA"
"================================================================"
```

---

## 📁 Estructura del Código Fuente

### MultLangCode (Sistema de Ejecución de Código Externo)

```
Calcpad.Common/MultLangCode/
├── MultLangManager.cs          # Gestor principal
├── MultLangProcessor.cs        # Procesa bloques @{lang}
├── LanguageExecutor.cs         # Ejecuta código externo
├── LanguageHtmlGenerator.cs    # Genera HTML con highlighting
└── MultLangConfig.json         # Configuración de lenguajes
```

**Cómo funciona:**
1. Detecta bloques `@{lenguaje}` en archivos .cpd
2. Extrae el código
3. Lo guarda en archivo temporal (`.py`, `.cs`, `.cpp`, etc.)
4. Ejecuta usando `Process.Start()` con el comando apropiado
5. Captura la salida (stdout/stderr)
6. Inserta resultado en HTML

### CustomFunction (Funciones Definidas por Usuario)

```
Calcpad.Core/Parsers/MathParser/
└── MathParser.CustomFunction.cs
```

**Clases:**
- `CustomFunction` (abstracta)
- `CustomFunction1` (1 parámetro)
- `CustomFunction2` (2 parámetros)
- `CustomFunction3` (3 parámetros)
- `CustomFunctionN` (N parámetros)

**Propósito:** Funciones definidas en sintaxis Calcpad, NO para cargar DLLs.

**Ejemplo:**
```calcpad
# Definir función personalizada
$Custom
    f(x; y) = x^2 + y^2
$End

# Usar función
result = f(3; 4)  # = 25
```

---

## 🔍 Evidencia en el Código

### 1. MultLangManager.cs muestra lenguajes soportados

```csharp
Languages = new Dictionary<string, LanguageDefinition>
{
    ["python"] = new LanguageDefinition { Command = "python", ... },
    ["cpp"] = new LanguageDefinition { Command = "g++", RequiresCompilation = true, ... },
    ["csharp"] = new LanguageDefinition { Command = "dotnet", RequiresCompilation = true, ... },
    // ... más lenguajes
}
```

### 2. Búsqueda en todo el código fuente

```bash
# Buscar LoadLibrary (carga de DLLs nativa)
grep -r "LoadLibrary" Calcpad.Core/
# Resultado: NO encontrado

# Buscar DllImport
grep -r "DllImport" Calcpad.Core/
# Resultado: Solo en HpMatrix (matrices de alto rendimiento internas)

# Buscar NativeLibrary
grep -r "NativeLibrary" Calcpad.Core/
# Resultado: NO encontrado
```

**Conclusión:** No hay mecanismo de carga de DLLs externas en Calcpad.Core.

---

## 💡 Conclusión Final

### Lo que Calcpad NO puede hacer:
- ❌ Cargar DLLs directamente con sintaxis tipo `CustomFunctions`
- ❌ Llamar funciones de DLLs desde expresiones de Calcpad
- ❌ Retornar valores de DLLs a variables de Calcpad directamente

### Lo que Calcpad SÍ puede hacer:
- ✅ Ejecutar código Python que cargue DLLs (usando `ctypes`)
- ✅ Ejecutar código C# que cargue DLLs (usando `DllImport`)
- ✅ Ejecutar código C++ que cargue DLLs (usando `LoadLibrary`)
- ✅ Capturar salida de estos programas en el HTML

### Mejor Enfoque:

**Para comparar DLLs de Mathcad con Calcpad:**

1. **Opción Simple:** Comparación manual
   - Calcpad genera resultados analíticos
   - Mathcad Prime usa CustomFunctions con DLLs
   - Usuario compara manualmente

2. **Opción Intermedia:** Python ctypes desde Calcpad
   - Calcpad ejecuta script Python
   - Python carga DLLs y compara con valores analíticos
   - Salida se muestra en HTML

3. **Opción Avanzada:** Aplicación .NET separada
   - Aplicación C# carga DLLs y hace comparación completa
   - Genera reporte JSON/HTML
   - Calcpad incluye/muestra el reporte

---

## 📚 Referencias

- **MultLangCode:** `Calcpad.Common/MultLangCode/`
- **Wrapper .NET para DLLs:** `Tests/MathcadFEM.NET/MathcadFEMWrapper.cs`
- **Configuración de lenguajes:** `MultLangConfig.json`
- **CustomFunction (interno):** `Calcpad.Core/Parsers/MathParser/MathParser.CustomFunction.cs`

---

## ⚠️ Aclaración Importante

La sintaxis `CustomFunctions` que se ve en **Screenshot_35.png** es de **Mathcad Prime**, NO de Calcpad.

**Mathcad Prime:**
```mathcad
CustomFunctions = [
  ["mathcad_fem.dll" "fem_beam_K" "Function: Invoke4"]
]
K := fem_beam_K(E, A, I, L)  # ✅ Funciona en Mathcad Prime
```

**Calcpad:**
```calcpad
CustomFunctions = [
  ["mathcad_fem.dll" "fem_beam_K" "Function: Invoke4"]
]
K = fem_beam_K(E, A, I, L)  # ❌ NO funciona en Calcpad
```

Son dos programas diferentes con capacidades diferentes.

---

**Última actualización:** 2026-01-22
