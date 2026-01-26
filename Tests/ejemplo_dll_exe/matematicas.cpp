// ============================================================================
// matematicas.cpp - CODIGO DE LA DLL
// ============================================================================
//
// Este archivo se compila como una DLL (Dynamic Link Library)
//
// IMPORTANTE:
//   - NO tiene main()
//   - NO se puede ejecutar directamente
//   - Contiene funciones que otros programas pueden usar
//
// Compilar:
//   g++ -shared -o matematicas.dll matematicas.cpp
//
// ============================================================================

#include <cmath>
#include <iostream>

// Macro para exportar funciones en Windows
#ifdef _WIN32
    #define DLL_EXPORT __declspec(dllexport)
#else
    #define DLL_EXPORT
#endif

// ============================================================================
// FUNCIONES EXPORTADAS
// ============================================================================
//
// "extern C" hace que los nombres de funciones no sean modificados (name mangling)
// Esto permite que otros lenguajes (Python, C#, etc.) puedan encontrarlas
//
extern "C" {

    // Suma dos números
    DLL_EXPORT double sumar(double a, double b) {
        return a + b;
    }

    // Resta dos números
    DLL_EXPORT double restar(double a, double b) {
        return a - b;
    }

    // Multiplica dos números
    DLL_EXPORT double multiplicar(double a, double b) {
        return a * b;
    }

    // Divide dos números
    DLL_EXPORT double dividir(double a, double b) {
        if (b == 0) {
            std::cerr << "Error: Division por cero" << std::endl;
            return 0;
        }
        return a / b;
    }

    // Calcula la raíz cuadrada
    DLL_EXPORT double raiz_cuadrada(double x) {
        if (x < 0) {
            std::cerr << "Error: Raiz de numero negativo" << std::endl;
            return 0;
        }
        return std::sqrt(x);
    }

    // Calcula x elevado a la potencia y
    DLL_EXPORT double potencia(double x, double y) {
        return std::pow(x, y);
    }

    // Calcula el valor absoluto
    DLL_EXPORT double valor_absoluto(double x) {
        return std::abs(x);
    }

}  // extern "C"

// ============================================================================
// NOTA IMPORTANTE
// ============================================================================
//
// ¿Ves? NO hay main() aquí.
//
// Esta DLL solo contiene funciones.
// Otro programa (un EXE) debe cargar esta DLL y llamar a estas funciones.
//
// No puedes ejecutar esta DLL directamente.
//
// ============================================================================
