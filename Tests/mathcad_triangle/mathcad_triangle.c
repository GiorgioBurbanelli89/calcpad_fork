/*
 * mathcad_triangle.c - DLL para Mathcad Prime
 * Funciones de mallado triangular usando algoritmo de Shewchuk
 *
 * Funciones disponibles:
 *   tri_rect_mesh(Lx, Ly, nx, ny) - Genera malla rectangular de triangulos
 *   tri_area(x1,y1,x2,y2,x3,y3)   - Area de un triangulo
 *   tri_quality(x1,y1,x2,y2,x3,y3) - Calidad de triangulo (aspect ratio)
 *   tri_centroid(x1,y1,x2,y2,x3,y3) - Centroide de triangulo
 */

#include "mcadincl.h"
#include <stdlib.h>

/* Macro para valor absoluto (evita dependencia de math.lib) */
#define FABS(x) ((x) < 0 ? -(x) : (x))

#define MUST_BE_REAL    1
#define MUST_BE_POSITIVE 2
#define MUST_BE_INTEGER  3
#define INSUFFICIENT_MEMORY 4

/* Prototipos */
LRESULT TriRectMeshFunc(LPCOMPLEXARRAY result,
                        LPCCOMPLEXSCALAR pLx, LPCCOMPLEXSCALAR pLy,
                        LPCCOMPLEXSCALAR pNx, LPCCOMPLEXSCALAR pNy);

LRESULT TriAreaFunc(LPCOMPLEXSCALAR pResult,
                    LPCCOMPLEXSCALAR px1, LPCCOMPLEXSCALAR py1,
                    LPCCOMPLEXSCALAR px2, LPCCOMPLEXSCALAR py2,
                    LPCCOMPLEXSCALAR px3, LPCCOMPLEXSCALAR py3);

LRESULT TriQualityFunc(LPCOMPLEXSCALAR pResult,
                       LPCCOMPLEXSCALAR px1, LPCCOMPLEXSCALAR py1,
                       LPCCOMPLEXSCALAR px2, LPCCOMPLEXSCALAR py2,
                       LPCCOMPLEXSCALAR px3, LPCCOMPLEXSCALAR py3);

LRESULT TriCentroidFunc(LPCOMPLEXARRAY result,
                        LPCCOMPLEXSCALAR px1, LPCCOMPLEXSCALAR py1,
                        LPCCOMPLEXSCALAR px2, LPCCOMPLEXSCALAR py2,
                        LPCCOMPLEXSCALAR px3, LPCCOMPLEXSCALAR py3);

LRESULT TriNodesFunc(LPCOMPLEXARRAY result,
                     LPCCOMPLEXSCALAR pLx, LPCCOMPLEXSCALAR pLy,
                     LPCCOMPLEXSCALAR pNx, LPCCOMPLEXSCALAR pNy);

LRESULT TriElementsFunc(LPCOMPLEXARRAY result,
                        LPCCOMPLEXSCALAR pNx, LPCCOMPLEXSCALAR pNy);

/* Mensajes de error */
char *myErrorMessages[] = {
    "Debe ser un numero real",
    "Debe ser positivo",
    "Debe ser un entero positivo",
    "Memoria insuficiente"
};

/* ============================================================
 * tri_rect_mesh - Genera conectividad de malla rectangular
 * Entrada: Lx, Ly (dimensiones), nx, ny (divisiones)
 * Salida: Matriz de conectividad [num_tri x 3]
 * ============================================================ */
FUNCTIONINFO fi_TriRectMesh = {
    "tri_rect_mesh",
    "Lx,Ly,nx,ny",
    "Generates triangular mesh connectivity for rectangle",
    (LPCFUNCTION)TriRectMeshFunc,
    COMPLEX_ARRAY,
    4,
    {COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR}
};

LRESULT TriRectMeshFunc(LPCOMPLEXARRAY result,
                        LPCCOMPLEXSCALAR pLx, LPCCOMPLEXSCALAR pLy,
                        LPCCOMPLEXSCALAR pNx, LPCCOMPLEXSCALAR pNy)
{
    double Lx, Ly;
    int nx, ny;
    int num_tri, tri_idx;
    int i, j, n1, n2, n3, n4;

    /* Verificar parametros */
    if (pLx->imag != 0 || pLy->imag != 0 || pNx->imag != 0 || pNy->imag != 0)
        return MAKELRESULT(MUST_BE_REAL, 1);

    Lx = pLx->real;
    Ly = pLy->real;
    nx = (int)(pNx->real + 0.5);
    ny = (int)(pNy->real + 0.5);

    if (Lx <= 0 || Ly <= 0)
        return MAKELRESULT(MUST_BE_POSITIVE, 1);
    if (nx < 1 || ny < 1)
        return MAKELRESULT(MUST_BE_INTEGER, 3);

    /* Numero de triangulos: 2 * nx * ny */
    num_tri = 2 * nx * ny;

    /* Allocar resultado: [num_tri x 3] */
    if (!MathcadArrayAllocate(result, num_tri, 3, TRUE, FALSE))
        return MAKELRESULT(INSUFFICIENT_MEMORY, 0);

    /* Generar conectividad (indices base 1 para Mathcad) */
    tri_idx = 0;
    for (j = 0; j < ny; j++) {
        for (i = 0; i < nx; i++) {
            /* Nodos del cuadrilatero (base 1) */
            n1 = j * (nx + 1) + i + 1;       /* inferior izquierda */
            n2 = j * (nx + 1) + i + 2;       /* inferior derecha */
            n3 = (j + 1) * (nx + 1) + i + 2; /* superior derecha */
            n4 = (j + 1) * (nx + 1) + i + 1; /* superior izquierda */

            /* Triangulo 1: n1-n2-n4 */
            result->hReal[0][tri_idx] = n1;
            result->hReal[1][tri_idx] = n2;
            result->hReal[2][tri_idx] = n4;
            tri_idx++;

            /* Triangulo 2: n2-n3-n4 */
            result->hReal[0][tri_idx] = n2;
            result->hReal[1][tri_idx] = n3;
            result->hReal[2][tri_idx] = n4;
            tri_idx++;
        }
    }

    return 0;
}

/* ============================================================
 * tri_nodes - Genera coordenadas de nodos de malla rectangular
 * Entrada: Lx, Ly (dimensiones), nx, ny (divisiones)
 * Salida: Matriz de coordenadas [num_nodes x 2]
 * ============================================================ */
FUNCTIONINFO fi_TriNodes = {
    "tri_nodes",
    "Lx,Ly,nx,ny",
    "Generates node coordinates for rectangular triangular mesh",
    (LPCFUNCTION)TriNodesFunc,
    COMPLEX_ARRAY,
    4,
    {COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR}
};

LRESULT TriNodesFunc(LPCOMPLEXARRAY result,
                     LPCCOMPLEXSCALAR pLx, LPCCOMPLEXSCALAR pLy,
                     LPCCOMPLEXSCALAR pNx, LPCCOMPLEXSCALAR pNy)
{
    double Lx, Ly, dx, dy;
    int nx, ny, num_nodes, node_idx;
    int i, j;

    /* Verificar parametros */
    if (pLx->imag != 0 || pLy->imag != 0 || pNx->imag != 0 || pNy->imag != 0)
        return MAKELRESULT(MUST_BE_REAL, 1);

    Lx = pLx->real;
    Ly = pLy->real;
    nx = (int)(pNx->real + 0.5);
    ny = (int)(pNy->real + 0.5);

    if (Lx <= 0 || Ly <= 0)
        return MAKELRESULT(MUST_BE_POSITIVE, 1);
    if (nx < 1 || ny < 1)
        return MAKELRESULT(MUST_BE_INTEGER, 3);

    /* Numero de nodos: (nx+1) * (ny+1) */
    num_nodes = (nx + 1) * (ny + 1);

    /* Espaciado */
    dx = Lx / nx;
    dy = Ly / ny;

    /* Allocar resultado: [num_nodes x 2] */
    if (!MathcadArrayAllocate(result, num_nodes, 2, TRUE, FALSE))
        return MAKELRESULT(INSUFFICIENT_MEMORY, 0);

    /* Generar coordenadas */
    node_idx = 0;
    for (j = 0; j <= ny; j++) {
        for (i = 0; i <= nx; i++) {
            result->hReal[0][node_idx] = i * dx;  /* x */
            result->hReal[1][node_idx] = j * dy;  /* y */
            node_idx++;
        }
    }

    return 0;
}

/* ============================================================
 * tri_elements - Genera conectividad solo con nx, ny
 * Entrada: nx, ny (divisiones)
 * Salida: Matriz de conectividad [num_tri x 3]
 * ============================================================ */
FUNCTIONINFO fi_TriElements = {
    "tri_elements",
    "nx,ny",
    "Generates triangular element connectivity for nx by ny grid",
    (LPCFUNCTION)TriElementsFunc,
    COMPLEX_ARRAY,
    2,
    {COMPLEX_SCALAR, COMPLEX_SCALAR}
};

LRESULT TriElementsFunc(LPCOMPLEXARRAY result,
                        LPCCOMPLEXSCALAR pNx, LPCCOMPLEXSCALAR pNy)
{
    int nx, ny;
    int num_tri, tri_idx;
    int i, j, n1, n2, n3, n4;

    /* Verificar parametros */
    if (pNx->imag != 0 || pNy->imag != 0)
        return MAKELRESULT(MUST_BE_REAL, 1);

    nx = (int)(pNx->real + 0.5);
    ny = (int)(pNy->real + 0.5);

    if (nx < 1 || ny < 1)
        return MAKELRESULT(MUST_BE_INTEGER, 1);

    /* Numero de triangulos: 2 * nx * ny */
    num_tri = 2 * nx * ny;

    /* Allocar resultado: [num_tri x 3] */
    if (!MathcadArrayAllocate(result, num_tri, 3, TRUE, FALSE))
        return MAKELRESULT(INSUFFICIENT_MEMORY, 0);

    /* Generar conectividad (indices base 1 para Mathcad) */
    tri_idx = 0;
    for (j = 0; j < ny; j++) {
        for (i = 0; i < nx; i++) {
            /* Nodos del cuadrilatero (base 1) */
            n1 = j * (nx + 1) + i + 1;
            n2 = j * (nx + 1) + i + 2;
            n3 = (j + 1) * (nx + 1) + i + 2;
            n4 = (j + 1) * (nx + 1) + i + 1;

            /* Triangulo 1: n1-n2-n4 */
            result->hReal[0][tri_idx] = n1;
            result->hReal[1][tri_idx] = n2;
            result->hReal[2][tri_idx] = n4;
            tri_idx++;

            /* Triangulo 2: n2-n3-n4 */
            result->hReal[0][tri_idx] = n2;
            result->hReal[1][tri_idx] = n3;
            result->hReal[2][tri_idx] = n4;
            tri_idx++;
        }
    }

    return 0;
}

/* ============================================================
 * tri_area - Calcula el area de un triangulo
 * Formula: A = 0.5 * |x1(y2-y3) + x2(y3-y1) + x3(y1-y2)|
 * ============================================================ */
FUNCTIONINFO fi_TriArea = {
    "tri_area",
    "x1,y1,x2,y2,x3,y3",
    "Calculates the area of a triangle given vertex coordinates",
    (LPCFUNCTION)TriAreaFunc,
    COMPLEX_SCALAR,
    6,
    {COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR,
     COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR}
};

LRESULT TriAreaFunc(LPCOMPLEXSCALAR pResult,
                    LPCCOMPLEXSCALAR px1, LPCCOMPLEXSCALAR py1,
                    LPCCOMPLEXSCALAR px2, LPCCOMPLEXSCALAR py2,
                    LPCCOMPLEXSCALAR px3, LPCCOMPLEXSCALAR py3)
{
    double x1, y1, x2, y2, x3, y3;
    double area;

    /* Verificar que sean reales */
    if (px1->imag != 0 || py1->imag != 0 ||
        px2->imag != 0 || py2->imag != 0 ||
        px3->imag != 0 || py3->imag != 0)
        return MAKELRESULT(MUST_BE_REAL, 1);

    x1 = px1->real; y1 = py1->real;
    x2 = px2->real; y2 = py2->real;
    x3 = px3->real; y3 = py3->real;

    /* Area usando formula del determinante */
    area = 0.5 * FABS(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2));

    pResult->real = area;
    pResult->imag = 0.0;

    return 0;
}

/* ============================================================
 * tri_quality - Calcula la calidad de un triangulo
 * Usa aspect ratio: 4*sqrt(3)*A / (a^2 + b^2 + c^2)
 * Valor 1 = triangulo equilatero perfecto
 * ============================================================ */
FUNCTIONINFO fi_TriQuality = {
    "tri_quality",
    "x1,y1,x2,y2,x3,y3",
    "Calculates triangle quality (1=equilateral, 0=degenerate)",
    (LPCFUNCTION)TriQualityFunc,
    COMPLEX_SCALAR,
    6,
    {COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR,
     COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR}
};

LRESULT TriQualityFunc(LPCOMPLEXSCALAR pResult,
                       LPCCOMPLEXSCALAR px1, LPCCOMPLEXSCALAR py1,
                       LPCCOMPLEXSCALAR px2, LPCCOMPLEXSCALAR py2,
                       LPCCOMPLEXSCALAR px3, LPCCOMPLEXSCALAR py3)
{
    double x1, y1, x2, y2, x3, y3;
    double a2, b2, c2;  /* longitudes al cuadrado */
    double area, quality;

    /* Verificar que sean reales */
    if (px1->imag != 0 || py1->imag != 0 ||
        px2->imag != 0 || py2->imag != 0 ||
        px3->imag != 0 || py3->imag != 0)
        return MAKELRESULT(MUST_BE_REAL, 1);

    x1 = px1->real; y1 = py1->real;
    x2 = px2->real; y2 = py2->real;
    x3 = px3->real; y3 = py3->real;

    /* Longitudes de lados al cuadrado */
    a2 = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1);
    b2 = (x3 - x2) * (x3 - x2) + (y3 - y2) * (y3 - y2);
    c2 = (x1 - x3) * (x1 - x3) + (y1 - y3) * (y1 - y3);

    /* Area con signo */
    area = 0.5 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2));

    /* Calidad: 4*sqrt(3)*A / (a^2 + b^2 + c^2) */
    if (a2 + b2 + c2 > 0) {
        quality = 4.0 * 1.7320508075688772 * FABS(area) / (a2 + b2 + c2);
    } else {
        quality = 0.0;
    }

    pResult->real = quality;
    pResult->imag = 0.0;

    return 0;
}

/* ============================================================
 * tri_centroid - Calcula el centroide de un triangulo
 * Salida: vector [x_c, y_c]
 * ============================================================ */
FUNCTIONINFO fi_TriCentroid = {
    "tri_centroid",
    "x1,y1,x2,y2,x3,y3",
    "Calculates triangle centroid [xc, yc]",
    (LPCFUNCTION)TriCentroidFunc,
    COMPLEX_ARRAY,
    6,
    {COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR,
     COMPLEX_SCALAR, COMPLEX_SCALAR, COMPLEX_SCALAR}
};

LRESULT TriCentroidFunc(LPCOMPLEXARRAY result,
                        LPCCOMPLEXSCALAR px1, LPCCOMPLEXSCALAR py1,
                        LPCCOMPLEXSCALAR px2, LPCCOMPLEXSCALAR py2,
                        LPCCOMPLEXSCALAR px3, LPCCOMPLEXSCALAR py3)
{
    double x1, y1, x2, y2, x3, y3;

    /* Verificar que sean reales */
    if (px1->imag != 0 || py1->imag != 0 ||
        px2->imag != 0 || py2->imag != 0 ||
        px3->imag != 0 || py3->imag != 0)
        return MAKELRESULT(MUST_BE_REAL, 1);

    x1 = px1->real; y1 = py1->real;
    x2 = px2->real; y2 = py2->real;
    x3 = px3->real; y3 = py3->real;

    /* Allocar resultado: vector de 2 elementos */
    if (!MathcadArrayAllocate(result, 2, 1, TRUE, FALSE))
        return MAKELRESULT(INSUFFICIENT_MEMORY, 0);

    /* Centroide = promedio de vertices */
    result->hReal[0][0] = (x1 + x2 + x3) / 3.0;
    result->hReal[0][1] = (y1 + y2 + y3) / 3.0;

    return 0;
}

/* ============================================================
 * DLL Entry Point
 * ============================================================ */
BOOL WINAPI DllEntryPoint(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
    switch (fdwReason) {
        case DLL_PROCESS_ATTACH:
            /* Registrar funciones */
            if (!CreateUserFunction(hinstDLL, &fi_TriRectMesh))
                return FALSE;
            if (!CreateUserFunction(hinstDLL, &fi_TriNodes))
                return FALSE;
            if (!CreateUserFunction(hinstDLL, &fi_TriElements))
                return FALSE;
            if (!CreateUserFunction(hinstDLL, &fi_TriArea))
                return FALSE;
            if (!CreateUserFunction(hinstDLL, &fi_TriQuality))
                return FALSE;
            if (!CreateUserFunction(hinstDLL, &fi_TriCentroid))
                return FALSE;

            /* Registrar mensajes de error */
            if (!CreateUserErrorMessageTable(hinstDLL, 4, myErrorMessages))
                return FALSE;
            break;

        case DLL_PROCESS_DETACH:
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
            break;
    }
    return TRUE;
}
