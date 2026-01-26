# ¿Dónde está la API de SMath Studio?

## 🎯 Respuesta Rápida

La API de SMath Studio **viene incluida** cuando instalas SMath Studio.

**Archivos de la API:**
```
C:\Program Files\SMath Studio\
├── SMath.Core.dll          ← API principal
├── SMath.Controls.dll      ← Controles y UI
├── SMath.Math.dll          ← Funciones matemáticas
└── ... más DLLs
```

---

## 📁 Ubicación de los Archivos API

### Windows (Instalación típica)

```
C:\Program Files\SMath Studio\
├── SMathStudio.exe               → Programa principal
│
├── DLLS DE LA API:
├── SMath.Core.dll                → ✅ ESTA es la API principal
├── SMath.Controls.dll            → Controles de UI
├── SMath.Math.dll                → Funciones matemáticas
├── SMath.Manager.dll             → Gestión de plugins
├── SMath.Drawing.dll             → Dibujo y gráficos
│
└── plugins\                      → Carpeta de plugins
    ├── plugin1.dll
    ├── plugin2.dll
    └── ... tus plugins aquí
```

### Carpeta de Usuario (Plugins personales)

```
%APPDATA%\SMath\
├── settings.xml                  → Configuración
└── plugins\                      → Tus plugins personales
    └── MathcadFEMPlugin.dll     → Tu plugin aquí
```

En Windows la ruta completa sería:
```
C:\Users\TuUsuario\AppData\Roaming\SMath\plugins\
```

---

## 🔧 Cómo Usar la API en tu Proyecto

### Paso 1: Instalar SMath Studio

**Descargar:** https://smath.com/en-US/view/SMathStudio/summary

**Instalar** en la ubicación predeterminada:
```
C:\Program Files\SMath Studio\
```

### Paso 2: Crear Proyecto en Visual Studio

**Crear nuevo proyecto:**
```
Archivo → Nuevo → Proyecto
Tipo: Biblioteca de clases (.NET Framework)
Nombre: MathcadFEMPlugin
```

### Paso 3: Referenciar la API de SMath

**En tu proyecto .csproj:**

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net48</TargetFramework>
    <OutputType>Library</OutputType>
  </PropertyGroup>

  <ItemGroup>
    <!-- REFERENCIAR LA API DE SMATH -->
    <Reference Include="SMath.Core">
      <HintPath>C:\Program Files\SMath Studio\SMath.Core.dll</HintPath>
    </Reference>
    <Reference Include="SMath.Manager">
      <HintPath>C:\Program Files\SMath Studio\SMath.Manager.dll</HintPath>
    </Reference>
    <Reference Include="SMath.Math">
      <HintPath>C:\Program Files\SMath Studio\SMath.Math.dll</HintPath>
    </Reference>
  </ItemGroup>
</Project>
```

**O usando Visual Studio GUI:**

1. Click derecho en "Referencias" → "Agregar referencia"
2. Click en "Examinar"
3. Navegar a: `C:\Program Files\SMath Studio\`
4. Seleccionar:
   - `SMath.Core.dll`
   - `SMath.Manager.dll`
   - `SMath.Math.dll`
5. Click "Aceptar"

### Paso 4: Ver las Clases Disponibles

Una vez referenciadas las DLLs, puedes ver la API en Visual Studio:

**En el código:**
```csharp
using SMath.Manager;      // ← Aparecerá con IntelliSense
using SMath.Math;         // ← Aparecerá con IntelliSense

// Ahora puedes usar las clases
public class MiPlugin : IPlugin
{
    // IntelliSense te mostrará todos los métodos y propiedades
}
```

---

## 📖 Documentación de la API

### Online (Web)

**URL:** https://smath.com/documentation/api/

**Namespaces principales:**
- `SMath.Manager` - Gestión de plugins
- `SMath.Math` - Funciones matemáticas
- `SMath.Controls` - Controles de UI
- `SMath.Drawing` - Gráficos

### Offline (Incluida con SMath)

Algunos archivos de ayuda vienen con la instalación:

```
C:\Program Files\SMath Studio\
├── help\
│   ├── en\                       → Ayuda en inglés
│   └── ru\                       → Ayuda en ruso
│
└── Examples\                     → Ejemplos de uso
    ├── example1.sm
    └── ...
```

### Intellisense en Visual Studio

Una vez que referencias las DLLs, **Visual Studio te mostrará la documentación automáticamente**:

```csharp
public class MiPlugin : IPlugin
{
    public void Initialize()
    {
        // Escribir "GlobalFunctions." y presionar Ctrl+Space
        // Visual Studio mostrará todos los métodos disponibles
        GlobalFunctions.  ← IntelliSense aquí
    }
}
```

---

## 🔍 Explorar la API sin Documentación

Si no encuentras documentación completa, puedes explorar las DLLs directamente:

### Opción 1: ILSpy (Recomendado)

**Descargar:** https://github.com/icsharpcode/ILSpy

**Usar:**
1. Abrir ILSpy
2. Arrastrar `SMath.Core.dll`
3. Ver todo el código decompilado
4. Ver todas las clases, métodos, propiedades

**Ejemplo:**
```
SMath.Core.dll
├── SMath.Manager
│   ├── IPlugin                    ← Interfaz para plugins
│   ├── GlobalFunctions            ← Registrar funciones
│   └── ...
├── SMath.Math
│   ├── Term                       ← Tipo de dato matemático
│   ├── Matrix                     ← Matrices
│   └── ...
```

### Opción 2: Visual Studio Object Browser

**En Visual Studio:**
1. Ver → Object Browser (Ctrl+Alt+J)
2. Buscar "SMath.Core"
3. Explorar namespaces y clases

### Opción 3: Reflexión en C#

```csharp
// Listar todos los tipos en SMath.Core.dll
var assembly = Assembly.LoadFrom(@"C:\Program Files\SMath Studio\SMath.Core.dll");
foreach (var type in assembly.GetTypes())
{
    Console.WriteLine(type.FullName);
}
```

---

## 🎓 Interfaces Principales de la API

### IPlugin (Interfaz básica de plugin)

```csharp
public interface IPlugin
{
    string Name { get; }              // Nombre del plugin
    string Description { get; }       // Descripción
    string Author { get; }            // Autor
    Version Version { get; }          // Versión

    void Initialize();                // Inicialización
    void Finalize();                  // Limpieza (opcional)
}
```

### IPluginCustomRegion (Regiones personalizadas)

```csharp
public interface IPluginCustomRegion : IPlugin
{
    RegionBase CreateRegion();        // Crear nueva región
    string RegionTypeName { get; }    // Nombre del tipo
}
```

### IPluginMenuExtender (Extender menús)

```csharp
public interface IPluginMenuExtender : IPlugin
{
    MenuItem[] GetMenuItems();        // Devolver items de menú
}
```

### GlobalFunctions (Registrar funciones)

```csharp
public static class GlobalFunctions
{
    public static void RegisterFunction(string name, Func<Term[], Term> function);
    public static void UnregisterFunction(string name);
    // ... más métodos
}
```

---

## 💻 Ejemplo Completo de Uso de la API

```csharp
// MathcadFEMPlugin.cs

using System;
using System.Runtime.InteropServices;
using SMath.Manager;        // ← De SMath.Manager.dll
using SMath.Math;           // ← De SMath.Math.dll

namespace MathcadFEMPlugin
{
    // Implementar IPlugin (viene de SMath.Manager.dll)
    public class FEMPlugin : IPlugin
    {
        // ================================================================
        // PROPIEDADES DEL PLUGIN (de IPlugin)
        // ================================================================
        public string Name => "Mathcad FEM Functions";
        public string Description => "Funciones de análisis FEM para vigas y placas";
        public string Author => "Tu Nombre";
        public Version Version => new Version(1, 0, 0);

        // ================================================================
        // IMPORTAR TUS DLLs EXISTENTES
        // ================================================================
        [DllImport("mathcad_fem.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern double cantilever_defl_export(double P, double L, double E, double I);

        // ================================================================
        // INICIALIZAR (de IPlugin)
        // ================================================================
        public void Initialize()
        {
            // Registrar función en SMath usando GlobalFunctions (de SMath.Manager)
            GlobalFunctions.RegisterFunction("cantilever_defl", CantileverDefl);

            Console.WriteLine("[FEM Plugin] Inicializado correctamente");
        }

        public void Finalize()
        {
            // Limpieza (opcional)
            GlobalFunctions.UnregisterFunction("cantilever_defl");
        }

        // ================================================================
        // WRAPPER DE LA FUNCION
        // ================================================================
        private static Term CantileverDefl(Term[] args)
        {
            // Term es un tipo de SMath.Math.dll
            try
            {
                // Convertir Term a double
                double P = args[0].obj.ToDouble();
                double L = args[1].obj.ToDouble();
                double E = args[2].obj.ToDouble();
                double I = args[3].obj.ToDouble();

                // Llamar a tu DLL
                double result = cantilever_defl_export(P, L, E, I);

                // Convertir resultado a Term
                return new Term(result, TermType.Scalar);
            }
            catch (Exception ex)
            {
                // Manejar error
                return new Term($"Error: {ex.Message}", TermType.Text);
            }
        }
    }
}
```

**Compilar:**
```bash
dotnet build -c Release
```

**Resultado:**
```
bin\Release\net48\MathcadFEMPlugin.dll
```

**Instalar:**
Copiar a:
```
C:\Program Files\SMath Studio\plugins\MathcadFEMPlugin.dll
```

O:
```
%APPDATA%\SMath\plugins\MathcadFEMPlugin.dll
```

**Usar en SMath:**
```
P := 10000
L := 5
E := 200000
I := 0.0001

δ := cantilever_defl(P, L, E, I)
```

---

## 📋 Checklist de Instalación

### ✅ Paso 1: Instalar SMath Studio
- [ ] Descargar de https://smath.com/
- [ ] Instalar en `C:\Program Files\SMath Studio\`
- [ ] Verificar que exista `SMath.Core.dll`

### ✅ Paso 2: Crear Proyecto Visual Studio
- [ ] Crear proyecto "Biblioteca de clases (.NET Framework)"
- [ ] Target Framework: .NET Framework 4.8

### ✅ Paso 3: Referenciar API
- [ ] Agregar referencia a `SMath.Core.dll`
- [ ] Agregar referencia a `SMath.Manager.dll`
- [ ] Agregar referencia a `SMath.Math.dll`

### ✅ Paso 4: Verificar IntelliSense
- [ ] Escribir `using SMath.Manager;`
- [ ] Verificar que aparezca IntelliSense
- [ ] Escribir `IPlugin` y verificar que exista

### ✅ Paso 5: Implementar Plugin
- [ ] Crear clase que implemente `IPlugin`
- [ ] Implementar método `Initialize()`
- [ ] Registrar funciones con `GlobalFunctions.RegisterFunction()`

### ✅ Paso 6: Compilar
- [ ] Build → Release
- [ ] Verificar que se crea la DLL

### ✅ Paso 7: Instalar Plugin
- [ ] Copiar DLL a carpeta de plugins
- [ ] Reiniciar SMath Studio
- [ ] Verificar que aparezca en lista de plugins

### ✅ Paso 8: Probar
- [ ] Abrir SMath Studio
- [ ] Usar la función registrada
- [ ] Verificar resultado

---

## 🔧 Troubleshooting

### "No encuentro SMath.Core.dll"

**Solución:**
```bash
# Buscar en:
C:\Program Files\SMath Studio\SMath.Core.dll
C:\Program Files (x86)\SMath Studio\SMath.Core.dll

# Si no está, reinstalar SMath Studio
```

### "No aparece IntelliSense"

**Solución:**
1. Verificar que la referencia esté agregada
2. Click derecho en referencia → Propiedades → "Copia local" = True
3. Limpiar y recompilar proyecto

### "Plugin no se carga en SMath"

**Solución:**
1. Verificar que la DLL esté en la carpeta correcta
2. Verificar que el Target Framework sea compatible (.NET 4.8)
3. Ver log de SMath: Herramientas → Ver log

### "Error al llamar función de DLL externa"

**Solución:**
1. Verificar que `mathcad_fem.dll` esté en la misma carpeta que el plugin
2. O copiarla a `C:\Program Files\SMath Studio\`
3. Verificar arquitectura (x64 vs x86)

---

## 🎯 Resumen

**La API de SMath Studio:**
- ✅ Viene incluida con la instalación
- ✅ Está en: `C:\Program Files\SMath Studio\SMath.Core.dll`
- ✅ Se referencia en tu proyecto C#
- ✅ Documentación online: https://smath.com/documentation/api/
- ✅ IntelliSense en Visual Studio funciona

**Para crear un plugin:**
1. Instalar SMath Studio
2. Crear proyecto C# en Visual Studio
3. Referenciar `SMath.Core.dll` y otras DLLs
4. Implementar `IPlugin`
5. Compilar y copiar a carpeta de plugins
6. Reiniciar SMath Studio

**No necesitas descargar la API por separado** - ya viene con SMath Studio.
