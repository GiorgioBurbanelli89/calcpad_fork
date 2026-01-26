# -*- coding: utf-8 -*-
"""
COMPARACIÓN COMPLETA FINAL: Calcpad vs SAP2000
Basado en documentación oficial CSI y sintaxis verificada

Soluciones aplicadas:
1. Crear áreas con RefreshView
2. Usar sintaxis oficial para extracción de resultados
3. AreaJointForceShell para fuerzas en shells
"""
import os
import comtypes.client

print("="*70)
print("COMPARACION COMPLETA: CALCPAD vs SAP2000")
print("="*70)

ModelPath = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\COMPARACION_FINAL.sdb'

try:
    # Iniciar SAP2000
    print("\n[1] Iniciando SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
    mySapObject.ApplicationStart()
    SapModel = mySapObject.SapModel
    print("    [OK] Iniciado")

    # Inicializar (kN, m, C)
    print("\n[2] Creando modelo...")
    SapModel.InitializeNewModel(6)
    SapModel.File.NewBlank()
    print("    [OK] Modelo en blanco")

    # Material: Concreto E=35000 MPa, nu=0.15
    print("\n[3] Definiendo material...")
    MATERIAL_CONCRETE = 2
    SapModel.PropMaterial.SetMaterial('CONC', MATERIAL_CONCRETE)
    SapModel.PropMaterial.SetMPIsotropic('CONC', 35000000, 0.15, 0.00001)
    print("    [OK] Material CONC (E=35000 MPa, nu=0.15)")

    # Propiedad de shell (Mindlin plate)
    print("\n[4] Definiendo propiedad de shell...")
    # ShellType 5 = Plate-Thick (Mindlin)
    SapModel.PropArea.SetShell_1('LOSA', 5, False, 'CONC', 0, 0.1, 0.1, 0, "", "")
    print("    [OK] LOSA (Mindlin, t=0.1m)")

    # Crear 4 puntos para una losa simple 2x2m
    print("\n[5] Creando puntos...")

    # MÉTODO CORRECTO según GitHub: Usar tuplas y obtener nombres
    areaPts = ()
    coords = [(0,0,0), (2,0,0), (2,2,0), (0,2,0)]

    for i, (x, y, z) in enumerate(coords):
        pt_name = f"P{i+1}"
        SapModel.PointObj.AddCartesian(x, y, z, pt_name)
        areaPts += (pt_name,)

    print(f"    [OK] {len(areaPts)} puntos creados")

    # Crear área - CLAVE: RefreshView después
    print("\n[6] Creando área...")
    nosPts = len(areaPts)
    newArea = "A1"

    # AddByPoint retorna (Name, ret)
    ret = SapModel.AreaObj.AddByPoint(nosPts, areaPts, newArea, "LOSA", newArea)
    print(f"    AddByPoint ret: {ret}")

    # CLAVE: RefreshView para que se cree el área
    ret_refresh = SapModel.View.RefreshView(0, False)
    print(f"    RefreshView ret: {ret_refresh}")

    num_areas = SapModel.AreaObj.Count()
    print(f"    [OK] {num_areas} áreas creadas")

    if num_areas == 0:
        print("\n    [ERROR] No se creó el área - intentando método alternativo...")

        # Método alternativo: AddByCoord
        x = [0, 2, 2, 0]
        y = [0, 0, 2, 2]
        z = [0, 0, 0, 0]

        ret2 = SapModel.AreaObj.AddByCoord(4, x, y, z, newArea, "LOSA", newArea)
        print(f"    AddByCoord ret: {ret2}")

        ret_refresh = SapModel.View.RefreshView(0, False)
        num_areas = SapModel.AreaObj.Count()
        print(f"    Áreas creadas: {num_areas}")

    # Apoyos simples en las esquinas
    print("\n[7] Aplicando apoyos...")
    # Solo U3 restringido (apoyo simple)
    Restraint = [False, False, True, False, False, False]

    for pt_name in areaPts:
        SapModel.PointObj.SetRestraint(pt_name, Restraint)

    print(f"    [OK] {len(areaPts)} apoyos simples")

    # Patrón de carga
    print("\n[8] Creando patrón de carga...")
    LTYPE_OTHER = 8
    SapModel.LoadPatterns.Add('DEAD', LTYPE_OTHER, 1, True)
    print("    [OK] Patrón DEAD")

    # Carga uniforme: 10 kN/m2
    print("\n[9] Aplicando carga...")
    # Dir = 6 means Gravity (downward)
    ret = SapModel.AreaObj.SetLoadUniform(newArea, 'DEAD', 10, 6, True, "Global", 0)
    print(f"    SetLoadUniform ret: {ret}")
    print("    [OK] Carga 10 kN/m2")

    # Guardar
    print(f"\n[10] Guardando modelo...")
    SapModel.File.Save(ModelPath)
    print(f"    [OK] Guardado: {ModelPath}")

    # Analizar
    print("\n[11] Ejecutando análisis...")
    ret = SapModel.Analyze.RunAnalysis()
    print(f"    [OK] Análisis completado (ret={ret})")

    # Guardar después del análisis
    SapModel.File.Save(ModelPath)
    print("    [OK] Modelo con resultados guardado")

    # ========== EXTRAER RESULTADOS ==========
    print("\n" + "="*70)
    print("EXTRACCION DE RESULTADOS")
    print("="*70)

    # Configurar output
    print("\n[12] Configurando output...")
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    SapModel.Results.Setup.SetCaseSelectedForOutput('DEAD')
    print("    [OK] Caso DEAD seleccionado")

    # DESPLAZAMIENTOS - Punto por punto
    print("\n[13] Extrayendo desplazamientos...")

    for pt_name in areaPts:
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
            SapModel.Results.JointDispl(pt_name, ObjectElm, NumberResults, Obj, Elm, ACase,
                                         StepType, StepNum, U1, U2, U3, R1, R2, R3)

        if NumberResults > 0:
            print(f"    {pt_name}: U3 = {U3[0]*1000:.4f} mm")

    # FUERZAS EN SHELL - Usar AreaJointForceShell
    print("\n[14] Extrayendo fuerzas en shell...")

    if num_areas > 0:
        NumberResults = 0
        Obj = []
        Elm = []
        PointElm = []
        LoadCase = []
        StepType = []
        StepNum = []
        F1 = []
        F2 = []
        F3 = []
        M1 = []
        M2 = []
        M3 = []
        ObjectElm = 0

        # Sintaxis oficial para AreaJointForceShell
        [NumberResults, Obj, Elm, PointElm, LoadCase, StepType, StepNum,
         F1, F2, F3, M1, M2, M3, ret] = \
            SapModel.Results.AreaJointForceShell(newArea, ObjectElm, NumberResults, Obj, Elm,
                                                  PointElm, LoadCase, StepType, StepNum,
                                                  F1, F2, F3, M1, M2, M3)

        print(f"    NumberResults = {NumberResults}")

        if NumberResults > 0:
            print(f"\n    [OK] {NumberResults} fuerzas en esquinas del shell")

            # Mostrar momentos (M1, M2)
            max_m1 = max(abs(m) for m in M1) if M1 else 0
            max_m2 = max(abs(m) for m in M2) if M2 else 0

            print(f"\n    MOMENTOS EN ESQUINAS:")
            print(f"      M1 máx = {max_m1:.6f} kN-m")
            print(f"      M2 máx = {max_m2:.6f} kN-m")

            # Primeros 5
            print(f"\n    Primeros resultados:")
            for i in range(min(5, NumberResults)):
                print(f"      {PointElm[i]}: M1={M1[i]:.4f}, M2={M2[i]:.4f} kN-m")

        else:
            print("    [WARN] Sin resultados de fuerzas en shell")

    # ========== COMPARACIÓN ==========
    print("\n" + "="*70)
    print("COMPARACION CON CALCPAD")
    print("="*70)

    print("\nModelo: Losa 2x2m, t=0.1m, q=10 kN/m2")
    print("        E=35000 MPa, nu=0.15")
    print("        Apoyos simples en 4 esquinas")

    print("\n  SAP2000 (Mindlin-Reissner):")
    print("    Ver resultados arriba")

    print("\n  CALCPAD (Kirchhoff):")
    print("    Ver archivo: calcpad_results.html")

    print("\n  NOTA:")
    print("    - Diferencia esperada < 5% para placa delgada")
    print("    - L/t = 20 (placa delgada)")

    # Cerrar SAP2000
    print("\n" + "="*70)
    print("Cerrando SAP2000...")
    print("="*70)

    mySapObject.ApplicationExit(False)
    print(f"    [OK] Cerrado")

    SapModel = None
    mySapObject = None

    print("\n[OK] COMPARACIÓN COMPLETADA!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

    try:
        if 'mySapObject' in locals():
            mySapObject.ApplicationExit(False)
    except:
        pass

print("\n[FIN]")
