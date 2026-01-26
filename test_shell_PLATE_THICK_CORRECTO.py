# -*- coding: utf-8 -*-
"""
Test Shell - CORREGIDO CON TIPO CORRECTO
ShellType 4 = Plate-Thick (CON MOMENTOS DE FLEXION)
ShellType 5 = Membrane (SIN MOMENTOS - SOLO MEMBRANA)
"""
import comtypes.client

print("="*70)
print("TEST SHELL - PLATE-THICK (TIPO 4 - CON FLEXION)")
print("="*70)

try:
    print("\n[1] Iniciando SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    SapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
    SapObject.ApplicationStart()
    SapModel = SapObject.SapModel
    print("    [OK] Iniciado")

    print("\n[2] Creando modelo...")
    SapModel.InitializeNewModel(6)  # kN, m, C
    SapModel.File.NewBlank()
    print("    [OK] Modelo en blanco")

    print("\n[3] Definiendo material...")
    MATERIAL_CONCRETE = 2
    SapModel.PropMaterial.SetMaterial('CONC', MATERIAL_CONCRETE)
    SapModel.PropMaterial.SetMPIsotropic('CONC', 25000000, 0.2, 0.00001)
    print("    [OK] Material CONC (E=25 GPa)")

    print("\n[4] Definiendo propiedad PLATE-THICK...")
    # SetShell_1(Name, ShellType, IncludeDrillingDOF, MatProp, MatAng, Thickness, Bending, Color, Notes, GUID)
    # ShellType 4 = Plate-Thick (INCLUYE MOMENTOS DE FLEXION)
    ret = SapModel.PropArea.SetShell_1('PLACA', 4, False, 'CONC', 0, 0.2, 0.2, -1, "", "")
    print(f"    [OK] PLACA (Plate-Thick tipo 4, t=0.2m, ret={ret})")

    print("\n[5] Creando 4 puntos...")
    x_coords = [0, 2, 2, 0]
    y_coords = [0, 0, 2, 2]
    z_coords = [0, 0, 0, 0]

    for i in range(4):
        ret = SapModel.PointObj.AddCartesian(x_coords[i], y_coords[i], z_coords[i], f"P{i+1}")

    print("    [OK] 4 puntos creados")

    print("\n[6] Creando area...")
    ret_area = SapModel.AreaObj.AddByCoord(4, x_coords, y_coords, z_coords, "A1", "PLACA", "A1")
    SapModel.View.RefreshView(0, False)
    num_areas = SapModel.AreaObj.Count()
    print(f"    [OK] {num_areas} area creada")

    print("\n[7] Aplicando apoyos simples...")
    # Solo U3 restringido (apoyo simple vertical)
    Restraint = [False, False, True, False, False, False]

    for i in range(1, 5):
        SapModel.PointObj.SetRestraint(f"P{i}", Restraint)

    print("    [OK] 4 apoyos simples (U3 fijo)")

    print("\n[8] Creando patron de carga...")
    LTYPE_OTHER = 8
    SapModel.LoadPatterns.Add('DEAD', LTYPE_OTHER, 1, True)
    print("    [OK] Patron DEAD")

    print("\n[9] Aplicando carga uniforme...")
    # Dir = 6 means Gravity (hacia abajo)
    ret = SapModel.AreaObj.SetLoadUniform("A1", 'DEAD', 10, 6, True, "Global", 0)
    print(f"    [OK] Carga 10 kN/m2 (ret={ret})")

    # Save
    ModelPath = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\TEST_PLATE_THICK.sdb'
    print(f"\n[10] Guardando...")
    SapModel.File.Save(ModelPath)
    print(f"    [OK] Guardado: {ModelPath}")

    # Analyze
    print("\n[11] Ejecutando analisis...")
    ret = SapModel.Analyze.RunAnalysis()
    print(f"    [OK] Analisis (ret={ret})")

    # Configure output
    print("\n[12] Configurando output...")
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")
    print("    [OK] Caso DEAD seleccionado")

    # Extract results
    print("\n[13] Extrayendo resultados...")

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
        SapModel.Results.AreaForceShell("A1", ObjectElm, NumberResults, Obj, Elm,
                                        PointElm, LoadCase, StepType, StepNum,
                                        F11, F22, F12, FMax, FMin, FAngle, FVM,
                                        M11, M22, M12, MMax, MMin, MAngle,
                                        V13, V23, VMax, VAngle)

    print(f"\n    NumberResults = {NumberResults}")
    print(f"    ret = {ret}")

    if NumberResults > 0:
        max_m11 = max(abs(m) for m in M11)
        max_m22 = max(abs(m) for m in M22)
        max_v13 = max(abs(v) for v in V13)

        print(f"\n    [OK] {NumberResults} resultados!")
        print(f"\n    MOMENTOS DE PLACA:")
        print(f"      M11 max = {max_m11:.6f} kN-m/m")
        print(f"      M22 max = {max_m22:.6f} kN-m/m")
        print(f"      V13 max = {max_v13:.6f} kN/m")

        print(f"\n    Primeros resultados:")
        for i in range(min(NumberResults, 4)):
            print(f"      {PointElm[i]}: M11={M11[i]:.4f}, M22={M22[i]:.4f}, V13={V13[i]:.4f}")

        # TEORIA: Losa cuadrada 2x2m, simplemente apoyada, q=10 kN/m2
        print(f"\n    COMPARACION TEORICA:")
        print(f"      Losa: 2x2m, t=0.2m, q=10 kN/m2")
        print(f"      Momento central aprox ~ q*L^2/8 = 10*4/8 = 5 kN-m/m")

        if max_m11 > 0 or max_m22 > 0:
            print(f"\n    [EXITO] MOMENTOS OBTENIDOS")
        else:
            print(f"\n    [WARNING] Momentos en cero")

    else:
        print("    [ERROR] Sin resultados")

    # Close
    print("\n[14] Cerrando...")
    SapObject.ApplicationExit(False)
    print("    [OK] Cerrado")

    print("\n" + "="*70)
    if NumberResults > 0 and (max_m11 > 0 or max_m22 > 0):
        print("EXITO TOTAL - RESULTADOS DE PLACA CON MOMENTOS")
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
