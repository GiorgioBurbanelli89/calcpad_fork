#!/bin/bash
################################################################################
# Script de Comparación FEM: Calcpad vs Mathcad
################################################################################

echo ""
echo "========================================================================"
echo "Sistema de Comparación FEM: Calcpad vs Mathcad"
echo "========================================================================"
echo ""

CLI_PATH="../Calcpad.Cli/bin/Release/net10.0/Cli.exe"
TEST_FILE="mathcad_fem_comparison.cpd"
OUTPUT_FILE="mathcad_fem_comparison.html"

# Verificar que existe el CLI
if [ ! -f "$CLI_PATH" ]; then
    echo "ERROR: No se encontró el CLI de Calcpad"
    echo ""
    echo "Compilando CLI..."
    cd ../Calcpad.Cli
    dotnet build -c Release
    cd ../Tests
    echo ""
fi

echo "[1/2] Generando resultados de Calcpad..."
echo ""
"$CLI_PATH" "$TEST_FILE" "$OUTPUT_FILE"

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Falló la generación del HTML"
    exit 1
fi

echo ""
echo "[2/2] HTML generado exitosamente: $OUTPUT_FILE"
echo "(El CLI abrirá automáticamente el HTML en el navegador)"

echo ""
echo "========================================================================"
echo "PRÓXIMO PASO:"
echo "========================================================================"
echo ""
echo "1. Revisa el HTML con los resultados de Calcpad"
echo "2. Abre Mathcad Prime 10"
echo "3. Copia el código de: INSTRUCCIONES_MATHCAD.md"
echo "4. Ejecuta en Mathcad y anota los resultados en: COMPARACION_RESULTADOS.md"
echo ""
echo "Archivos generados:"
echo "  - $OUTPUT_FILE"
echo "  - RESULTADOS_CALCPAD.md"
echo "  - INSTRUCCIONES_MATHCAD.md"
echo "  - COMPARACION_RESULTADOS.md"
echo ""
echo "========================================================================"
