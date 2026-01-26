# -*- coding: utf-8 -*-
"""
SAP2000 API - Extraer resultados del modelo YA ABIERTO
"""
import comtypes.client

print("="*70)
print("EXTRAER RESULTADOS DEL MODELO ABIERTO")
print("="*70)

try:
    # Conectar a SAP2000 que YA ESTA ABIERTO
    print("\n[1] Conectando a SAP2000 activo...")
    myHelper = comtypes.client.GetActiveObject("SAP2000v1.Helper")
    myHelper = myHelper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    mySapObject = myHelper.GetObject("CSI.SAP2000.API.SapObject")
    model = mySapObject.SapModel
    print("    [OK] Conectado")

    # Información del modelo
    print("\n[2] Información del modelo:")
    version = model.GetVersion()
    filename = model.GetModelFilename()
    num_points = model.PointObj.Count()
    num_areas = model.AreaObj.Count()

    print(f"    Version: {version[0]}")
    print(f"    Archivo: {filename}")
    print(f"    Puntos: {num_points}")
    print(f"    Areas: {num_areas}")

    # Desbloquear
    print("\n[3] Desbloqueando modelo...")
    model.SetModelIsLocked(False)
    print("    [OK] Desbloqueado")

    # ¿El modelo ya está analizado?
    print("\n[4] Verificando estado del análisis...")

    # Listar casos de carga disponibles
    print("\n[5] Casos de carga en el modelo:")
    # Obtener nombres de casos
    ret_cases = model.LoadCases.GetNameList()
    if ret_cases[0] > 0:
        case_names = ret_cases[1]
        print(f"    Total casos: {ret_cases[0]}")
        for i, case_name in enumerate(case_names):
            print(f"      {i+1}. {case_name}")
    else:
        print("    No hay casos de carga")

    # Si no está analizado, analizar
    print("\n[6] Ejecutando análisis...")
    ret1 = model.Analyze.CreateAnalysisModel()
    ret2 = model.Analyze.RunAnalysis()
    print(f"    CreateAnalysisModel: ret={ret1}")
    print(f"    RunAnalysis: ret={ret2}")

    # Guardar después del análisis
    print("\n[7] Guardando modelo...")
    ret_save = model.File.Save(filename)
    print(f"    Save: ret={ret_save}")

    # EXTRACCIÓN DE RESULTADOS
    print("\n" + "="*70)
    print("EXTRACCIÓN DE RESULTADOS")
    print("="*70)

    # Seleccionar caso DEAD
    print("\n[8] Seleccionando caso DEAD...")
    model.Results.Setup.DeselectAllCasesAndCombosForOutput()
    ret_select = model.Results.Setup.SetCaseSelectedForOutput("DEAD")
    print(f"    SetCaseSelectedForOutput: ret={ret_select}")

    # Método 1: Todos los desplazamientos
    print("\n[9] Desplazamientos de juntas...")
    print("    Llamando JointDispl(\"\", 0)...")
    ret = model.Results.JointDispl("", 0)

    print(f"\n    Tipo de retorno: {type(ret)}")
    print(f"    Longitud: {len(ret)}")
    print(f"    ret[0] (NumberResults): {ret[0]}")

    if ret[0] > 0:
        NumberResults = ret[0]
        Obj = ret[1]
        Elm = ret[2]
        LoadCase = ret[3]
        StepType = ret[4]
        StepNum = ret[5]
        U1 = ret[6]
        U2 = ret[7]
        U3 = ret[8]
        R1 = ret[9]
        R2 = ret[10]
        R3 = ret[11]

        print(f"\n    [OK] {NumberResults} resultados obtenidos!")
        print("\n    Primeros 10 resultados:")
        print(f"    {'Obj':<10} {'LoadCase':<10} {'U1 (mm)':<12} {'U2 (mm)':<12} {'U3 (mm)':<12}")
        print("    " + "-"*60)

        for i in range(min(10, NumberResults)):
            print(f"    {Obj[i]:<10} {LoadCase[i]:<10} {U1[i]*1000:>11.4f} {U2[i]*1000:>11.4f} {U3[i]*1000:>11.4f}")

        # Encontrar máximo desplazamiento vertical
        max_u3_idx = max(range(NumberResults), key=lambda i: abs(U3[i]))
        print(f"\n    Desplazamiento vertical máximo:")
        print(f"      Punto: {Obj[max_u3_idx]}")
        print(f"      U3 = {U3[max_u3_idx]*1000:.4f} mm")

    else:
        print(f"    [WARN] Sin resultados (ret[0]={ret[0]})")

        # Debug: intentar con diferentes parámetros
        print("\n    Intentando con ItemTypeElm=2...")
        ret2 = model.Results.JointDispl("", 2)
        print(f"    ret[0] con ItemTypeElm=2: {ret2[0]}")

    # Método 2: Fuerzas en áreas (momentos)
    if num_areas > 0:
        print("\n[10] Fuerzas en áreas (Shell)...")
        area_names = model.AreaObj.GetNameList()[1]
        print(f"    Total áreas: {len(area_names)}")

        # Tomar primera área
        first_area = area_names[0]
        print(f"    Extrayendo de área: {first_area}")

        ret_area = model.Results.AreaForceShell(first_area, 0)
        print(f"    ret[0] (NumberResults): {ret_area[0]}")

        if ret_area[0] > 0:
            NumberResults = ret_area[0]
            M11 = ret_area[12]  # Momento M11
            M22 = ret_area[13]  # Momento M22
            M12 = ret_area[14]  # Momento M12

            print(f"\n    [OK] {NumberResults} resultados en área")
            print(f"    M11 max: {max(abs(m) for m in M11):.4f} kN-m/m")
            print(f"    M22 max: {max(abs(m) for m in M22):.4f} kN-m/m")
            print(f"    M12 max: {max(abs(m) for m in M12):.4f} kN-m/m")

    # Método 3: Reacciones
    print("\n[11] Reacciones...")
    ret_react = model.Results.JointReact("", 0)
    print(f"    ret[0] (NumberResults): {ret_react[0]}")

    if ret_react[0] > 0:
        NumberResults = ret_react[0]
        F1 = ret_react[6]
        F2 = ret_react[7]
        F3 = ret_react[8]

        # Suma de reacciones verticales
        total_F3 = sum(F3)
        print(f"\n    [OK] {NumberResults} reacciones")
        print(f"    Suma F3 (vertical): {total_F3:.4f} kN")

    print("\n" + "="*70)
    print("MODELO SIGUE ABIERTO EN SAP2000")
    print("="*70)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n[FIN]")
