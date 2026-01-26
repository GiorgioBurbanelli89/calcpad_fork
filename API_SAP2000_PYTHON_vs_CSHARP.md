# SAP2000 API: C# vs Python - Guía Completa

## Respuesta a tu pregunta: ¿Si tengo API C#, puedo hacer API Python?

**SÍ, ABSOLUTAMENTE.** Si tienes acceso a la API de C#, puedes usarla desde Python.

### ¿Por qué?

SAP2000 expone su API a través de **COM/OLE Automation**, que es independiente del lenguaje. Tanto C# como Python acceden a la MISMA API subyacente, solo que de diferentes maneras.

---

## Dos Formas de Usar SAP2000 API en Python

Según la documentación oficial (CSI_OAPI_Documentation.chm), hay DOS métodos:

### 1. **Python con comtypes** (Example 7)
- Usa `comtypes` para acceder a la API COM
- Más similar a VBA/VBScript
- Acceso directo a COM

### 2. **Python.NET (pythonnet)** (Example 8) ⭐ RECOMENDADO
- Usa `pythonnet` (`clr`)
- Accede a las DLLs .NET de SAP2000
- MÁS ROBUSTO y MODERNO
- **Prácticamente idéntico a C#**

---

## Comparación: C# vs Python.NET

### Arquitectura

```
┌─────────────────────────────────────────┐
│          SAP2000 Aplicación             │
└────────────────┬────────────────────────┘
                 │
        ┌────────▼────────┐
        │  SAP2000v1.dll  │  ← DLL .NET
        └────────┬────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼────┐            ┌───────▼─────┐
│   C#   │            │ Python.NET  │
│        │            │   (clr)     │
└────────┘            └─────────────┘
```

### Conversión C# → Python.NET

**C# Example**:
```csharp
using SAP2000v1;

// Create helper
var helper = new Helper();
var mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject");
mySapObject.ApplicationStart();

// Get model
var SapModel = mySapObject.SapModel;

// Set material
SapModel.PropMaterial.SetMaterial("CONC", 2);
SapModel.PropMaterial.SetMPIsotropic("CONC", 3600, 0.2, 0.0000055);

// Add frame
string frameName = "";
SapModel.FrameObj.AddByCoord(0, 0, 0, 0, 0, 10, ref frameName, "R1", "1");
```

**Python.NET Equivalente**:
```python
import clr

# Agregar referencia a DLL
clr.AddReference(R'C:\Program Files\Computers and Structures\SAP2000 24\SAP2000v1.dll')
from SAP2000v1 import *

# Create helper
helper = cHelper(Helper())
mySAPObject = cOAPI(helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject"))
mySAPObject.ApplicationStart()

# Get model
SapModel = cSapModel(mySAPObject.SapModel)

# Set material
PropMaterial = cPropMaterial(SapModel.PropMaterial)
ret = PropMaterial.SetMaterial('CONC', 2)
ret = PropMaterial.SetMPIsotropic('CONC', 3600, 0.2, 0.0000055)

# Add frame
FrameObj = cFrameObj(SapModel.FrameObj)
FrameName = ' '
[ret, FrameName] = FrameObj.AddByCoord(0, 0, 0, 0, 0, 10, FrameName, 'R1', '1', 'Global')
```

### Diferencias Clave

| Aspecto | C# | Python.NET |
|---------|----|-----------|
| **Importar DLL** | `using SAP2000v1;` | `clr.AddReference(...)`<br>`from SAP2000v1 import *` |
| **Crear objetos** | `new Helper()` | `cHelper(Helper())` |
| **Wrappers** | No necesarios | `cSapModel()`, `cFrameObj()`, etc. |
| **Parámetros ref** | `ref frameName` | `[ret, FrameName] = ...` (retorna tuple) |
| **Sintaxis general** | C# estándar | Muy similar a C# |

---

## Por Qué Puede NO Funcionar Tu Python API

### Problema 1: Usando `comtypes` en lugar de `pythonnet`

Si tus scripts usan:
```python
import comtypes.client
mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
```

**Problemas comunes**:
- Requiere que SAP2000 ya esté abierto
- Puede fallar si no está registrado en COM
- Menos estable que pythonnet

### Problema 2: Versión incorrecta de SAP2000

Tus scripts referencian:
```python
# En pythonnet:
clr.AddReference(R'C:\Program Files\Computers and Structures\SAP2000 22\SAP2000v1.dll')
```

Verifica la ruta correcta. Para SAP2000 v24:
```python
clr.AddReference(R'C:\Program Files\Computers and Structures\SAP2000 24\SAP2000v1.dll')
```

### Problema 3: pythonnet no instalado

```bash
python -m pip install pythonnet
```

**IMPORTANTE**: pythonnet requiere Python **3.4-3.8** (no funciona con Python 3.9+)

### Problema 4: Sintaxis incorrecta de wrappers

En Python.NET debes usar los wrappers `cXXX`:
```python
# ❌ INCORRECTO
SapModel = mySAPObject.SapModel

# ✅ CORRECTO
SapModel = cSapModel(mySAPObject.SapModel)
```

---

## Ejemplo Funcional: C# vs Python.NET

### C# - Crear Losa Rectangular

```csharp
using System;
using SAP2000v1;

class Program
{
    static void Main()
    {
        // Initialize
        var helper = new Helper();
        var sapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject");
        sapObject.ApplicationStart();
        var model = sapObject.SapModel;

        // Units: kN, m, C
        model.InitializeNewModel(6);
        model.File.NewBlank();

        // Material
        model.PropMaterial.SetMaterial("CONC", 2);
        model.PropMaterial.SetMPIsotropic("CONC", 35000000, 0.15, 0.0000099);

        // Shell property (Plate-Thick)
        model.PropArea.SetShell_1("LOSA", 5, false, "CONC", 0, 0.1, 0.1, 0, "", "");

        // Add point
        model.PointObj.AddCartesian(0, 0, 0, "1");

        // Add area by coordinates
        double[] x = {0, 1, 1, 0};
        double[] y = {0, 0, 1, 1};
        double[] z = {0, 0, 0, 0};
        string name = "";
        model.AreaObj.AddByCoord(4, ref x, ref y, ref z, ref name, "LOSA", "A1");

        // Restraint
        bool[] restraint = {true, true, true, false, false, true};
        model.PointObj.SetRestraint("1", ref restraint);

        // Load
        model.AreaObj.SetLoadUniform("A1", "Dead", 10, 6, true, "Global", 0);

        // Analyze
        model.Analyze.RunAnalysis();

        // Results
        int numResults = 0;
        string[] obj = null;
        string[] elm = null;
        string[] loadCase = null;
        string[] stepType = null;
        double[] stepNum = null;
        double[] u1 = null, u2 = null, u3 = null;
        double[] r1 = null, r2 = null, r3 = null;

        model.Results.Setup.SetCaseSelectedForOutput("Dead");
        model.Results.JointDispl("1", 0, ref numResults, ref obj, ref elm,
                                 ref loadCase, ref stepType, ref stepNum,
                                 ref u1, ref u2, ref u3, ref r1, ref r2, ref r3);

        Console.WriteLine($"Desplazamiento U3: {u3[0] * 1000} mm");

        // Save
        model.File.Save(@"C:\temp\model.sdb");

        // Close
        sapObject.ApplicationExit(false);
    }
}
```

### Python.NET - Equivalente Exacto

```python
import os
import clr

# Agregar referencia a SAP2000v1.dll
clr.AddReference(R'C:\Program Files\Computers and Structures\SAP2000 24\SAP2000v1.dll')
from SAP2000v1 import *

# Initialize
helper = cHelper(Helper())
mySAPObject = cOAPI(helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject"))
mySAPObject.ApplicationStart()
SapModel = cSapModel(mySAPObject.SapModel)

# Units: kN, m, C
SapModel.InitializeNewModel(6)
File = cFile(SapModel.File)
File.NewBlank()

# Material
PropMaterial = cPropMaterial(SapModel.PropMaterial)
PropMaterial.SetMaterial('CONC', 2)
PropMaterial.SetMPIsotropic('CONC', 35000000, 0.15, 0.0000099)

# Shell property (Plate-Thick)
PropArea = cPropArea(SapModel.PropArea)
PropArea.SetShell_1('LOSA', 5, False, 'CONC', 0, 0.1, 0.1, 0, '', '')

# Add point
PointObj = cPointObj(SapModel.PointObj)
PointObj.AddCartesian(0, 0, 0, '1')

# Add area by coordinates
x = [0, 1, 1, 0]
y = [0, 0, 1, 1]
z = [0, 0, 0, 0]
name = ''
AreaObj = cAreaObj(SapModel.AreaObj)
[ret, name] = AreaObj.AddByCoord(4, x, y, z, name, 'LOSA', 'A1')

# Restraint
restraint = [True, True, True, False, False, True]
PointObj.SetRestraint('1', restraint)

# Load
AreaObj.SetLoadUniform('A1', 'Dead', 10, 6, True, 'Global', 0)

# Analyze
Analyze = cAnalyze(SapModel.Analyze)
Analyze.RunAnalysis()

# Results
Results = cAnalysisResults(SapModel.Results)
Setup = cAnalysisResultsSetup(Results.Setup)
Setup.SetCaseSelectedForOutput('Dead')

NumberResults = 0
Obj = []
Elm = []
ACase = []
StepType = []
StepNum = []
U1 = []
U2 = []
U3 = []
R1 = []
R2 = []
R3 = []
ObjectElm = 0

[ret, NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3] = \
    Results.JointDispl('1', ObjectElm, NumberResults, Obj, Elm, ACase, StepType,
                       StepNum, U1, U2, U3, R1, R2, R3)

print(f"Desplazamiento U3: {U3[0] * 1000} mm")

# Save
File.Save(R'C:\temp\model.sdb')

# Close
mySAPObject.ApplicationExit(False)
```

---

## Cómo Convertir Tu Código Actual a Python.NET

### Script Actual (comtypes) - sap2000_rectangular_slab.py

```python
import comtypes.client

# Conectar a SAP2000
mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

# Inicializar
SapModel.InitializeNewModel(6)
SapModel.File.NewBlank()

# Material
SapModel.PropMaterial.SetMaterial("CONC", 2)
SapModel.PropMaterial.SetMPIsotropic("CONC", E, nu, 0.0, G)
```

### Versión Corregida (pythonnet)

```python
import clr

# Agregar referencia
clr.AddReference(R'C:\Program Files\Computers and Structures\SAP2000 24\SAP2000v1.dll')
from SAP2000v1 import *

# Crear helper
helper = cHelper(Helper())

# Opción 1: Conectar a instancia existente
try:
    mySAPObject = cOAPI(helper.GetObject("CSI.SAP2000.API.SAPObject"))
except:
    # Opción 2: Crear nueva instancia
    mySAPObject = cOAPI(helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject"))
    mySAPObject.ApplicationStart()

SapModel = cSapModel(mySAPObject.SapModel)

# Inicializar
SapModel.InitializeNewModel(6)
File = cFile(SapModel.File)
File.NewBlank()

# Material
PropMaterial = cPropMaterial(SapModel.PropMaterial)
PropMaterial.SetMaterial("CONC", 2)
E = 35000000  # kPa
nu = 0.15
PropMaterial.SetMPIsotropic("CONC", E, nu, 0.0000099)
```

---

## Checklist para Hacer Funcionar la API

### ✅ Paso 1: Instalar pythonnet

```bash
# Verificar versión de Python (debe ser 3.4-3.8)
python --version

# Si tienes Python 3.9+, instala Python 3.8
# Descargar de python.org

# Instalar pythonnet
python -m pip install pythonnet
```

### ✅ Paso 2: Localizar SAP2000v1.dll

```bash
# Buscar el archivo
dir "C:\Program Files\Computers and Structures\" /s /b | findstr SAP2000v1.dll
```

Ejemplo de rutas:
- `C:\Program Files\Computers and Structures\SAP2000 24\SAP2000v1.dll`
- `C:\Program Files\Computers and Structures\SAP2000 23\SAP2000v1.dll`

### ✅ Paso 3: Crear script de prueba

Guardar como `test_sap2000_api.py`:

```python
import clr
import sys

# Ruta a SAP2000v1.dll (AJUSTAR SEGÚN TU INSTALACIÓN)
dll_path = R'C:\Program Files\Computers and Structures\SAP2000 24\SAP2000v1.dll'

try:
    clr.AddReference(dll_path)
    print("✓ DLL cargada correctamente")
except Exception as e:
    print(f"✗ Error cargando DLL: {e}")
    sys.exit(1)

try:
    from SAP2000v1 import *
    print("✓ SAP2000v1 importado correctamente")
except Exception as e:
    print(f"✗ Error importando SAP2000v1: {e}")
    sys.exit(1)

try:
    helper = cHelper(Helper())
    print("✓ Helper creado correctamente")
except Exception as e:
    print(f"✗ Error creando Helper: {e}")
    sys.exit(1)

try:
    # Intentar conectar a instancia existente
    mySAPObject = cOAPI(helper.GetObject("CSI.SAP2000.API.SAPObject"))
    print("✓ Conectado a SAP2000 existente")
except:
    try:
        # Crear nueva instancia
        mySAPObject = cOAPI(helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject"))
        mySAPObject.ApplicationStart()
        print("✓ Nueva instancia de SAP2000 creada")
    except Exception as e:
        print(f"✗ Error creando SAP2000: {e}")
        sys.exit(1)

try:
    SapModel = cSapModel(mySAPObject.SapModel)
    version = SapModel.GetVersion()
    print(f"✓ SAP2000 versión: {version[0]}")
    print("\n¡API funcionando correctamente!")

    # Cerrar
    mySAPObject.ApplicationExit(False)
except Exception as e:
    print(f"✗ Error accediendo a SapModel: {e}")
    sys.exit(1)
```

### ✅ Paso 4: Ejecutar

```bash
python test_sap2000_api.py
```

**Salida esperada**:
```
✓ DLL cargada correctamente
✓ SAP2000v1 importado correctamente
✓ Helper creado correctamente
✓ Nueva instancia de SAP2000 creada
✓ SAP2000 versión: 24.0.0
¡API funcionando correctamente!
```

---

## Conclusión

✅ **SÍ**, si tienes la API de C#, puedes usarla desde Python
✅ **Usa Python.NET** (`pythonnet`), NO `comtypes`
✅ **La conversión de C# a Python.NET** es directa y sencilla
✅ **Verifica** que estés usando la versión correcta de Python (3.4-3.8)
✅ **Asegúrate** de tener la ruta correcta a `SAP2000v1.dll`

---

## Recursos

### Documentación Oficial
- **CSI_OAPI_Documentation.chm** → Example 8 (Python.NET)
- **CSI_OAPI_Documentation.chm** → Example 3 (Visual C# 2005)

### Archivos Clave
```
C:\Users\j-b-j\Documents\Calcpad-7.5.7\
├── CSI_OAPI_Documentation.chm
├── CHM_extracted\Example_Code\
│   ├── Example_8_(Python_NET).htm
│   └── Example_3_(Visual_C_2005).htm
└── sap2000_rectangular_slab.py (tu script actual)
```

### Próximos Pasos
1. Ejecutar `test_sap2000_api.py` para verificar instalación
2. Convertir scripts existentes de `comtypes` a `pythonnet`
3. Comparar resultados con Calcpad usando Calcpad CLI

---

**Creado**: 2026-01-17
**Herramienta**: Claude Code
**Basado en**: CSI OAPI Documentation (Examples 3, 7, 8)
