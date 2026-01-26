# -*- coding: utf-8 -*-
"""
Ejecutar Rectangular Slab FEA con PyCalcpad
"""
import sys
import os

# Agregar el path a PyCalcpad
sys.path.append(r'C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Api\PyCalcpad\bin\Debug\net10.0')

try:
    import clr
    clr.AddReference('PyCalcpad')
    from PyCalcpad import Calculator

    # Ruta al archivo .cpd
    cpd_file = r'C:\Users\j-b-j\Documents\Calcpad\Examples\Mechanics\Finite Elements\Rectangular Slab FEA.cpd'

    print("="*70)
    print("EJECUTANDO: Rectangular Slab FEA.cpd")
    print("="*70)

    # Leer el archivo
    with open(cpd_file, 'r', encoding='utf-8') as f:
        code = f.read()

    # Crear calculator
    calc = Calculator()

    # Ejecutar
    print("\nEjecutando cálculo...")
    result = calc.Calculate(code)

    # Guardar resultado
    output_file = r'C:\Users\j-b-j\Documents\Calcpad-7.5.7\rectangular_slab_calcpad_output.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"\n[OK] Resultado guardado en: {output_file}")

    # Extraer valores específicos del resultado
    print("\n" + "="*70)
    print("BUSCANDO VALORES CLAVE EN EL RESULTADO")
    print("="*70)

    # Buscar w(a/2; b/2)
    if "w(a/2; b/2)" in result or "w(3; 2)" in result:
        print("\n[ENCONTRADO] Desplazamiento en el centro")

    # Buscar M_x(a/2; b/2)
    if "M_x(a/2; b/2)" in result or "Maximal value" in result:
        print("[ENCONTRADO] Momentos máximos")

    # Extraer líneas con resultados numéricos importantes
    lines = result.split('\n')
    for i, line in enumerate(lines):
        if 'Maximal value' in line or 'w(a/2; b/2)' in line or 'M_x(a/2; b/2)' in line or 'M_y(a/2; b/2)' in line:
            print(f"\nLínea {i}: {line[:200]}")

    print("\n" + "="*70)
    print("Para ver el resultado completo, abre:")
    print(output_file)
    print("="*70)

except ImportError as e:
    print(f"\n[ERROR] No se pudo importar PyCalcpad: {e}")
    print("\nVerificando si existe PyCalcpad.dll...")
    pycalcpad_path = r'C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Api\PyCalcpad\bin\Debug\net10.0\PyCalcpad.dll'
    if os.path.exists(pycalcpad_path):
        print(f"[OK] PyCalcpad.dll existe en: {pycalcpad_path}")
    else:
        print(f"[ERROR] No se encontró PyCalcpad.dll en: {pycalcpad_path}")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n[FIN]")
