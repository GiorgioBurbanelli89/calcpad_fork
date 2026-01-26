# SMath Studio + Solver Externo C++ - Guía Completa

## 🎯 Respuesta Directa

**SÍ, puedes combinar un solver externo de C++ con SMath Studio** y obtener los resultados para hacer gráficas.

Hay **3 formas** de hacerlo:

---

## 🚀 Método 1: Solver C++ como Función (Más Simple)

### Concepto
Tu solver C++ es una **DLL** que SMath llama directamente como función.

### Flujo
```
SMath Studio → Llama función del plugin → Plugin llama DLL C++ → Solver ejecuta
                                                                      ↓
SMath Studio ← Graficar resultados ← Plugin recibe resultados ← Solver retorna
```

### Ejemplo: Solver FEM en C++

#### Paso 1: Tu Solver C++ (DLL)

**fem_solver.cpp**
```cpp
// fem_solver.cpp - Solver de elementos finitos en C++

#include <vector>
#include <cmath>

#ifdef _WIN32
    #define DLL_EXPORT __declspec(dllexport)
#else
    #define DLL_EXPORT
#endif

extern "C" {
    // Solver de viga - retorna desplazamientos en cada nodo
    DLL_EXPORT void solve_beam(
        double E,           // Módulo de elasticidad
        double A,           // Área
        double I,           // Momento de inercia
        double L,           // Longitud
        int n_nodes,        // Número de nodos
        double* loads,      // Cargas en cada nodo (entrada)
        double* displacements // Desplazamientos (salida)
    )
    {
        // 1. Construir matriz de rigidez global
        std::vector<std::vector<double>> K(n_nodes * 3, std::vector<double>(n_nodes * 3, 0));

        // 2. Ensamblar elementos
        int n_elements = n_nodes - 1;
        double Le = L / n_elements;

        for (int e = 0; e < n_elements; e++)
        {
            // Calcular matriz de rigidez del elemento
            double k_local[6][6];
            calculate_element_stiffness(E, A, I, Le, k_local);

            // Ensamblar en matriz global
            assemble_element(K, k_local, e);
        }

        // 3. Aplicar condiciones de frontera
        apply_boundary_conditions(K, 0); // Nodo 0 empotrado

        // 4. Resolver sistema K * u = F
        solve_linear_system(K, loads, displacements, n_nodes * 3);
    }

    // Solver de placa - análisis de placas
    DLL_EXPORT void solve_plate(
        double Lx, double Ly,      // Dimensiones
        int nx, int ny,            // Elementos en x, y
        double E, double nu, double t, // Propiedades material
        double q,                  // Carga distribuida
        double* deflections        // Deflexiones (salida)
    )
    {
        // Análisis de placa con elementos finitos
        int n_nodes = (nx + 1) * (ny + 1);

        // 1. Generar malla
        std::vector<Node> nodes = generate_mesh(Lx, Ly, nx, ny);

        // 2. Construir matriz de rigidez
        std::vector<std::vector<double>> K = build_plate_stiffness(nodes, E, nu, t);

        // 3. Vector de cargas
        std::vector<double> F(n_nodes, q * (Lx / nx) * (Ly / ny));

        // 4. Resolver
        solve_linear_system(K, F.data(), deflections, n_nodes);
    }
}
```

**Compilar:**
```bash
g++ -shared -o fem_solver.dll fem_solver.cpp -O3
```

#### Paso 2: Plugin SMath que usa el Solver

**FEMSolverPlugin.cs**
```csharp
using System;
using System.Runtime.InteropServices;
using SMath.Manager;
using SMath.Math.Numeric;

namespace FEMSolverPlugin
{
    public class FEMSolver : IPluginLowLevelEvaluationFast
    {
        // ================================================================
        // IMPORTAR SOLVER C++
        // ================================================================
        [DllImport("fem_solver.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern void solve_beam(
            double E, double A, double I, double L,
            int n_nodes,
            double[] loads,
            double[] displacements
        );

        [DllImport("fem_solver.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern void solve_plate(
            double Lx, double Ly,
            int nx, int ny,
            double E, double nu, double t,
            double q,
            double[] deflections
        );

        // ================================================================
        // REGISTRAR FUNCIONES
        // ================================================================
        public void Initialize()
        {
            GlobalFunctions.RegisterFunction("solve_beam", SolveBeam);
            GlobalFunctions.RegisterFunction("solve_plate", SolvePlate);
        }

        // ================================================================
        // WRAPPER: SOLVER DE VIGA
        // ================================================================
        private static Term SolveBeam(Term[] args)
        {
            try
            {
                // Extraer parámetros
                double E = args[0].obj.ToDouble();
                double A = args[1].obj.ToDouble();
                double I = args[2].obj.ToDouble();
                double L = args[3].obj.ToDouble();
                int n_nodes = (int)args[4].obj.ToDouble();

                // Vector de cargas (Term es una matriz en SMath)
                Matrix loads_matrix = args[5].obj.ToMatrix();
                double[] loads = new double[n_nodes * 3];
                for (int i = 0; i < loads_matrix.Rows; i++)
                {
                    loads[i] = loads_matrix[i, 0].ToDouble();
                }

                // Array de salida
                double[] displacements = new double[n_nodes * 3];

                // ¡LLAMAR AL SOLVER C++!
                solve_beam(E, A, I, L, n_nodes, loads, displacements);

                // Convertir resultado a matriz de SMath
                Matrix result = new Matrix(n_nodes * 3, 1);
                for (int i = 0; i < displacements.Length; i++)
                {
                    result[i, 0] = new Term(displacements[i]);
                }

                return new Term(result);
            }
            catch (Exception ex)
            {
                return new Term($"Error: {ex.Message}");
            }
        }

        // ================================================================
        // WRAPPER: SOLVER DE PLACA
        // ================================================================
        private static Term SolvePlate(Term[] args)
        {
            double Lx = args[0].obj.ToDouble();
            double Ly = args[1].obj.ToDouble();
            int nx = (int)args[2].obj.ToDouble();
            int ny = (int)args[3].obj.ToDouble();
            double E = args[4].obj.ToDouble();
            double nu = args[5].obj.ToDouble();
            double t = args[6].obj.ToDouble();
            double q = args[7].obj.ToDouble();

            int n_nodes = (nx + 1) * (ny + 1);
            double[] deflections = new double[n_nodes];

            // ¡LLAMAR AL SOLVER C++!
            solve_plate(Lx, Ly, nx, ny, E, nu, t, q, deflections);

            // Convertir a matriz 2D para graficar
            Matrix result = new Matrix(ny + 1, nx + 1);
            int idx = 0;
            for (int j = 0; j <= ny; j++)
            {
                for (int i = 0; i <= nx; i++)
                {
                    result[j, i] = new Term(deflections[idx++]);
                }
            }

            return new Term(result);
        }
    }
}
```

#### Paso 3: Usar en SMath Studio

```
# Análisis de viga
E := 200000        # MPa
A := 0.01          # m²
I := 0.0001        # m⁴
L := 10            # m
n := 11            # nodos

# Vector de cargas (3 DOF por nodo: Fx, Fy, M)
F := [0, 0, 0,     # Nodo 0 (empotrado)
      0, -1000, 0, # Nodo 1
      0, -1000, 0, # Nodo 2
      ...]         # etc

# ¡RESOLVER CON SOLVER C++!
u := solve_beam(E, A, I, L, n, F)

# Extraer desplazamientos verticales
y_disp := [u[1,0], u[4,0], u[7,0], ...]

# GRAFICAR
x := 0,L/10..L
plot(x, y_disp)    # ← ¡Gráfica de deformada!
```

**Resultado:** Gráfica de la viga deformada calculada por tu solver C++.

---

## 🎨 Método 2: Solver Externo + Archivos (Más Flexible)

### Concepto
El solver C++ es un **ejecutable** que escribe resultados a archivo, el plugin lee el archivo.

### Flujo
```
SMath → Plugin ejecuta solver.exe → Solver escribe results.txt
                                          ↓
SMath ← Graficar ← Plugin lee results.txt
```

### Ejemplo: Solver ANSYS/CalculiX Style

#### Paso 1: Tu Solver C++ (Ejecutable)

**fem_solver_standalone.cpp**
```cpp
// fem_solver_standalone.cpp - Solver independiente

#include <iostream>
#include <fstream>
#include <vector>

int main(int argc, char* argv[])
{
    if (argc < 2)
    {
        std::cerr << "Uso: fem_solver input.txt" << std::endl;
        return 1;
    }

    // 1. Leer archivo de entrada
    std::ifstream input(argv[1]);

    double E, A, I, L, q;
    int n_nodes;
    input >> E >> A >> I >> L >> q >> n_nodes;

    std::vector<double> loads(n_nodes);
    for (int i = 0; i < n_nodes; i++)
    {
        input >> loads[i];
    }
    input.close();

    // 2. RESOLVER (tu algoritmo FEM)
    std::vector<double> displacements(n_nodes);

    // ... código del solver
    solve_fem(E, A, I, L, loads.data(), displacements.data(), n_nodes);

    // 3. Escribir resultados
    std::ofstream output("results.txt");
    output << n_nodes << std::endl;
    for (int i = 0; i < n_nodes; i++)
    {
        double x = L * i / (n_nodes - 1);
        output << x << " " << displacements[i] << std::endl;
    }
    output.close();

    std::cout << "Solver completado. Resultados en results.txt" << std::endl;

    return 0;
}
```

**Compilar:**
```bash
g++ -o fem_solver.exe fem_solver_standalone.cpp -O3
```

#### Paso 2: Plugin que ejecuta el solver

**FEMSolverExternalPlugin.cs**
```csharp
using System;
using System.Diagnostics;
using System.IO;
using SMath.Manager;
using SMath.Math.Numeric;

namespace FEMSolverExternalPlugin
{
    public class ExternalSolver : IPluginLowLevelEvaluationFast
    {
        public void Initialize()
        {
            GlobalFunctions.RegisterFunction("solve_fem_external", SolveFEMExternal);
        }

        private static Term SolveFEMExternal(Term[] args)
        {
            try
            {
                // 1. Extraer parámetros
                double E = args[0].obj.ToDouble();
                double A = args[1].obj.ToDouble();
                double I = args[2].obj.ToDouble();
                double L = args[3].obj.ToDouble();
                double q = args[4].obj.ToDouble();
                int n_nodes = (int)args[5].obj.ToDouble();

                // 2. Escribir archivo de entrada para el solver
                using (StreamWriter sw = new StreamWriter("input.txt"))
                {
                    sw.WriteLine($"{E} {A} {I} {L} {q} {n_nodes}");
                    for (int i = 0; i < n_nodes; i++)
                    {
                        sw.WriteLine(q); // Carga en cada nodo
                    }
                }

                // 3. EJECUTAR SOLVER C++ EXTERNO
                ProcessStartInfo psi = new ProcessStartInfo
                {
                    FileName = "fem_solver.exe",
                    Arguments = "input.txt",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    CreateNoWindow = true
                };

                Process process = Process.Start(psi);
                string output = process.StandardOutput.ReadToEnd();
                process.WaitForExit();

                if (process.ExitCode != 0)
                {
                    return new Term("Error: Solver falló");
                }

                // 4. Leer resultados
                Matrix results = new Matrix(n_nodes, 2); // [x, displacement]

                using (StreamReader sr = new StreamReader("results.txt"))
                {
                    int n = int.Parse(sr.ReadLine());
                    for (int i = 0; i < n; i++)
                    {
                        string[] parts = sr.ReadLine().Split(' ');
                        results[i, 0] = new Term(double.Parse(parts[0])); // x
                        results[i, 1] = new Term(double.Parse(parts[1])); // displacement
                    }
                }

                return new Term(results);
            }
            catch (Exception ex)
            {
                return new Term($"Error: {ex.Message}");
            }
        }
    }
}
```

#### Paso 3: Usar en SMath

```
# Parámetros
E := 200000
A := 0.01
I := 0.0001
L := 10
q := -1000
n := 21

# ¡EJECUTAR SOLVER EXTERNO!
results := solve_fem_external(E, A, I, L, q, n)

# Extraer coordenadas y desplazamientos
x := results[0..20, 0]      # Primera columna (x)
y := results[0..20, 1]      # Segunda columna (displacement)

# GRAFICAR
plot(x, y)                  # ← Gráfica de deformada
```

---

## 📊 Método 3: Región Personalizada con Visualización

### Concepto
Crear una **región personalizada** en SMath que ejecuta el solver y visualiza resultados directamente.

### Ejemplo: Widget FEM Interactivo

**FEMVisualizerRegion.cs**
```csharp
using System;
using System.Drawing;
using System.Runtime.InteropServices;
using SMath.Controls;

namespace FEMVisualizerPlugin
{
    public class FEMVisualizerPlugin : IPluginCustomRegion
    {
        public RegionBase CreateRegion()
        {
            return new FEMVisualizerRegion();
        }

        public string RegionTypeName => "FEM Visualizer";
    }

    public class FEMVisualizerRegion : RegionBase
    {
        // Importar solver
        [DllImport("fem_solver.dll")]
        private static extern void solve_beam(
            double E, double A, double I, double L,
            int n_nodes, double[] loads, double[] displacements
        );

        // Parámetros editables
        public double E = 200000;
        public double A = 0.01;
        public double I = 0.0001;
        public double L = 10;
        public int Nodes = 11;

        private double[] displacements;

        public override void Calculate()
        {
            // Ejecutar solver
            double[] loads = new double[Nodes * 3];
            loads[4] = -1000; // Carga en el medio

            displacements = new double[Nodes * 3];
            solve_beam(E, A, I, L, Nodes, loads, displacements);
        }

        public override void Draw(Graphics g, Rectangle bounds)
        {
            // Dibujar viga original
            Pen blackPen = new Pen(Color.Black, 2);
            g.DrawLine(blackPen, bounds.Left, bounds.Top + bounds.Height / 2,
                       bounds.Right, bounds.Top + bounds.Height / 2);

            // Dibujar viga deformada
            Pen redPen = new Pen(Color.Red, 2);

            float scale = 1000; // Factor de escala para visualizar

            for (int i = 0; i < Nodes - 1; i++)
            {
                float x1 = bounds.Left + (bounds.Width * i / (Nodes - 1));
                float y1 = bounds.Top + bounds.Height / 2 + (float)(displacements[i * 3 + 1] * scale);

                float x2 = bounds.Left + (bounds.Width * (i + 1) / (Nodes - 1));
                float y2 = bounds.Top + bounds.Height / 2 + (float)(displacements[(i + 1) * 3 + 1] * scale);

                g.DrawLine(redPen, x1, y1, x2, y2);
            }

            // Leyenda
            g.DrawString($"E={E}, L={L}, Nodes={Nodes}",
                         SystemFonts.DefaultFont, Brushes.Black,
                         bounds.Left, bounds.Bottom - 20);
        }
    }
}
```

**Usar en SMath:**
```
Insertar → Región FEM → FEM Visualizer

[Widget interactivo que muestra viga deformada en tiempo real]

Editar parámetros:
  E = 200000
  L = 10
  Nodes = 21

[Widget se actualiza automáticamente mostrando nueva deformada]
```

---

## 🎯 Comparación de Métodos

| Método | Complejidad | Velocidad | Flexibilidad | Visualización |
|--------|-------------|-----------|--------------|---------------|
| **1. DLL como función** | ⭐⭐ Media | ⭐⭐⭐⭐⭐ Muy rápida | ⭐⭐⭐ Buena | ⭐⭐⭐ Gráficas SMath |
| **2. Ejecutable + archivos** | ⭐⭐⭐ Media-Alta | ⭐⭐⭐ Rápida | ⭐⭐⭐⭐⭐ Máxima | ⭐⭐⭐ Gráficas SMath |
| **3. Región personalizada** | ⭐⭐⭐⭐ Alta | ⭐⭐⭐⭐ Muy rápida | ⭐⭐⭐⭐ Muy buena | ⭐⭐⭐⭐⭐ Interactiva |

---

## 💡 Caso de Uso Real: Análisis de Placa

### Tu Solver C++ (ya lo tienes)

```cpp
// Ya tienes esto compilado como mathcad_plate.dll
void solve_rectangular_plate(
    double Lx, double Ly,
    int nx, int ny,
    double E, double nu, double t, double q,
    double* deflections
);
```

### Plugin SMath

```csharp
public class PlateAnalysisPlugin : IPluginLowLevelEvaluationFast
{
    [DllImport("mathcad_plate.dll")]
    static extern void solve_rectangular_plate(
        double Lx, double Ly, int nx, int ny,
        double E, double nu, double t, double q,
        double[] deflections
    );

    public void Initialize()
    {
        GlobalFunctions.RegisterFunction("analyze_plate", AnalyzePlate);
    }

    private static Term AnalyzePlate(Term[] args)
    {
        double Lx = args[0].obj.ToDouble();
        double Ly = args[1].obj.ToDouble();
        int nx = (int)args[2].obj.ToDouble();
        int ny = (int)args[3].obj.ToDouble();
        double E = args[4].obj.ToDouble();
        double nu = args[5].obj.ToDouble();
        double t = args[6].obj.ToDouble();
        double q = args[7].obj.ToDouble();

        int n_nodes = (nx + 1) * (ny + 1);
        double[] deflections = new double[n_nodes];

        // ¡LLAMAR TU SOLVER!
        solve_rectangular_plate(Lx, Ly, nx, ny, E, nu, t, q, deflections);

        // Convertir a matriz 2D
        Matrix result = new Matrix(ny + 1, nx + 1);
        int idx = 0;
        for (int j = 0; j <= ny; j++)
            for (int i = 0; i <= nx; i++)
                result[j, i] = new Term(deflections[idx++]);

        return new Term(result);
    }
}
```

### Usar en SMath con Gráfica 3D

```
# Parámetros de la placa
Lx := 4        # m
Ly := 3        # m
nx := 20       # elementos en x
ny := 15       # elementos en y

E := 200000    # MPa
ν := 0.3
t := 0.2       # m (espesor)
q := -10       # kN/m² (carga)

# ¡ANALIZAR CON TU SOLVER C++!
w := analyze_plate(Lx, Ly, nx, ny, E, ν, t, q)

# Coordenadas
x := 0,Lx/nx..Lx
y := 0,Ly/ny..Ly

# GRAFICAR EN 3D
surface3D(x, y, w)    # ← ¡Superficie 3D de deflexiones!

# Valores extremos
w_max := max(w)       # Deflexión máxima
w_min := min(w)       # Deflexión mínima

# Gráfica de contorno
contour(x, y, w)      # ← ¡Contornos de deflexión!
```

---

## 🚀 Ventajas de Este Enfoque

### 1. **Reutilización de Código**
```
Tu solver C++ (ya existe)
    ↓
Plugin SMath (wrapper simple)
    ↓
Funciona en SMath Studio
```

No reescribes tu solver, solo lo llamas.

### 2. **Máximo Rendimiento**
- Solver C++ compilado = velocidad máxima
- Sin overhead de interpretación
- Optimizaciones del compilador C++

### 3. **Mejor de Ambos Mundos**
- **C++:** Cálculos pesados, álgebra lineal, solvers
- **SMath:** Entrada de datos, gráficas, reportes, UI

### 4. **Flexible**
Puedes usar:
- Tu propio solver FEM
- Bibliotecas externas (Eigen, BLAS, LAPACK)
- Solvers comerciales (si tienen API C)
- Código legacy que ya existe

---

## 📚 Ejemplo Completo: Análisis de Viga con Gráficas

### Archivo SMath (.sm)

```
====================================================================
ANÁLISIS DE VIGA CON SOLVER C++ EXTERNO
====================================================================

PARÁMETROS:
-----------
E := 200·10^3·MPa    # Módulo de elasticidad (acero)
A := 100·cm^2        # Área de sección
I := 8333·cm^4       # Momento de inercia
L := 10·m            # Longitud de viga
n := 21              # Número de nodos

CARGAS:
-------
# Carga distribuida equivalente en nodos
q := 10·kN/m
F := q·(L/(n-1))     # Carga en cada nodo

# Vector de cargas (3 DOF por nodo: Fx, Fy, M)
loads := [0, 0, 0,           # Nodo 0 (apoyo)
          0, -F, 0,          # Nodo 1
          0, -F, 0,          # Nodo 2
          ...                # etc.
          0, 0, 0]           # Nodo n-1 (apoyo)

RESOLVER:
---------
# ¡Llamar solver C++ externo!
u := solve_beam(E, A, I, L, n, loads)

# Extraer desplazamientos verticales
x := 0, L/(n-1)..L
y_disp := [u[1,0], u[4,0], u[7,0], ..., u[3(n-1)+1,0]]

GRÁFICAS:
---------
# Deformada de la viga
plot(x, y_disp)
title("Deformada de la Viga")
xlabel("Posición (m)")
ylabel("Desplazamiento (m)")

# Deflexión máxima
δ_max := max(abs(y_disp))

RESULTADOS:
-----------
"Deflexión máxima: " δ_max " m"

# Comparar con solución analítica
δ_analytic := (5·q·L^4)/(384·E·I)
"Deflexión analítica: " δ_analytic " m"
"Error: " abs((δ_max - δ_analytic)/δ_analytic·100) " %"

====================================================================
```

---

## ✅ Conclusión

### Pregunta Original:
> "Es decir puedo combinar un solver externo de c++ y obtener los resultados en smath studio para hacer las graficas?"

### Respuesta:
**¡SÍ, PERFECTAMENTE!**

### Puedes:
1. ✅ **Ejecutar tu solver C++** desde SMath
2. ✅ **Obtener resultados** en variables de SMath
3. ✅ **Hacer gráficas** 2D, 3D, contornos, etc.
4. ✅ **Hacer cálculos** post-procesamiento en SMath
5. ✅ **Generar reportes** con resultados y gráficas
6. ✅ **Combinar** múltiples solvers

### Métodos:
- **Método 1 (Recomendado):** DLL C++ llamada como función
- **Método 2:** Ejecutable externo + archivos
- **Método 3:** Región personalizada con visualización

### Para tu proyecto:
Ya tienes los solvers C++ compilados:
- `mathcad_fem.dll`
- `mathcad_triangle.dll`
- `mathcad_plate.dll`

Solo necesitas crear el plugin que los llame y ya puedes:
- Analizar vigas, placas, mallas
- Graficar deformadas, diagramas, contornos
- Comparar con soluciones analíticas
- Generar reportes profesionales

**Todo en SMath Studio (gratis) con la potencia de tu solver C++.**
