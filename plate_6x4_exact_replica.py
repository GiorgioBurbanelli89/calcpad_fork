# -*- coding: utf-8 -*-
"""
REPLICA EXACTA del archivo Plate-6x4.s2k
Basado 100% en la estructura del archivo .s2k original
"""
import comtypes.client

print("="*70)
print("REPLICA EXACTA - Plate-6x4.s2k")
print("="*70)

try:
    # ========== INICIAR SAP2000 ==========
    print("\n[1] Iniciando SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    SapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
    SapObject.ApplicationStart()
    SapModel = SapObject.SapModel
    print("    [OK] Iniciado")

    # ========== CREAR MODELO ==========
    print("\n[2] Creando modelo...")
    SapModel.InitializeNewModel(6)  # kN, m, C
    SapModel.File.NewBlank()
    print("    [OK] Modelo en blanco")

    # ========== MATERIAL (segun .s2k linea 74) ==========
    print("\n[3] Definiendo material CONC...")
    MATERIAL_CONCRETE = 2
    SapModel.PropMaterial.SetMaterial('CONC', MATERIAL_CONCRETE)
    # E=3.5E+07 kN/m2 (ya en unidades correctas)
    SapModel.PropMaterial.SetMPIsotropic('CONC', 3.5E+07, 0.15, 0.0000099)
    print(f"    [OK] Material CONC: E=35000 MPa, nu=0.15")

    # ========== SHELL SECTION (segun .s2k linea 79) ==========
    print("\n[4] Definiendo SSEC1 (Plate,Thin)...")
    # TYPE=Plate,Thin → ShellType=3
    ret = SapModel.PropArea.SetShell_1('SSEC1', 3, False, 'CONC', 0, 0.1, 0.1, -1, "", "")
    print(f"    [OK] SSEC1 (Plate-Thin, t=0.1m, ret={ret})")

    # ========== CREAR JOINTS (segun .s2k lineas 8-43) ==========
    print("\n[5] Creando 35 joints...")
    joints_coords = [
        (1, -3, -2, 0), (2, -3, -1, 0), (3, -3, 0, 0), (4, -3, 1, 0), (5, -3, 2, 0),
        (6, -2, -2, 0), (7, -2, -1, 0), (8, -2, 0, 0), (9, -2, 1, 0), (10, -2, 2, 0),
        (11, -1, -2, 0), (12, -1, -1, 0), (13, -1, 0, 0), (14, -1, 1, 0), (15, -1, 2, 0),
        (16, 0, -2, 0), (17, 0, -1, 0), (18, 0, 0, 0), (19, 0, 1, 0), (20, 0, 2, 0),
        (21, 1, -2, 0), (22, 1, -1, 0), (23, 1, 0, 0), (24, 1, 1, 0), (25, 1, 2, 0),
        (26, 2, -2, 0), (27, 2, -1, 0), (28, 2, 0, 0), (29, 2, 1, 0), (30, 2, 2, 0),
        (31, 3, -2, 0), (32, 3, -1, 0), (33, 3, 0, 0), (34, 3, 1, 0), (35, 3, 2, 0)
    ]

    for jid, x, y, z in joints_coords:
        SapModel.PointObj.AddCartesian(x, y, z, str(jid))

    print(f"    [OK] 35 joints creados")

    # ========== RESTRAINTS (segun .s2k lineas 45-65) ==========
    print("\n[6] Aplicando restricciones...")
    # Esquinas: U3, R1, R2
    for j in [1, 5, 31, 35]:
        SapModel.PointObj.SetRestraint(str(j), [False, False, True, True, True, False])

    # Bordes horizontales (Y=-2 y Y=2): U3, R2
    for j in [6, 10, 11, 15, 16, 20, 21, 25, 26, 30]:
        SapModel.PointObj.SetRestraint(str(j), [False, False, True, False, True, False])

    # Bordes verticales (X=-3 y X=3): U3, R1
    for j in [2, 3, 4, 32, 33, 34]:
        SapModel.PointObj.SetRestraint(str(j), [False, False, True, True, False, False])

    print(f"    [OK] Restricciones aplicadas")

    # ========== CREAR SHELLS POR COORDENADAS (orden anti-horario) ==========
    print("\n[7] Creando 24 shells...")
    # Orden anti-horario: abajo-izq, abajo-der, arriba-der, arriba-izq
    shell_coords = [
        # Shell 1: abajo-izq, abajo-der, arriba-der, arriba-izq
        (1, [(-3,-2), (-2,-2), (-2,-1), (-3,-1)]),
        (2, [(-3,-1), (-2,-1), (-2,0), (-3,0)]),
        (3, [(-3,0), (-2,0), (-2,1), (-3,1)]),
        (4, [(-3,1), (-2,1), (-2,2), (-3,2)]),
        (5, [(-2,-2), (-1,-2), (-1,-1), (-2,-1)]),
        (6, [(-2,-1), (-1,-1), (-1,0), (-2,0)]),
        (7, [(-2,0), (-1,0), (-1,1), (-2,1)]),
        (8, [(-2,1), (-1,1), (-1,2), (-2,2)]),
        (9, [(-1,-2), (0,-2), (0,-1), (-1,-1)]),
        (10, [(-1,-1), (0,-1), (0,0), (-1,0)]),
        (11, [(-1,0), (0,0), (0,1), (-1,1)]),
        (12, [(-1,1), (0,1), (0,2), (-1,2)]),
        (13, [(0,-2), (1,-2), (1,-1), (0,-1)]),
        (14, [(0,-1), (1,-1), (1,0), (0,0)]),
        (15, [(0,0), (1,0), (1,1), (0,1)]),
        (16, [(0,1), (1,1), (1,2), (0,2)]),
        (17, [(1,-2), (2,-2), (2,-1), (1,-1)]),
        (18, [(1,-1), (2,-1), (2,0), (1,0)]),
        (19, [(1,0), (2,0), (2,1), (1,1)]),
        (20, [(1,1), (2,1), (2,2), (1,2)]),
        (21, [(2,-2), (3,-2), (3,-1), (2,-1)]),
        (22, [(2,-1), (3,-1), (3,0), (2,0)]),
        (23, [(2,0), (3,0), (3,1), (2,1)]),
        (24, [(2,1), (3,1), (3,2), (2,2)])
    ]

    for sid, coords in shell_coords:
        x_coords = [c[0] for c in coords]
        y_coords = [c[1] for c in coords]
        z_coords = [0, 0, 0, 0]
        ret = SapModel.AreaObj.AddByCoord(4, x_coords, y_coords, z_coords, str(sid), "SSEC1", str(sid))
        if ret != 0:
            print(f"    [AVISO] Shell {sid}: ret={ret}")

    SapModel.View.RefreshView(0, False)
    num_areas = SapModel.AreaObj.Count()
    print(f"    [OK] {num_areas} shells creados")

    # ========== CARGAS (segun .s2k) ==========
    print("\n[8] Aplicando cargas uniformes...")
    LTYPE_DEAD = 1
    SapModel.LoadPatterns.Add('LOAD1', LTYPE_DEAD, 1, True)

    # Aplicar carga UZ=-10 a todos los shells
    for sid in range(1, 25):
        # Dir = 6 (Gravity), Value = 10 (positivo porque Gravity ya incluye el signo)
        SapModel.AreaObj.SetLoadUniform(str(sid), 'LOAD1', 10, 6, True, "Global", 0)

    print(f"    [OK] Cargas aplicadas a 24 shells")

    # ========== GUARDAR ==========
    ModelPath = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\plate_6x4_replica.sdb'
    print(f"\n[9] Guardando...")
    SapModel.File.Save(ModelPath)
    print(f"    [OK] Guardado: {ModelPath}")

    # ========== ANALIZAR ==========
    print("\n[10] Ejecutando analisis...")
    ret = SapModel.Analyze.RunAnalysis()
    print(f"    [OK] Analisis (ret={ret})")

    # ========== CONFIGURAR SALIDA ==========
    print("\n[11] Configurando output...")
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    SapModel.Results.Setup.SetCaseSelectedForOutput("LOAD1")
    print("    [OK] Caso LOAD1 seleccionado")

    # ========== EXTRAER DESPLAZAMIENTOS DEL CENTRO (Joint 18) ==========
    print("\n[12] Extrayendo desplazamientos del centro (Joint 18)...")

    NumberResults = 0
    Obj = []
    Elm = []
    LoadCase = []
    StepType = []
    StepNum = []
    U1 = []
    U2 = []
    U3 = []
    R1 = []
    R2 = []
    R3 = []

    [NumberResults, Obj, Elm, LoadCase, StepType, StepNum,
     U1, U2, U3, R1, R2, R3, ret] = \
        SapModel.Results.JointDispl("18", 0, NumberResults, Obj, Elm,
                                     LoadCase, StepType, StepNum,
                                     U1, U2, U3, R1, R2, R3)

    w_center = 0.0
    if NumberResults > 0:
        w_center = abs(U3[0]) * 1000  # convertir a mm
        print(f"    Desplazamiento centro (Joint 18): {w_center:.3f} mm")
        print(f"    R1 = {R1[0]:.6f} rad")
        print(f"    R2 = {R2[0]:.6f} rad")
    else:
        print(f"    [AVISO] No se obtuvieron desplazamientos")

    # ========== EXTRAER MOMENTOS DE SHELL 14 (centro) ==========
    print("\n[13] Extrayendo momentos de Shell 14 (centro)...")

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
        SapModel.Results.AreaForceShell("14", 0, 0, [], [],
                                        [], [], [], [],
                                        [], [], [], [], [], [], [],
                                        [], [], [], [], [], [],
                                        [], [], [], [])

    print(f"\n    NumberResults = {NumberResults}")
    if NumberResults > 0:
        for i in range(NumberResults):
            print(f"    Punto {i+1}: M11={M11[i]:.4f}, M22={M22[i]:.4f}, M12={M12[i]:.4f}")

    # ========== EXTRAER MOMENTOS GLOBALES ==========
    print("\n[14] Extrayendo momentos maximos globales...")

    all_M11 = []
    all_M22 = []
    all_M12 = []

    for sid in range(1, 25):
        [NumberResults, Obj, Elm, PointElm, LoadCase, StepType, StepNum,
         F11, F22, F12, FMax, FMin, FAngle, FVM,
         M11, M22, M12, MMax, MMin, MAngle,
         V13, V23, VMax, VAngle, ret] = \
            SapModel.Results.AreaForceShell(str(sid), 0, 0, [], [],
                                            [], [], [], [],
                                            [], [], [], [], [], [], [],
                                            [], [], [], [], [], [],
                                            [], [], [], [])

        if NumberResults > 0:
            all_M11.extend(M11)
            all_M22.extend(M22)
            all_M12.extend(M12)

    if all_M11:
        global_max_m11 = max(abs(m) for m in all_M11)
        global_max_m22 = max(abs(m) for m in all_M22)
        global_max_m12 = max(abs(m) for m in all_M12)

        print(f"\n    MOMENTOS MAXIMOS GLOBALES:")
        print(f"      M11 max = {global_max_m11:.6f} kN-m/m")
        print(f"      M22 max = {global_max_m22:.6f} kN-m/m")
        print(f"      M12 max = {global_max_m12:.6f} kN-m/m")

    # ========== CERRAR ==========
    print("\n[15] Cerrando...")
    SapObject.ApplicationExit(False)
    print("    [OK] Cerrado")

    # ========== COMPARACION CON PDF ==========
    print("\n" + "="*70)
    print("COMPARACION CON PDF")
    print("="*70)
    print("PDF (SAP2000 antiguo):  w=6.529mm  Mx=6.22  My=12.76  Mxy=7.25")
    if 'global_max_m11' in locals():
        print(f"Este script:            w={w_center:.3f}mm  M11={global_max_m11:.2f}  M22={global_max_m22:.2f}  M12={global_max_m12:.2f}")
    else:
        print(f"Este script:            w={w_center:.3f}mm  [No se obtuvieron momentos]")
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
