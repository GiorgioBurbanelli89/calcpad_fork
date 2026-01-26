# -*- coding: utf-8 -*-
"""
COMPARACION - Rectangular Slab FEA
Modelo equivalente a Rectangular Slab FEA.cpd de Calcpad
"""
import comtypes.client

print("="*70)
print("COMPARACION: RECTANGULAR SLAB 6x4m - SAP2000 vs CALCPAD")
print("="*70)

# ========== PARAMETROS (IDENTICOS A CALCPAD) ==========
a = 6.0  # m
b = 4.0  # m
t = 0.1  # m
q = 10.0  # kN/m2
E = 35000  # MPa
nu = 0.15
n_a = 6  # elementos en direccion a
n_b = 4  # elementos en direccion b

print(f"\nPARAMETROS DEL MODELO:")
print(f"  Dimensiones: {a}m x {b}m")
print(f"  Espesor: {t}m")
print(f"  Carga: {q} kN/m2")
print(f"  E = {E} MPa")
print(f"  nu = {nu}")
print(f"  Malla: {n_a} x {n_b} elementos")

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

    # ========== MATERIAL ==========
    print("\n[3] Definiendo material...")
    MATERIAL_CONCRETE = 2
    SapModel.PropMaterial.SetMaterial('MAT', MATERIAL_CONCRETE)
    # E en kN/m2 = MPa * 1000
    SapModel.PropMaterial.SetMPIsotropic('MAT', E*1000, nu, 0.00001)
    print(f"    [OK] Material: E={E} MPa, nu={nu}")

    # ========== PROPIEDAD DE SHELL ==========
    print("\n[4] Definiendo propiedad Plate-Thin...")
    # Tipo 3 = Plate-Thin (Kirchhoff) - MISMO QUE .s2k
    ret = SapModel.PropArea.SetShell_1('LOSA', 3, False, 'MAT', 0, t, t, -1, "", "")
    print(f"    [OK] LOSA (Plate-Thin/Kirchhoff, t={t}m, ret={ret})")

    # ========== CREAR PUNTOS ==========
    print(f"\n[5] Creando malla de puntos ({n_a+1} x {n_b+1})...")
    dx = a / n_a
    dy = b / n_b

    point_names = []
    for i in range(n_a + 1):
        for j in range(n_b + 1):
            x = i * dx
            y = j * dy
            z = 0
            name = f"P{i}_{j}"
            SapModel.PointObj.AddCartesian(x, y, z, name)
            point_names.append((i, j, name))

    print(f"    [OK] {(n_a+1)*(n_b+1)} puntos creados")

    # ========== CREAR AREAS ==========
    print(f"\n[6] Creando areas ({n_a} x {n_b})...")
    area_count = 0
    for i in range(n_a):
        for j in range(n_b):
            # Coordenadas de los 4 puntos del area (sentido antihorario desde abajo-izq)
            x_coords = [i*dx, (i+1)*dx, (i+1)*dx, i*dx]
            y_coords = [j*dy, j*dy, (j+1)*dy, (j+1)*dy]
            z_coords = [0, 0, 0, 0]

            area_name = f"A{i}_{j}"
            ret = SapModel.AreaObj.AddByCoord(4, x_coords, y_coords, z_coords, area_name, "LOSA", area_name)
            area_count += 1

    SapModel.View.RefreshView(0, False)
    num_areas = SapModel.AreaObj.Count()
    print(f"    [OK] {num_areas} areas creadas")

    # ========== APOYOS (TODOS LOS BORDES) ==========
    print("\n[7] Aplicando apoyos en todos los bordes...")
    # Restricciones segun PDF:
    # - U3 siempre restringido en bordes
    # - R1 restringido en bordes x=0 y x=a (bordes verticales)
    # - R2 restringido en bordes y=0 y y=b (bordes horizontales)

    support_count = 0
    for i, j, name in point_names:
        is_x_border = (i == 0 or i == n_a)  # x=0 o x=a (bordes verticales)
        is_y_border = (j == 0 or j == n_b)  # y=0 o y=b (bordes horizontales)

        if is_x_border or is_y_border:
            # U1, U2, U3, R1, R2, R3
            Restraint = [
                False,           # U1
                False,           # U2
                True,            # U3 - siempre restringido en bordes
                is_x_border,     # R1 - restringido en bordes x=0 o x=a
                is_y_border,     # R2 - restringido en bordes y=0 o y=b
                False            # R3
            ]
            SapModel.PointObj.SetRestraint(name, Restraint)
            support_count += 1

    print(f"    [OK] {support_count} apoyos aplicados")

    # ========== CARGAS ==========
    print("\n[8] Aplicando carga uniforme...")
    LTYPE_OTHER = 8
    SapModel.LoadPatterns.Add('DEAD', LTYPE_OTHER, 1, True)

    # Aplicar carga a todas las areas
    for i in range(n_a):
        for j in range(n_b):
            area_name = f"A{i}_{j}"
            # Dir = Gravity, Value negativo para carga hacia abajo (como PDF)
            SapModel.AreaObj.SetLoadUniform(area_name, 'DEAD', -q, 3, False, "Global", 0)

    print(f"    [OK] Carga {q} kN/m2 aplicada a {num_areas} areas")

    # ========== GUARDAR ==========
    ModelPath = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\rectangular_slab_fea.sdb'
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
    SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")
    print("    [OK] Caso DEAD seleccionado")

    # ========== EXTRAER DESPLAZAMIENTOS ==========
    print("\n[12] Extrayendo desplazamientos...")

    # Desplazamiento en el centro (aprox)
    center_i = n_a // 2
    center_j = n_b // 2
    center_point = f"P{center_i}_{center_j}"

    # Inicializar variable
    w_center = 0.0

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
        SapModel.Results.JointDispl(center_point, 0, NumberResults, Obj, Elm,
                                     LoadCase, StepType, StepNum,
                                     U1, U2, U3, R1, R2, R3)

    if NumberResults > 0:
        w_center = abs(U3[0]) * 1000  # convertir a mm
        print(f"    Desplazamiento en centro ({center_point}): {w_center:.4f} mm")
    else:
        print(f"    [AVISO] No se obtuvieron desplazamientos para {center_point}")

    # ========== EXTRAER MOMENTOS ==========
    print("\n[13] Extrayendo momentos de un area central...")

    # Area central
    center_area = f"A{center_i-1}_{center_j-1}"

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
        SapModel.Results.AreaForceShell(center_area, ObjectElm, NumberResults, Obj, Elm,
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

        print(f"\n    Area analizada: {center_area}")
        print(f"\n    MOMENTOS:")
        print(f"      M11 max = {max_m11:.6f} kN-m/m")
        print(f"      M22 max = {max_m22:.6f} kN-m/m")
        print(f"      V13 max = {max_v13:.6f} kN/m")

        print(f"\n    Resultados por punto del area:")
        for i in range(NumberResults):
            print(f"      Punto {PointElm[i]}: M11={M11[i]:.4f}, M22={M22[i]:.4f}")

    # ========== EXTRAER MOMENTOS DE TODAS LAS AREAS ==========
    print("\n[14] Extrayendo momentos maximos globales...")

    all_M11 = []
    all_M22 = []
    all_M12 = []

    for i in range(n_a):
        for j in range(n_b):
            area_name = f"A{i}_{j}"

            [NumberResults, Obj, Elm, PointElm, LoadCase, StepType, StepNum,
             F11, F22, F12, FMax, FMin, FAngle, FVM,
             M11, M22, M12, MMax, MMin, MAngle,
             V13, V23, VMax, VAngle, ret] = \
                SapModel.Results.AreaForceShell(area_name, 0, 0, [], [],
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

    print("\n" + "="*70)
    print("RESULTADOS SAP2000 - LOSA RECTANGULAR 6x4m")
    print("="*70)
    if 'global_max_m11' in locals() and global_max_m11 is not None:
        print(f"Desplazamiento centro: {w_center:.4f} mm")
        print(f"M11 maximo global: {global_max_m11:.6f} kN-m/m")
        print(f"M22 maximo global: {global_max_m22:.6f} kN-m/m")
        print(f"M12 maximo global: {global_max_m12:.6f} kN-m/m")
    else:
        print("No se obtuvieron resultados de momentos globales")
    print("="*70)

    print("\nAhora ejecuta Calcpad para comparar:")
    print("  Archivo: Rectangular Slab FEA.cpd")
    print("  Busca los valores de:")
    print("    - w(a/2; b/2) (desplazamiento centro)")
    print("    - M_x(a/2; b/2) (momento Mx)")
    print("    - M_y(a/2; b/2) (momento My)")

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
