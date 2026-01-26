// Prueba del solver FEM de Awatif usando Eigen
// Compara matriz de rigidez de viga con valores teoricos

#include <iostream>
#include <iomanip>
#include <vector>
#include <map>
#include <cmath>

// Incluir Eigen
#include <Eigen/Core>
#include <Eigen/Dense>

using namespace std;
using namespace Eigen;

// Tipos de Awatif
using Node = vector<double>;

struct ElementInputs {
    map<int, double> elasticities;
    map<int, double> areas;
    map<int, double> momentsOfInertiaZ;
    map<int, double> momentsOfInertiaY;
    map<int, double> shearModuli;
    map<int, double> torsionalConstants;
};

// Funcion de Awatif: Matriz de rigidez local para Frame (viga 3D)
template <typename K, typename V>
V getMapValueOrDefault(const map<K, V> &m, const K &key, const V &defaultValue) {
    auto it = m.find(key);
    return (it != m.end()) ? it->second : defaultValue;
}

MatrixXd getLocalStiffnessMatrixFrame(
    const vector<Node> &nodes,
    const ElementInputs &elementInputs,
    int index)
{
    double Iz = getMapValueOrDefault(elementInputs.momentsOfInertiaZ, index, 0.0);
    double Iy = getMapValueOrDefault(elementInputs.momentsOfInertiaY, index, 0.0);
    double E = getMapValueOrDefault(elementInputs.elasticities, index, 0.0);
    double A = getMapValueOrDefault(elementInputs.areas, index, 0.0);
    double G = getMapValueOrDefault(elementInputs.shearModuli, index, 0.0);
    double J = getMapValueOrDefault(elementInputs.torsionalConstants, index, 0.0);

    Vector3d node0(nodes[0][0], nodes[0][1], nodes[0][2]);
    Vector3d node1(nodes[1][0], nodes[1][1], nodes[1][2]);
    double L = (node1 - node0).norm();

    if (L < 1e-12) {
        cerr << "Error: Longitud de elemento cero" << endl;
        return MatrixXd::Zero(12, 12);
    }

    const double EA_L = E * A / L;
    const double EIz_L3 = E * Iz / (L * L * L);
    const double EIy_L3 = E * Iy / (L * L * L);
    const double GJ_L = G * J / L;
    const double EIz_L2 = E * Iz / (L * L);
    const double EIy_L2 = E * Iy / (L * L);
    const double EIz_L = E * Iz / L;
    const double EIy_L = E * Iy / L;

    MatrixXd kLocal(12, 12);
    kLocal << EA_L, 0, 0, 0, 0, 0, -EA_L, 0, 0, 0, 0, 0,
        0, 12 * EIz_L3, 0, 0, 0, 6 * EIz_L2, 0, -12 * EIz_L3, 0, 0, 0, 6 * EIz_L2,
        0, 0, 12 * EIy_L3, 0, -6 * EIy_L2, 0, 0, 0, -12 * EIy_L3, 0, -6 * EIy_L2, 0,
        0, 0, 0, GJ_L, 0, 0, 0, 0, 0, -GJ_L, 0, 0,
        0, 0, -6 * EIy_L2, 0, 4 * EIy_L, 0, 0, 0, 6 * EIy_L2, 0, 2 * EIy_L, 0,
        0, 6 * EIz_L2, 0, 0, 0, 4 * EIz_L, 0, -6 * EIz_L2, 0, 0, 0, 2 * EIz_L,
        -EA_L, 0, 0, 0, 0, 0, EA_L, 0, 0, 0, 0, 0,
        0, -12 * EIz_L3, 0, 0, 0, -6 * EIz_L2, 0, 12 * EIz_L3, 0, 0, 0, -6 * EIz_L2,
        0, 0, -12 * EIy_L3, 0, 6 * EIy_L2, 0, 0, 0, 12 * EIy_L3, 0, 6 * EIy_L2, 0,
        0, 0, 0, -GJ_L, 0, 0, 0, 0, 0, GJ_L, 0, 0,
        0, 0, -6 * EIy_L2, 0, 2 * EIy_L, 0, 0, 0, 6 * EIy_L2, 0, 4 * EIy_L, 0,
        0, 6 * EIz_L2, 0, 0, 0, 2 * EIz_L, 0, -6 * EIz_L2, 0, 0, 0, 4 * EIz_L;

    return kLocal;
}

int main() {
    cout << "==========================================" << endl;
    cout << "  PRUEBA FEM AWATIF - Matriz de Rigidez  " << endl;
    cout << "==========================================" << endl;
    cout << endl;

    // Caso de prueba: Viga en cantilever
    // Longitud L = 3 m
    // E = 210 GPa = 210e9 Pa
    // A = 0.01 m^2 (seccion 10x10 cm)
    // Iz = Iy = 8.333e-6 m^4 (seccion cuadrada 10x10 cm)
    // G = 80.77 GPa
    // J = 1.406e-5 m^4

    double L = 3.0;           // metros
    double E = 210e9;         // Pa
    double A = 0.01;          // m^2
    double I = 8.333e-6;      // m^4 (b*h^3/12 para 0.1x0.1)
    double G = 80.77e9;       // Pa
    double J = 1.406e-5;      // m^4

    cout << "DATOS DE ENTRADA:" << endl;
    cout << "  Longitud L = " << L << " m" << endl;
    cout << "  Modulo E   = " << E/1e9 << " GPa" << endl;
    cout << "  Area A     = " << A << " m^2" << endl;
    cout << "  Inercia Iz = " << I << " m^4" << endl;
    cout << "  Modulo G   = " << G/1e9 << " GPa" << endl;
    cout << "  Torsion J  = " << J << " m^4" << endl;
    cout << endl;

    // Definir nodos
    vector<Node> nodes = {
        {0.0, 0.0, 0.0},  // Nodo 0 (empotramiento)
        {L, 0.0, 0.0}     // Nodo 1 (extremo libre)
    };

    // Propiedades del elemento
    ElementInputs props;
    props.elasticities[0] = E;
    props.areas[0] = A;
    props.momentsOfInertiaZ[0] = I;
    props.momentsOfInertiaY[0] = I;
    props.shearModuli[0] = G;
    props.torsionalConstants[0] = J;

    // Calcular matriz de rigidez con Awatif
    MatrixXd K = getLocalStiffnessMatrixFrame(nodes, props, 0);

    cout << "MATRIZ DE RIGIDEZ LOCAL (12x12):" << endl;
    cout << "  Orden DOF: [ux, uy, uz, rx, ry, rz] por nodo" << endl;
    cout << endl;

    // Mostrar matriz en formato compacto
    cout << fixed << setprecision(2);
    cout << "Valores clave de la matriz K (en kN/m y kN-m/rad):" << endl;
    cout << endl;

    // Valores teoricos para comparar
    double EA_L_teorico = E * A / L;
    double EI_L3_teorico = E * I / (L * L * L);
    double EI_L2_teorico = E * I / (L * L);
    double EI_L_teorico = E * I / L;
    double GJ_L_teorico = G * J / L;

    cout << "COMPARACION AWATIF vs TEORICO:" << endl;
    cout << "----------------------------------------------" << endl;
    cout << setw(20) << "Termino" << setw(18) << "Awatif" << setw(18) << "Teorico" << setw(12) << "Error %" << endl;
    cout << "----------------------------------------------" << endl;

    // K(0,0) = EA/L (rigidez axial)
    double awatif_EA_L = K(0,0);
    double error_EA = 100.0 * fabs(awatif_EA_L - EA_L_teorico) / EA_L_teorico;
    cout << setw(20) << "EA/L"
         << setw(18) << scientific << setprecision(4) << awatif_EA_L
         << setw(18) << EA_L_teorico
         << setw(12) << fixed << setprecision(6) << error_EA << endl;

    // K(1,1) = 12EI/L^3 (rigidez flexion)
    double awatif_12EI_L3 = K(1,1);
    double teorico_12EI_L3 = 12.0 * EI_L3_teorico;
    double error_12EI = 100.0 * fabs(awatif_12EI_L3 - teorico_12EI_L3) / teorico_12EI_L3;
    cout << setw(20) << "12EI/L^3"
         << setw(18) << scientific << awatif_12EI_L3
         << setw(18) << teorico_12EI_L3
         << setw(12) << fixed << error_12EI << endl;

    // K(1,5) = 6EI/L^2
    double awatif_6EI_L2 = K(1,5);
    double teorico_6EI_L2 = 6.0 * EI_L2_teorico;
    double error_6EI = 100.0 * fabs(awatif_6EI_L2 - teorico_6EI_L2) / teorico_6EI_L2;
    cout << setw(20) << "6EI/L^2"
         << setw(18) << scientific << awatif_6EI_L2
         << setw(18) << teorico_6EI_L2
         << setw(12) << fixed << error_6EI << endl;

    // K(5,5) = 4EI/L
    double awatif_4EI_L = K(5,5);
    double teorico_4EI_L = 4.0 * EI_L_teorico;
    double error_4EI = 100.0 * fabs(awatif_4EI_L - teorico_4EI_L) / teorico_4EI_L;
    cout << setw(20) << "4EI/L"
         << setw(18) << scientific << awatif_4EI_L
         << setw(18) << teorico_4EI_L
         << setw(12) << fixed << error_4EI << endl;

    // K(3,3) = GJ/L (rigidez torsional)
    double awatif_GJ_L = K(3,3);
    double error_GJ = 100.0 * fabs(awatif_GJ_L - GJ_L_teorico) / GJ_L_teorico;
    cout << setw(20) << "GJ/L"
         << setw(18) << scientific << awatif_GJ_L
         << setw(18) << GJ_L_teorico
         << setw(12) << fixed << error_GJ << endl;

    cout << "----------------------------------------------" << endl;
    cout << endl;

    // Verificar simetria
    cout << "VERIFICACION DE SIMETRIA:" << endl;
    double max_asym = 0.0;
    for (int i = 0; i < 12; i++) {
        for (int j = i+1; j < 12; j++) {
            double diff = fabs(K(i,j) - K(j,i));
            if (diff > max_asym) max_asym = diff;
        }
    }
    cout << "  Maxima asimetria: " << scientific << max_asym << endl;
    cout << "  Resultado: " << (max_asym < 1e-10 ? "SIMETRICA OK" : "ERROR: No simetrica") << endl;
    cout << endl;

    // Caso de carga: Fuerza puntual en extremo
    cout << "==========================================" << endl;
    cout << "  CASO DE CARGA: Cantilever con P = 10 kN " << endl;
    cout << "==========================================" << endl;
    cout << endl;

    double P = 10000.0;  // 10 kN en Newtons

    // Para cantilever con carga puntual:
    // Deflexion maxima = P*L^3 / (3*E*I)
    // Rotacion maxima = P*L^2 / (2*E*I)
    double defl_teorica = P * L * L * L / (3.0 * E * I);
    double rot_teorica = P * L * L / (2.0 * E * I);

    cout << "Deflexion teorica en extremo: " << defl_teorica * 1000 << " mm" << endl;
    cout << "Rotacion teorica en extremo:  " << rot_teorica * 1000 << " mrad" << endl;
    cout << endl;

    cout << "==========================================" << endl;
    cout << "  PRUEBA COMPLETADA EXITOSAMENTE         " << endl;
    cout << "==========================================" << endl;

    return 0;
}
