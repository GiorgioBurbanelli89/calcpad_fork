# -*- coding: utf-8 -*-
"""
Comparación FINAL Calcpad vs SAP2000
Usando sintaxis oficial CSI para extracción de resultados
"""
import os
import sys
import comtypes.client

print("="*70)
print("COMPARACION FINAL: CALCPAD vs SAP2000")
print("="*70)

# Archivo del modelo de comparación (ya existente)
ModelPath = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Comparacion.sdb'

if not os.path.exists(ModelPath):
    print(f"[ERROR] Archivo no existe: {ModelPath}")
    sys.exit(1)

try:
    # Crear helper
    print("\n[1] Iniciando SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)

    # Crear instancia de SAP2000
    mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
    mySapObject.ApplicationStart()

    SapModel = mySapObject.SapModel
    print("    [OK] SAP2000 iniciado")

    # Abrir modelo existente
    print(f"\n[2] Abriendo modelo de comparación...")
    ret = SapModel.File.OpenFile(ModelPath)
    print(f"    [OK] Modelo abierto (ret={ret})")

    # Información del modelo
    num_points = SapModel.PointObj.Count()
    num_areas = SapModel.AreaObj.Count()
    print(f"\n[3] Información del modelo:")
    print(f"    Puntos: {num_points}")
    print(f"    Áreas: {num_areas}")

    # Desbloquear modelo
    SapModel.SetModelIsLocked(False)

    # Re-ejecutar análisis
    print("\n[4] Ejecutando análisis...")
    ret = SapModel.Analyze.RunAnalysis()
    print(f"    [OK] Análisis completado (ret={ret})")

    # Guardar (IMPORTANTE para que tenga resultados)
    print("\n[5] Guardando modelo con resultados...")
    ret = SapModel.File.Save(ModelPath)
    print(f"    [OK] Guardado")

    # ========== EXTRAER RESULTADOS ==========
    print("\n" + "="*70)
    print("RESULTADOS SAP2000")
    print("="*70)

    # Configurar output
    print("\n[6] Configurando output...")
    ret = SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    ret = SapModel.Results.Setup.SetCaseSelectedForOutput('DEAD')
    print("    [OK] Caso DEAD seleccionado")

    # DESPLAZAMIENTOS - TODOS LOS PUNTOS
    print("\n[7] Extrayendo desplazamientos (todos los puntos)...")

    NumberResults = 0
    Obj = []
    Elm = []
    ACase = []
    StepType = []
    StepNum = []
    U1 = []
    U2 = []
    U3 = []
    R1 = []
    R2 = []
    R3 = []
    ObjectElm = 0

    # Sintaxis oficial CSI
    [NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3, ret] = \
        SapModel.Results.JointDispl("", ObjectElm, NumberResults, Obj, Elm, ACase,
                                     StepType, StepNum, U1, U2, U3, R1, R2, R3)

    print(f"\n    NumberResults = {NumberResults}")

    if NumberResults > 0:
        print(f"\n    [OK] {NumberResults} resultados de desplazamiento")

        # Encontrar desplazamiento vertical máximo
        max_u3 = max(abs(u) for u in U3)
        max_idx = [i for i, u in enumerate(U3) if abs(u) == max_u3][0]

        print(f"\n    DESPLAZAMIENTO VERTICAL MÁXIMO:")
        print(f"      Punto: {Obj[max_idx]}")
        print(f"      U3 = {U3[max_idx]*1000:.6f} mm")

        # Mostrar primeros 10
        print(f"\n    Primeros 10 desplazamientos:")
        print(f"    {'Punto':<8} {'U1 (mm)':<12} {'U2 (mm)':<12} {'U3 (mm)':<12}")
        print("    " + "-"*50)
        for i in range(min(10, NumberResults)):
            print(f"    {Obj[i]:<8} {U1[i]*1000:>11.4f} {U2[i]*1000:>11.4f} {U3[i]*1000:>11.4f}")

        # Guardar para comparación
        sap_max_deflection = abs(U3[max_idx]) * 1000  # en mm

    else:
        print("    [ERROR] Sin resultados de desplazamiento")
        sap_max_deflection = 0

    # MOMENTOS EN ÁREAS (SHELL)
    print("\n[8] Extrayendo momentos en áreas...")

    if num_areas > 0:
        NumberResults = 0
        Obj = []
        Elm = []
        PointElm = []
        LoadCase = []
        StepType = []
        StepNum = []
        F11 = []
        F22 = []
        F12 = []
        FMax = []
        FMin = []
        FAngle = []
        FVM = []
        M11 = []
        M22 = []
        M12 = []
        MMax = []
        MMin = []
        MAngle = []
        V13 = []
        V23 = []
        VMax = []
        VAngle = []

        # Sintaxis oficial para AreaForceShell
        [NumberResults, Obj, Elm, PointElm, LoadCase, StepType, StepNum,
         F11, F22, F12, FMax, FMin, FAngle, FVM,
         M11, M22, M12, MMax, MMin, MAngle,
         V13, V23, VMax, VAngle, ret] = \
            SapModel.Results.AreaForceShell("", ObjectElm, NumberResults, Obj, Elm, PointElm,
                                            LoadCase, StepType, StepNum,
                                            F11, F22, F12, FMax, FMin, FAngle, FVM,
                                            M11, M22, M12, MMax, MMin, MAngle,
                                            V13, V23, VMax, VAngle)

        print(f"\n    NumberResults = {NumberResults}")

        if NumberResults > 0:
            print(f"\n    [OK] {NumberResults} resultados de momentos")

            # Encontrar momentos máximos
            max_m11 = max(abs(m) for m in M11) if M11 else 0
            max_m22 = max(abs(m) for m in M22) if M22 else 0
            max_m12 = max(abs(m) for m in M12) if M12 else 0

            print(f"\n    MOMENTOS MÁXIMOS:")
            print(f"      M11 (Mx) = {max_m11:.6f} kN-m/m")
            print(f"      M22 (My) = {max_m22:.6f} kN-m/m")
            print(f"      M12 (Mxy) = {max_m12:.6f} kN-m/m")

            # Mostrar primeros 5
            print(f"\n    Primeros 5 puntos de momento:")
            print(f"    {'Área':<8} {'M11':<12} {'M22':<12} {'M12':<12}")
            print("    " + "-"*50)
            for i in range(min(5, NumberResults)):
                print(f"    {Obj[i]:<8} {M11[i]:>11.6f} {M22[i]:>11.6f} {M12[i]:>11.6f}")

            sap_max_m11 = max_m11
            sap_max_m22 = max_m22

        else:
            print("    [ERROR] Sin resultados de momentos")
            sap_max_m11 = 0
            sap_max_m22 = 0

    # REACCIONES
    print("\n[9] Extrayendo reacciones...")

    NumberResults = 0
    Obj = []
    Elm = []
    LoadCase = []
    StepType = []
    StepNum = []
    F1 = []
    F2 = []
    F3 = []
    M1 = []
    M2 = []
    M3 = []

    [NumberResults, Obj, Elm, LoadCase, StepType, StepNum, F1, F2, F3, M1, M2, M3, ret] = \
        SapModel.Results.JointReact("", ObjectElm, NumberResults, Obj, Elm, LoadCase,
                                    StepType, StepNum, F1, F2, F3, M1, M2, M3)

    if NumberResults > 0:
        total_F3 = sum(F3)
        print(f"\n    [OK] {NumberResults} reacciones")
        print(f"    Suma F3 (vertical): {total_F3:.4f} kN")
    else:
        print("    [ERROR] Sin resultados de reacciones")

    # ========== COMPARACIÓN CON CALCPAD ==========
    print("\n" + "="*70)
    print("COMPARACIÓN CON CALCPAD")
    print("="*70)

    print("\nModelo: Losa rectangular 6x4m, espesor 0.1m, carga 10 kN/m2")
    print("\nRESULTADOS SAP2000 (Mindlin-Reissner):")
    print(f"  Desplazamiento máximo: {sap_max_deflection:.6f} mm")
    if num_areas > 0 and NumberResults > 0:
        print(f"  Momento M11 (Mx) máximo: {sap_max_m11:.6f} kN-m/m")
        print(f"  Momento M22 (My) máximo: {sap_max_m22:.6f} kN-m/m")

    print("\nRESULTADOS CALCPAD (Kirchhoff):")
    print("  Ver archivo: calcpad_results.html")

    print("\n  NOTA: Calcpad usa teoría de Kirchhoff (placa delgada)")
    print("        SAP2000 usa teoría de Mindlin-Reissner (incluye cortante)")
    print("        Para placas delgadas (L/t > 20), diferencia esperada < 10%")

    # Cerrar SAP2000
    print("\n" + "="*70)
    print("COMPLETADO")
    print(f"Modelo guardado en: {ModelPath}")
    print("SAP2000 se cerrará")
    print("="*70)

    ret = mySapObject.ApplicationExit(False)
    SapModel = None
    mySapObject = None

    print("\n[OK] Comparación completada exitosamente!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n[FIN]")
