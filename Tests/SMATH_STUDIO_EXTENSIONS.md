# SMath Studio - Crear Extensiones/Plugins

## 🎯 ¿Qué es SMath Studio?

**SMath Studio** es un programa de cálculo matemático similar a Mathcad, pero:
- ✅ **Gratuito** (Mathcad es de pago)
- ✅ **Open source**
- ✅ **Multiplataforma** (Windows, Linux, Android)
- ✅ **Soporta plugins/extensiones** en C#

**URL:** https://smath.com/

---

## 📊 Comparación: Mathcad vs SMath Studio vs Calcpad

| Característica | Mathcad Prime | SMath Studio | Calcpad |
|----------------|---------------|--------------|---------|
| **Precio** | 💰 Pago ($$$) | ✅ Gratuito | ✅ Gratuito |
| **Código** | Cerrado | Open Source | Open Source |
| **Carga DLLs** | ✅ CustomFunctions | ✅ Plugins C# | ❌ No directamente |
| **Extensiones** | ✅ Sí | ✅ Sí (C#) | ⚠️ MultLangCode |
| **Lenguaje** | Mathcad | Similar Mathcad | Propio |
| **API** | Limitada | ✅ Completa | ❌ No para DLLs |

**Conclusión:** SMath Studio puede ser una excelente alternativa para usar tus DLLs.

---

## 🔍 Repositorios que Compartiste

### 1. AcadToSMath
**URL:** https://github.com/rumata-ap/AcadToSMath

**¿Qué es?**
- Extensión de SMath Studio para vincular AutoCAD y archivos DXF
- Escrita en C# 100%
- Ejemplo de cómo crear una extensión para SMath

**Archivos clave:**
```
AcadToSMath/
├── AcadToSMath.sln          → Solución Visual Studio
├── AcadToSMath/
│   ├── AcadToSMath.csproj   → Proyecto C#
│   └── [código fuente]
```

### 2. MatrixExtension_SMathStudio
**URL:** https://github.com/rumata-ap/MatrixExtension_SMathStudio

**¿Qué es?**
- Extensión de matrices para SMath Studio
- Añade funcionalidad matricial adicional
- Ejemplo de extensión matemática

**Archivos clave:**
```
MatrixExtension/
├── MatrixExtensions.sln
├── MatrixExtensions.cs      → Código de la extensión
├── MatrixL.cs               → Lógica de matrices
└── Utilites.cs              → Utilidades
```

### 3. NetEFI
**URL:** https://github.com/ViacheslavMezentsev/NetEFI

**¿Qué es?**
- ⚠️ **NO es para SMath Studio**
- Es para **Mathcad Prime** (versiones 15 y Prime)
- Framework para crear funciones personalizadas en .NET

**Nota:** Este no te sirve directamente para SMath, pero muestra cómo crear funciones para Mathcad.

### 4. API de SMath Studio
**URL:** https://smath.com/documentation/api/

**¿Qué es?**
- Documentación oficial de la API
- Namespace principal: `SMath.Controls`
- Interfaces para crear plugins

**Clases principales:**
- `Worksheet` - Documento/hoja de trabajo
- `RegionBase` - Regiones editables
- `IPluginCustomRegion` - Crear regiones personalizadas
- `IPluginMenuExtender` - Extender menús
- `IPluginHandleFileTypes` - Tipos de archivo
- `IPluginDataInputOutput` - I/O de datos

---

## 🔧 Cómo Crear una Extensión para SMath Studio

### Estructura Básica

Una extensión de SMath Studio es una **DLL en C#** que implementa interfaces específicas.

### Paso 1: Crear Proyecto en Visual Studio

```xml
<!-- MiExtension.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net48</TargetFramework>
    <OutputType>Library</OutputType>
  </PropertyGroup>

  <ItemGroup>
    <Reference Include="SMath.Core">
      <HintPath>C:\Program Files\SMath Studio\SMath.Core.dll</HintPath>
    </Reference>
  </ItemGroup>
</Project>
```

### Paso 2: Implementar la Interfaz del Plugin

```csharp
// MathcadFEMPlugin.cs

using System;
using SMath.Manager;

namespace MathcadFEMPlugin
{
    public class FEMFunctions : IPlugin
    {
        // Información del plugin
        public string Name => "Mathcad FEM Functions";
        public string Description => "Funciones de análisis FEM de vigas y placas";
        public string Author => "Tu Nombre";
        public Version Version => new Version(1, 0, 0);

        // Inicialización
        public void Initialize()
        {
            // Registrar funciones personalizadas
            GlobalFunctions.RegisterFunction("cantilever_defl", CantileverDeflection);
            GlobalFunctions.RegisterFunction("fem_beam_K", BeamStiffnessMatrix);
            GlobalFunctions.RegisterFunction("tri_area", TriangleArea);
        }

        // Implementación de funciones
        private static Term CantileverDeflection(Term[] args)
        {
            // args[0] = P (carga)
            // args[1] = L (longitud)
            // args[2] = E (módulo de elasticidad)
            // args[3] = I (momento de inercia)

            double P = args[0].ToDouble();
            double L = args[1].ToDouble();
            double E = args[2].ToDouble();
            double I = args[3].ToDouble();

            // Fórmula: δ = P*L³/(3*E*I)
            double delta = (P * L * L * L) / (3.0 * E * I);

            return new Term(delta);
        }

        private static Term BeamStiffnessMatrix(Term[] args)
        {
            double E = args[0].ToDouble();
            double A = args[1].ToDouble();
            double I = args[2].ToDouble();
            double L = args[3].ToDouble();

            // Crear matriz 6x6
            Matrix K = new Matrix(6, 6);

            double EA_L = E * A / L;
            double EI_L3 = E * I / (L * L * L);
            double EI_L2 = E * I / (L * L);
            double EI_L = E * I / L;

            // Rigidez axial
            K[0, 0] = EA_L;
            K[0, 3] = -EA_L;
            K[3, 0] = -EA_L;
            K[3, 3] = EA_L;

            // Rigidez de flexión
            K[1, 1] = 12 * EI_L3;
            K[1, 2] = 6 * EI_L2;
            K[1, 4] = -12 * EI_L3;
            K[1, 5] = 6 * EI_L2;

            K[2, 1] = 6 * EI_L2;
            K[2, 2] = 4 * EI_L;
            K[2, 4] = -6 * EI_L2;
            K[2, 5] = 2 * EI_L;

            K[4, 1] = -12 * EI_L3;
            K[4, 2] = -6 * EI_L2;
            K[4, 4] = 12 * EI_L3;
            K[4, 5] = -6 * EI_L2;

            K[5, 1] = 6 * EI_L2;
            K[5, 2] = 2 * EI_L;
            K[5, 4] = -6 * EI_L2;
            K[5, 5] = 4 * EI_L;

            return new Term(K);
        }

        private static Term TriangleArea(Term[] args)
        {
            double x1 = args[0].ToDouble();
            double y1 = args[1].ToDouble();
            double x2 = args[2].ToDouble();
            double y2 = args[3].ToDouble();
            double x3 = args[4].ToDouble();
            double y3 = args[5].ToDouble();

            double area = 0.5 * Math.Abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1));

            return new Term(area);
        }
    }
}
```

### Paso 3: Compilar

```bash
dotnet build -c Release
```

**Resultado:** `MathcadFEMPlugin.dll`

### Paso 4: Instalar en SMath Studio

Copiar la DLL a la carpeta de plugins:

```
C:\Program Files\SMath Studio\plugins\
└── MathcadFEMPlugin.dll
```

O en la carpeta de usuario:

```
%APPDATA%\SMath\plugins\
└── MathcadFEMPlugin.dll
```

### Paso 5: Usar en SMath Studio

Abrir SMath Studio y usar las funciones:

```
E := 200000
A := 0.01
I := 0.0001
L := 5
P := 10000

δ := cantilever_defl(P, L, E, I)

K := fem_beam_K(E, A, I, L)
```

---

## 💡 Ventajas de Usar SMath Studio

### 1. Integración Nativa
```
Tu DLL C# → Plugin de SMath → Funciones nativas
```

No necesitas Python, ctypes, ni workarounds.

### 2. Reutilizar tu Código Existente

Puedes **wrapper** tus DLLs existentes:

```csharp
using System.Runtime.InteropServices;

public class FEMPluginWrapper : IPlugin
{
    // Importar tu DLL existente
    [DllImport("mathcad_fem.dll")]
    private static extern double cantilever_defl_export(double P, double L, double E, double I);

    // Wrappear para SMath
    private static Term CantileverDeflection(Term[] args)
    {
        double P = args[0].ToDouble();
        double L = args[1].ToDouble();
        double E = args[2].ToDouble();
        double I = args[3].ToDouble();

        // Llamar a tu DLL original
        double result = cantilever_defl_export(P, L, E, I);

        return new Term(result);
    }
}
```

### 3. Interfaz Similar a Mathcad

SMath Studio tiene una interfaz muy similar a Mathcad:
- Variables con unidades
- Notación matemática
- Gráficos
- Matrices

---

## 📚 Ejemplos de Extensiones Existentes

### MatrixExtension (del repo que compartiste)

```csharp
// Ejemplo simplificado de MatrixExtension

public class MatrixExtension : IPlugin
{
    public void Initialize()
    {
        // Registrar funciones de matrices
        GlobalFunctions.RegisterFunction("MatInv", MatrixInverse);
        GlobalFunctions.RegisterFunction("MatDet", MatrixDeterminant);
        GlobalFunctions.RegisterFunction("MatEig", MatrixEigenvalues);
    }

    private static Term MatrixInverse(Term[] args)
    {
        Matrix M = args[0].ToMatrix();
        Matrix inv = M.Inverse();
        return new Term(inv);
    }

    // ... más funciones
}
```

### AcadToSMath (del repo que compartiste)

```csharp
// Ejemplo simplificado de AcadToSMath

public class AcadPlugin : IPlugin, IPluginHandleFileTypes
{
    public void Initialize()
    {
        // Registrar tipo de archivo DXF
        FileTypeManager.RegisterFileType("dxf", this);
    }

    public Worksheet LoadFromFile(string filename)
    {
        // Leer archivo DXF
        var dxf = DXFReader.Read(filename);

        // Convertir a worksheet de SMath
        var worksheet = new Worksheet();
        // ... conversión

        return worksheet;
    }
}
```

---

## 🔍 Comparación: Opciones para Usar tus DLLs

### Opción 1: Mathcad Prime (Lo que tienes ahora)

```mathcad
CustomFunctions := [
  ["mathcad_fem.dll" "cantilever_defl" "Function: Invoke4"]
]

δ := cantilever_defl(P, L, E, I)
```

**Ventajas:**
- ✅ Funciona directamente
- ✅ No necesitas modificar nada

**Desventajas:**
- ❌ Mathcad Prime es de pago
- ❌ Licencias caras

### Opción 2: SMath Studio (Nueva opción)

```csharp
// Crear plugin C#
public class FEMPlugin : IPlugin {
    // Wrapper de tu DLL o reimplementación
}
```

Luego en SMath:
```
δ := cantilever_defl(P, L, E, I)
```

**Ventajas:**
- ✅ SMath es gratuito
- ✅ Open source
- ✅ Similar a Mathcad
- ✅ Integración nativa

**Desventajas:**
- ⚠️ Necesitas crear un plugin C#
- ⚠️ Algo de trabajo inicial

### Opción 3: Calcpad + Python (Solución actual)

```calcpad
@{python}
import ctypes
dll = ctypes.CDLL("mathcad_fem.dll")
delta = dll.cantilever_defl_export(...)
@{end python}
```

**Ventajas:**
- ✅ Funciona en Calcpad
- ✅ Gratuito

**Desventajas:**
- ❌ No es integración nativa
- ❌ Requiere Python
- ❌ Salida solo a consola

---

## 🚀 Recomendación para Tu Proyecto

### Si quieres alternativa a Mathcad Prime:

**Usa SMath Studio + Plugin C#**

**Pasos:**

1. **Descargar SMath Studio** (gratuito)
2. **Crear plugin C#** que wrappee tus DLLs existentes
3. **Compilar e instalar** el plugin
4. **Usar** en SMath como funciones nativas

### Template de Plugin para Empezar

```csharp
// MathcadFEMPlugin.cs

using System;
using System.Runtime.InteropServices;
using SMath.Manager;

namespace MathcadFEMPlugin
{
    public class FEMPlugin : IPlugin
    {
        // ================================================================
        // CONFIGURACION DEL PLUGIN
        // ================================================================
        public string Name => "Mathcad FEM Functions";
        public string Description => "Funciones de análisis FEM";
        public string Author => "Tu Nombre";
        public Version Version => new Version(1, 0, 0);

        // ================================================================
        // IMPORTAR TUS DLLs EXISTENTES
        // ================================================================
        [DllImport("mathcad_fem.dll")]
        private static extern double cantilever_defl_export(double P, double L, double E, double I);

        [DllImport("mathcad_fem.dll")]
        private static extern double cantilever_rot_export(double P, double L, double E, double I);

        [DllImport("mathcad_triangle/mathcad_triangle.dll")]
        private static extern double tri_area_export(double x1, double y1, double x2, double y2, double x3, double y3);

        // ================================================================
        // INICIALIZACION
        // ================================================================
        public void Initialize()
        {
            // Registrar funciones en SMath
            GlobalFunctions.RegisterFunction("cantilever_defl", WrapCantileverDefl);
            GlobalFunctions.RegisterFunction("cantilever_rot", WrapCantileverRot);
            GlobalFunctions.RegisterFunction("tri_area", WrapTriArea);
        }

        // ================================================================
        // WRAPPERS (conectan SMath con tus DLLs)
        // ================================================================
        private static Term WrapCantileverDefl(Term[] args)
        {
            try
            {
                double P = args[0].ToDouble();
                double L = args[1].ToDouble();
                double E = args[2].ToDouble();
                double I = args[3].ToDouble();

                double result = cantilever_defl_export(P, L, E, I);

                return new Term(result);
            }
            catch (Exception ex)
            {
                return new Term($"Error: {ex.Message}");
            }
        }

        private static Term WrapCantileverRot(Term[] args)
        {
            double P = args[0].ToDouble();
            double L = args[1].ToDouble();
            double E = args[2].ToDouble();
            double I = args[3].ToDouble();

            double result = cantilever_rot_export(P, L, E, I);

            return new Term(result);
        }

        private static Term WrapTriArea(Term[] args)
        {
            double x1 = args[0].ToDouble();
            double y1 = args[1].ToDouble();
            double x2 = args[2].ToDouble();
            double y2 = args[3].ToDouble();
            double x3 = args[4].ToDouble();
            double y3 = args[5].ToDouble();

            double result = tri_area_export(x1, y1, x2, y2, x3, y3);

            return new Term(result);
        }
    }
}
```

---

## 📖 Recursos Adicionales

### Documentación Oficial
- **API Documentation:** https://smath.com/documentation/api/
- **Forum:** https://en.smath.com/forum/
- **Wiki:** https://en.smath.com/wiki/

### Repositorios de Ejemplo
- **AcadToSMath:** https://github.com/rumata-ap/AcadToSMath
- **MatrixExtension:** https://github.com/rumata-ap/MatrixExtension_SMathStudio
- **Más plugins:** https://en.smath.com/forum/yaf_postst1583_New-Plugins.aspx

### Tutoriales
- Crear tu primer plugin: https://en.smath.com/wiki/GetStart.ashx
- Plugin API Guide: Incluido en SMath Studio

---

## 🎯 Conclusión

SMath Studio es una excelente alternativa gratuita a Mathcad que:

1. ✅ **Soporta plugins en C#** - Puedes wrappear tus DLLs existentes
2. ✅ **Es gratuito y open source** - No necesitas licencias
3. ✅ **Tiene API completa** - Documentación disponible
4. ✅ **Comunidad activa** - Muchos ejemplos de plugins

**Para tu proyecto:**
- Crea un plugin C# que use tus DLLs existentes con `DllImport`
- Instálalo en SMath Studio
- Úsalo como funciones nativas

Es más trabajo inicial que Mathcad Prime, pero obtienes una solución gratuita y totalmente funcional.
