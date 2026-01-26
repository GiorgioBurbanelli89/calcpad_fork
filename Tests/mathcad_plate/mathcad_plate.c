/*
 * mathcad_plate.c - DLL para Mathcad Prime
 * Funciones FEM para analisis de placas con elementos shell triangulares
 *
 * Funciones disponibles:
 *   plate_Kb(x1,y1,x2,y2,x3,y3,E,nu,t) - Matriz rigidez flexion (9x9)
 *   plate_Ks(x1,y1,x2,y2,x3,y3,E,nu,t) - Matriz rigidez cortante (9x9)
 *   plate_K(x1,y1,x2,y2,x3,y3,E,nu,t)  - Matriz rigidez total (9x9)
 *   plate_defl(q,a,E,nu,t)              - Deflexion central placa empotrada
 */

#include "mcadincl.h"
#include <stdlib.h>

/* Macro para valor absoluto */
#define FABS(x) ((x) < 0 ? -(x) : (x))

#define MUST_BE_REAL    1
#define MUST_BE_POSITIVE 2
#define INSUFFICIENT_MEMORY 3

/* Prototipos */
LRESULT PlateKbFunc(LPCOMPLEXARRAY result,
                    LPCCOMPLEXSCALAR px1, LPCCOMPLEXSCALAR py1,
                    LPCCOMPLEXSCALAR px2, LPCCOMPLEXSCALAR py2,
                    LPCCOMPLEXSCALAR px3, LPCCOMPLEXSCALAR py3,
                    LPCCOMPLEXSCALAR pE, LPCCOMPLEXSCALAR pNu, LPCCOMPLEXSCALAR pT);

LRESULT PlateKsFunc(LPCOMPLEXARRAY result,
                    LPCCOMPLEXSCALAR px1, LPCCOMPLEXSCALAR py1,
                    LPCCOMPLEXSCALAR px2, LPCCOMPLEXSCALAR py2,
                    LPCCOMPLEXSCALAR px3, LPCCOMPLEXSCALAR py3,
                    LPCCOMPLEXSCALAR pE, LPCCOMPLEXSCALAR pNu, LPCCOMPLEXSCALAR pT);

LRESULT PlateKFunc(LPCOMPLEXARRAY result,
                   LPCCOMPLEXSCALAR px1, LPCCOMPLEXSCALAR py1,
                   LPCCOMPLEXSCALAR px2, LPCCOMPLEXSCALAR py2,
                   LPCCOMPLEXSCALAR px3, LPCCOMPLEXSCALAR py3,
                   LPCCOMPLEXSCALAR pE, LPCCOMPLEXSCALAR pNu, LPCCOMPLEXSCALAR pT);

LRESULT PlateDeflFunc(LPCOMPLEXSCALAR pResult,
                      LPCCOMPLEXSCALAR pQ, LPCCOMPLEXSCALAR pA,
                      LPCCOMPLEXSCALAR pE, LPCCOMPLEXSCALAR pNu, LPCCOMPLEXSCALAR pT);

/* Mensajes de error */
char *myErrorMessages[] = {
    "Debe ser un numero real",
    "Debe ser positivo",
    "Memoria insuficiente"
};

/* Funcion auxiliar: area de triangulo */
double triangleArea(double x1, double y1, double x2, double y2, double x3, double y3) {
    double x21 = x2 - x1;
    double y21 = y2 - y1;
    double x31 = x3 - x1;
    double y31 = y3 - y1;
    return 0.5 * FABS(x21 * y31 - x31 * y21);
}

/* ============================================================
 * plate_Kb - Matriz de rigidez de flexion (9x9)
 * DOFs: w1, theta_x1, theta_y1, w2, theta_x2, theta_y2, w3, theta_x3, theta_y3
 * ============================================================ */
FUNCTIONINFO fi_PlateKb = {
    "plate_Kb",
    "x1,y1,x2,y2,x3,y3,E,nu,t",
    "Bending stiffness matrix (9x9) for triangular plate element",
    (LPCFUNCTION)PlateKbFunc,
    COMPLEX_ARRAY,
    9,
    {COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR,
     COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR}
};

LRESULT PlateKbFunc(LPCOMPLEXARRAY result,
                    LPCCOMPLEXSCALAR px1, LPCCOMPLEXSCALAR py1,
                    LPCCOMPLEXSCALAR px2, LPCCOMPLEXSCALAR py2,
                    LPCCOMPLEXSCALAR px3, LPCCOMPLEXSCALAR py3,
                    LPCCOMPLEXSCALAR pE, LPCCOMPLEXSCALAR pNu, LPCCOMPLEXSCALAR pT)
{
    double x1, y1, x2, y2, x3, y3, E, nu, t;
    double A, D, inv2A;
    double b1, b2, b3, c1, c2, c3;
    double Db[3][3], Bb[3][9], Kb[9][9];
    int i, j, k;

    /* Verificar parametros reales */
    if (px1->imag != 0 || py1->imag != 0 || px2->imag != 0 || py2->imag != 0 ||
        px3->imag != 0 || py3->imag != 0 || pE->imag != 0 || pNu->imag != 0 || pT->imag != 0)
        return MAKELRESULT(MUST_BE_REAL, 1);

    x1 = px1->real; y1 = py1->real;
    x2 = px2->real; y2 = py2->real;
    x3 = px3->real; y3 = py3->real;
    E = pE->real; nu = pNu->real; t = pT->real;

    if (E <= 0 || t <= 0)
        return MAKELRESULT(MUST_BE_POSITIVE, 7);

    /* Allocar resultado 9x9 */
    if (!MathcadArrayAllocate(result, 9, 9, TRUE, FALSE))
        return MAKELRESULT(INSUFFICIENT_MEMORY, 0);

    /* Calcular area */
    A = triangleArea(x1, y1, x2, y2, x3, y3);
    if (A < 1e-12) {
        /* Triangulo degenerado - retornar ceros */
        for (i = 0; i < 9; i++)
            for (j = 0; j < 9; j++)
                result->hReal[j][i] = 0.0;
        return 0;
    }

    /* Matriz constitutiva de flexion Db */
    D = E * t * t * t / (12.0 * (1.0 - nu * nu));
    Db[0][0] = D;       Db[0][1] = D * nu;   Db[0][2] = 0;
    Db[1][0] = D * nu;  Db[1][1] = D;        Db[1][2] = 0;
    Db[2][0] = 0;       Db[2][1] = 0;        Db[2][2] = D * (1 - nu) / 2;

    /* Derivadas de funciones de forma */
    b1 = y2 - y3;
    b2 = y3 - y1;
    b3 = y1 - y2;
    c1 = x3 - x2;
    c2 = x1 - x3;
    c3 = x2 - x1;

    inv2A = 1.0 / (2.0 * A);

    /* Inicializar Bb a cero */
    for (i = 0; i < 3; i++)
        for (j = 0; j < 9; j++)
            Bb[i][j] = 0;

    /* Matriz Bb (strain-displacement para curvatura) */
    /* Fila 0: curvatura kappa_x = d(theta_y)/dx */
    Bb[0][2] = b1 * inv2A;
    Bb[0][5] = b2 * inv2A;
    Bb[0][8] = b3 * inv2A;

    /* Fila 1: curvatura kappa_y = -d(theta_x)/dy */
    Bb[1][1] = -c1 * inv2A;
    Bb[1][4] = -c2 * inv2A;
    Bb[1][7] = -c3 * inv2A;

    /* Fila 2: curvatura de torsion */
    Bb[2][1] = -b1 * inv2A;
    Bb[2][2] = c1 * inv2A;
    Bb[2][4] = -b2 * inv2A;
    Bb[2][5] = c2 * inv2A;
    Bb[2][7] = -b3 * inv2A;
    Bb[2][8] = c3 * inv2A;

    /* Kb = Bb^T * Db * Bb * A */
    /* Primero: temp = Db * Bb */
    double temp[3][9];
    for (i = 0; i < 3; i++) {
        for (j = 0; j < 9; j++) {
            temp[i][j] = 0;
            for (k = 0; k < 3; k++) {
                temp[i][j] += Db[i][k] * Bb[k][j];
            }
        }
    }

    /* Luego: Kb = Bb^T * temp * A */
    for (i = 0; i < 9; i++) {
        for (j = 0; j < 9; j++) {
            Kb[i][j] = 0;
            for (k = 0; k < 3; k++) {
                Kb[i][j] += Bb[k][i] * temp[k][j];
            }
            Kb[i][j] *= A;
        }
    }

    /* Copiar a resultado (Mathcad usa [col][row]) */
    for (i = 0; i < 9; i++)
        for (j = 0; j < 9; j++)
            result->hReal[j][i] = Kb[i][j];

    return 0;
}

/* ============================================================
 * plate_Ks - Matriz de rigidez de cortante (9x9)
 * ============================================================ */
FUNCTIONINFO fi_PlateKs = {
    "plate_Ks",
    "x1,y1,x2,y2,x3,y3,E,nu,t",
    "Shear stiffness matrix (9x9) for triangular plate element",
    (LPCFUNCTION)PlateKsFunc,
    COMPLEX_ARRAY,
    9,
    {COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR,
     COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR}
};

LRESULT PlateKsFunc(LPCOMPLEXARRAY result,
                    LPCCOMPLEXSCALAR px1, LPCCOMPLEXSCALAR py1,
                    LPCCOMPLEXSCALAR px2, LPCCOMPLEXSCALAR py2,
                    LPCCOMPLEXSCALAR px3, LPCCOMPLEXSCALAR py3,
                    LPCCOMPLEXSCALAR pE, LPCCOMPLEXSCALAR pNu, LPCCOMPLEXSCALAR pT)
{
    double x1, y1, x2, y2, x3, y3, E, nu, t;
    double A, G, kappa, Ds_val, inv2A;
    double dN1dx, dN2dx, dN3dx, dN1dy, dN2dy, dN3dy;
    double N1, N2, N3;
    double Ds[2][2], Bs[2][9], Ks[9][9];
    int i, j, k;

    /* Verificar parametros */
    if (px1->imag != 0 || py1->imag != 0 || px2->imag != 0 || py2->imag != 0 ||
        px3->imag != 0 || py3->imag != 0 || pE->imag != 0 || pNu->imag != 0 || pT->imag != 0)
        return MAKELRESULT(MUST_BE_REAL, 1);

    x1 = px1->real; y1 = py1->real;
    x2 = px2->real; y2 = py2->real;
    x3 = px3->real; y3 = py3->real;
    E = pE->real; nu = pNu->real; t = pT->real;

    if (E <= 0 || t <= 0)
        return MAKELRESULT(MUST_BE_POSITIVE, 7);

    /* Allocar resultado 9x9 */
    if (!MathcadArrayAllocate(result, 9, 9, TRUE, FALSE))
        return MAKELRESULT(INSUFFICIENT_MEMORY, 0);

    /* Calcular area */
    A = triangleArea(x1, y1, x2, y2, x3, y3);
    if (A < 1e-12) {
        for (i = 0; i < 9; i++)
            for (j = 0; j < 9; j++)
                result->hReal[j][i] = 0.0;
        return 0;
    }

    /* Matriz constitutiva de cortante */
    kappa = 5.0 / 6.0;
    G = E / (2.0 * (1.0 + nu));
    Ds_val = kappa * G * t;
    Ds[0][0] = Ds_val; Ds[0][1] = 0;
    Ds[1][0] = 0;      Ds[1][1] = Ds_val;

    /* Funciones de forma en centroide */
    N1 = N2 = N3 = 1.0 / 3.0;

    /* Derivadas */
    inv2A = 1.0 / (2.0 * A);
    dN1dx = (y2 - y3) * inv2A;
    dN2dx = (y3 - y1) * inv2A;
    dN3dx = (y1 - y2) * inv2A;
    dN1dy = (x3 - x2) * inv2A;
    dN2dy = (x1 - x3) * inv2A;
    dN3dy = (x2 - x1) * inv2A;

    /* Inicializar Bs */
    for (i = 0; i < 2; i++)
        for (j = 0; j < 9; j++)
            Bs[i][j] = 0;

    /* Matriz Bs: gamma_xz = dw/dx - theta_y, gamma_yz = dw/dy + theta_x */
    Bs[0][0] = dN1dx;  Bs[0][2] = -N1;
    Bs[0][3] = dN2dx;  Bs[0][5] = -N2;
    Bs[0][6] = dN3dx;  Bs[0][8] = -N3;

    Bs[1][0] = dN1dy;  Bs[1][1] = N1;
    Bs[1][3] = dN2dy;  Bs[1][4] = N2;
    Bs[1][6] = dN3dy;  Bs[1][7] = N3;

    /* Ks = Bs^T * Ds * Bs * A */
    double temp[2][9];
    for (i = 0; i < 2; i++) {
        for (j = 0; j < 9; j++) {
            temp[i][j] = 0;
            for (k = 0; k < 2; k++) {
                temp[i][j] += Ds[i][k] * Bs[k][j];
            }
        }
    }

    for (i = 0; i < 9; i++) {
        for (j = 0; j < 9; j++) {
            Ks[i][j] = 0;
            for (k = 0; k < 2; k++) {
                Ks[i][j] += Bs[k][i] * temp[k][j];
            }
            Ks[i][j] *= A;
        }
    }

    /* Copiar a resultado */
    for (i = 0; i < 9; i++)
        for (j = 0; j < 9; j++)
            result->hReal[j][i] = Ks[i][j];

    return 0;
}

/* ============================================================
 * plate_K - Matriz de rigidez total (Kb + Ks)
 * ============================================================ */
FUNCTIONINFO fi_PlateK = {
    "plate_K",
    "x1,y1,x2,y2,x3,y3,E,nu,t",
    "Total stiffness matrix (9x9) for triangular plate element (bending + shear)",
    (LPCFUNCTION)PlateKFunc,
    COMPLEX_ARRAY,
    9,
    {COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR,
     COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR}
};

LRESULT PlateKFunc(LPCOMPLEXARRAY result,
                   LPCCOMPLEXSCALAR px1, LPCCOMPLEXSCALAR py1,
                   LPCCOMPLEXSCALAR px2, LPCCOMPLEXSCALAR py2,
                   LPCCOMPLEXSCALAR px3, LPCCOMPLEXSCALAR py3,
                   LPCCOMPLEXSCALAR pE, LPCCOMPLEXSCALAR pNu, LPCCOMPLEXSCALAR pT)
{
    COMPLEXARRAY Kb_arr, Ks_arr;
    LRESULT res;
    int i, j;

    /* Calcular Kb */
    res = PlateKbFunc(&Kb_arr, px1, py1, px2, py2, px3, py3, pE, pNu, pT);
    if (res != 0) return res;

    /* Calcular Ks */
    res = PlateKsFunc(&Ks_arr, px1, py1, px2, py2, px3, py3, pE, pNu, pT);
    if (res != 0) {
        MathcadArrayFree(&Kb_arr);
        return res;
    }

    /* Allocar resultado */
    if (!MathcadArrayAllocate(result, 9, 9, TRUE, FALSE)) {
        MathcadArrayFree(&Kb_arr);
        MathcadArrayFree(&Ks_arr);
        return MAKELRESULT(INSUFFICIENT_MEMORY, 0);
    }

    /* Sumar Kb + Ks */
    for (i = 0; i < 9; i++) {
        for (j = 0; j < 9; j++) {
            result->hReal[j][i] = Kb_arr.hReal[j][i] + Ks_arr.hReal[j][i];
        }
    }

    MathcadArrayFree(&Kb_arr);
    MathcadArrayFree(&Ks_arr);

    return 0;
}

/* ============================================================
 * plate_defl - Deflexion central de placa rectangular empotrada
 * Formula: w = alpha * q * a^4 / D
 *          D = E * t^3 / (12 * (1 - nu^2))
 *          alpha = 0.00126 (para placa cuadrada empotrada)
 * ============================================================ */
FUNCTIONINFO fi_PlateDefl = {
    "plate_defl",
    "q,a,E,nu,t",
    "Central deflection of clamped square plate under uniform load",
    (LPCFUNCTION)PlateDeflFunc,
    COMPLEX_SCALAR,
    5,
    {COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR}
};

LRESULT PlateDeflFunc(LPCOMPLEXSCALAR pResult,
                      LPCCOMPLEXSCALAR pQ, LPCCOMPLEXSCALAR pA,
                      LPCCOMPLEXSCALAR pE, LPCCOMPLEXSCALAR pNu, LPCCOMPLEXSCALAR pT)
{
    double q, a, E, nu, t, D, w;

    if (pQ->imag != 0 || pA->imag != 0 || pE->imag != 0 || pNu->imag != 0 || pT->imag != 0)
        return MAKELRESULT(MUST_BE_REAL, 1);

    q = pQ->real;
    a = pA->real;
    E = pE->real;
    nu = pNu->real;
    t = pT->real;

    if (a <= 0 || E <= 0 || t <= 0)
        return MAKELRESULT(MUST_BE_POSITIVE, 2);

    /* Rigidez a flexion */
    D = E * t * t * t / (12.0 * (1.0 - nu * nu));

    /* Deflexion central (coef. para placa cuadrada empotrada) */
    w = 0.00126 * FABS(q) * a * a * a * a / D;

    pResult->real = w;
    pResult->imag = 0.0;

    return 0;
}

/* ============================================================
 * DLL Entry Point
 * ============================================================ */
BOOL WINAPI DllEntryPoint(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
    switch (fdwReason) {
        case DLL_PROCESS_ATTACH:
            if (!CreateUserFunction(hinstDLL, &fi_PlateKb))
                return FALSE;
            if (!CreateUserFunction(hinstDLL, &fi_PlateKs))
                return FALSE;
            if (!CreateUserFunction(hinstDLL, &fi_PlateK))
                return FALSE;
            if (!CreateUserFunction(hinstDLL, &fi_PlateDefl))
                return FALSE;

            if (!CreateUserErrorMessageTable(hinstDLL, 3, myErrorMessages))
                return FALSE;
            break;

        case DLL_PROCESS_DETACH:
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
            break;
    }
    return TRUE;
}
