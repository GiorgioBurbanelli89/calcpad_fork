// ============================================================================
// calculadora.cpp - CODIGO DEL EXE
// ============================================================================
//
// Este archivo se compila como un EXE (Ejecutable)
//
// IMPORTANTE:
//   - SI tiene main()
//   - SI se puede ejecutar directamente
//   - Carga la DLL matematicas.dll
//   - Usa las funciones de la DLL
//
// Compilar:
//   g++ -o calculadora.exe calculadora.cpp
//
// Ejecutar:
//   calculadora.exe
//
// ============================================================================

#include <iostream>
#include <windows.h>
#include <iomanip>

using namespace std;

// ============================================================================
// DEFINICION DE TIPOS DE FUNCIONES
// ============================================================================

// Tipo para funciones que toman 2 doubles y retornan double
typedef double (*FuncDosDoblesRetornaDoble)(double, double);

// Tipo para funciones que toman 1 double y retornan double
typedef double (*FuncUnDobleRetornaDoble)(double);

// ============================================================================
// FUNCION PRINCIPAL (PUNTO DE ENTRADA)
// ============================================================================

int main() {
    // Configurar precision de salida
    cout << fixed << setprecision(4);

    cout << "========================================" << endl;
    cout << "     CALCULADORA (usando DLL)" << endl;
    cout << "========================================" << endl;
    cout << endl;

    // ------------------------------------------------------------------------
    // PASO 1: CARGAR LA DLL
    // ------------------------------------------------------------------------
    cout << "PASO 1: Cargando matematicas.dll..." << endl;

    HMODULE dll = LoadLibrary("matematicas.dll");

    if (!dll) {
        cout << "  ✗ ERROR: No se pudo cargar matematicas.dll" << endl;
        cout << endl;
        cout << "Asegurate de que matematicas.dll este en la misma carpeta" << endl;
        cout << "Compila la DLL primero con: compilar.bat" << endl;
        system("pause");
        return 1;
    }

    cout << "  ✓ DLL cargada exitosamente" << endl;
    cout << endl;

    // ------------------------------------------------------------------------
    // PASO 2: OBTENER LAS FUNCIONES DE LA DLL
    // ------------------------------------------------------------------------
    cout << "PASO 2: Obteniendo funciones de la DLL..." << endl;

    // GetProcAddress busca la función por su nombre en la DLL
    auto sumar = (FuncDosDoblesRetornaDoble)GetProcAddress(dll, "sumar");
    auto restar = (FuncDosDoblesRetornaDoble)GetProcAddress(dll, "restar");
    auto multiplicar = (FuncDosDoblesRetornaDoble)GetProcAddress(dll, "multiplicar");
    auto dividir = (FuncDosDoblesRetornaDoble)GetProcAddress(dll, "dividir");
    auto raiz_cuadrada = (FuncUnDobleRetornaDoble)GetProcAddress(dll, "raiz_cuadrada");
    auto potencia = (FuncDosDoblesRetornaDoble)GetProcAddress(dll, "potencia");
    auto valor_absoluto = (FuncUnDobleRetornaDoble)GetProcAddress(dll, "valor_absoluto");

    // Verificar que todas las funciones se encontraron
    if (!sumar || !restar || !multiplicar || !dividir ||
        !raiz_cuadrada || !potencia || !valor_absoluto) {
        cout << "  ✗ ERROR: No se pudieron encontrar las funciones en la DLL" << endl;
        FreeLibrary(dll);
        system("pause");
        return 1;
    }

    cout << "  ✓ Funciones encontradas:" << endl;
    cout << "    - sumar()" << endl;
    cout << "    - restar()" << endl;
    cout << "    - multiplicar()" << endl;
    cout << "    - dividir()" << endl;
    cout << "    - raiz_cuadrada()" << endl;
    cout << "    - potencia()" << endl;
    cout << "    - valor_absoluto()" << endl;
    cout << endl;

    // ------------------------------------------------------------------------
    // PASO 3: USAR LAS FUNCIONES DE LA DLL
    // ------------------------------------------------------------------------
    cout << "PASO 3: Usando las funciones de la DLL..." << endl;
    cout << endl;

    double a = 10.0;
    double b = 5.0;

    cout << "Numeros de prueba:" << endl;
    cout << "  a = " << a << endl;
    cout << "  b = " << b << endl;
    cout << endl;

    cout << "Resultados:" << endl;
    cout << "  a + b        = " << sumar(a, b) << endl;
    cout << "  a - b        = " << restar(a, b) << endl;
    cout << "  a * b        = " << multiplicar(a, b) << endl;
    cout << "  a / b        = " << dividir(a, b) << endl;
    cout << "  √a           = " << raiz_cuadrada(a) << endl;
    cout << "  a^b          = " << potencia(a, b) << endl;
    cout << "  |-7.5|       = " << valor_absoluto(-7.5) << endl;
    cout << endl;

    // ------------------------------------------------------------------------
    // PASO 4: EJEMPLO PRACTICO - ECUACION CUADRATICA
    // ------------------------------------------------------------------------
    cout << "EJEMPLO PRACTICO: Ecuacion cuadratica" << endl;
    cout << "  ax² + bx + c = 0" << endl;
    cout << "  a=1, b=-5, c=6" << endl;
    cout << endl;

    double coef_a = 1.0;
    double coef_b = -5.0;
    double coef_c = 6.0;

    // Discriminante: b² - 4ac
    double discriminante = restar(
        potencia(coef_b, 2),
        multiplicar(multiplicar(4, coef_a), coef_c)
    );

    cout << "  Discriminante = b² - 4ac = " << discriminante << endl;

    if (discriminante >= 0) {
        double sqrt_discriminante = raiz_cuadrada(discriminante);

        // x1 = (-b + √discriminante) / (2a)
        double x1 = dividir(
            sumar(multiplicar(-1, coef_b), sqrt_discriminante),
            multiplicar(2, coef_a)
        );

        // x2 = (-b - √discriminante) / (2a)
        double x2 = dividir(
            restar(multiplicar(-1, coef_b), sqrt_discriminante),
            multiplicar(2, coef_a)
        );

        cout << "  x1 = " << x1 << endl;
        cout << "  x2 = " << x2 << endl;
    } else {
        cout << "  No hay soluciones reales" << endl;
    }
    cout << endl;

    // ------------------------------------------------------------------------
    // PASO 4: LIBERAR LA DLL
    // ------------------------------------------------------------------------
    cout << "PASO 4: Liberando la DLL..." << endl;
    FreeLibrary(dll);
    cout << "  ✓ DLL liberada" << endl;
    cout << endl;

    cout << "========================================" << endl;
    cout << "         PROGRAMA TERMINADO" << endl;
    cout << "========================================" << endl;
    cout << endl;

    system("pause");
    return 0;
}

// ============================================================================
// EXPLICACION DEL FLUJO
// ============================================================================
//
// 1. Este programa (calculadora.exe) es un EJECUTABLE
//    - Tiene main()
//    - Se puede ejecutar directamente
//
// 2. Cuando se ejecuta:
//    a) Carga matematicas.dll con LoadLibrary()
//    b) Busca las funciones en la DLL con GetProcAddress()
//    c) Llama a esas funciones como si fueran propias
//    d) Libera la DLL con FreeLibrary()
//
// 3. La DLL (matematicas.dll) NO se ejecuta sola
//    - No tiene main()
//    - Solo contiene funciones
//    - Este EXE las usa
//
// ============================================================================
// ANALOGIA
// ============================================================================
//
// DLL = Caja de herramientas (martillo, destornillador, sierra)
// EXE = Carpintero que usa las herramientas
//
// La caja de herramientas sola no construye nada.
// El carpintero (EXE) toma las herramientas (funciones de la DLL) y las usa.
//
// ============================================================================
