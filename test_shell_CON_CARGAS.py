# -*- coding: utf-8 -*-
"""
Test Shell Results - CON CARGAS APLICADAS
Basado en ejemplo VBA oficial pero agregando cargas
"""
import comtypes.client

print("="*70)
print("TEST SHELL - CON CARGAS")
print("="*70)

try:
    print("\n[1] Iniciando SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    SapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
    SapObject.ApplicationStart()
    SapModel = SapObject.SapModel
    print("    [OK] Iniciado")

    print("\n[2] Inicializando modelo...")
    ret = SapModel.InitializeNewModel(6)  # kN, m, C
    print(f"    [OK] ret={ret}")

    print("\n[3] Creando desde template NewWall...")
    ret = SapModel.File.NewWall(6, 1, 6, 1)  # Muro más pequeño
    print(f"    [OK] NewWall (ret={ret})")

    # AGREGAR CARGA UNIFORME A TODAS LAS ÁREAS
    print("\n[4] Aplicando carga uniforme...")

    # Obtener nombres de todas las áreas
    ret_areas = SapModel.AreaObj.GetNameList()
    num_areas = ret_areas[0]
    area_names = ret_areas[1]

    print(f"    Áreas en el modelo: {num_areas}")

    if num_areas > 0:
        # Aplicar carga a cada área
        for area_name in area_names:
            # SetLoadUniform(Name, LoadPat, Value, Dir, Replace, CSys, ItemType)
            # Dir = 6 means Gravity
            ret = SapModel.AreaObj.SetLoadUniform(area_name, "DEAD", 10, 6, True, "Global", 0)

        print(f"    [OK] Carga de 10 kN/m2 aplicada a {num_areas} áreas")

    # Save
    ModelPath = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\TEST_WALL_CARGAS.sdb'
    print(f"\n[5] Guardando...")
    ret = SapModel.File.Save(ModelPath)
    print(f"    [OK] Guardado (ret={ret})")

    # Run analysis
    print("\n[6] Ejecutando análisis...")
    ret = SapModel.Analyze.RunAnalysis()
    print(f"    [OK] Análisis (ret={ret})")

    # Configure output
    print("\n[7] Configurando output...")
    ret = SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    ret = SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")
    print("    [OK] Caso DEAD seleccionado")

    # Extract results for FIRST area
    print("\n[8] Extrayendo resultados...")

    if num_areas > 0:
        first_area = area_names[0]
        print(f"    Extrayendo de área: {first_area}")

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
        ObjectElm = 0

        [NumberResults, Obj, Elm, PointElm, LoadCase, StepType, StepNum,
         F11, F22, F12, FMax, FMin, FAngle, FVM,
         M11, M22, M12, MMax, MMin, MAngle,
         V13, V23, VMax, VAngle, ret] = \
            SapModel.Results.AreaForceShell(first_area, ObjectElm, NumberResults, Obj, Elm,
                                            PointElm, LoadCase, StepType, StepNum,
                                            F11, F22, F12, FMax, FMin, FAngle, FVM,
                                            M11, M22, M12, MMax, MMin, MAngle,
                                            V13, V23, VMax, VAngle)

        print(f"\n    NumberResults = {NumberResults}")
        print(f"    ret = {ret}")

        if NumberResults > 0:
            print(f"\n    [OK] {NumberResults} resultados!")

            max_m11 = max(abs(m) for m in M11) if M11 else 0
            max_m22 = max(abs(m) for m in M22) if M22 else 0
            max_v13 = max(abs(v) for v in V13) if V13 else 0
            max_v23 = max(abs(v) for v in V23) if V23 else 0

            print(f"\n    RESULTADOS:")
            print(f"      M11 máx = {max_m11:.6f} kN-m/m")
            print(f"      M22 máx = {max_m22:.6f} kN-m/m")
            print(f"      V13 máx = {max_v13:.6f} kN/m")
            print(f"      V23 máx = {max_v23:.6f} kN/m")

            print(f"\n    Primeros 5 puntos:")
            for i in range(min(5, NumberResults)):
                print(f"      {PointElm[i]}: M11={M11[i]:.4f}, M22={M22[i]:.4f}, V13={V13[i]:.4f}")

        else:
            print("    [ERROR] Sin resultados")

    # Close
    print("\n[9] Cerrando...")
    SapObject.ApplicationExit(False)
    print("    [OK] Cerrado")

    print("\n" + "="*70)
    if NumberResults > 0 and max_m11 > 0:
        print("EXITO - RESULTADOS DE SHELL OBTENIDOS")
    elif NumberResults > 0:
        print("RESULTADOS OBTENIDOS - PERO MOMENTOS EN CERO")
    else:
        print("SIN RESULTADOS")
    print("="*70)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

    try:
        if 'SapObject' in locals():
            SapObject.ApplicationExit(False)
    except:
        pass

print("\n[FIN]")
