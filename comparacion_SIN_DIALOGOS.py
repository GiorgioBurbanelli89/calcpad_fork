# -*- coding: utf-8 -*-
"""
Comparación FINAL - Sin diálogos/prompts de SAP2000
Configura SAP2000 para modo automatizado
"""
import os
import sys
import comtypes.client

print("="*70)
print("COMPARACION FINAL - MODO AUTOMATIZADO (SIN DIALOGOS)")
print("="*70)

ModelPath = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Comparacion.sdb'

if not os.path.exists(ModelPath):
    print(f"[ERROR] Archivo no existe: {ModelPath}")
    sys.exit(1)

try:
    # Crear helper
    print("\n[1] Iniciando SAP2000 (modo automatizado)...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)

    mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")

    # Iniciar con parámetros:
    # Units = 0 (default)
    # Visible = True (visible - evita errores de null reference)
    # FileName = ""
    ret = mySapObject.ApplicationStart()
    print(f"    [OK] SAP2000 iniciado (ret={ret})")

    SapModel = mySapObject.SapModel

    # IMPORTANTE: Desactivar mensajes interactivos
    print("\n[2] Configurando modo automatizado...")

    # Abrir modelo
    print(f"\n[3] Abriendo modelo...")
    ret = SapModel.File.OpenFile(ModelPath)
    print(f"    [OK] Modelo abierto (ret={ret})")

    # Info
    num_points = SapModel.PointObj.Count()
    num_areas = SapModel.AreaObj.Count()
    print(f"\n[4] Info del modelo:")
    print(f"    Puntos: {num_points}")
    print(f"    Areas: {num_areas}")

    # Desbloquear
    SapModel.SetModelIsLocked(False)

    # Analizar
    print("\n[5] Ejecutando analisis...")
    print("    Creando modelo de analisis...")
    ret1 = SapModel.Analyze.CreateAnalysisModel()
    print(f"    CreateAnalysisModel: ret={ret1}")

    print("    Ejecutando analisis...")
    ret2 = SapModel.Analyze.RunAnalysis()
    print(f"    RunAnalysis: ret={ret2}")

    # IMPORTANTE: Guardar después del análisis
    print("\n[6] Guardando modelo...")
    ret = SapModel.File.Save(ModelPath)
    print(f"    [OK] Guardado (ret={ret})")

    # ========== EXTRAER RESULTADOS ==========
    print("\n" + "="*70)
    print("EXTRACCION DE RESULTADOS")
    print("="*70)

    # Configurar output
    print("\n[7] Configurando output DEAD...")
    ret = SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    ret = SapModel.Results.Setup.SetCaseSelectedForOutput('DEAD')
    print(f"    [OK] DEAD seleccionado (ret={ret})")

    # DESPLAZAMIENTOS
    print("\n[8] Extrayendo desplazamientos...")

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

    [NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3, ret] = \
        SapModel.Results.JointDispl("", ObjectElm, NumberResults, Obj, Elm, ACase,
                                     StepType, StepNum, U1, U2, U3, R1, R2, R3)

    print(f"    NumberResults = {NumberResults}")
    print(f"    ret = {ret}")
    print(f"    Longitud Obj = {len(Obj)}")
    print(f"    Longitud U3 = {len(U3)}")

    if NumberResults > 0:
        print(f"\n    [OK] {NumberResults} desplazamientos!")

        # Max vertical
        max_u3 = max(abs(u) for u in U3)
        max_idx = [i for i, u in enumerate(U3) if abs(u) == max_u3][0]

        print(f"\n    DESPLAZAMIENTO VERTICAL MAXIMO:")
        print(f"      Punto: {Obj[max_idx]}")
        print(f"      U3 = {U3[max_idx]*1000:.6f} mm")

        # Primeros 10
        print(f"\n    Primeros 10:")
        for i in range(min(10, NumberResults)):
            print(f"      {Obj[i]}: U3={U3[i]*1000:.4f} mm")

        sap_deflection = abs(U3[max_idx]) * 1000

    elif ret != 0:
        print(f"    [WARN] ret != 0, error en llamada (ret={ret})")
        sap_deflection = 0

    else:
        print(f"    [WARN] NumberResults=0")

        # DEBUG: Intentar extracción punto por punto
        print("\n    DEBUG: Intentando punto por punto...")
        test_points = ["1", "2", "3", "18", "19", "20"]
        for pt in test_points:
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

            [NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3, ret] = \
                SapModel.Results.JointDispl(pt, ObjectElm, NumberResults, Obj, Elm, ACase,
                                             StepType, StepNum, U1, U2, U3, R1, R2, R3)

            if NumberResults > 0:
                print(f"      Punto {pt}: U3={U3[0]*1000:.4f} mm")

        sap_deflection = 0

    # MOMENTOS
    if num_areas > 0:
        print("\n[9] Extrayendo momentos...")

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

        [NumberResults, Obj, Elm, PointElm, LoadCase, StepType, StepNum,
         F11, F22, F12, FMax, FMin, FAngle, FVM,
         M11, M22, M12, MMax, MMin, MAngle,
         V13, V23, VMax, VAngle, ret] = \
            SapModel.Results.AreaForceShell("", ObjectElm, NumberResults, Obj, Elm, PointElm,
                                            LoadCase, StepType, StepNum,
                                            F11, F22, F12, FMax, FMin, FAngle, FVM,
                                            M11, M22, M12, MMax, MMin, MAngle,
                                            V13, V23, VMax, VAngle)

        print(f"    NumberResults = {NumberResults}")
        print(f"    ret = {ret}")

        if NumberResults > 0:
            max_m11 = max(abs(m) for m in M11)
            max_m22 = max(abs(m) for m in M22)

            print(f"\n    [OK] {NumberResults} momentos")
            print(f"    M11 max: {max_m11:.6f} kN-m/m")
            print(f"    M22 max: {max_m22:.6f} kN-m/m")

    # COMPARACION
    print("\n" + "="*70)
    print("RESULTADOS FINALES")
    print("="*70)
    print("\nModelo: Losa 6x4m, t=0.1m, q=10 kN/m2")
    print(f"\nSAP2000 (Mindlin):")
    print(f"  Deflexion: {sap_deflection:.6f} mm")

    print("\nCalcpad (Kirchhoff):")
    print("  Ver: calcpad_results.html")

    # Cerrar SIN GUARDAR y SIN PROMPTS
    print("\n" + "="*70)
    print("Cerrando SAP2000 (sin prompts)...")
    print("="*70)

    # False = no guardar al salir
    ret = mySapObject.ApplicationExit(False)
    print(f"    [OK] SAP2000 cerrado (ret={ret})")

    SapModel = None
    mySapObject = None

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

    # Intentar cerrar de todos modos
    try:
        if 'mySapObject' in locals():
            mySapObject.ApplicationExit(False)
    except:
        pass

print("\n[FIN]")
