// DLL de funciones FEM para Mathcad Prime 10
// Codigo C puro - compatible con el formato oficial de PTC

#include "mcadincl.h"

#define  INVALID_LENGTH         1
#define  INSUFFICIENT_MEMORY    2
#define  INVALID_PARAMETER      3
#define  ALL_CONSTRAINED        4
#define  NUMBER_OF_ERRORS       4

// Tabla de mensajes de error
char * femErrorMessageTable[NUMBER_OF_ERRORS] = {
    "invalid length (must be > 0)",
    "insufficient memory",
    "invalid parameter",
    "all DOFs are constrained"
};

// ============================================
// FUNCION 1: fem_beam_K(E, A, I, L) -> 6x6
// Matriz de rigidez para viga 2D
// DOFs: [ux1, uy1, rz1, ux2, uy2, rz2]
// ============================================

LRESULT FemBeamKFunc(LPCOMPLEXARRAY K_out,
                     LPCCOMPLEXSCALAR pE,
                     LPCCOMPLEXSCALAR pA,
                     LPCCOMPLEXSCALAR pI,
                     LPCCOMPLEXSCALAR pL);

FUNCTIONINFO fi_FemBeamK = {
    "fem_beam_K",
    "E,A,I,L",
    "Stiffness matrix 6x6 for 2D beam element",
    (LPCFUNCTION)FemBeamKFunc,
    COMPLEX_ARRAY,
    4,
    {COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR}
};

LRESULT FemBeamKFunc(LPCOMPLEXARRAY K_out,
                     LPCCOMPLEXSCALAR pE,
                     LPCCOMPLEXSCALAR pA,
                     LPCCOMPLEXSCALAR pI,
                     LPCCOMPLEXSCALAR pL)
{
    double E = pE->real;
    double A = pA->real;
    double I = pI->real;
    double L = pL->real;
    unsigned int i, j;

    double EA_L, EI_L3, EI_L2, EI_L;
    double K[6][6];

    if (L <= 0)
        return MAKELRESULT(INVALID_LENGTH, 4);

    // Asignar matriz 6x6
    if (!MathcadArrayAllocate(K_out, 6, 6, TRUE, FALSE))
        return INSUFFICIENT_MEMORY;

    // Calcular coeficientes
    EA_L = E * A / L;
    EI_L3 = E * I / (L * L * L);
    EI_L2 = E * I / (L * L);
    EI_L = E * I / L;

    // Inicializar a cero
    for (i = 0; i < 6; i++)
        for (j = 0; j < 6; j++)
            K[i][j] = 0.0;

    // Llenar matriz de rigidez
    // Nodo 1
    K[0][0] = EA_L;
    K[1][1] = 12.0 * EI_L3;
    K[1][2] = 6.0 * EI_L2;
    K[2][1] = 6.0 * EI_L2;
    K[2][2] = 4.0 * EI_L;

    // Nodo 2
    K[3][3] = EA_L;
    K[4][4] = 12.0 * EI_L3;
    K[4][5] = -6.0 * EI_L2;
    K[5][4] = -6.0 * EI_L2;
    K[5][5] = 4.0 * EI_L;

    // Acoplamiento
    K[0][3] = -EA_L;
    K[3][0] = -EA_L;
    K[1][4] = -12.0 * EI_L3;
    K[4][1] = -12.0 * EI_L3;
    K[1][5] = 6.0 * EI_L2;
    K[5][1] = 6.0 * EI_L2;
    K[2][4] = -6.0 * EI_L2;
    K[4][2] = -6.0 * EI_L2;
    K[2][5] = 2.0 * EI_L;
    K[5][2] = 2.0 * EI_L;

    // Copiar a salida (Mathcad usa [col][row])
    for (i = 0; i < 6; i++)
        for (j = 0; j < 6; j++)
            K_out->hReal[j][i] = K[i][j];

    return 0;
}

// ============================================
// FUNCION 2: cantilever_defl(P, L, E, I)
// Deflexion analitica de cantilever
// ============================================

LRESULT CantileverDeflFunc(LPCOMPLEXSCALAR result,
                           LPCCOMPLEXSCALAR pP,
                           LPCCOMPLEXSCALAR pL,
                           LPCCOMPLEXSCALAR pE,
                           LPCCOMPLEXSCALAR pI);

FUNCTIONINFO fi_CantileverDefl = {
    "cantilever_defl",
    "P,L,E,I",
    "Cantilever deflection: P*L^3/(3*E*I)",
    (LPCFUNCTION)CantileverDeflFunc,
    COMPLEX_SCALAR,
    4,
    {COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR}
};

LRESULT CantileverDeflFunc(LPCOMPLEXSCALAR result,
                           LPCCOMPLEXSCALAR pP,
                           LPCCOMPLEXSCALAR pL,
                           LPCCOMPLEXSCALAR pE,
                           LPCCOMPLEXSCALAR pI)
{
    double P = pP->real;
    double L = pL->real;
    double E = pE->real;
    double I = pI->real;

    if (E <= 0 || I <= 0 || L <= 0)
        return MAKELRESULT(INVALID_PARAMETER, 0);

    result->real = P * L * L * L / (3.0 * E * I);
    result->imag = 0.0;
    return 0;
}

// ============================================
// FUNCION 3: cantilever_rot(P, L, E, I)
// Rotacion analitica de cantilever
// ============================================

LRESULT CantileverRotFunc(LPCOMPLEXSCALAR result,
                          LPCCOMPLEXSCALAR pP,
                          LPCCOMPLEXSCALAR pL,
                          LPCCOMPLEXSCALAR pE,
                          LPCCOMPLEXSCALAR pI);

FUNCTIONINFO fi_CantileverRot = {
    "cantilever_rot",
    "P,L,E,I",
    "Cantilever rotation: P*L^2/(2*E*I)",
    (LPCFUNCTION)CantileverRotFunc,
    COMPLEX_SCALAR,
    4,
    {COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR}
};

LRESULT CantileverRotFunc(LPCOMPLEXSCALAR result,
                          LPCCOMPLEXSCALAR pP,
                          LPCCOMPLEXSCALAR pL,
                          LPCCOMPLEXSCALAR pE,
                          LPCCOMPLEXSCALAR pI)
{
    double P = pP->real;
    double L = pL->real;
    double E = pE->real;
    double I = pI->real;

    if (E <= 0 || I <= 0 || L <= 0)
        return MAKELRESULT(INVALID_PARAMETER, 0);

    result->real = P * L * L / (2.0 * E * I);
    result->imag = 0.0;
    return 0;
}

// ============================================
// FUNCION 4: fem_frame3d_K(E, G, A, Iy, Iz, J, L)
// Matriz de rigidez 12x12 para frame 3D
// ============================================

LRESULT FemFrame3dKFunc(LPCOMPLEXARRAY K_out,
                        LPCCOMPLEXSCALAR pE,
                        LPCCOMPLEXSCALAR pG,
                        LPCCOMPLEXSCALAR pA,
                        LPCCOMPLEXSCALAR pIy,
                        LPCCOMPLEXSCALAR pIz,
                        LPCCOMPLEXSCALAR pJ,
                        LPCCOMPLEXSCALAR pL);

FUNCTIONINFO fi_FemFrame3dK = {
    "fem_frame3d_K",
    "E,G,A,Iy,Iz,J,L",
    "Stiffness matrix 12x12 for 3D frame element",
    (LPCFUNCTION)FemFrame3dKFunc,
    COMPLEX_ARRAY,
    7,
    {COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR,
     COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR}
};

LRESULT FemFrame3dKFunc(LPCOMPLEXARRAY K_out,
                        LPCCOMPLEXSCALAR pE,
                        LPCCOMPLEXSCALAR pG,
                        LPCCOMPLEXSCALAR pA,
                        LPCCOMPLEXSCALAR pIy,
                        LPCCOMPLEXSCALAR pIz,
                        LPCCOMPLEXSCALAR pJ,
                        LPCCOMPLEXSCALAR pL)
{
    double E = pE->real;
    double G = pG->real;
    double A = pA->real;
    double Iy = pIy->real;
    double Iz = pIz->real;
    double J = pJ->real;
    double L = pL->real;
    unsigned int i, j;

    double EA_L, EIz_L3, EIy_L3, GJ_L, EIz_L2, EIy_L2, EIz_L, EIy_L;
    double K[12][12];

    if (L <= 0)
        return MAKELRESULT(INVALID_LENGTH, 7);

    if (!MathcadArrayAllocate(K_out, 12, 12, TRUE, FALSE))
        return INSUFFICIENT_MEMORY;

    // Calcular coeficientes
    EA_L = E * A / L;
    EIz_L3 = E * Iz / (L * L * L);
    EIy_L3 = E * Iy / (L * L * L);
    GJ_L = G * J / L;
    EIz_L2 = E * Iz / (L * L);
    EIy_L2 = E * Iy / (L * L);
    EIz_L = E * Iz / L;
    EIy_L = E * Iy / L;

    // Inicializar a cero
    for (i = 0; i < 12; i++)
        for (j = 0; j < 12; j++)
            K[i][j] = 0.0;

    // Matriz de rigidez local para frame 3D
    // DOFs: [ux, uy, uz, rx, ry, rz] por nodo

    // Diagonal nodo 1
    K[0][0] = EA_L;
    K[1][1] = 12.0 * EIz_L3;
    K[2][2] = 12.0 * EIy_L3;
    K[3][3] = GJ_L;
    K[4][4] = 4.0 * EIy_L;
    K[5][5] = 4.0 * EIz_L;

    // Diagonal nodo 2
    K[6][6] = EA_L;
    K[7][7] = 12.0 * EIz_L3;
    K[8][8] = 12.0 * EIy_L3;
    K[9][9] = GJ_L;
    K[10][10] = 4.0 * EIy_L;
    K[11][11] = 4.0 * EIz_L;

    // Acoplamiento flexion-rotacion nodo 1
    K[1][5] = 6.0 * EIz_L2;   K[5][1] = 6.0 * EIz_L2;
    K[2][4] = -6.0 * EIy_L2;  K[4][2] = -6.0 * EIy_L2;

    // Acoplamiento nodo 1 - nodo 2
    K[0][6] = -EA_L;          K[6][0] = -EA_L;
    K[1][7] = -12.0 * EIz_L3; K[7][1] = -12.0 * EIz_L3;
    K[2][8] = -12.0 * EIy_L3; K[8][2] = -12.0 * EIy_L3;
    K[3][9] = -GJ_L;          K[9][3] = -GJ_L;

    K[1][11] = 6.0 * EIz_L2;  K[11][1] = 6.0 * EIz_L2;
    K[2][10] = -6.0 * EIy_L2; K[10][2] = -6.0 * EIy_L2;
    K[4][8] = 6.0 * EIy_L2;   K[8][4] = 6.0 * EIy_L2;
    K[5][7] = -6.0 * EIz_L2;  K[7][5] = -6.0 * EIz_L2;

    K[4][10] = 2.0 * EIy_L;   K[10][4] = 2.0 * EIy_L;
    K[5][11] = 2.0 * EIz_L;   K[11][5] = 2.0 * EIz_L;

    // Acoplamiento flexion-rotacion nodo 2
    K[7][11] = -6.0 * EIz_L2; K[11][7] = -6.0 * EIz_L2;
    K[8][10] = 6.0 * EIy_L2;  K[10][8] = 6.0 * EIy_L2;

    // Copiar a salida
    for (i = 0; i < 12; i++)
        for (j = 0; j < 12; j++)
            K_out->hReal[j][i] = K[i][j];

    return 0;
}

// ============================================
// Punto de entrada DLL
// ============================================

BOOL WINAPI _CRT_INIT(HINSTANCE hinstDLL, DWORD dwReason, LPVOID lpReserved);

BOOL WINAPI DllEntryPoint(HANDLE hDLL, DWORD dwReason, LPVOID lpReserved)
{
    switch (dwReason)
    {
    case DLL_PROCESS_ATTACH:
        if (!_CRT_INIT(hDLL, dwReason, lpReserved))
            return FALSE;

        // Registrar tabla de errores
        if (!CreateUserErrorMessageTable(hDLL, NUMBER_OF_ERRORS, femErrorMessageTable))
            break;

        // Registrar funciones
        CreateUserFunction(hDLL, &fi_FemBeamK);
        CreateUserFunction(hDLL, &fi_CantileverDefl);
        CreateUserFunction(hDLL, &fi_CantileverRot);
        CreateUserFunction(hDLL, &fi_FemFrame3dK);
        break;

    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        if (!_CRT_INIT(hDLL, dwReason, lpReserved))
            return FALSE;
        break;
    }
    return TRUE;
}

#undef INVALID_LENGTH
#undef INSUFFICIENT_MEMORY
#undef INVALID_PARAMETER
#undef ALL_CONSTRAINED
#undef NUMBER_OF_ERRORS
