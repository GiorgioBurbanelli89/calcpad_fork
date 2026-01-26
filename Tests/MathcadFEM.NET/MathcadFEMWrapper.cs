// MathcadFEMWrapper.cs - Wrapper C# para las DLLs de Mathcad FEM
// Este archivo permite usar las funciones de mathcad_fem.dll, mathcad_triangle.dll
// y mathcad_plate.dll desde cualquier aplicacion .NET (C#, VB.NET, F#)

using System;
using System.Runtime.InteropServices;

namespace MathcadFEM.NET
{
    /// <summary>
    /// Wrapper para mathcad_fem.dll - Funciones de matrices de rigidez FEM
    /// </summary>
    public static class FEMBeam
    {
        private const string DllPath = "mathcad_fem.dll";

        /// <summary>
        /// Calcula la deflexion de una viga en voladizo
        /// </summary>
        /// <param name="P">Carga puntual en el extremo (N)</param>
        /// <param name="L">Longitud de la viga (m)</param>
        /// <param name="E">Modulo de elasticidad (Pa)</param>
        /// <param name="I">Momento de inercia (m^4)</param>
        /// <returns>Deflexion maxima (m)</returns>
        [DllImport(DllPath, CallingConvention = CallingConvention.Cdecl, EntryPoint = "cantilever_defl_export")]
        public static extern double CantileverDeflection(double P, double L, double E, double I);

        /// <summary>
        /// Calcula la rotacion de una viga en voladizo
        /// </summary>
        [DllImport(DllPath, CallingConvention = CallingConvention.Cdecl, EntryPoint = "cantilever_rot_export")]
        public static extern double CantileverRotation(double P, double L, double E, double I);

        /// <summary>
        /// Calcula la matriz de rigidez 6x6 para viga 2D (Euler-Bernoulli)
        /// Formula: delta = P*L^3 / (3*E*I)
        /// </summary>
        public static double[,] BeamStiffnessMatrix2D(double E, double A, double I, double L)
        {
            // Implementacion directa en C# (equivalente a fem_beam_K)
            double EA_L = E * A / L;
            double EI_L3 = E * I / (L * L * L);
            double EI_L2 = E * I / (L * L);
            double EI_L = E * I / L;

            double[,] K = new double[6, 6];

            // Rigidez axial
            K[0, 0] = EA_L;
            K[0, 3] = -EA_L;
            K[3, 0] = -EA_L;
            K[3, 3] = EA_L;

            // Rigidez de flexion
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

            return K;
        }

        /// <summary>
        /// Calcula la matriz de rigidez 12x12 para frame 3D
        /// </summary>
        public static double[,] FrameStiffnessMatrix3D(double E, double G, double A, double Iy, double Iz, double J, double L)
        {
            double[,] K = new double[12, 12];

            double EA_L = E * A / L;
            double GJ_L = G * J / L;
            double EIy_L3 = E * Iy / (L * L * L);
            double EIy_L2 = E * Iy / (L * L);
            double EIy_L = E * Iy / L;
            double EIz_L3 = E * Iz / (L * L * L);
            double EIz_L2 = E * Iz / (L * L);
            double EIz_L = E * Iz / L;

            // Rigidez axial (DOF 0, 6)
            K[0, 0] = EA_L; K[0, 6] = -EA_L;
            K[6, 0] = -EA_L; K[6, 6] = EA_L;

            // Rigidez torsional (DOF 3, 9)
            K[3, 3] = GJ_L; K[3, 9] = -GJ_L;
            K[9, 3] = -GJ_L; K[9, 9] = GJ_L;

            // Flexion en plano XY (DOF 1, 5, 7, 11)
            K[1, 1] = 12 * EIz_L3; K[1, 5] = 6 * EIz_L2;
            K[1, 7] = -12 * EIz_L3; K[1, 11] = 6 * EIz_L2;
            K[5, 1] = 6 * EIz_L2; K[5, 5] = 4 * EIz_L;
            K[5, 7] = -6 * EIz_L2; K[5, 11] = 2 * EIz_L;
            K[7, 1] = -12 * EIz_L3; K[7, 5] = -6 * EIz_L2;
            K[7, 7] = 12 * EIz_L3; K[7, 11] = -6 * EIz_L2;
            K[11, 1] = 6 * EIz_L2; K[11, 5] = 2 * EIz_L;
            K[11, 7] = -6 * EIz_L2; K[11, 11] = 4 * EIz_L;

            // Flexion en plano XZ (DOF 2, 4, 8, 10)
            K[2, 2] = 12 * EIy_L3; K[2, 4] = -6 * EIy_L2;
            K[2, 8] = -12 * EIy_L3; K[2, 10] = -6 * EIy_L2;
            K[4, 2] = -6 * EIy_L2; K[4, 4] = 4 * EIy_L;
            K[4, 8] = 6 * EIy_L2; K[4, 10] = 2 * EIy_L;
            K[8, 2] = -12 * EIy_L3; K[8, 4] = 6 * EIy_L2;
            K[8, 8] = 12 * EIy_L3; K[8, 10] = 6 * EIy_L2;
            K[10, 2] = -6 * EIy_L2; K[10, 4] = 2 * EIy_L;
            K[10, 8] = 6 * EIy_L2; K[10, 10] = 4 * EIy_L;

            return K;
        }
    }

    /// <summary>
    /// Wrapper para mathcad_triangle.dll - Funciones de generacion de mallas
    /// </summary>
    public static class TriangleMesh
    {
        /// <summary>
        /// Genera nodos para malla rectangular
        /// </summary>
        public static double[,] GenerateNodes(double Lx, double Ly, int nx, int ny)
        {
            int numNodes = (nx + 1) * (ny + 1);
            double[,] nodes = new double[numNodes, 2];

            double dx = Lx / nx;
            double dy = Ly / ny;

            int idx = 0;
            for (int j = 0; j <= ny; j++)
            {
                for (int i = 0; i <= nx; i++)
                {
                    nodes[idx, 0] = i * dx;
                    nodes[idx, 1] = j * dy;
                    idx++;
                }
            }

            return nodes;
        }

        /// <summary>
        /// Genera conectividad de elementos triangulares (base 0)
        /// </summary>
        public static int[,] GenerateElements(int nx, int ny)
        {
            int numElements = 2 * nx * ny;
            int[,] elements = new int[numElements, 3];

            int idx = 0;
            for (int j = 0; j < ny; j++)
            {
                for (int i = 0; i < nx; i++)
                {
                    int n1 = j * (nx + 1) + i;
                    int n2 = j * (nx + 1) + i + 1;
                    int n3 = (j + 1) * (nx + 1) + i + 1;
                    int n4 = (j + 1) * (nx + 1) + i;

                    // Triangulo 1: n1-n2-n4
                    elements[idx, 0] = n1;
                    elements[idx, 1] = n2;
                    elements[idx, 2] = n4;
                    idx++;

                    // Triangulo 2: n2-n3-n4
                    elements[idx, 0] = n2;
                    elements[idx, 1] = n3;
                    elements[idx, 2] = n4;
                    idx++;
                }
            }

            return elements;
        }

        /// <summary>
        /// Calcula el area de un triangulo
        /// </summary>
        public static double TriangleArea(double x1, double y1, double x2, double y2, double x3, double y3)
        {
            double area = 0.5 * Math.Abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1));
            return area;
        }

        /// <summary>
        /// Calcula la calidad del triangulo (1.0 = equilatero)
        /// </summary>
        public static double TriangleQuality(double x1, double y1, double x2, double y2, double x3, double y3)
        {
            double a = Math.Sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
            double b = Math.Sqrt((x3 - x2) * (x3 - x2) + (y3 - y2) * (y3 - y2));
            double c = Math.Sqrt((x1 - x3) * (x1 - x3) + (y1 - y3) * (y1 - y3));

            double s = (a + b + c) / 2.0;
            double area = Math.Sqrt(s * (s - a) * (s - b) * (s - c));

            // Calidad = 4 * sqrt(3) * area / (a^2 + b^2 + c^2)
            double quality = 4.0 * Math.Sqrt(3.0) * area / (a * a + b * b + c * c);
            return quality;
        }

        /// <summary>
        /// Calcula el centroide del triangulo
        /// </summary>
        public static (double x, double y) TriangleCentroid(double x1, double y1, double x2, double y2, double x3, double y3)
        {
            return ((x1 + x2 + x3) / 3.0, (y1 + y2 + y3) / 3.0);
        }
    }

    /// <summary>
    /// Wrapper para mathcad_plate.dll - Funciones de analisis de placas
    /// </summary>
    public static class PlateElement
    {
        /// <summary>
        /// Calcula la matriz de rigidez de flexion 9x9 para elemento shell triangular
        /// Teoria de Mindlin-Reissner
        /// </summary>
        public static double[,] BendingStiffnessMatrix(
            double x1, double y1,
            double x2, double y2,
            double x3, double y3,
            double E, double nu, double t)
        {
            double area = TriangleMesh.TriangleArea(x1, y1, x2, y2, x3, y3);
            if (area < 1e-12) return new double[9, 9];

            // Matriz constitutiva de flexion
            double D = E * Math.Pow(t, 3) / (12.0 * (1.0 - nu * nu));
            double[,] Db = new double[3, 3]
            {
                { D,      D * nu,  0 },
                { D * nu, D,       0 },
                { 0,      0,       D * (1 - nu) / 2 }
            };

            // Derivadas de funciones de forma
            double b1 = y2 - y3;
            double b2 = y3 - y1;
            double b3 = y1 - y2;
            double c1 = x3 - x2;
            double c2 = x1 - x3;
            double c3 = x2 - x1;

            double inv2A = 1.0 / (2.0 * area);

            // Matriz Bb (3x9)
            double[,] Bb = new double[3, 9];

            // dNi/dx para theta_y (curvatura kappa_x)
            Bb[0, 2] = b1 * inv2A;
            Bb[0, 5] = b2 * inv2A;
            Bb[0, 8] = b3 * inv2A;

            // dNi/dy para -theta_x (curvatura kappa_y)
            Bb[1, 1] = -c1 * inv2A;
            Bb[1, 4] = -c2 * inv2A;
            Bb[1, 7] = -c3 * inv2A;

            // Curvatura de torsion
            Bb[2, 1] = -b1 * inv2A;
            Bb[2, 2] = c1 * inv2A;
            Bb[2, 4] = -b2 * inv2A;
            Bb[2, 5] = c2 * inv2A;
            Bb[2, 7] = -b3 * inv2A;
            Bb[2, 8] = c3 * inv2A;

            // Kb = Bb^T * Db * Bb * area
            return MatrixMultiply(MatrixMultiply(Transpose(Bb), Db), Bb, area);
        }

        /// <summary>
        /// Calcula la matriz de rigidez de cortante 9x9 para elemento shell triangular
        /// </summary>
        public static double[,] ShearStiffnessMatrix(
            double x1, double y1,
            double x2, double y2,
            double x3, double y3,
            double E, double nu, double t)
        {
            double area = TriangleMesh.TriangleArea(x1, y1, x2, y2, x3, y3);
            if (area < 1e-12) return new double[9, 9];

            // Factor de correccion de cortante
            double kappa = 5.0 / 6.0;
            double G = E / (2.0 * (1.0 + nu));
            double Ds_val = kappa * G * t;

            // Funciones de forma en centroide
            double N1 = 1.0 / 3.0, N2 = 1.0 / 3.0, N3 = 1.0 / 3.0;

            // Derivadas de N
            double inv2A = 1.0 / (2.0 * area);
            double dN1dx = (y2 - y3) * inv2A;
            double dN2dx = (y3 - y1) * inv2A;
            double dN3dx = (y1 - y2) * inv2A;
            double dN1dy = (x3 - x2) * inv2A;
            double dN2dy = (x1 - x3) * inv2A;
            double dN3dy = (x2 - x1) * inv2A;

            // Matriz Bs (2x9)
            double[,] Bs = new double[2, 9];

            // gamma_xz = dw/dx - theta_y
            Bs[0, 0] = dN1dx; Bs[0, 2] = -N1;
            Bs[0, 3] = dN2dx; Bs[0, 5] = -N2;
            Bs[0, 6] = dN3dx; Bs[0, 8] = -N3;

            // gamma_yz = dw/dy + theta_x
            Bs[1, 0] = dN1dy; Bs[1, 1] = N1;
            Bs[1, 3] = dN2dy; Bs[1, 4] = N2;
            Bs[1, 6] = dN3dy; Bs[1, 7] = N3;

            // Ds matrix
            double[,] Ds = new double[2, 2]
            {
                { Ds_val, 0 },
                { 0, Ds_val }
            };

            // Ks = Bs^T * Ds * Bs * area
            return MatrixMultiply(MatrixMultiply(Transpose(Bs), Ds), Bs, area);
        }

        /// <summary>
        /// Calcula la matriz de rigidez total 9x9 (flexion + cortante)
        /// </summary>
        public static double[,] TotalStiffnessMatrix(
            double x1, double y1,
            double x2, double y2,
            double x3, double y3,
            double E, double nu, double t)
        {
            double[,] Kb = BendingStiffnessMatrix(x1, y1, x2, y2, x3, y3, E, nu, t);
            double[,] Ks = ShearStiffnessMatrix(x1, y1, x2, y2, x3, y3, E, nu, t);

            double[,] K = new double[9, 9];
            for (int i = 0; i < 9; i++)
            {
                for (int j = 0; j < 9; j++)
                {
                    K[i, j] = Kb[i, j] + Ks[i, j];
                }
            }
            return K;
        }

        /// <summary>
        /// Deflexion analitica para placa cuadrada empotrada
        /// </summary>
        public static double AnalyticalDeflection(double q, double a, double E, double nu, double t)
        {
            double D = E * Math.Pow(t, 3) / (12.0 * (1.0 - nu * nu));
            return 0.00126 * Math.Abs(q) * Math.Pow(a, 4) / D;
        }

        #region Matrix Helpers
        private static double[,] Transpose(double[,] A)
        {
            int rows = A.GetLength(0);
            int cols = A.GetLength(1);
            double[,] result = new double[cols, rows];
            for (int i = 0; i < rows; i++)
                for (int j = 0; j < cols; j++)
                    result[j, i] = A[i, j];
            return result;
        }

        private static double[,] MatrixMultiply(double[,] A, double[,] B, double scale = 1.0)
        {
            int rowsA = A.GetLength(0);
            int colsA = A.GetLength(1);
            int colsB = B.GetLength(1);
            double[,] result = new double[rowsA, colsB];

            for (int i = 0; i < rowsA; i++)
            {
                for (int j = 0; j < colsB; j++)
                {
                    double sum = 0;
                    for (int k = 0; k < colsA; k++)
                        sum += A[i, k] * B[k, j];
                    result[i, j] = sum * scale;
                }
            }
            return result;
        }
        #endregion
    }
}
