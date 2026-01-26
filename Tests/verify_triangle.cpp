// Verificacion de funciones de mallado triangular
// Para comparar con mathcad_triangle.dll en Mathcad Prime
// Compilar: g++ -o verify_triangle verify_triangle.cpp

#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>

using namespace std;

// Genera coordenadas de nodos
void tri_nodes(double Lx, double Ly, int nx, int ny,
               vector<double>& x, vector<double>& y) {
    int num_nodes = (nx + 1) * (ny + 1);
    x.resize(num_nodes);
    y.resize(num_nodes);

    double dx = Lx / nx;
    double dy = Ly / ny;

    int idx = 0;
    for (int j = 0; j <= ny; j++) {
        for (int i = 0; i <= nx; i++) {
            x[idx] = i * dx;
            y[idx] = j * dy;
            idx++;
        }
    }
}

// Genera conectividad de elementos (base 1)
void tri_elements(int nx, int ny, vector<vector<int>>& elements) {
    int num_tri = 2 * nx * ny;
    elements.resize(num_tri, vector<int>(3));

    int tri_idx = 0;
    for (int j = 0; j < ny; j++) {
        for (int i = 0; i < nx; i++) {
            // Nodos del cuadrilatero (base 1)
            int n1 = j * (nx + 1) + i + 1;
            int n2 = j * (nx + 1) + i + 2;
            int n3 = (j + 1) * (nx + 1) + i + 2;
            int n4 = (j + 1) * (nx + 1) + i + 1;

            // Triangulo 1: n1-n2-n4
            elements[tri_idx][0] = n1;
            elements[tri_idx][1] = n2;
            elements[tri_idx][2] = n4;
            tri_idx++;

            // Triangulo 2: n2-n3-n4
            elements[tri_idx][0] = n2;
            elements[tri_idx][1] = n3;
            elements[tri_idx][2] = n4;
            tri_idx++;
        }
    }
}

// Calcula el area de un triangulo
double tri_area(double x1, double y1, double x2, double y2, double x3, double y3) {
    return 0.5 * fabs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2));
}

// Calcula la calidad de un triangulo (1 = equilatero perfecto)
double tri_quality(double x1, double y1, double x2, double y2, double x3, double y3) {
    // Longitudes de lados al cuadrado
    double a2 = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1);
    double b2 = (x3 - x2) * (x3 - x2) + (y3 - y2) * (y3 - y2);
    double c2 = (x1 - x3) * (x1 - x3) + (y1 - y3) * (y1 - y3);

    // Area
    double area = 0.5 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2));

    // Calidad: 4*sqrt(3)*A / (a^2 + b^2 + c^2)
    if (a2 + b2 + c2 > 0) {
        return 4.0 * 1.7320508075688772 * fabs(area) / (a2 + b2 + c2);
    }
    return 0.0;
}

// Calcula el centroide
void tri_centroid(double x1, double y1, double x2, double y2, double x3, double y3,
                  double& cx, double& cy) {
    cx = (x1 + x2 + x3) / 3.0;
    cy = (y1 + y2 + y3) / 3.0;
}

int main() {
    cout << "============================================================" << endl;
    cout << "  Verificacion de funciones de mallado triangular" << endl;
    cout << "  Para comparar con Mathcad Prime" << endl;
    cout << "============================================================" << endl;
    cout << endl;

    // Parametros de prueba
    double Lx = 6.0, Ly = 4.0;
    int nx = 3, ny = 2;

    cout << "Parametros: Lx=" << Lx << ", Ly=" << Ly;
    cout << ", nx=" << nx << ", ny=" << ny << endl << endl;

    // 1. Generar nodos
    cout << "1. TRI_NODES - Coordenadas de nodos" << endl;
    cout << "----------------------------------------" << endl;
    vector<double> nodes_x, nodes_y;
    tri_nodes(Lx, Ly, nx, ny, nodes_x, nodes_y);
    cout << "   Numero de nodos: " << nodes_x.size() << endl;
    cout << "   Primeros 5 nodos:" << endl;
    cout << fixed << setprecision(4);
    for (int i = 0; i < 5 && i < (int)nodes_x.size(); i++) {
        cout << "     Nodo " << i+1 << ": (" << nodes_x[i] << ", " << nodes_y[i] << ")" << endl;
    }
    cout << endl;

    // 2. Generar elementos
    cout << "2. TRI_ELEMENTS - Conectividad" << endl;
    cout << "----------------------------------------" << endl;
    vector<vector<int>> elements;
    tri_elements(nx, ny, elements);
    cout << "   Numero de triangulos: " << elements.size() << endl;
    cout << "   Primeros 6 elementos:" << endl;
    for (int i = 0; i < 6 && i < (int)elements.size(); i++) {
        cout << "     Elem " << i+1 << ": [" << elements[i][0];
        cout << ", " << elements[i][1] << ", " << elements[i][2] << "]" << endl;
    }
    cout << endl;

    // 3. Calcular area
    cout << "3. TRI_AREA - Area de triangulo" << endl;
    cout << "----------------------------------------" << endl;
    double area1 = tri_area(0, 0, 2, 0, 0, 2);
    cout << "   Triangulo: (0,0), (2,0), (0,2)" << endl;
    cout << setprecision(6);
    cout << "   Area = " << area1 << " (esperado: 2.0)" << endl << endl;

    double h = sqrt(3.0) / 2.0;
    double area_eq = tri_area(0, 0, 1, 0, 0.5, h);
    cout << "   Triangulo equilatero lado 1:" << endl;
    cout << "   Area = " << area_eq << " (esperado: " << sqrt(3.0)/4.0 << ")" << endl << endl;

    // 4. Calidad
    cout << "4. TRI_QUALITY - Calidad de triangulo" << endl;
    cout << "----------------------------------------" << endl;
    double q_eq = tri_quality(0, 0, 1, 0, 0.5, h);
    cout << "   Triangulo equilatero: quality = " << q_eq << " (esperado: 1.0)" << endl;

    double q_rect = tri_quality(0, 0, 2, 0, 0, 2);
    cout << "   Triangulo rectangulo isoceles: quality = " << q_rect << endl;

    double q_thin = tri_quality(0, 0, 10, 0, 5, 0.1);
    cout << "   Triangulo muy alargado: quality = " << q_thin << endl << endl;

    // 5. Centroide
    cout << "5. TRI_CENTROID - Centroide de triangulo" << endl;
    cout << "----------------------------------------" << endl;
    double cx, cy;
    tri_centroid(0, 0, 3, 0, 0, 3, cx, cy);
    cout << "   Triangulo (0,0), (3,0), (0,3)" << endl;
    cout << "   Centroide = (" << cx << ", " << cy << ") (esperado: 1.0, 1.0)" << endl << endl;

    // 6. Resumen para Mathcad
    cout << "============================================================" << endl;
    cout << "  VALORES PARA VERIFICAR EN MATHCAD PRIME" << endl;
    cout << "============================================================" << endl;
    cout << endl;
    cout << "Con Lx=6, Ly=4, nx=3, ny=2:" << endl;
    cout << "  tri_nodes(6,4,3,2) -> matriz " << nodes_x.size() << "x2" << endl;
    cout << "  tri_elements(3,2) -> matriz " << elements.size() << "x3" << endl;
    cout << endl;
    cout << "Pruebas de area:" << endl;
    cout << "  tri_area(0,0, 2,0, 0,2) = " << tri_area(0,0,2,0,0,2) << endl;
    cout << "  tri_area(0,0, 1,0, 0.5," << h << ") = " << area_eq << endl;
    cout << endl;
    cout << "Pruebas de calidad:" << endl;
    cout << "  tri_quality(0,0, 1,0, 0.5," << h << ") = " << q_eq << endl;
    cout << "  tri_quality(0,0, 2,0, 0,2) = " << q_rect << endl;
    cout << endl;
    cout << "Pruebas de centroide:" << endl;
    cout << "  tri_centroid(0,0, 3,0, 0,3) = (" << cx << ", " << cy << ")" << endl;

    return 0;
}
