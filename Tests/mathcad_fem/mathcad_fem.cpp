// DLL de funciones FEM para Mathcad Prime 10
// Usa Eigen para calculos matriciales

#include "mcadincl.h"
#include <cmath>
#include <vector>
#include <Eigen/Core>
#include <Eigen/Dense>

using namespace Eigen;

// ============================================
// Funciones de ayuda
// ============================================

void EigenToMathcad(const MatrixXd& eigen, LPCOMPLEXARRAY out) {
    for (unsigned int c = 0; c < out->cols; c++) {
        for (unsigned int r = 0; r < out->rows; r++) {
            out->hReal[c][r] = eigen(r, c);
        }
    }
}

MatrixXd MathcadToEigen(LPCCOMPLEXARRAY in) {
    MatrixXd eigen(in->rows, in->cols);
    for (unsigned int c = 0; c < in->cols; c++) {
        for (unsigned int r = 0; r < in->rows; r++) {
            eigen(r, c) = (in->hReal != NULL) ? in->hReal[c][r] : 0.0;
        }
    }
    return eigen;
}

void EigenVectorToMathcad(const VectorXd& vec, LPCOMPLEXARRAY out) {
    for (unsigned int r = 0; r < out->rows; r++) {
        out->hReal[0][r] = vec(r);
    }
}

// ============================================
// FUNCION 1: fem_beam_K(E, A, I, L) -> 6x6
// ============================================

LRESULT FemBeamKFunc(LPCOMPLEXARRAY K_out,
                     LPCCOMPLEXSCALAR pE,
                     LPCCOMPLEXSCALAR pA,
                     LPCCOMPLEXSCALAR pI,
                     LPCCOMPLEXSCALAR pL);

FUNCTIONINFO fi_FemBeamK = {
    (char*)"fem_beam_K",
    (char*)"E,A,I,L",
    (char*)"Matriz de rigidez 6x6 para viga 2D",
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

    if (L <= 0) return 1;
    if (!MathcadArrayAllocate(K_out, 6, 6, TRUE, FALSE)) return 2;

    double EA_L = E * A / L;
    double EI_L3 = E * I / (L * L * L);
    double EI_L2 = E * I / (L * L);
    double EI_L = E * I / L;

    MatrixXd K = MatrixXd::Zero(6, 6);
    K(0, 0) = EA_L;       K(0, 3) = -EA_L;
    K(1, 1) = 12*EI_L3;   K(1, 2) = 6*EI_L2;   K(1, 4) = -12*EI_L3;  K(1, 5) = 6*EI_L2;
    K(2, 1) = 6*EI_L2;    K(2, 2) = 4*EI_L;    K(2, 4) = -6*EI_L2;   K(2, 5) = 2*EI_L;
    K(3, 0) = -EA_L;      K(3, 3) = EA_L;
    K(4, 1) = -12*EI_L3;  K(4, 2) = -6*EI_L2;  K(4, 4) = 12*EI_L3;   K(4, 5) = -6*EI_L2;
    K(5, 1) = 6*EI_L2;    K(5, 2) = 2*EI_L;    K(5, 4) = -6*EI_L2;   K(5, 5) = 4*EI_L;

    EigenToMathcad(K, K_out);
    return 0;
}

// ============================================
// FUNCION 2: fem_solve(K, F, supports) -> U
// ============================================

LRESULT FemSolveFunc(LPCOMPLEXARRAY U_out,
                     LPCCOMPLEXARRAY pK,
                     LPCCOMPLEXARRAY pF,
                     LPCCOMPLEXARRAY pSupports);

FUNCTIONINFO fi_FemSolve = {
    (char*)"fem_solve",
    (char*)"K,F,supports",
    (char*)"Resuelve K*U=F con restricciones",
    (LPCFUNCTION)FemSolveFunc,
    COMPLEX_ARRAY,
    3,
    {COMPLEX_ARRAY, COMPLEX_ARRAY, COMPLEX_ARRAY}
};

LRESULT FemSolveFunc(LPCOMPLEXARRAY U_out,
                     LPCCOMPLEXARRAY pK,
                     LPCCOMPLEXARRAY pF,
                     LPCCOMPLEXARRAY pSupports)
{
    MatrixXd K = MathcadToEigen(pK);
    MatrixXd F_mat = MathcadToEigen(pF);
    MatrixXd Supports = MathcadToEigen(pSupports);

    int n = K.rows();
    VectorXd F = F_mat.col(0);

    std::vector<int> freeIdx;
    for (int i = 0; i < n; i++) {
        if (i >= (int)Supports.rows() || Supports(i, 0) == 0) {
            freeIdx.push_back(i);
        }
    }

    int nFree = (int)freeIdx.size();
    if (nFree == 0) return 1;

    MatrixXd K_red(nFree, nFree);
    VectorXd F_red(nFree);

    for (int i = 0; i < nFree; i++) {
        F_red(i) = F(freeIdx[i]);
        for (int j = 0; j < nFree; j++) {
            K_red(i, j) = K(freeIdx[i], freeIdx[j]);
        }
    }

    VectorXd U_red = K_red.colPivHouseholderQr().solve(F_red);

    VectorXd U = VectorXd::Zero(n);
    for (int i = 0; i < nFree; i++) {
        U(freeIdx[i]) = U_red(i);
    }

    if (!MathcadArrayAllocate(U_out, n, 1, TRUE, FALSE)) return 2;
    EigenVectorToMathcad(U, U_out);
    return 0;
}

// ============================================
// FUNCION 3: cantilever_defl(P, L, E, I)
// ============================================

LRESULT CantileverDeflFunc(LPCOMPLEXSCALAR result,
                           LPCCOMPLEXSCALAR pP,
                           LPCCOMPLEXSCALAR pL,
                           LPCCOMPLEXSCALAR pE,
                           LPCCOMPLEXSCALAR pI);

FUNCTIONINFO fi_CantileverDefl = {
    (char*)"cantilever_defl",
    (char*)"P,L,E,I",
    (char*)"Deflexion analitica: P*L^3/(3*E*I)",
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

    if (E <= 0 || I <= 0 || L <= 0) return 1;

    result->real = P * L * L * L / (3.0 * E * I);
    result->imag = 0;
    return 0;
}

// ============================================
// FUNCION 4: fem_frame3d_K (12x12)
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
    (char*)"fem_frame3d_K",
    (char*)"E,G,A,Iy,Iz,J,L",
    (char*)"Matriz rigidez 12x12 frame 3D",
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

    if (L <= 0) return 1;
    if (!MathcadArrayAllocate(K_out, 12, 12, TRUE, FALSE)) return 2;

    double EA_L = E * A / L;
    double EIz_L3 = E * Iz / (L * L * L);
    double EIy_L3 = E * Iy / (L * L * L);
    double GJ_L = G * J / L;
    double EIz_L2 = E * Iz / (L * L);
    double EIy_L2 = E * Iy / (L * L);
    double EIz_L = E * Iz / L;
    double EIy_L = E * Iy / L;

    MatrixXd K(12, 12);
    K << EA_L, 0, 0, 0, 0, 0, -EA_L, 0, 0, 0, 0, 0,
        0, 12*EIz_L3, 0, 0, 0, 6*EIz_L2, 0, -12*EIz_L3, 0, 0, 0, 6*EIz_L2,
        0, 0, 12*EIy_L3, 0, -6*EIy_L2, 0, 0, 0, -12*EIy_L3, 0, -6*EIy_L2, 0,
        0, 0, 0, GJ_L, 0, 0, 0, 0, 0, -GJ_L, 0, 0,
        0, 0, -6*EIy_L2, 0, 4*EIy_L, 0, 0, 0, 6*EIy_L2, 0, 2*EIy_L, 0,
        0, 6*EIz_L2, 0, 0, 0, 4*EIz_L, 0, -6*EIz_L2, 0, 0, 0, 2*EIz_L,
        -EA_L, 0, 0, 0, 0, 0, EA_L, 0, 0, 0, 0, 0,
        0, -12*EIz_L3, 0, 0, 0, -6*EIz_L2, 0, 12*EIz_L3, 0, 0, 0, -6*EIz_L2,
        0, 0, -12*EIy_L3, 0, 6*EIy_L2, 0, 0, 0, 12*EIy_L3, 0, 6*EIy_L2, 0,
        0, 0, 0, -GJ_L, 0, 0, 0, 0, 0, GJ_L, 0, 0,
        0, 0, -6*EIy_L2, 0, 2*EIy_L, 0, 0, 0, 6*EIy_L2, 0, 4*EIy_L, 0,
        0, 6*EIz_L2, 0, 0, 0, 2*EIz_L, 0, -6*EIz_L2, 0, 0, 0, 4*EIz_L;

    EigenToMathcad(K, K_out);
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
        if (!_CRT_INIT((HINSTANCE)hDLL, dwReason, lpReserved))
            return FALSE;

        CreateUserFunction((HINSTANCE)hDLL, &fi_FemBeamK);
        CreateUserFunction((HINSTANCE)hDLL, &fi_FemSolve);
        CreateUserFunction((HINSTANCE)hDLL, &fi_CantileverDefl);
        CreateUserFunction((HINSTANCE)hDLL, &fi_FemFrame3dK);
        break;

    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        if (!_CRT_INIT((HINSTANCE)hDLL, dwReason, lpReserved))
            return FALSE;
        break;
    }
    return TRUE;
}
