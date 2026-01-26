// Program.cs - Programa de prueba para MathcadFEMWrapper
// Compara resultados con las DLLs de Mathcad Prime

using System;
using MathcadFEM.NET;

namespace MathcadFEMTest
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("============================================================");
            Console.WriteLine("  MathcadFEM.NET - Verificacion de Funciones FEM");
            Console.WriteLine("  Comparacion con mathcad_fem.dll, mathcad_triangle.dll");
            Console.WriteLine("============================================================");
            Console.WriteLine();

            TestBeamStiffness();
            TestTriangleMesh();
            TestPlateElement();

            Console.WriteLine("\nPresione cualquier tecla para salir...");
            Console.ReadKey();
        }

        static void TestBeamStiffness()
        {
            Console.WriteLine("--- TEST 1: Matriz de Rigidez de Viga 2D ---");
            Console.WriteLine();

            // Parametros (mismos que en Mathcad)
            double E = 210e9;      // Pa (210 GPa)
            double A = 100e-4;     // m2 (100 cm2)
            double I = 833.3e-8;   // m4 (833.3 cm4)
            double L = 3.0;        // m

            Console.WriteLine($"E = {E / 1e9} GPa");
            Console.WriteLine($"A = {A * 1e4} cm2");
            Console.WriteLine($"I = {I * 1e8} cm4");
            Console.WriteLine($"L = {L} m");
            Console.WriteLine();

            // Calcular matriz de rigidez
            double[,] K = FEMBeam.BeamStiffnessMatrix2D(E, A, I, L);

            // Valores esperados
            double K00_expected = E * A / L;                    // EA/L
            double K11_expected = 12 * E * I / (L * L * L);    // 12EI/L^3
            double K22_expected = 4 * E * I / L;               // 4EI/L

            Console.WriteLine("Resultados:");
            Console.WriteLine($"  K[0,0] = {K[0, 0]:E6}  (esperado: {K00_expected:E6})");
            Console.WriteLine($"  K[1,1] = {K[1, 1]:E6}  (esperado: {K11_expected:E6})");
            Console.WriteLine($"  K[2,2] = {K[2, 2]:E6}  (esperado: {K22_expected:E6})");
            Console.WriteLine();

            // Verificar errores
            double err0 = Math.Abs(K[0, 0] - K00_expected) / K00_expected * 100;
            double err1 = Math.Abs(K[1, 1] - K11_expected) / K11_expected * 100;
            double err2 = Math.Abs(K[2, 2] - K22_expected) / K22_expected * 100;

            Console.WriteLine($"  Error K[0,0]: {err0:F6}%");
            Console.WriteLine($"  Error K[1,1]: {err1:F6}%");
            Console.WriteLine($"  Error K[2,2]: {err2:F6}%");
            Console.WriteLine();

            // Test cantilever (solo si DLL esta disponible)
            Console.WriteLine("Deflexion voladizo (formula: PL^3/3EI):");
            double P = 10000;  // N
            double defl_calc = P * L * L * L / (3 * E * I);
            Console.WriteLine($"  P = {P} N, L = {L} m");
            Console.WriteLine($"  Deflexion calculada = {defl_calc * 1000:F6} mm");
            Console.WriteLine();
        }

        static void TestTriangleMesh()
        {
            Console.WriteLine("--- TEST 2: Generacion de Malla Triangular ---");
            Console.WriteLine();

            double Lx = 6.0;
            double Ly = 4.0;
            int nx = 3;
            int ny = 2;

            Console.WriteLine($"Placa: {Lx} x {Ly} m");
            Console.WriteLine($"Divisiones: {nx} x {ny}");
            Console.WriteLine();

            // Generar malla
            double[,] nodes = TriangleMesh.GenerateNodes(Lx, Ly, nx, ny);
            int[,] elements = TriangleMesh.GenerateElements(nx, ny);

            int numNodes = nodes.GetLength(0);
            int numElements = elements.GetLength(0);

            Console.WriteLine($"Nodos generados: {numNodes}");
            Console.WriteLine($"Elementos generados: {numElements}");
            Console.WriteLine();

            // Mostrar primeros nodos
            Console.WriteLine("Primeros 5 nodos:");
            for (int i = 0; i < Math.Min(5, numNodes); i++)
            {
                Console.WriteLine($"  Nodo {i}: ({nodes[i, 0]:F2}, {nodes[i, 1]:F2})");
            }
            Console.WriteLine();

            // Mostrar primeros elementos
            Console.WriteLine("Primeros 4 elementos:");
            for (int i = 0; i < Math.Min(4, numElements); i++)
            {
                Console.WriteLine($"  Elem {i}: [{elements[i, 0]}, {elements[i, 1]}, {elements[i, 2]}]");
            }
            Console.WriteLine();

            // Test funciones geometricas
            Console.WriteLine("Funciones geometricas:");

            double area = TriangleMesh.TriangleArea(0, 0, 2, 0, 0, 2);
            Console.WriteLine($"  tri_area(0,0, 2,0, 0,2) = {area} (esperado: 2.0)");

            double quality = TriangleMesh.TriangleQuality(0, 0, 1, 0, 0.5, 0.866025);
            Console.WriteLine($"  tri_quality(equilatero) = {quality:F4} (esperado: 1.0)");

            var centroid = TriangleMesh.TriangleCentroid(0, 0, 3, 0, 0, 3);
            Console.WriteLine($"  tri_centroid(0,0, 3,0, 0,3) = ({centroid.x:F2}, {centroid.y:F2}) (esperado: 1.0, 1.0)");
            Console.WriteLine();
        }

        static void TestPlateElement()
        {
            Console.WriteLine("--- TEST 3: Elemento Shell de Placa ---");
            Console.WriteLine();

            // Triangulo de prueba
            double x1 = 0, y1 = 0;
            double x2 = 2, y2 = 0;
            double x3 = 0, y3 = 2;

            // Material
            double E = 210e9;    // Pa
            double nu = 0.3;
            double t = 0.1;     // m (100 mm)

            Console.WriteLine("Triangulo:");
            Console.WriteLine($"  Nodo 1: ({x1}, {y1})");
            Console.WriteLine($"  Nodo 2: ({x2}, {y2})");
            Console.WriteLine($"  Nodo 3: ({x3}, {y3})");
            Console.WriteLine();

            Console.WriteLine("Material:");
            Console.WriteLine($"  E = {E / 1e9} GPa");
            Console.WriteLine($"  nu = {nu}");
            Console.WriteLine($"  t = {t * 1000} mm");
            Console.WriteLine();

            // Calcular matrices
            double[,] Kb = PlateElement.BendingStiffnessMatrix(x1, y1, x2, y2, x3, y3, E, nu, t);
            double[,] Ks = PlateElement.ShearStiffnessMatrix(x1, y1, x2, y2, x3, y3, E, nu, t);
            double[,] K = PlateElement.TotalStiffnessMatrix(x1, y1, x2, y2, x3, y3, E, nu, t);

            Console.WriteLine("Matriz de rigidez de flexion Kb (diagonal):");
            for (int i = 0; i < 9; i++)
            {
                Console.WriteLine($"  Kb[{i},{i}] = {Kb[i, i]:E4}");
            }
            Console.WriteLine();

            Console.WriteLine("Matriz de rigidez de cortante Ks (diagonal):");
            for (int i = 0; i < 9; i++)
            {
                Console.WriteLine($"  Ks[{i},{i}] = {Ks[i, i]:E4}");
            }
            Console.WriteLine();

            // Deflexion analitica
            Console.WriteLine("Deflexion analitica para placa empotrada:");
            double q = 1000;    // N/m2
            double a = 4.0;     // m (lado menor)

            double w_analytical = PlateElement.AnalyticalDeflection(q, a, E, nu, t);
            Console.WriteLine($"  q = {q} N/m2");
            Console.WriteLine($"  a = {a} m");
            Console.WriteLine($"  w_analitico = {w_analytical * 1000:F6} mm");
            Console.WriteLine();

            // Verificar rigidez D
            double D = E * Math.Pow(t, 3) / (12.0 * (1.0 - nu * nu));
            Console.WriteLine($"Rigidez de flexion D = Et^3/(12(1-nu^2)) = {D:E4} N*m");
            Console.WriteLine();
        }
    }
}
