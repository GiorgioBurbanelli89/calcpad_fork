# SMath Studio API - Capacidades y Límites

## 🎯 ¿Qué Puedes Hacer con la API de SMath Studio?

### Resumen
La API de SMath Studio te permite crear **plugins/extensiones** que modifican o amplían el comportamiento del programa.

---

## 📋 Interfaces Disponibles (Lo que puedes hacer)

### 1. **IPluginLowLevelEvaluationFast**
**Interceptar operadores y funciones matemáticas**

**¿Qué hace?**
- Intercepta operaciones básicas (+, -, *, /, ^, etc.)
- Intercepta funciones (sin, cos, sqrt, etc.)
- Permite redefinir cómo se evalúan

**Ejemplo de uso:**
```csharp
public class MiPluginEvaluacion : IPluginLowLevelEvaluationFast
{
    public bool EvaluateFast(string funcName, ref Term result, params Term[] args)
    {
        // Interceptar la función "sin"
        if (funcName == "sin")
        {
            // Tu implementación personalizada
            double value = args[0].obj.ToDouble();
            result = new Term(Math.Sin(value));
            return true; // Ya manejado
        }
        return false; // Dejar que SMath lo maneje
    }
}
```

**Capacidades:**
- ✅ Agregar nuevas funciones matemáticas
- ✅ Sobrescribir funciones existentes
- ✅ Optimizar cálculos específicos
- ✅ Agregar funciones de DLLs externas

**Tu caso de uso:** ⭐⭐⭐⭐⭐
```csharp
// Agregar tus funciones FEM
if (funcName == "cantilever_defl")
{
    result = CallYourDLL(args);
    return true;
}
```

---

### 2. **IPluginMathNumericEvaluation**
**Interceptar cálculos numéricos**

**¿Qué hace?**
- Intercepta evaluación numérica de expresiones
- Permite cálculos especializados
- Control sobre precisión numérica

**Ejemplo de uso:**
```csharp
public class CalculadoraEspecial : IPluginMathNumericEvaluation
{
    public bool EvaluateNumeric(Entry entry, ref Store result)
    {
        // Interceptar cálculos específicos
        if (entry.Type == EntryType.Equation)
        {
            // Tu lógica de evaluación
            return true;
        }
        return false;
    }
}
```

**Capacidades:**
- ✅ Cálculos de alta precisión personalizados
- ✅ Integración con bibliotecas numéricas externas
- ✅ Optimizaciones específicas del dominio

**Tu caso de uso:** ⭐⭐⭐
```csharp
// Cálculos FEM especializados
// Integración con solvers externos
```

---

### 3. **IPluginCustomRegion**
**Crear regiones/elementos personalizados en la hoja**

**¿Qué hace?**
- Crea nuevos tipos de regiones en el documento
- Como regiones de texto, ecuaciones, gráficos, etc.
- Pero personalizadas

**Ejemplo de uso:**
```csharp
public class MiRegionPersonalizada : IPluginCustomRegion
{
    public RegionBase CreateRegion()
    {
        return new FEMVisualizerRegion();
    }

    public string RegionTypeName => "FEM Visualizer";
}

public class FEMVisualizerRegion : RegionBase
{
    // Define cómo se dibuja, edita, guarda, etc.
}
```

**Capacidades:**
- ✅ Widgets interactivos en la hoja
- ✅ Visualizadores de datos personalizados
- ✅ Controles especiales
- ✅ Gráficos 3D personalizados

**Tu caso de uso:** ⭐⭐⭐⭐
```csharp
// Región que muestra malla FEM
// Región que muestra diagrama de viga
// Región interactiva para definir geometría
```

---

### 4. **IPluginRegionDrawing**
**Interceptar el dibujo de fórmulas matemáticas**

**¿Qué hace?**
- Controla cómo se dibujan elementos en fórmulas
- Personaliza la visualización

**Ejemplo de uso:**
```csharp
public class MiRenderizador : IPluginRegionDrawing
{
    public void DrawFormula(Graphics g, Entry entry, Rectangle bounds)
    {
        // Dibujar fórmula con estilo personalizado
    }
}
```

**Capacidades:**
- ✅ Sintaxis highlighting personalizada
- ✅ Notación matemática especial
- ✅ Símbolos personalizados

**Tu caso de uso:** ⭐⭐
```csharp
// Resaltar variables FEM
// Notación especial para matrices de rigidez
```

---

### 5. **IPluginSaveFileTypes**
**Guardar en formatos personalizados**

**¿Qué hace?**
- Exportar a formatos de archivo personalizados
- Guardar datos en formatos especiales

**Ejemplo de uso:**
```csharp
public class ExportadorFEM : IPluginSaveFileTypes
{
    public string[] GetSupportedFileTypes()
    {
        return new[] { ".fem", ".inp", ".dat" };
    }

    public void SaveToFile(Worksheet worksheet, string filename)
    {
        // Exportar a formato FEM
    }
}
```

**Capacidades:**
- ✅ Exportar a formatos CAD (DXF, STL)
- ✅ Exportar a formatos FEM (ANSYS, ABAQUS)
- ✅ Exportar a Excel, JSON, XML
- ✅ Exportar a formatos personalizados

**Tu caso de uso:** ⭐⭐⭐⭐⭐
```csharp
// Exportar a formato SAP2000
// Exportar a ANSYS APDL
// Exportar a CalculiX
```

---

### 6. **IPluginOpenFileTypes**
**Abrir/Importar formatos personalizados**

**¿Qué hace?**
- Leer archivos de formatos externos
- Importar datos a SMath

**Ejemplo de uso:**
```csharp
public class ImportadorFEM : IPluginOpenFileTypes
{
    public string[] GetSupportedFileTypes()
    {
        return new[] { ".fem", ".inp" };
    }

    public Worksheet OpenFromFile(string filename)
    {
        // Leer archivo FEM y convertir a worksheet de SMath
        var worksheet = new Worksheet();
        // ... parsear archivo y crear regiones
        return worksheet;
    }
}
```

**Capacidades:**
- ✅ Importar desde CAD (DXF, DWG)
- ✅ Importar desde Excel
- ✅ Importar desde archivos FEM
- ✅ Importar desde formatos propietarios

**Tu caso de uso:** ⭐⭐⭐⭐
```csharp
// Importar modelo SAP2000
// Importar malla desde CAD
// Importar resultados de análisis
```

---

### 7. **IPluginDataInputOutput**
**Personalizar entrada/salida de datos**

**¿Qué hace?**
- Interfaz para automatización
- Integración con otros programas
- APIs externas

**Ejemplo de uso:**
```csharp
public class IntegracionExterna : IPluginDataInputOutput
{
    public void ImportData(Worksheet worksheet, string source)
    {
        // Importar desde API, base de datos, etc.
    }

    public void ExportData(Worksheet worksheet, string destination)
    {
        // Exportar a API, base de datos, etc.
    }
}
```

**Capacidades:**
- ✅ Conexión a bases de datos
- ✅ APIs REST
- ✅ Automatización con otros programas
- ✅ Integración con sistemas externos

**Tu caso de uso:** ⭐⭐⭐
```csharp
// Conexión a base de datos de materiales
// API para compartir cálculos
// Integración con SAP2000 API
```

---

## 🎨 Ejemplos de Plugins Reales (del ecosistema SMath)

### Plugins Matemáticos
- **Maxima Plugin** - Integración con sistema de álgebra computacional
- **Matrix Extension** - Operaciones matriciales avanzadas
- **Statistics Plugin** - Funciones estadísticas

### Plugins de I/O
- **Excel Plugin** - Importar/exportar Excel
- **XML Plugin** - Leer/escribir XML
- **Files Plugin** - Manejo de archivos

### Plugins Gráficos
- **Chart Plugin** - Gráficos avanzados
- **3D Plot Plugin** - Gráficos 3D
- **Drawing Plugin** - Herramientas de dibujo

### Plugins de Integración
- **AutoCAD Plugin** - Importar DXF
- **Python Plugin** - Ejecutar Python
- **Database Plugin** - Conexión a BD

---

## 💡 Qué Puedes Hacer para Tu Proyecto FEM

### Opción 1: Plugin de Funciones (Más Simple)
```csharp
public class FEMFunctions : IPluginLowLevelEvaluationFast
{
    [DllImport("mathcad_fem.dll")]
    static extern double cantilever_defl_export(double P, double L, double E, double I);

    public bool EvaluateFast(string funcName, ref Term result, params Term[] args)
    {
        if (funcName == "cantilever_defl")
        {
            double P = args[0].obj.ToDouble();
            double L = args[1].obj.ToDouble();
            double E = args[2].obj.ToDouble();
            double I = args[3].obj.ToDouble();

            double delta = cantilever_defl_export(P, L, E, I);
            result = new Term(delta);
            return true;
        }

        // Más funciones FEM...

        return false;
    }
}
```

**Usar en SMath:**
```
P := 10000
L := 5
E := 200000
I := 0.0001

δ := cantilever_defl(P, L, E, I)
```

### Opción 2: Plugin de Visualización FEM
```csharp
public class FEMVisualizer : IPluginCustomRegion
{
    public RegionBase CreateRegion()
    {
        return new BeamDiagramRegion();
    }
}

public class BeamDiagramRegion : RegionBase
{
    // Región que dibuja diagrama de momento/cortante
    public override void Draw(Graphics g, Rectangle bounds)
    {
        // Dibujar viga con carga, diagrama de momentos, etc.
    }
}
```

**Usar en SMath:**
```
Insertar → Región FEM → Beam Diagram
```

### Opción 3: Plugin de Exportación
```csharp
public class SAP2000Exporter : IPluginSaveFileTypes
{
    public string[] GetSupportedFileTypes()
    {
        return new[] { ".s2k" };
    }

    public void SaveToFile(Worksheet worksheet, string filename)
    {
        // Exportar cálculos a formato SAP2000
        var s2kContent = ConvertToSAP2000(worksheet);
        File.WriteAllText(filename, s2kContent);
    }
}
```

**Usar en SMath:**
```
Archivo → Exportar → SAP2000 (.s2k)
```

---

## ⚠️ Límites de la API

### Límites Técnicos

#### 1. **Framework .NET**
- ✅ Requiere .NET Framework 2.0 o superior
- ⚠️ No .NET Core nativo (pero funciona con .NET Framework)
- ✅ Compatible con C#, VB.NET, F#

#### 2. **Compatibilidad Multiplataforma**
- ✅ Windows - Totalmente soportado
- ⚠️ Linux - Funciona con Mono, algunas limitaciones
- ⚠️ Android - API limitada

**Recomendación:** Usar SMath.Drawing library para máxima compatibilidad.

#### 3. **Acceso al Sistema**
- ✅ Puedes usar DLLs externas (DllImport)
- ✅ Acceso a sistema de archivos
- ✅ Acceso a red/internet
- ⚠️ Algunos plugins requieren permisos especiales

#### 4. **Rendimiento**
- ✅ Plugins compilados = rápidos
- ⚠️ Cálculos muy pesados pueden bloquear UI
- ✅ Puedes usar threads para cálculos largos

### Límites Funcionales

#### 1. **No Puedes:**
- ❌ Modificar el core de SMath Studio directamente
- ❌ Cambiar la sintaxis del lenguaje base
- ❌ Acceder a regiones privadas de otras extensiones
- ❌ Sobrescribir completamente el motor de cálculo

#### 2. **Sí Puedes:**
- ✅ Agregar funciones ilimitadas
- ✅ Crear tipos de regiones personalizadas
- ✅ Importar/exportar cualquier formato
- ✅ Integrar con cualquier sistema externo
- ✅ Usar bibliotecas externas (DLLs, NuGet)

### Límites de Distribución

#### 1. **Licenciamiento**
- ✅ SMath Studio es gratuito
- ✅ Puedes crear plugins comerciales
- ✅ Puedes crear plugins gratuitos
- ⚠️ Debes respetar licencias de bibliotecas que uses

#### 2. **Instalación**
- ✅ Instalación manual (copiar DLL)
- ✅ Plugin Store de SMath (oficial)
- ✅ Instaladores personalizados
- ⚠️ Algunos plugins necesitan dependencias extras

---

## 📊 Comparación: SMath Studio vs Otros

| Característica | SMath Studio | Mathcad Prime | MATLAB |
|----------------|--------------|---------------|--------|
| **API Abierta** | ✅ Completa | ⚠️ Limitada | ✅ Completa |
| **Crear Funciones** | ✅ Sí | ✅ Sí (CustomFunctions) | ✅ Sí |
| **Crear Regiones Custom** | ✅ Sí | ❌ No | ✅ Sí (GUI) |
| **Importar/Exportar** | ✅ Sí | ⚠️ Limitado | ✅ Sí |
| **Costo** | ✅ Gratis | ❌ Pago | ❌ Pago |
| **Open Source** | ✅ Sí | ❌ No | ❌ No |

---

## 🚀 Recomendación para Tu Proyecto

### Plugin Recomendado para Mathcad FEM Functions

**Tipo:** IPluginLowLevelEvaluationFast

**Estructura:**
```
MathcadFEMPlugin/
├── MathcadFEMPlugin.csproj
├── FEMPlugin.cs                    → Plugin principal
├── FunctionWrappers.cs             → Wrappers de tus DLLs
├── mathcad_fem.dll                 → Tu DLL existente
├── mathcad_triangle.dll            → Tu DLL existente
└── mathcad_plate.dll               → Tu DLL existente
```

**Capacidades que obtienes:**
- ✅ Todas tus funciones FEM disponibles en SMath
- ✅ Sintaxis similar a Mathcad
- ✅ Sin necesidad de Mathcad Prime (gratuito)
- ✅ Compatible con tus DLLs existentes
- ✅ Puedes distribuirlo a otros usuarios

**Esfuerzo:** 2-4 horas de desarrollo

**Complejidad:** ⭐⭐ Media

---

## 📚 Recursos

### Documentación
- **Plugin API:** https://smath.com/documentation/api/
- **All Plugins:** https://smath.com/documentation/api/AllExtensions_EN.htm
- **Wiki:** https://wiki.smath.com/en-US/Plugins
- **Forum:** https://smath.com/en-US/forum/

### Ejemplos
- **How to create plugins:** https://smath.com/en-US/forum/topic/Nry48r/How-to-create-plugins-for-SMath-Studio
- **Plugin register:** https://smath.com/files/Download/LMgg9/All%20SMath%20Studio%20plugins.pdf
- **Matrix Extension:** https://github.com/rumata-ap/MatrixExtension_SMathStudio
- **AcadToSMath:** https://github.com/rumata-ap/AcadToSMath

---

## ✅ Conclusión

### Lo que SÍ puedes hacer:
- ✅ Agregar funciones matemáticas personalizadas (tus DLLs FEM)
- ✅ Crear visualizadores personalizados (diagramas, mallas)
- ✅ Importar/exportar formatos personalizados (SAP2000, ANSYS)
- ✅ Integrar con sistemas externos (bases de datos, APIs)
- ✅ Crear regiones interactivas personalizadas
- ✅ Optimizar cálculos específicos
- ✅ Distribuir tu plugin a otros usuarios

### Lo que NO puedes hacer:
- ❌ Modificar el lenguaje base de SMath
- ❌ Cambiar el core del motor de cálculo
- ❌ Acceso completo a internals privados

### Para tu proyecto específico:

**La API de SMath Studio es PERFECTA para:**
- ✅ Usar tus DLLs de Mathcad (cantilever_defl, fem_beam_K, etc.)
- ✅ Crear alternativa gratuita a Mathcad Prime
- ✅ Distribuir tus funciones FEM a otros ingenieros
- ✅ Integrar con SAP2000 y otros software

**El límite es tu imaginación** (y .NET Framework).

---

**Sources:**
- [All SMath Studio plugins](https://smath.com/documentation/api/AllExtensions_EN.htm)
- [Plugins - SMath Wiki](https://wiki.smath.com/en-US/Plugins)
- [How to create plugins for SMath Studio](https://smath.com/en-US/forum/topic/Nry48r/How-to-create-plugins-for-SMath-Studio)
- [Engineering Calculation Limitations of SMath?](https://smath.com/en-US/forum/topic/c4dDyC/Engineering-Calculation-Limitations-of-SMath_)
