# -*- coding: utf-8 -*-
"""
Test Shell - DESDE CERO con propiedades SHELL correctas
Crear shell con capacidad de flexión de placa (Mindlin)
"""
import comtypes.client

print("="*70)
print("TEST SHELL - DESDE CERO CON FLEXION")
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
    print("    [OK] Material CONC")

    print("\n[4] Definiendo propiedad de SHELL...")
    # SetShell_1(Name, ShellType, MatProp, MatAng, Thickness, Thickness, BendThick, Color, Notes, GUID)
    # ShellType 5 = Shell-Thick (Mindlin) - PERMITE FLEXIÓN DE PLACA
    ret = SapModel.PropArea.SetShell_1('SHELL1', 5, False, 'CONC', 0, 0.2, 0.2, 0, "", "")
    print(f"    [OK] SHELL1 creada (Mindlin, t=0.2m, ret={ret})")

    print("\n[5] Creando 4 puntos...")
    x_coords = [0, 2, 2, 0]
    y_coords = [0, 0, 2, 2]
    z_coords = [0, 0, 0, 0]

    for i in range(4):
        ret = SapModel.PointObj.AddCartesian(x_coords[i], y_coords[i], z_coords[i], f"P{i+1}")

    print("    [OK] 4 puntos creados")

    print("\n[6] Creando área...")
    # MÉTODO CORRECTO: AddByCoord
    ret_area = SapModel.AreaObj.AddByCoord(4, x_coords, y_coords, z_coords, "A1", "SHELL1", "A1")
    print(f"    AddByCoord ret: {ret_area}")

    # RefreshView
    SapModel.View.RefreshView(0, False)

    num_areas = SapModel.AreaObj.Count()
    print(f"    [OK] {num_areas} áreas creadas")

    print("\n[7] Aplicando apoyos simples...")
    # Solo U3 restringido en las 4 esquinas
    Restraint = [False, False, True, False, False, False]

    for i in range(1, 5):
        SapModel.PointObj.SetRestraint(f"P{i}", Restraint)

    print("    [OK] 4 apoyos simples")

    print("\n[8] Creando patrón de carga...")
    LTYPE_OTHER = 8
    SapModel.LoadPatterns.Add('DEAD', LTYPE_OTHER, 1, True)
    print("    [OK] Patrón DEAD")

    print("\n[9] Aplicando carga uniforme...")
    # Dir = 6 means Gravity (hacia abajo)
    ret = SapModel.AreaObj.SetLoadUniform("A1", 'DEAD', 10, 6, True, "Global", 0)
    print(f"    [OK] Carga 10 kN/m2 (ret={ret})")

    # Save
    ModelPath = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\TEST_SHELL_MINDLIN.sdb'
    print(f"\n[10] Guardando...")
    SapModel.File.Save(ModelPath)
    print(f"    [OK] Guardado")

    # Analyze
    print("\n[11] Ejecutando análisis...")
    ret = SapModel.Analyze.RunAnalysis()
    print(f"    [OK] Análisis (ret={ret})")

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
        print(f"      M11 máx = {max_m11:.6f} kN-m/m")
        print(f"      M22 máx = {max_m22:.6f} kN-m/m")
        print(f"      V13 máx = {max_v13:.6f} kN/m")

        print(f"\n    Primeros resultados:")
        for i in range(min(NumberResults, 4)):
            print(f"      {PointElm[i]}: M11={M11[i]:.4f}, M22={M22[i]:.4f}")

        # TEORÍA: Losa cuadrada 2x2m, simplemente apoyada, q=10 kN/m2
        print(f"\n    COMPARACIÓN TEÓRICA:")
        print(f"      Losa: 2x2m, t=0.2m, q=10 kN/m2")
        print(f"      Momento central aproximado ~ q*L^2/8 = 10*4/8 = 5 kN-m/m")

        if max_m11 > 0 or max_m22 > 0:
            print(f"\n    ✅ ÉXITO - MOMENTOS OBTENIDOS")
        else:
            print(f"\n    ⚠️ Momentos en cero - verificar propiedades")

    else:
        print("    [ERROR] Sin resultados")

    # Close
    print("\n[14] Cerrando...")
    SapObject.ApplicationExit(False)
    print("    [OK] Cerrado")

    print("\n" + "="*70)
    if NumberResults > 0 and (max_m11 > 0 or max_m22 > 0):
        print("✅ ÉXITO TOTAL - RESULTADOS DE SHELL CON MOMENTOS")
    elif NumberResults > 0:
        print("⚠️ RESULTADOS OBTENIDOS - PERO MOMENTOS EN CERO")
    else:
        print("❌ SIN RESULTADOS")
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
