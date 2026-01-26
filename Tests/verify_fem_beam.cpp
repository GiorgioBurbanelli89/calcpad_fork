// Verificación de matriz de rigidez viga 2D
// Compilar: g++ -o verify_fem_beam verify_fem_beam.cpp

#include <iostream>
#include <iomanip>
#include <cmath>

int main() {
    // Parámetros (igual que en Mathcad)
    double E = 210e9;       // Pa (210 GPa)
    double A = 0.01;        // m² (100 cm²)
    double I = 833.3e-8;    // m⁴ (833.3 cm⁴)
    double L = 3.0;         // m

    std::cout << "=== Verificación Matriz Rigidez Viga 2D ===" << std::endl;
    std::cout << std::endl;
    std::cout << "Parámetros:" << std::endl;
    std::cout << "  E = " << E/1e9 << " GPa" << std::endl;
    std::cout << "  A = " << A*1e4 << " cm²" << std::endl;
    std::cout << "  I = " << I*1e8 << " cm⁴" << std::endl;
    std::cout << "  L = " << L << " m" << std::endl;
    std::cout << std::endl;

    // Coeficientes de la matriz
    double EA_L = E * A / L;
    double EI_L3 = E * I / (L * L * L);
    double EI_L2 = E * I / (L * L);
    double EI_L = E * I / L;

    double k11 = EA_L;              // EA/L
    double k22 = 12 * EI_L3;        // 12EI/L³
    double k23 = 6 * EI_L2;         // 6EI/L²
    double k33 = 4 * EI_L;          // 4EI/L
    double k36 = 2 * EI_L;          // 2EI/L

    std::cout << "Coeficientes calculados:" << std::endl;
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "  EA/L     = " << k11 << std::endl;
    std::cout << "  12EI/L³  = " << k22 << std::endl;
    std::cout << "  6EI/L²   = " << k23 << std::endl;
    std::cout << "  4EI/L    = " << k33 << std::endl;
    std::cout << "  2EI/L    = " << k36 << std::endl;
    std::cout << std::endl;

    // Matriz completa 6x6
    double K[6][6] = {
        { k11,    0,     0,   -k11,    0,     0   },
        {   0,  k22,   k23,      0, -k22,   k23   },
        {   0,  k23,   k33,      0, -k23,   k36   },
        {-k11,    0,     0,    k11,    0,     0   },
        {   0, -k22,  -k23,      0,  k22,  -k23   },
        {   0,  k23,   k36,      0, -k23,   k33   }
    };

    std::cout << "Matriz de Rigidez K (6x6):" << std::endl;
    std::cout << std::setprecision(2);
    for (int i = 0; i < 6; i++) {
        std::cout << "  [";
        for (int j = 0; j < 6; j++) {
            std::cout << std::setw(14) << K[i][j];
            if (j < 5) std::cout << ", ";
        }
        std::cout << "]" << std::endl;
    }
    std::cout << std::endl;

    // Comparación con valores de Mathcad
    std::cout << "=== Comparación con Mathcad ===" << std::endl;
    double mathcad_values[6][6] = {
        { 700000000,          0,         0, -700000000,           0,         0},
        {         0,  777746.667,  1166620,          0,  -777746.667,  1166620},
        {         0,    1166620,   2333240,          0,    -1166620,  1166620},
        {-700000000,          0,         0,  700000000,           0,         0},
        {         0, -777746.667, -1166620,          0,   777746.667, -1166620},
        {         0,    1166620,   1166620,          0,    -1166620,  2333240}
    };

    double max_error = 0;
    for (int i = 0; i < 6; i++) {
        for (int j = 0; j < 6; j++) {
            double error = std::abs(K[i][j] - mathcad_values[i][j]);
            if (error > max_error) max_error = error;
        }
    }

    std::cout << "Error máximo: " << max_error << std::endl;
    std::cout << std::endl;

    // Verificación cantilever
    std::cout << "=== Verificación Cantilever ===" << std::endl;
    double P = 1000;  // N
    double defl_teorica = P * L * L * L / (3 * E * I);
    double rot_teorica = P * L * L / (2 * E * I);

    std::cout << std::setprecision(6);
    std::cout << "  P = " << P << " N" << std::endl;
    std::cout << "  Deflexión teórica = PL³/(3EI) = " << defl_teorica * 1000 << " mm" << std::endl;
    std::cout << "  Rotación teórica  = PL²/(2EI) = " << rot_teorica * 1000 << " mrad" << std::endl;

    return 0;
}
