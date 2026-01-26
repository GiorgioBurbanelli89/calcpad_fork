# -*- coding: utf-8 -*-
"""
SAP2000 - Comparación FINAL con Calcpad
Abre modelo existente y extrae resultados
"""
import comtypes.client
import os

print("="*70)
print("COMPARACION SAP2000 vs CALCPAD - EXTRACCION FINAL")
print("="*70)

# Archivo del modelo de comparación
model_file = R"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Comparacion.sdb"

if not os.path.exists(model_file):
    print(f"[ERROR] Archivo no existe: {model_file}")
    exit(1)

try:
    # Iniciar SAP2000
    print("\n[1] Iniciando SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    sap = helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject")
    sap.ApplicationStart()
    model = sap.SapModel
    print("    [OK] SAP2000 iniciado")

    # Abrir modelo de comparación
    print(f"\n[2] Abriendo modelo...")
    print(f"    {model_file}")
    ret = model.File.OpenFile(model_file)
    print(f"    [OK] Modelo abierto (ret={ret})")

    # Info
    num_points = model.PointObj.Count()
    num_areas = model.AreaObj.Count()
    print(f"\n[3] Información del modelo:")
    print(f"    Puntos: {num_points}")
    print(f"    Áreas: {num_areas}")

    # RE-ANALIZAR (por si acaso)
    print("\n[4] Re-ejecutando análisis...")
    model.SetModelIsLocked(False)
    ret1 = model.Analyze.CreateAnalysisModel()
    ret2 = model.Analyze.RunAnalysis()
    print(f"    CreateAnalysisModel: ret={ret1}")
    print(f"    RunAnalysis: ret={ret2}")

    # RESULTADOS
    print("\n" + "="*70)
    print("EXTRACCION DE RESULTADOS")
    print("="*70)

    # Seleccionar caso DEAD
    print("\n[5] Configurando output...")
    model.Results.Setup.DeselectAllCasesAndCombosForOutput()
    model.Results.Setup.SetCaseSelectedForOutput("DEAD")
    print("    [OK] Caso DEAD seleccionado")

    # DESPLAZAMIENTOS
    print("\n[6] Desplazamientos de juntas...")
    ret = model.Results.JointDispl("", 0)

    print(f"    Tipo: {type(ret)}")
    print(f"    Longitud tuple: {len(ret)}")
    print(f"    ret[0] (NumberResults): {ret[0]}")

    if ret[0] > 0:
        NumberResults = ret[0]
        Obj = ret[1]  # Nombres de puntos
        U1 = ret[6]   # Despl X
        U2 = ret[7]   # Despl Y
        U3 = ret[8]   # Despl Z (vertical)

        print(f"\n    [OK] {NumberResults} resultados extraídos!")

        # Encontrar desplazamiento vertical máximo
        max_u3 = max(abs(u) for u in U3)
        max_idx = [i for i, u in enumerate(U3) if abs(u) == max_u3][0]

        print(f"\n    Desplazamiento vertical MÁXIMO:")
        print(f"      Punto: {Obj[max_idx]}")
        print(f"      U3 = {U3[max_idx]*1000:.6f} mm")

        # Mostrar primeros 10
        print(f"\n    Primeros 10 puntos:")
        print(f"    {'Punto':<8} {'U1 (mm)':<12} {'U2 (mm)':<12} {'U3 (mm)':<12}")
        print("    " + "-"*50)
        for i in range(min(10, NumberResults)):
            print(f"    {Obj[i]:<8} {U1[i]*1000:>11.4f} {U2[i]*1000:>11.4f} {U3[i]*1000:>11.4f}")

    else:
        print("    [ERROR] Sin resultados!")

    # FUERZAS EN ÁREAS (MOMENTOS)
    if num_areas > 0:
        print("\n[7] Fuerzas en áreas (momentos de placa)...")
        area_names = model.AreaObj.GetNameList()[1]

        # Extraer de todas las áreas
        ret_area = model.Results.AreaForceShell("", 0)
        print(f"    ret[0] (NumberResults): {ret_area[0]}")

        if ret_area[0] > 0:
            NumberResults = ret_area[0]
            AreaName = ret_area[1]
            M11 = ret_area[12]  # Momento en dirección 1-1 (kN-m/m)
            M22 = ret_area[13]  # Momento en dirección 2-2 (kN-m/m)
            M12 = ret_area[14]  # Momento de torsión (kN-m/m)

            print(f"\n    [OK] {NumberResults} resultados de momentos")

            # Máximos absolutos
            max_m11 = max(abs(m) for m in M11)
            max_m22 = max(abs(m) for m in M22)
            max_m12 = max(abs(m) for m in M12)

            print(f"\n    Momentos MÁXIMOS:")
            print(f"      M11 (Mx) = {max_m11:.4f} kN-m/m")
            print(f"      M22 (My) = {max_m22:.4f} kN-m/m")
            print(f"      M12 (Mxy) = {max_m12:.4f} kN-m/m")

        else:
            print("    [ERROR] Sin resultados de áreas!")

    # REACCIONES
    print("\n[8] Reacciones en apoyos...")
    ret_react = model.Results.JointReact("", 0)
    print(f"    ret[0] (NumberResults): {ret_react[0]}")

    if ret_react[0] > 0:
        NumberResults = ret_react[0]
        F3 = ret_react[8]  # Fuerza vertical

        total_reaction = sum(F3)
        print(f"\n    [OK] {NumberResults} reacciones")
        print(f"    Suma de reacciones verticales: {total_reaction:.4f} kN")

    # COMPARACIÓN CON CALCPAD
    print("\n" + "="*70)
    print("COMPARACION CON CALCPAD")
    print("="*70)
    print("\nModelo: Losa 6x4m, t=0.1m, q=10 kN/m2")
    print("\nRESULTADOS CALCPAD (esperados):")
    print("  - Ver archivo: calcpad_results.html")
    print("\nRESULTADOS SAP2000 (obtenidos arriba):")
    print("  - Desplazamiento máximo (U3)")
    print("  - Momentos máximos (M11, M22)")
    print("\nNOTA: Diferencias esperadas debido a:")
    print("  - Calcpad: Kirchhoff (placa delgada)")
    print("  - SAP2000: Mindlin-Reissner (deformación por cortante)")
    print("  - Para placas delgadas (L/t>20): diferencia <10%")

    print("\n" + "="*70)
    print("SAP2000 dejado abierto para inspección")
    print(f"Modelo: {model_file}")
    print("="*70)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n[FIN]")
