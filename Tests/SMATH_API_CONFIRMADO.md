# ✅ API de SMath Studio - Confirmado

## 📍 Ubicación Confirmada

```
C:\Program Files (x86)\SMath Studio\
```

## 🎯 DLLs de la API Encontradas

```
✅ SMath.Manager.dll          → Gestión de plugins (232 KB)
✅ SMath.Controls.dll          → Controles UI (211 KB)
✅ SMath.Document.dll          → Documentos (289 KB)
✅ SMath.Drawing.dll           → Gráficos (97 KB)
✅ SMath.Environment.dll       → Entorno (92 KB)
✅ SMath.Math.Numeric.dll      → Matemáticas numéricas (127 KB)
✅ SMath.Math.Symbolic.dll     → Matemáticas simbólicas (94 KB)
✅ SMath.UI.dll                → UI principal (154 KB)
✅ SMath.UI.Accessories.dll    → Accesorios UI (654 KB)
```

## 📂 Estructura Confirmada

```
C:\Program Files (x86)\SMath Studio\
├── SMathStudio_Desktop.exe    → Programa principal
│
├── API (DLLs que usas en tu plugin):
├── SMath.Manager.dll          ← Importante para plugins
├── SMath.Controls.dll
├── SMath.Math.Numeric.dll
├── SMath.Math.Symbolic.dll
│
├── plugins\                   → Carpeta de plugins
│   ├── 02f1ab51-...\
│   │   └── MathRegion.dll     → Plugin ejemplo
│   ├── 06b5df04-...\
│   └── ... (10 plugins instalados)
│
├── examples\                  → Ejemplos de uso
├── lang\                      → Traducciones
└── snippets\                  → Snippets de código
```

## 🔧 Cómo Usarla en Visual Studio

### Referenciar en .csproj

```xml
<ItemGroup>
  <Reference Include="SMath.Manager">
    <HintPath>C:\Program Files (x86)\SMath Studio\SMath.Manager.dll</HintPath>
  </Reference>
  <Reference Include="SMath.Math.Numeric">
    <HintPath>C:\Program Files (x86)\SMath Studio\SMath.Math.Numeric.dll</HintPath>
  </Reference>
</ItemGroup>
```

### Usar en código

```csharp
using SMath.Manager;

public class MiPlugin : IPlugin
{
    // La API funciona
}
```

## ✅ Plugins Instalados

Hay **10 plugins** ya instalados en tu SMath Studio. Cada plugin es una DLL en una carpeta con GUID.

**Ejemplo:** `plugins/02f1ab51-215b-466e-a74d-5d8b1cf85e8d/MathRegion.dll`

## 🎯 Para Tu Proyecto

### Crear plugin que use tus DLLs:

```csharp
// MathcadFEMPlugin.cs
using System.Runtime.InteropServices;
using SMath.Manager;

public class FEMPlugin : IPlugin
{
    [DllImport("mathcad_fem.dll")]
    static extern double cantilever_defl_export(double P, double L, double E, double I);

    public void Initialize()
    {
        GlobalFunctions.RegisterFunction("cantilever_defl", WrapFunction);
    }

    static Term WrapFunction(Term[] args)
    {
        double result = cantilever_defl_export(
            args[0].obj.ToDouble(),
            args[1].obj.ToDouble(),
            args[2].obj.ToDouble(),
            args[3].obj.ToDouble()
        );
        return new Term(result);
    }
}
```

### Compilar e instalar:

```bash
# Compilar
dotnet build -c Release

# Copiar a plugins
cp bin/Release/net48/MathcadFEMPlugin.dll "C:/Program Files (x86)/SMath Studio/plugins/mi-plugin/"
```

### Usar en SMath:

```
δ := cantilever_defl(10000, 5, 200000, 0.0001)
```

## ✅ Conclusión

**La API está ahí, lista para usar.**

DLLs principales:
- `SMath.Manager.dll` → Para plugins
- `SMath.Math.Numeric.dll` → Matemáticas

Ya tienes todo lo necesario para crear tu plugin.
