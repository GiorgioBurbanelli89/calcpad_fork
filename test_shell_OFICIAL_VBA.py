# -*- coding: utf-8 -*-
"""
Test Shell Results - SINTAXIS OFICIAL BASADA EN EJEMPLO VBA
Documento fuente: AreaForceShell.htm línea 147
"""
import comtypes.client

print("="*70)
print("TEST SHELL - SINTAXIS OFICIAL CSI VBA")
print("="*70)

try:
    # Crear SAP2000
    print("\n[1] Iniciando SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    SapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
    SapObject.ApplicationStart()
    SapModel = SapObject.SapModel
    print("    [OK] Iniciado")

    # Initialize model
    print("\n[2] Inicializando modelo...")
    ret = SapModel.InitializeNewModel()
    print(f"    [OK] ret={ret}")

    # Create model from template - USA EL MISMO QUE EL EJEMPLO
    # NewWall(NumberXDivisions, XSpacing, NumberZDivisions, ZSpacing)
    print("\n[3] Creando modelo desde template NewWall...")
    ret = SapModel.File.NewWall(6, 48, 6, 48)
    print(f"    [OK] NewWall creado (ret={ret})")

    # Save
    ModelPath = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\TEST_WALL_VBA.sdb'
    print(f"\n[4] Guardando...")
    ret = SapModel.File.Save(ModelPath)
    print(f"    [OK] Guardado (ret={ret})")

    # Run analysis
    print("\n[5] Ejecutando análisis...")
    ret = SapModel.Analyze.RunAnalysis()
    print(f"    [OK] Análisis (ret={ret})")

    # Clear all case and combo output selections
    print("\n[6] Configurando output...")
    ret = SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    ret = SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")
    print("    [OK] Caso DEAD seleccionado")

    # Get area forces for area object "1" - SINTAXIS EXACTA DEL EJEMPLO VBA
    print("\n[7] Extrayendo fuerzas de área...")

    # Initialize variables - EXACTAMENTE como en el ejemplo VBA
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

    # ItemTypeElm: ObjectElm = 0
    ObjectElm = 0

    # SINTAXIS OFICIAL - línea 147 del VBA example
    [NumberResults, Obj, Elm, PointElm, LoadCase, StepType, StepNum,
     F11, F22, F12, FMax, FMin, FAngle, FVM,
     M11, M22, M12, MMax, MMin, MAngle,
     V13, V23, VMax, VAngle, ret] = \
        SapModel.Results.AreaForceShell("1", ObjectElm, NumberResults, Obj, Elm,
                                        PointElm, LoadCase, StepType, StepNum,
                                        F11, F22, F12, FMax, FMin, FAngle, FVM,
                                        M11, M22, M12, MMax, MMin, MAngle,
                                        V13, V23, VMax, VAngle)

    print(f"\n    NumberResults = {NumberResults}")
    print(f"    ret = {ret}")

    if NumberResults > 0:
        print(f"\n    [OK] {NumberResults} resultados obtenidos!")

        # Mostrar momentos máximos
        max_m11 = max(abs(m) for m in M11) if M11 else 0
        max_m22 = max(abs(m) for m in M22) if M22 else 0

        print(f"\n    MOMENTOS PLACA:")
        print(f"      M11 máx = {max_m11:.6f} kN-m/m")
        print(f"      M22 máx = {max_m22:.6f} kN-m/m")

        # Primeros 10
        print(f"\n    Primeros 10 resultados:")
        for i in range(min(10, NumberResults)):
            print(f"      {PointElm[i]}: M11={M11[i]:.4f}, M22={M22[i]:.4f}")

    else:
        print(f"    [ERROR] Sin resultados (NumberResults={NumberResults})")

    # Close SAP2000
    print("\n[8] Cerrando...")
    SapObject.ApplicationExit(False)
    print("    [OK] Cerrado")

    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    print(f"Modelo: {ModelPath}")
    print(f"Resultados: {NumberResults}")
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
