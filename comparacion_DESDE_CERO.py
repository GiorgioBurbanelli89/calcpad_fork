# -*- coding: utf-8 -*-
"""
Comparación Calcpad vs SAP2000 - DESDE CERO
Crea modelo, analiza, extrae resultados, cierra correctamente
Losa 6x4m, espesor 0.1m, carga 10 kN/m2
"""
import os
import sys
import comtypes.client

print("="*70)
print("COMPARACION CALCPAD vs SAP2000 - DESDE CERO")
print("="*70)

ModelPath = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Comparacion_NUEVO.sdb'

try:
    # Iniciar SAP2000
    print("\n[1] Iniciando SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
    mySapObject.ApplicationStart()
    SapModel = mySapObject.SapModel
    print("    [OK] Iniciado")

    # Inicializar modelo (kN, m, C)
    print("\n[2] Creando modelo...")
    SapModel.InitializeNewModel(6)
    SapModel.File.NewBlank()
    print("    [OK] Modelo en blanco")

    # Material: Concreto E=35000 MPa, nu=0.15
    print("\n[3] Definiendo material...")
    MATERIAL_CONCRETE = 2
    ret = SapModel.PropMaterial.SetMaterial('CONC', MATERIAL_CONCRETE)
    ret = SapModel.PropMaterial.SetMPIsotropic('CONC', 35000000, 0.15, 0.00001)
    print("    [OK] Material CONC (E=35000 MPa, nu=0.15)")

    # Propiedad de área: Shell (Mindlin plate)
    print("\n[4] Definiendo propiedad de shell...")
    # Shell tipo 5 = Plate-Thick (Mindlin)
    ret = SapModel.PropArea.SetShell_1('LOSA', 5, False, 'CONC', 0, 0.1, 0.1, 0, "", "")
    # Parámetros: Name, ShellType, MatProp, MatAng, Thickness, Thickness (membrana), BendThick, Color, Notes, GUID
    print("    [OK] LOSA (Mindlin, t=0.1m)")

    # Crear malla de puntos (6x4m, malla 6x5 = 35 puntos)
    print("\n[5] Creando malla de puntos...")
    nx = 7  # puntos en X (6 divisiones)
    ny = 6  # puntos en Y (5 divisiones)
    Lx = 6.0  # largo en X
    Ly = 4.0  # largo en Y

    for i in range(nx):
        for j in range(ny):
            x = i * Lx / (nx - 1)
            y = j * Ly / (ny - 1)
            point_name = f"P{i*ny + j + 1}"
            ret = SapModel.PointObj.AddCartesian(x, y, 0, point_name)

    num_points = SapModel.PointObj.Count()
    print(f"    [OK] {num_points} puntos creados")

    # Crear áreas (elementos de placa)
    print("\n[6] Creando elementos de área...")
    area_count = 0
    for i in range(nx - 1):
        for j in range(ny - 1):
            # 4 puntos de cada elemento (sentido antihorario desde abajo-izquierda)
            # Bottom-left, Top-left, Top-right, Bottom-right
            p1 = f"P{i*ny + j + 1}"           # (i, j)
            p2 = f"P{i*ny + (j+1) + 1}"       # (i, j+1)
            p3 = f"P{(i+1)*ny + (j+1) + 1}"   # (i+1, j+1)
            p4 = f"P{(i+1)*ny + j + 1}"       # (i+1, j)

            area_name = f"A{area_count + 1}"
            ret = SapModel.AreaObj.AddByPoint(4, [p1, p2, p3, p4], area_name, "LOSA", area_name)
            area_count += 1

    num_areas = SapModel.AreaObj.Count()
    print(f"    [OK] {num_areas} áreas creadas")

    # Apoyos simples en los bordes
    print("\n[7] Aplicando apoyos simples...")
    # Apoyo simple: solo U3 restringido
    Restraint = [False, False, True, False, False, False]

    apoyo_count = 0
    for i in range(nx):
        for j in range(ny):
            # Apoyos en los 4 bordes
            if i == 0 or i == nx-1 or j == 0 or j == ny-1:
                point_name = f"P{i*ny + j + 1}"
                ret = SapModel.PointObj.SetRestraint(point_name, Restraint)
                apoyo_count += 1

    print(f"    [OK] {apoyo_count} apoyos simples")

    # Patrón de carga
    print("\n[8] Creando patrón de carga...")
    LTYPE_OTHER = 8
    ret = SapModel.LoadPatterns.Add('DEAD', LTYPE_OTHER, 1, True)
    print("    [OK] Patrón DEAD")

    # Carga uniforme en todas las áreas: 10 kN/m2
    print("\n[9] Aplicando carga uniforme...")
    for i in range(1, area_count + 1):
        area_name = f"A{i}"
        # SetLoadUniform(Name, LoadPat, Value, Dir, Replace, CSys, ItemType)
        # Dir = 6 means Gravity (downward)
        ret = SapModel.AreaObj.SetLoadUniform(area_name, 'DEAD', 10, 6, True, "Global", 0)

    print("    [OK] Carga 10 kN/m2 en todas las áreas")

    # Guardar ANTES del análisis
    print(f"\n[10] Guardando modelo...")
    ret = SapModel.File.Save(ModelPath)
    print(f"    [OK] Guardado: {ModelPath}")

    # Ejecutar análisis
    print("\n[11] Ejecutando análisis...")
    ret = SapModel.Analyze.RunAnalysis()
    print(f"    [OK] Análisis completado (ret={ret})")

    # Guardar después del análisis
    ret = SapModel.File.Save(ModelPath)
    print(f"    [OK] Modelo con resultados guardado")

    # ========== EXTRAER RESULTADOS ==========
    print("\n" + "="*70)
    print("EXTRACCION DE RESULTADOS")
    print("="*70)

    # Configurar output
    print("\n[12] Configurando output...")
    ret = SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    ret = SapModel.Results.Setup.SetCaseSelectedForOutput('DEAD')
    print("    [OK] Caso DEAD seleccionado")

    # DESPLAZAMIENTOS
    print("\n[13] Extrayendo desplazamientos...")

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

    if NumberResults > 0:
        print(f"\n    [OK] {NumberResults} desplazamientos extraídos!")

        # Encontrar desplazamiento máximo
        max_u3 = max(abs(u) for u in U3)
        max_idx = [i for i, u in enumerate(U3) if abs(u) == max_u3][0]

        print(f"\n    DESPLAZAMIENTO VERTICAL MAXIMO:")
        print(f"      Punto: {Obj[max_idx]}")
        print(f"      U3 = {U3[max_idx]*1000:.6f} mm")

        # Primeros 10
        print(f"\n    Primeros 10 desplazamientos:")
        for i in range(min(10, NumberResults)):
            print(f"      {Obj[i]}: U3={U3[i]*1000:.4f} mm")

        sap_deflection = abs(U3[max_idx]) * 1000

    else:
        print("    [ERROR] Sin resultados de desplazamiento")
        sap_deflection = 0

    # MOMENTOS EN AREAS
    print("\n[14] Extrayendo momentos en áreas...")

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

    if NumberResults > 0:
        print(f"\n    [OK] {NumberResults} resultados de momentos")

        # Momentos máximos
        max_m11 = max(abs(m) for m in M11)
        max_m22 = max(abs(m) for m in M22)

        print(f"\n    MOMENTOS MAXIMOS:")
        print(f"      M11 (Mx) = {max_m11:.6f} kN-m/m")
        print(f"      M22 (My) = {max_m22:.6f} kN-m/m")

        # Primeros 5
        print(f"\n    Primeros 5 puntos:")
        for i in range(min(5, NumberResults)):
            print(f"      {Obj[i]}: M11={M11[i]:.4f}, M22={M22[i]:.4f} kN-m/m")

        sap_m11 = max_m11
        sap_m22 = max_m22

    else:
        print("    [ERROR] Sin resultados de momentos")
        sap_m11 = 0
        sap_m22 = 0

    # ========== COMPARACION ==========
    print("\n" + "="*70)
    print("RESULTADOS FINALES - COMPARACION")
    print("="*70)

    print("\nModelo: Losa 6x4m, t=0.1m, q=10 kN/m2")
    print("        E=35000 MPa, nu=0.15")
    print("        Apoyos simples en los 4 bordes")

    print("\n  SAP2000 (Mindlin-Reissner):")
    print(f"    Deflexión máxima: {sap_deflection:.6f} mm")
    print(f"    Momento M11 máx: {sap_m11:.6f} kN-m/m")
    print(f"    Momento M22 máx: {sap_m22:.6f} kN-m/m")

    print("\n  CALCPAD (Kirchhoff):")
    print("    Ver archivo: calcpad_results.html")

    print("\n  NOTA:")
    print("    - Calcpad: Kirchhoff (placa delgada, sin cortante)")
    print("    - SAP2000: Mindlin-Reissner (con deformación por cortante)")
    print("    - Para L/t = 60 (placa delgada): diferencia esperada < 5%")

    # Cerrar SAP2000 SIN GUARDAR
    print("\n" + "="*70)
    print("Cerrando SAP2000...")
    print("="*70)

    ret = mySapObject.ApplicationExit(False)
    print(f"    [OK] SAP2000 cerrado")

    SapModel = None
    mySapObject = None

    print("\n[OK] Comparación completada exitosamente!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

    # Cerrar de todos modos
    try:
        if 'mySapObject' in locals():
            mySapObject.ApplicationExit(False)
    except:
        pass

print("\n[FIN]")
