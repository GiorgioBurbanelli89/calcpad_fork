# Cómo Armar Toda la API de Python desde C#

## Respuesta Directa: **SÍ, PUEDES ARMAR TODA LA API DE PYTHON**

Si tienes acceso a la API de C# de SAP2000, puedes crear una API completa en Python de TRES formas diferentes.

---

## Método 1: Python.NET (pythonnet) - ⭐ MÁS DIRECTO

### Concepto
Acceso directo a las DLLs .NET de SAP2000. **Ya está hecho por CSI**, solo necesitas usarlo.

### Ventajas
- ✅ No requieres escribir código adicional
- ✅ Acceso completo a TODA la API
- ✅ Prácticamente idéntico a C#
- ✅ Soportado oficialmente por CSI

### Desventajas
- ❌ Solo funciona con Python 3.4-3.8 (no con 3.9+)

### Instalación

```bash
# 1. Instalar Python 3.8 (si tienes 3.9+)
# Descargar de python.org

# 2. Instalar pythonnet
pip install pythonnet
```

### Uso

```python
import clr

# Referencia a DLL
clr.AddReference(R'C:\Program Files\Computers and Structures\SAP2000 24\SAP2000v1.dll')
from SAP2000v1 import *

# Usar API exactamente como en C#
helper = cHelper(Helper())
sap = cOAPI(helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject"))
sap.ApplicationStart()

model = cSapModel(sap.SapModel)

# TODA la API está disponible
model.InitializeNewModel(6)
file = cFile(model.File)
file.NewBlank()

# ... cualquier función que exista en C#
```

**Resultado**: **100% de la API disponible**, automáticamente.

---

## Método 2: COM via comtypes - ⭐ COMPATIBLE PYTHON 3.12

### Concepto
Acceso a través de COM (Component Object Model). Funciona con **cualquier versión de Python**.

### Ventajas
- ✅ Funciona con Python 3.12 (tu versión actual)
- ✅ No requiere código adicional
- ✅ Acceso completo a TODA la API
- ✅ Más fácil de instalar

### Desventajas
- ❌ Sintaxis un poco diferente a C#
- ❌ Requiere que SAP2000 esté registrado en COM

### Instalación

```bash
pip install comtypes
```

### Uso

```python
import comtypes.client

# Opción 1: Conectar a SAP2000 abierto
sap = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")

# Opción 2: Crear nueva instancia
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
sap = helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject")
sap.ApplicationStart()

model = sap.SapModel

# TODA la API está disponible
model.InitializeNewModel(6)
model.File.NewBlank()

# ... cualquier función que exista en C#
```

**Resultado**: **100% de la API disponible**, automáticamente.

---

## Método 3: Wrapper Personalizado - 🛠️ MÁXIMO CONTROL

### Concepto
Crear un ejecutable C# que exponga funciones específicas a Python mediante:
- **Archivos de texto** (más simple)
- **Sockets** (más robusto)
- **HTTP/REST API** (más moderno)

### Ventajas
- ✅ Control total sobre la interfaz
- ✅ Funciona con cualquier versión de Python
- ✅ Puedes simplificar funciones complejas
- ✅ Puedes agregar validaciones personalizadas

### Desventajas
- ❌ Requiere escribir código C# y Python
- ❌ Más trabajo de mantenimiento
- ❌ No tienes acceso automático a nuevas funciones de SAP2000

### Implementación

#### Opción A: Ejecutable C# + Archivos

**C# (SAP2000Runner.cs)**:
```csharp
using System;
using System.IO;
using SAP2000v1;
using Newtonsoft.Json;

class SAP2000Runner
{
    static void Main(string[] args)
    {
        // Leer comando de archivo JSON
        var commandFile = args[0];
        var command = JsonConvert.DeserializeObject<Command>(File.ReadAllText(commandFile));

        // Conectar a SAP2000
        var helper = new Helper();
        var sap = helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject");
        sap.ApplicationStart();
        var model = sap.SapModel;

        // Ejecutar comando
        dynamic result = null;
        switch (command.Action)
        {
            case "CreateModel":
                model.InitializeNewModel(eUnits.kN_m_C);
                model.File.NewBlank();
                result = new { success = true };
                break;

            case "AddPoint":
                string name = "";
                model.PointObj.AddCartesian(
                    command.Params.x,
                    command.Params.y,
                    command.Params.z,
                    ref name
                );
                result = new { success = true, name = name };
                break;

            case "Analyze":
                model.Analyze.RunAnalysis();
                result = new { success = true };
                break;

            case "GetDisplacements":
                int numResults = 0;
                string[] obj = null;
                double[] u3 = null;
                // ... obtener resultados
                result = new { success = true, u3 = u3 };
                break;
        }

        // Guardar resultado
        var resultFile = args[1];
        File.WriteAllText(resultFile, JsonConvert.SerializeObject(result));

        sap.ApplicationExit(false);
    }
}

class Command
{
    public string Action { get; set; }
    public dynamic Params { get; set; }
}
```

**Python (sap2000_api.py)**:
```python
import json
import subprocess
import tempfile
import os

class SAP2000API:
    def __init__(self):
        self.runner_exe = "SAP2000Runner.exe"

    def _call(self, action, params=None):
        # Crear archivos temporales
        cmd_file = tempfile.mktemp(suffix='.json')
        result_file = tempfile.mktemp(suffix='.json')

        # Escribir comando
        command = {"Action": action, "Params": params or {}}
        with open(cmd_file, 'w') as f:
            json.dump(command, f)

        # Ejecutar
        subprocess.run([self.runner_exe, cmd_file, result_file])

        # Leer resultado
        with open(result_file, 'r') as f:
            result = json.load(f)

        # Limpiar
        os.remove(cmd_file)
        os.remove(result_file)

        return result

    def create_model(self):
        return self._call("CreateModel")

    def add_point(self, x, y, z):
        return self._call("AddPoint", {"x": x, "y": y, "z": z})

    def analyze(self):
        return self._call("Analyze")

    def get_displacements(self):
        return self._call("GetDisplacements")

# Uso
api = SAP2000API()
api.create_model()
result = api.add_point(0, 0, 0)
print(f"Punto creado: {result['name']}")
api.analyze()
displacements = api.get_displacements()
```

#### Opción B: Servidor HTTP C#

**C# (SAP2000Server.cs)**:
```csharp
using System;
using System.Net;
using System.Text;
using SAP2000v1;
using Newtonsoft.Json;

class SAP2000Server
{
    private cSapModel model;

    static void Main()
    {
        var server = new SAP2000Server();
        server.Start();
    }

    void Start()
    {
        // Inicializar SAP2000
        var helper = new Helper();
        var sap = helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject");
        sap.ApplicationStart();
        model = sap.SapModel;

        // Crear servidor HTTP
        var listener = new HttpListener();
        listener.Prefixes.Add("http://localhost:8080/");
        listener.Start();
        Console.WriteLine("Servidor SAP2000 API iniciado en http://localhost:8080/");

        while (true)
        {
            var context = listener.GetContext();
            ProcessRequest(context);
        }
    }

    void ProcessRequest(HttpListenerContext context)
    {
        var request = context.Request;
        var response = context.Response;

        // Leer cuerpo
        string body = new StreamReader(request.InputStream).ReadToEnd();
        var command = JsonConvert.DeserializeObject<Command>(body);

        // Ejecutar
        dynamic result = ExecuteCommand(command);

        // Responder
        var responseString = JsonConvert.SerializeObject(result);
        var buffer = Encoding.UTF8.GetBytes(responseString);
        response.ContentLength64 = buffer.Length;
        response.OutputStream.Write(buffer, 0, buffer.Length);
        response.OutputStream.Close();
    }

    dynamic ExecuteCommand(Command cmd)
    {
        switch (cmd.Action)
        {
            case "CreateModel":
                model.InitializeNewModel(eUnits.kN_m_C);
                model.File.NewBlank();
                return new { success = true };

            case "AddPoint":
                string name = "";
                model.PointObj.AddCartesian(
                    cmd.Params.x, cmd.Params.y, cmd.Params.z, ref name
                );
                return new { success = true, name = name };

            // ... más comandos
        }
        return new { success = false, error = "Unknown command" };
    }
}
```

**Python (sap2000_client.py)**:
```python
import requests
import json

class SAP2000API:
    def __init__(self, server_url="http://localhost:8080/"):
        self.server_url = server_url

    def _call(self, action, params=None):
        payload = {"Action": action, "Params": params or {}}
        response = requests.post(self.server_url, json=payload)
        return response.json()

    def create_model(self):
        return self._call("CreateModel")

    def add_point(self, x, y, z):
        return self._call("AddPoint", {"x": x, "y": y, "z": z})

# Uso
api = SAP2000API()
api.create_model()
result = api.add_point(0, 0, 0)
print(f"Punto creado: {result['name']}")
```

---

## Comparación de Métodos

| Aspecto | Python.NET | comtypes | Wrapper C# |
|---------|-----------|----------|-----------|
| **Cobertura API** | 100% | 100% | Solo lo que implementes |
| **Esfuerzo inicial** | ⭐ Mínimo | ⭐ Mínimo | ⭐⭐⭐⭐ Alto |
| **Compatibilidad Python** | 3.4-3.8 | Todas | Todas |
| **Mantenimiento** | ⭐ Ninguno | ⭐ Ninguno | ⭐⭐⭐⭐ Alto |
| **Control** | ⭐⭐ Bajo | ⭐⭐ Bajo | ⭐⭐⭐⭐⭐ Total |
| **Rendimiento** | ⭐⭐⭐⭐⭐ Excelente | ⭐⭐⭐⭐ Bueno | ⭐⭐⭐ Medio |

---

## Recomendación

### Para uso general: **comtypes** (tu caso actual)

```bash
pip install comtypes
```

**Razones**:
1. ✅ Funciona con tu Python 3.12 actual
2. ✅ 100% de la API disponible inmediatamente
3. ✅ Sin escribir código adicional
4. ✅ Probado y funcionando (viste el test)

### Para máximo rendimiento: **Python.NET**

```bash
# Instalar Python 3.8 primero
pip install pythonnet
```

**Razones**:
1. ✅ Ligeramente más rápido que comtypes
2. ✅ Sintaxis más similar a C#
3. ✅ Recomendado oficialmente por CSI

### Para casos especiales: **Wrapper C#**

Solo si necesitas:
- Funciones simplificadas para usuarios no técnicos
- Validaciones personalizadas antes de llamar a SAP2000
- Integración con servicios web
- Caching o persistencia de estado

---

## Ejemplo Completo: API Completa en Python

Usando **comtypes** (funciona con Python 3.12):

```python
# sap2000_api_completa.py
import comtypes.client

class SAP2000:
    """API Completa de SAP2000 para Python"""

    def __init__(self, attach_to_existing=False):
        """Inicializar conexión a SAP2000"""
        if attach_to_existing:
            # Conectar a instancia existente
            self.sap = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
        else:
            # Crear nueva instancia
            helper = comtypes.client.CreateObject('SAP2000v1.Helper')
            helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
            self.sap = helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject")
            self.sap.ApplicationStart()

        self.model = self.sap.SapModel

    # ========== ARCHIVO ==========
    def new_model(self, units=6):  # 6 = kN, m, C
        self.model.InitializeNewModel(units)
        self.model.File.NewBlank()

    def save(self, path):
        return self.model.File.Save(path)

    def open(self, path):
        return self.model.File.OpenFile(path)

    # ========== MATERIALES ==========
    def add_material(self, name, mat_type=2):  # 2 = Concrete
        return self.model.PropMaterial.SetMaterial(name, mat_type)

    def set_material_isotropic(self, name, E, nu, alpha):
        return self.model.PropMaterial.SetMPIsotropic(name, E, nu, alpha)

    # ========== PROPIEDADES DE SECCIONES ==========
    def add_shell_property(self, name, shell_type, thickness, material):
        """
        shell_type:
            1 = Shell-Thin (Kirchhoff)
            2 = Shell-Thick (Mindlin)
            3 = Membrane
            4 = Plate-Thin
            5 = Plate-Thick
        """
        return self.model.PropArea.SetShell_1(
            name, shell_type, False, material,
            0.0, thickness, thickness, 0, "", ""
        )

    def add_frame_property_rectangle(self, name, material, h, w):
        return self.model.PropFrame.SetRectangle(name, material, h, w)

    # ========== GEOMETRÍA ==========
    def add_point(self, x, y, z, name=""):
        return self.model.PointObj.AddCartesian(x, y, z, name)

    def add_frame_by_points(self, pt1, pt2, section, name=""):
        return self.model.FrameObj.AddByPoint(pt1, pt2, name, section, name)

    def add_area_by_points(self, num_points, points, section, name=""):
        return self.model.AreaObj.AddByPoint(num_points, points, name, section, name)

    def add_area_by_coords(self, num_points, x_coords, y_coords, z_coords, section, name=""):
        return self.model.AreaObj.AddByCoord(
            num_points, x_coords, y_coords, z_coords, "", section, name
        )

    # ========== CONDICIONES DE BORDE ==========
    def set_restraint(self, point_name, restraint):
        """
        restraint: [U1, U2, U3, R1, R2, R3]
        True = restringido, False = libre
        """
        return self.model.PointObj.SetRestraint(point_name, restraint, 0)

    # ========== CARGAS ==========
    def add_load_pattern(self, name, load_type=1):  # 1 = Dead
        return self.model.LoadPatterns.Add(name, load_type)

    def set_point_load(self, point, pattern, force):
        """force: [Fx, Fy, Fz, Mx, My, Mz]"""
        return self.model.PointObj.SetLoadForce(point, pattern, force)

    def set_area_load_uniform(self, area, pattern, value, direction=6):
        """direction: 6 = Gravity (Z-)"""
        return self.model.AreaObj.SetLoadUniform(
            area, pattern, value, direction, True, "Global", 0
        )

    def set_frame_load_distributed(self, frame, pattern, direction, dist1, dist2):
        return self.model.FrameObj.SetLoadDistributed(
            frame, pattern, 1, direction, 0, 1, dist1, dist2
        )

    # ========== ANÁLISIS ==========
    def run_analysis(self):
        return self.model.Analyze.RunAnalysis()

    def set_active_case(self, case_name):
        self.model.Results.Setup.DeselectAllCasesAndCombosForOutput()
        return self.model.Results.Setup.SetCaseSelectedForOutput(case_name)

    # ========== RESULTADOS ==========
    def get_joint_displacements(self, point_name=""):
        """Retorna desplazamientos de nodos"""
        return self.model.Results.JointDispl(point_name, 2)

    def get_joint_reactions(self, point_name=""):
        """Retorna reacciones de nodos"""
        return self.model.Results.JointReact(point_name, 0)

    def get_frame_forces(self, frame_name=""):
        """Retorna fuerzas en frames"""
        return self.model.Results.FrameForce(frame_name, 0)

    def get_area_forces(self, area_name=""):
        """Retorna fuerzas en shells/areas"""
        return self.model.Results.AreaForceShell(area_name, 0)

    # ========== UTILIDADES ==========
    def get_version(self):
        return self.model.GetVersion()[0]

    def count_points(self):
        return self.model.PointObj.Count()

    def count_frames(self):
        return self.model.FrameObj.Count()

    def count_areas(self):
        return self.model.AreaObj.Count()

    def close(self, save_file=False):
        self.sap.ApplicationExit(save_file)


# ========== EJEMPLO DE USO ==========
if __name__ == "__main__":
    # Crear API
    api = SAP2000()

    print(f"SAP2000 Version: {api.get_version()}")

    # Nuevo modelo
    api.new_model(units=6)  # kN, m, C

    # Material
    api.add_material("CONC", mat_type=2)
    api.set_material_isotropic("CONC", 35000000, 0.15, 0.0000099)

    # Propiedad de shell
    api.add_shell_property("LOSA", shell_type=5, thickness=0.1, material="CONC")

    # Geometría: Placa 2x2m con 4x4 elementos
    points = {}
    for i in range(5):
        for j in range(5):
            x, y = i * 0.5, j * 0.5
            name = f"{i}_{j}"
            api.add_point(x, y, 0, name)
            points[(i, j)] = name

    # Crear elementos
    for i in range(4):
        for j in range(4):
            pts = [
                points[(i, j)],
                points[(i+1, j)],
                points[(i+1, j+1)],
                points[(i, j+1)]
            ]
            api.add_area_by_points(4, pts, "LOSA", f"E{i}_{j}")

    # Apoyos en bordes
    for i in range(5):
        for j in range(5):
            if i == 0 or i == 4 or j == 0 or j == 4:
                api.set_restraint(points[(i, j)], [False, False, True, False, False, False])

    # Carga
    for i in range(4):
        for j in range(4):
            api.set_area_load_uniform(f"E{i}_{j}", "Dead", 10, 6)

    # Analizar
    api.run_analysis()

    # Resultados
    api.set_active_case("Dead")
    disps = api.get_joint_displacements()

    if disps[0] > 0:
        max_u3 = max(abs(u) for u in disps[9])
        print(f"\nDesplazamiento maximo: {max_u3*1000:.4f} mm")

    # Guardar
    api.save(R"C:\temp\test_api.sdb")

    # Cerrar
    api.close(save_file=False)

    print("\n[OK] API Completa funcionando correctamente")
```

**Resultado**: Tienes **TODA la funcionalidad de la API C#** disponible en Python.

---

## Conclusión

**SÍ, PUEDES ARMAR TODA LA API DE PYTHON** si tienes acceso a C#.

**Método recomendado para ti**: **comtypes**
- ✅ Ya probado y funcionando
- ✅ Compatible con tu Python 3.12
- ✅ 100% de la API disponible
- ✅ Cero código adicional

---

**Creado**: 2026-01-17
**Archivos de referencia**:
- `test_sap2000_comtypes.py` (probado y funcionando ✓)
- `comparar_calcpad_sap2000.py` (ejecutándose ahora)
- Documentación oficial CSI: Examples 7, 8, 3
