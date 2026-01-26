# -*- coding: utf-8 -*-
"""
SAP2000 API - VERSION FINAL FUNCIONANDO
Basado en ejemplos oficiales CSI y pruebas iterativas
"""
import sys
import comtypes.client

print("="*70)
print("SAP2000 API - VERSION FINAL FUNCIONANDO")
print("="*70)

try:
    # Crear SAP2000
    print("\n[1] Creando instancia de SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    sap = helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject")
    sap.ApplicationStart()
    model = sap.SapModel
    print("    [OK] SAP2000 iniciado")

    # Version
    version = model.GetVersion()
    print(f"    [OK] Version: {version[0]}")

    # Crear modelo simple
    print("\n[2] Creando modelo...")
    model.InitializeNewModel(6)  # kN, m, C
    model.File.NewBlank()
    print("    [OK] Modelo inicializado")

    # Material
    print("\n[3] Definiendo material...")
    model.PropMaterial.SetMaterial("CONC", 2)
    model.PropMaterial.SetMPIsotropic("CONC", 25000000, 0.2, 0.0000099)
    print("    [OK] Material CONC creado")

    # Frame property (para probar con algo simple)
    print("\n[4] Definiendo seccion de viga...")
    model.PropFrame.SetRectangle("R1", "CONC", 0.3, 0.3)
    print("    [OK] Seccion R1 creada (0.3x0.3m)")

    # Crear estructura simple: viga en voladizo
    print("\n[5] Creando geometria...")
    # Punto base
    model.PointObj.AddCartesian(0, 0, 0, "1")
    # Punto extremo
    model.PointObj.AddCartesian(3, 0, 0, "2")
    print("    [OK] 2 puntos creados")

    # Viga
    model.FrameObj.AddByPoint("1", "2", "", "R1", "VIGA1")
    print("    [OK] Viga creada")

    # Apoyo empotrado en punto 1
    model.PointObj.SetRestraint("1", [True, True, True, True, True, True], 0)
    print("    [OK] Apoyo empotrado en punto 1")

    # Carga puntual en punto 2
    print("\n[6] Aplicando carga...")
    model.PointObj.SetLoadForce("2", "DEAD", [0, 0, -10, 0, 0, 0], False, "", 0)
    print("    [OK] Carga de 10 kN en punto 2")

    # Guardar ANTES de analizar
    path_before = R"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_FINAL_BEFORE.sdb"
    model.File.Save(path_before)
    print(f"\n[7] Modelo guardado: {path_before}")

    # CLAVE: Crear modelo de analisis ANTES de ejecutar
    print("\n[8] Creando modelo de analisis...")
    ret_create = model.Analyze.CreateAnalysisModel()
    print(f"    [OK] Modelo de analisis creado (ret={ret_create})")

    # Analizar
    print("\n[9] Ejecutando analisis...")
    ret_run = model.Analyze.RunAnalysis()
    print(f"    [OK] Analisis ejecutado (ret={ret_run})")

    # Guardar DESPUES
    path_after = R"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_FINAL_AFTER.sdb"
    model.File.Save(path_after)
    print(f"\n[10] Modelo guardado: {path_after}")

    # RESULTADOS - Probar VARIOS metodos
    print("\n" + "="*70)
    print("EXTRAYENDO RESULTADOS")
    print("="*70)

    # Seleccionar caso
    model.Results.Setup.DeselectAllCasesAndCombosForOutput()
    model.Results.Setup.SetCaseSelectedForOutput("DEAD")
    print("\n[OK] Caso DEAD seleccionado")

    # Metodo 1: Por nombre de punto
    print("\n--- Metodo 1: Desplazamientos por nombre ---")
    ret = model.Results.JointDispl("2", 0)  # 0 = Object
    if ret[0] > 0:
        U3 = ret[9]
        print(f"[OK] Punto 2: U3 = {U3[0]*1000:.4f} mm")
    else:
        print(f"[WARN] Sin resultados (num={ret[0]})")

    # Metodo 2: Todos los puntos
    print("\n--- Metodo 2: Todos los desplazamientos ---")
    ret = model.Results.JointDispl("", 0)
    if ret[0] > 0:
        nombres = ret[2]
        U3_all = ret[9]
        print(f"[OK] {ret[0]} resultados obtenidos")
        for i in range(min(ret[0], 5)):
            print(f"     Punto {nombres[i]}: U3 = {U3_all[i]*1000:.4f} mm")
    else:
        print(f"[WARN] Sin resultados")

    # Metodo 3: Reacciones
    print("\n--- Metodo 3: Reacciones ---")
    ret = model.Results.JointReact("1", 0)
    if ret[0] > 0:
        F3 = ret[9]
        print(f"[OK] Punto 1: Reaccion F3 = {F3[0]:.4f} kN")
    else:
        print(f"[WARN] Sin resultados")

    # Metodo 4: Fuerzas en frame
    print("\n--- Metodo 4: Fuerzas en viga ---")
    ret = model.Results.FrameForce("VIGA1", 0)
    if ret[0] > 0:
        V2 = ret[11]  # Cortante
        M3 = ret[13]  # Momento
        print(f"[OK] {ret[0]} puntos en viga")
        print(f"     V2 max = {max(abs(v) for v in V2):.4f} kN")
        print(f"     M3 max = {max(abs(m) for m in M3):.4f} kNm")
    else:
        print(f"[WARN] Sin resultados")

    # VERIFICACION TEORICA
    print("\n" + "="*70)
    print("VERIFICACION TEORICA")
    print("="*70)
    print("\nViga en voladizo:")
    print("  L = 3m, P = 10 kN")
    print("  Deflexion teorica = PL^3/(3EI)")
    print("  Momento teorico = PL = 10*3 = 30 kNm")
    print("  Reaccion teorica = P = 10 kN")

    if ret[0] > 0:
        print("\n[OK] RESULTADOS OBTENIDOS EXITOSAMENTE")
    else:
        print("\n[WARN] No se obtuvieron resultados - revisar modelo en SAP2000")

    print("\n" + "="*70)
    print("SAP2000 dejado abierto para revision")
    print("Archivos guardados:")
    print(f"  BEFORE: {path_before}")
    print(f"  AFTER:  {path_after}")
    print("="*70)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n[FIN]")
