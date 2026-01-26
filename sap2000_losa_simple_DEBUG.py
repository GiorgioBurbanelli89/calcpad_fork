# -*- coding: utf-8 -*-
"""
SAP2000 Losa Simple con DEBUG
Versión simplificada para diagnosticar problemas
"""
import sys
import comtypes.client

print("="*70)
print("SAP2000 LOSA SIMPLE - DEBUG")
print("="*70)

try:
    # Crear SAP2000
    print("\nCreando SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    sap = helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject")
    sap.ApplicationStart()
    model = sap.SapModel

    version = model.GetVersion()
    print(f"[OK] SAP2000 v{version[0]}")

    # Crear modelo simple: 1 elemento de placa 1x1m
    print("\n--- Modelo Simple: 1 elemento 1x1m ---")

    model.InitializeNewModel(6)  # kN, m, C
    model.File.NewBlank()

    # Material
    model.PropMaterial.SetMaterial("CONC", 2)
    model.PropMaterial.SetMPIsotropic("CONC", 35000000, 0.15, 0.0000099)
    print("[OK] Material creado")

    # Shell property (Plate-Thick, Mindlin)
    model.PropArea.SetShell_1("LOSA", 5, False, "CONC", 0, 0.1, 0.1, 0, "", "")
    print("[OK] Seccion de shell creada")

    # 4 puntos para 1 elemento
    model.PointObj.AddCartesian(0, 0, 0, "1")
    model.PointObj.AddCartesian(1, 0, 0, "2")
    model.PointObj.AddCartesian(1, 1, 0, "3")
    model.PointObj.AddCartesian(0, 1, 0, "4")
    print("[OK] 4 puntos creados")

    # 1 elemento
    pts = ["1", "2", "3", "4"]
    model.AreaObj.AddByPoint(4, pts, "AREA1", "LOSA", "AREA1")
    print("[OK] 1 elemento creado")

    # Apoyos SOLO en esquinas (4 puntos)
    # Apoyo simple: Solo U3 restringido
    for pt in ["1", "2", "3", "4"]:
        model.PointObj.SetRestraint(pt, [False, False, True, False, False, False], 0)
    print("[OK] Apoyos en 4 esquinas (solo U3)")

    # Carga uniforme
    model.AreaObj.SetLoadUniform("AREA1", "Dead", 10, 6, True, "Global", 0)
    print("[OK] Carga 10 kN/m2 aplicada")

    # Guardar modelo ANTES del análisis
    path_before = R"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_DEBUG_BEFORE.sdb"
    model.File.Save(path_before)
    print(f"[OK] Modelo guardado ANTES analisis: {path_before}")

    # Ejecutar análisis
    print("\n--- Ejecutando Analisis ---")
    ret = model.Analyze.RunAnalysis()
    print(f"[OK] Analisis completado (ret={ret})")

    # Guardar modelo DESPUES del análisis
    path_after = R"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_DEBUG_AFTER.sdb"
    model.File.Save(path_after)
    print(f"[OK] Modelo guardado DESPUES analisis: {path_after}")

    # Verificar casos de carga disponibles
    print("\n--- Verificando Casos de Carga ---")
    num_cases = 0
    case_names = []
    result = model.LoadCases.GetNameList(num_cases, case_names)
    num_cases = result[0]
    case_names = result[1]
    print(f"Casos encontrados: {num_cases}")
    for i, case in enumerate(case_names):
        print(f"  [{i+1}] {case}")

    # Seleccionar caso para output
    print("\n--- Seleccionando Caso para Output ---")
    model.Results.Setup.DeselectAllCasesAndCombosForOutput()

    # Intentar con MODAL primero (siempre existe)
    try:
        ret = model.Results.Setup.SetCaseSelectedForOutput("MODAL")
        print(f"[OK] Caso MODAL seleccionado (ret={ret})")
    except:
        print("[WARN] MODAL no disponible")

    # Intentar con DEAD
    try:
        ret = model.Results.Setup.SetCaseSelectedForOutput("DEAD")
        print(f"[OK] Caso DEAD seleccionado (ret={ret})")
    except:
        print("[ERROR] DEAD no disponible")

    # Extraer desplazamientos
    print("\n--- Extrayendo Desplazamientos ---")

    # Método 1: Todos los nodos
    ret = model.Results.JointDispl("", 0)  # 0 = ObjectElm
    num_results = ret[0]
    print(f"Numero de resultados: {num_results}")

    if num_results > 0:
        obj_names = ret[2]
        elm_names = ret[3]
        load_cases = ret[4]
        U1 = ret[7]
        U2 = ret[8]
        U3 = ret[9]
        R1 = ret[10]
        R2 = ret[11]
        R3 = ret[12]

        print(f"\nTotal de resultados: {len(U3)}")
        print("\nDesplazamientos U3 por nodo:")
        for i in range(min(10, len(U3))):  # Mostrar primeros 10
            print(f"  Nodo {obj_names[i]:8s} Caso {load_cases[i]:10s} U3 = {U3[i]*1000:10.4f} mm")

        # Buscar máximo
        max_u3 = 0
        max_idx = 0
        for i in range(len(U3)):
            if abs(U3[i]) > abs(max_u3):
                max_u3 = U3[i]
                max_idx = i

        print(f"\n[RESULTADO] Desplazamiento maximo:")
        print(f"  Nodo: {obj_names[max_idx]}")
        print(f"  Caso: {load_cases[max_idx]}")
        print(f"  U3:   {abs(max_u3)*1000:.4f} mm")
    else:
        print("[ERROR] No hay resultados de desplazamientos")
        print("         Revisa que el analisis se ejecuto correctamente")

    # Extraer fuerzas en shell
    print("\n--- Extrayendo Fuerzas en Shell ---")
    ret = model.Results.AreaForceShell("AREA1", 0)
    num_results = ret[0]
    print(f"Numero de resultados: {num_results}")

    if num_results > 0:
        obj_names = ret[2]
        load_cases = ret[4]
        M11 = ret[14]
        M22 = ret[15]
        M12 = ret[16]

        print(f"\nTotal de resultados: {len(M11)}")
        print("\nMomentos por punto:")
        for i in range(min(num_results, 10)):
            print(f"  Area {obj_names[i]:8s} Caso {load_cases[i]:10s} M11={M11[i]:8.4f} M22={M22[i]:8.4f} M12={M12[i]:8.4f}")

        # Promedios
        avg_m11 = sum(M11) / len(M11)
        avg_m22 = sum(M22) / len(M22)
        avg_m12 = sum(M12) / len(M12)

        print(f"\n[RESULTADO] Momentos promedio:")
        print(f"  M11: {abs(avg_m11):.4f} kNm/m")
        print(f"  M22: {abs(avg_m22):.4f} kNm/m")
        print(f"  M12: {abs(avg_m12):.4f} kNm/m")
    else:
        print("[ERROR] No hay resultados de fuerzas en shell")

    # Reacciones
    print("\n--- Extrayendo Reacciones ---")
    ret = model.Results.JointReact("", 0)
    num_results = ret[0]

    if num_results > 0:
        obj_names = ret[2]
        load_cases = ret[4]
        F3 = ret[9]

        total_reaction = sum(F3)
        print(f"Reaccion total vertical: {abs(total_reaction):.4f} kN")
        print(f"Carga total aplicada:    {10.0 * 1.0 * 1.0:.4f} kN")
        print(f"Diferencia:              {abs(abs(total_reaction) - 10.0):.4f} kN")

    print("\n" + "="*70)
    print("FIN DEBUG")
    print("="*70)
    print("\nSAP2000 dejado abierto para revision manual")
    print("Abre los archivos .sdb para comparar BEFORE y AFTER analisis")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
