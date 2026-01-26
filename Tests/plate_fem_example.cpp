/*
 * plate_fem_example.cpp - Ejemplo de placa FEM simplificado
 * Basado en Awatif-FEM (elementos shell triangulares)
 *
 * Compilar: g++ -I C:\Users\j-b-j\eigen -o plate_fem_example plate_fem_example.cpp
 */

#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
#include <Eigen/Dense>
#include <Eigen/Sparse>

using namespace std;
using namespace Eigen;

// ============================================================
// CONSTANTES
// ============================================================
const double PI = 3.14159265358979323846;

// ============================================================
// ESTRUCTURAS DE DATOS
// ============================================================
struct Node {
    double x, y, z;
};

struct Element {
    int n1, n2, n3;  // Indices de nodos (base 0)
};

struct Material {
    double E;    // Modulo de elasticidad
    double nu;   // Coeficiente de Poisson
    double t;    // Espesor
};

// ============================================================
// FUNCIONES DE GENERACION DE MALLA
// ============================================================
void generateRectangularMesh(
    double Lx, double Ly, int nx, int ny,
    vector<Node>& nodes, vector<Element>& elements)
{
    nodes.clear();
    elements.clear();

    double dx = Lx / nx;
    double dy = Ly / ny;

    // Generar nodos
    for (int j = 0; j <= ny; j++) {
        for (int i = 0; i <= nx; i++) {
            Node n;
            n.x = i * dx;
            n.y = j * dy;
            n.z = 0;
            nodes.push_back(n);
        }
    }

    // Generar elementos triangulares
    for (int j = 0; j < ny; j++) {
        for (int i = 0; i < nx; i++) {
            int n1 = j * (nx + 1) + i;
            int n2 = j * (nx + 1) + i + 1;
            int n3 = (j + 1) * (nx + 1) + i + 1;
            int n4 = (j + 1) * (nx + 1) + i;

            // Triangulo 1: n1-n2-n4
            Element e1;
            e1.n1 = n1; e1.n2 = n2; e1.n3 = n4;
            elements.push_back(e1);

            // Triangulo 2: n2-n3-n4
            Element e2;
            e2.n1 = n2; e2.n2 = n3; e2.n3 = n4;
            elements.push_back(e2);
        }
    }
}

// ============================================================
// MATRIZ DE RIGIDEZ PARA PLACA (MINDLIN-REISSNER SIMPLIFICADO)
// ============================================================
double triangleArea(const Node& n1, const Node& n2, const Node& n3) {
    double x21 = n2.x - n1.x;
    double y21 = n2.y - n1.y;
    double x31 = n3.x - n1.x;
    double y31 = n3.y - n1.y;
    return 0.5 * abs(x21 * y31 - x31 * y21);
}

// Matriz de rigidez de flexion para triangulo (3 DOF por nodo: w, theta_x, theta_y)
MatrixXd getBendingStiffnessMatrix(
    const Node& n1, const Node& n2, const Node& n3,
    double E, double nu, double t)
{
    double A = triangleArea(n1, n2, n3);
    if (A < 1e-12) return MatrixXd::Zero(9, 9);

    // Matriz constitutiva de flexion D_b
    double D = E * t * t * t / (12.0 * (1.0 - nu * nu));
    Matrix3d Db;
    Db << 1,   nu,  0,
          nu,  1,   0,
          0,   0,   (1-nu)/2;
    Db *= D;

    // Coordenadas
    double x1 = n1.x, y1 = n1.y;
    double x2 = n2.x, y2 = n2.y;
    double x3 = n3.x, y3 = n3.y;

    // Derivadas de funciones de forma
    double b1 = y2 - y3;
    double b2 = y3 - y1;
    double b3 = y1 - y2;
    double c1 = x3 - x2;
    double c2 = x1 - x3;
    double c3 = x2 - x1;

    // Matriz B de deformacion-curvatura (simplificada)
    MatrixXd Bb = MatrixXd::Zero(3, 9);
    double inv2A = 1.0 / (2.0 * A);

    // dNi/dx para theta_y
    Bb(0, 2) = b1 * inv2A;
    Bb(0, 5) = b2 * inv2A;
    Bb(0, 8) = b3 * inv2A;

    // dNi/dy para -theta_x
    Bb(1, 1) = -c1 * inv2A;
    Bb(1, 4) = -c2 * inv2A;
    Bb(1, 7) = -c3 * inv2A;

    // dNi/dy para theta_y + dNi/dx para -theta_x
    Bb(2, 1) = -b1 * inv2A;
    Bb(2, 2) = c1 * inv2A;
    Bb(2, 4) = -b2 * inv2A;
    Bb(2, 5) = c2 * inv2A;
    Bb(2, 7) = -b3 * inv2A;
    Bb(2, 8) = c3 * inv2A;

    return Bb.transpose() * Db * Bb * A;
}

// Matriz de rigidez de cortante para triangulo
MatrixXd getShearStiffnessMatrix(
    const Node& n1, const Node& n2, const Node& n3,
    double E, double nu, double t)
{
    double A = triangleArea(n1, n2, n3);
    if (A < 1e-12) return MatrixXd::Zero(9, 9);

    // Factor de correccion de cortante
    double kappa = 5.0 / 6.0;
    double G = E / (2.0 * (1.0 + nu));
    double Ds_val = kappa * G * t;

    Matrix2d Ds;
    Ds << Ds_val, 0,
          0,      Ds_val;

    // Coordenadas
    double x1 = n1.x, y1 = n1.y;
    double x2 = n2.x, y2 = n2.y;
    double x3 = n3.x, y3 = n3.y;

    // Centroide
    double xc = (x1 + x2 + x3) / 3.0;
    double yc = (y1 + y2 + y3) / 3.0;

    // Funciones de forma en centroide
    double N1 = 1.0 / 3.0;
    double N2 = 1.0 / 3.0;
    double N3 = 1.0 / 3.0;

    // Derivadas de N
    double inv2A = 1.0 / (2.0 * A);
    double dN1dx = (y2 - y3) * inv2A;
    double dN2dx = (y3 - y1) * inv2A;
    double dN3dx = (y1 - y2) * inv2A;
    double dN1dy = (x3 - x2) * inv2A;
    double dN2dy = (x1 - x3) * inv2A;
    double dN3dy = (x2 - x1) * inv2A;

    // Matriz Bs (gamma = dw/dx - theta_y, dw/dy + theta_x)
    MatrixXd Bs = MatrixXd::Zero(2, 9);

    // gamma_xz = dw/dx - theta_y
    Bs(0, 0) = dN1dx;  Bs(0, 2) = -N1;
    Bs(0, 3) = dN2dx;  Bs(0, 5) = -N2;
    Bs(0, 6) = dN3dx;  Bs(0, 8) = -N3;

    // gamma_yz = dw/dy + theta_x
    Bs(1, 0) = dN1dy;  Bs(1, 1) = N1;
    Bs(1, 3) = dN2dy;  Bs(1, 4) = N2;
    Bs(1, 6) = dN3dy;  Bs(1, 7) = N3;

    return Bs.transpose() * Ds * Bs * A;
}

// Matriz de rigidez local completa del elemento shell
MatrixXd getLocalStiffnessMatrix(
    const Node& n1, const Node& n2, const Node& n3,
    const Material& mat)
{
    MatrixXd Kb = getBendingStiffnessMatrix(n1, n2, n3, mat.E, mat.nu, mat.t);
    MatrixXd Ks = getShearStiffnessMatrix(n1, n2, n3, mat.E, mat.nu, mat.t);
    return Kb + Ks;
}

// ============================================================
// ENSAMBLAJE GLOBAL
// ============================================================
SparseMatrix<double> assembleGlobalStiffness(
    const vector<Node>& nodes,
    const vector<Element>& elements,
    const Material& mat)
{
    int numNodes = nodes.size();
    int dof = numNodes * 3;  // 3 DOF por nodo (w, theta_x, theta_y)

    SparseMatrix<double> K(dof, dof);
    vector<Triplet<double>> triplets;

    for (size_t e = 0; e < elements.size(); e++) {
        const Element& elem = elements[e];
        const Node& n1 = nodes[elem.n1];
        const Node& n2 = nodes[elem.n2];
        const Node& n3 = nodes[elem.n3];

        MatrixXd Ke = getLocalStiffnessMatrix(n1, n2, n3, mat);

        // Indices de DOF
        int dofs[9] = {
            elem.n1 * 3,     elem.n1 * 3 + 1, elem.n1 * 3 + 2,
            elem.n2 * 3,     elem.n2 * 3 + 1, elem.n2 * 3 + 2,
            elem.n3 * 3,     elem.n3 * 3 + 1, elem.n3 * 3 + 2
        };

        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < 9; j++) {
                if (abs(Ke(i, j)) > 1e-15) {
                    triplets.push_back(Triplet<double>(dofs[i], dofs[j], Ke(i, j)));
                }
            }
        }
    }

    K.setFromTriplets(triplets.begin(), triplets.end());
    return K;
}

// ============================================================
// APLICAR CONDICIONES DE FRONTERA
// ============================================================
void applyBoundaryConditions(
    SparseMatrix<double>& K,
    VectorXd& F,
    const vector<int>& fixedDofs)
{
    // Metodo de penalizacion
    double penalty = 1e20;

    for (int dof : fixedDofs) {
        K.coeffRef(dof, dof) += penalty;
        F(dof) = 0;
    }
}

// ============================================================
// MAIN
// ============================================================
int main() {
    cout << "============================================================" << endl;
    cout << "  Ejemplo de Placa FEM - Elementos Shell Triangulares" << endl;
    cout << "  (Similar al ejemplo plate de Awatif)" << endl;
    cout << "============================================================" << endl;
    cout << endl;

    // Parametros de la placa
    double Lx = 6.0;   // Longitud en X (m)
    double Ly = 4.0;   // Longitud en Y (m)
    int nx = 3;        // Divisiones en X
    int ny = 2;        // Divisiones en Y

    // Material
    Material mat;
    mat.E = 210e9;     // Modulo de Young (Pa)
    mat.nu = 0.3;      // Coeficiente de Poisson
    mat.t = 0.1;       // Espesor (m)

    // Carga distribuida
    double q = -1000;  // N/m² (carga uniforme hacia abajo)

    cout << "Parametros:" << endl;
    cout << "  Placa: " << Lx << " x " << Ly << " m" << endl;
    cout << "  Malla: " << nx << " x " << ny << " elementos" << endl;
    cout << "  E = " << mat.E / 1e9 << " GPa" << endl;
    cout << "  nu = " << mat.nu << endl;
    cout << "  t = " << mat.t * 1000 << " mm" << endl;
    cout << "  q = " << q << " N/m²" << endl;
    cout << endl;

    // Generar malla
    vector<Node> nodes;
    vector<Element> elements;
    generateRectangularMesh(Lx, Ly, nx, ny, nodes, elements);

    cout << "Malla generada:" << endl;
    cout << "  Nodos: " << nodes.size() << endl;
    cout << "  Elementos: " << elements.size() << endl;
    cout << endl;

    // Ensamblar matriz de rigidez global
    int numNodes = nodes.size();
    int dof = numNodes * 3;

    SparseMatrix<double> K = assembleGlobalStiffness(nodes, elements, mat);

    // Vector de fuerzas (carga distribuida convertida a nodal)
    VectorXd F = VectorXd::Zero(dof);
    double area_per_node = (Lx * Ly) / numNodes;
    for (int i = 0; i < numNodes; i++) {
        F(i * 3) = q * area_per_node;  // Fuerza en w
    }

    // Condiciones de frontera: bordes empotrados
    vector<int> fixedDofs;
    for (int i = 0; i < numNodes; i++) {
        double x = nodes[i].x;
        double y = nodes[i].y;

        // Nodos en los bordes
        if (abs(x) < 1e-6 || abs(x - Lx) < 1e-6 ||
            abs(y) < 1e-6 || abs(y - Ly) < 1e-6) {
            fixedDofs.push_back(i * 3);      // w = 0
            fixedDofs.push_back(i * 3 + 1);  // theta_x = 0
            fixedDofs.push_back(i * 3 + 2);  // theta_y = 0
        }
    }

    cout << "Condiciones de frontera:" << endl;
    cout << "  Nodos fijos en bordes: " << fixedDofs.size() / 3 << endl;
    cout << endl;

    // Aplicar condiciones de frontera
    applyBoundaryConditions(K, F, fixedDofs);

    // Resolver sistema
    ConjugateGradient<SparseMatrix<double>, Lower|Upper> solver;
    solver.compute(K);

    if (solver.info() != Success) {
        cerr << "Error: Descomposicion de matriz fallida" << endl;
        return 1;
    }

    VectorXd U = solver.solve(F);

    if (solver.info() != Success) {
        cerr << "Error: Solucion fallida" << endl;
        return 1;
    }

    // Resultados
    cout << "============================================================" << endl;
    cout << "  RESULTADOS" << endl;
    cout << "============================================================" << endl;
    cout << endl;

    // Encontrar desplazamiento maximo
    double wmax = 0;
    int nodeMax = -1;
    for (int i = 0; i < numNodes; i++) {
        double w = U(i * 3);
        if (abs(w) > abs(wmax)) {
            wmax = w;
            nodeMax = i;
        }
    }

    cout << fixed << setprecision(6);
    cout << "Desplazamiento maximo (w):" << endl;
    cout << "  Nodo " << nodeMax << " en (" << nodes[nodeMax].x << ", " << nodes[nodeMax].y << ")" << endl;
    cout << "  w_max = " << wmax * 1000 << " mm" << endl;
    cout << endl;

    // Solucion analitica para placa rectangular empotrada (aproximacion)
    // w_max ≈ 0.00126 * q * a^4 / (D) donde D = E*t³/(12*(1-nu²))
    double D = mat.E * pow(mat.t, 3) / (12.0 * (1.0 - mat.nu * mat.nu));
    double a = min(Lx, Ly);
    double w_analytical = 0.00126 * abs(q) * pow(a, 4) / D;

    cout << "Comparacion con solucion analitica (placa empotrada):" << endl;
    cout << "  w_analitico ≈ " << w_analytical * 1000 << " mm" << endl;
    cout << "  Error: " << abs(abs(wmax) - w_analytical) / w_analytical * 100 << " %" << endl;
    cout << endl;

    // Mostrar algunos desplazamientos
    cout << "Desplazamientos en nodos centrales:" << endl;
    cout << setw(6) << "Nodo" << setw(10) << "x" << setw(10) << "y";
    cout << setw(15) << "w (mm)" << setw(15) << "theta_x" << setw(15) << "theta_y" << endl;

    for (int i = 0; i < numNodes; i++) {
        double x = nodes[i].x;
        double y = nodes[i].y;

        // Solo nodos interiores
        if (x > 0.5 && x < Lx - 0.5 && y > 0.5 && y < Ly - 0.5) {
            cout << setw(6) << i;
            cout << setw(10) << x << setw(10) << y;
            cout << setw(15) << U(i * 3) * 1000;
            cout << setw(15) << U(i * 3 + 1);
            cout << setw(15) << U(i * 3 + 2) << endl;
        }
    }

    return 0;
}
