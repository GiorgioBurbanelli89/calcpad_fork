# -*- coding: utf-8 -*-
"""
SAP2000 API - Test minimalista con template 2D Frame
Basado en ejemplos CSI - usando template en lugar de NewBlank
"""
import comtypes.client
import os

print("="*70)
print("SAP2000 - TEST MINIMAL CON TEMPLATE")
print("="*70)

try:
    # Conectar
    print("\n[1] Creando SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    sap = helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject")
    sap.ApplicationStart()
    model = sap.SapModel
    print("    [OK] Iniciado")

    # Usar template en lugar de NewBlank
    print("\n[2] Creando modelo desde template 2D Frame...")
    ret = model.File.New2DFrame(7, 2, 3, 3, 4, 3)
    # portalFrame = 7 (CONCRETE)
    # NumberStorys = 2
    # StoryHeight = 3 m
    # NumberBays = 3
    # BayWidth = 4 m
    # Restraint = 3 (fixed)
    print(f"    [OK] Template creado (ret={ret})")

    # Información
    num_points = model.PointObj.Count()
    num_frames = model.FrameObj.Count()
    print(f"    Puntos: {num_points}")
    print(f"    Frames: {num_frames}")

    # Añadir carga simple
    print("\n[3] Añadiendo carga...")
    # Carga en punto superior izquierdo
    ret = model.PointObj.SetLoadForce("3", "DEAD", [10, 0, -20, 0, 0, 0], False, "", 0)
    print(f"    [OK] Carga añadida (ret={ret})")

    # Guardar ANTES
    path_before = R"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_MINIMAL_BEFORE.sdb"
    model.File.Save(path_before)
    print(f"\n[4] Guardado BEFORE: {path_before}")

    # Analizar
    print("\n[5] Analizando...")
    ret1 = model.Analyze.CreateAnalysisModel()
    ret2 = model.Analyze.RunAnalysis()
    print(f"    CreateAnalysisModel: ret={ret1}")
    print(f"    RunAnalysis: ret={ret2}")

    # Guardar AFTER
    path_after = R"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_MINIMAL_AFTER.sdb"
    model.File.Save(path_after)
    print(f"\n[6] Guardado AFTER: {path_after}")

    # RESULTADOS
    print("\n" + "="*70)
    print("EXTRACCION RESULTADOS")
    print("="*70)

    # Configurar output
    print("\n[7] Configurando output...")
    model.Results.Setup.DeselectAllCasesAndCombosForOutput()
    ret = model.Results.Setup.SetCaseSelectedForOutput("DEAD")
    print(f"    SetCaseSelectedForOutput: ret={ret}")

    # Intentar extraer
    print("\n[8] Extrayendo desplazamientos...")

    # Método A: Todos los puntos
    print("\n  [A] Todos los puntos (ItemTypeElm=0)")
    ret = model.Results.JointDispl("", 0)
    print(f"      ret = {ret}")
    print(f"      Tipo: {type(ret)}")
    print(f"      Longitud: {len(ret) if hasattr(ret, '__len__') else 'N/A'}")

    if len(ret) > 0:
        print(f"      ret[0] = {ret[0]} (num results)")
        if ret[0] > 0:
            print(f"      [OK] {ret[0]} resultados!")
            U3 = ret[9]
            joint_names = ret[2]
            for i in range(min(5, ret[0])):
                print(f"      Punto {joint_names[i]}: U3 = {U3[i]*1000:.4f} mm")
        else:
            print("      [WARN] ret[0]=0, sin resultados")

    # Método B: Punto específico
    print("\n  [B] Punto específico (punto 3)")
    ret = model.Results.JointDispl("3", 0)
    print(f"      ret[0] = {ret[0]} (num results)")
    if ret[0] > 0:
        U3 = ret[9]
        print(f"      Punto 3: U3 = {U3[0]*1000:.4f} mm")

    # Método C: Reacciones
    print("\n  [C] Reacciones (punto 1)")
    ret = model.Results.JointReact("1", 0)
    print(f"      ret[0] = {ret[0]} (num results)")
    if ret[0] > 0:
        F3 = ret[9]
        print(f"      Punto 1: F3 = {F3[0]:.4f} kN")

    print("\n" + "="*70)
    print("ARCHIVOS GUARDADOS:")
    print(f"  BEFORE: {path_before}")
    print(f"  AFTER:  {path_after}")
    print("\nSAP2000 dejado abierto - revisar manualmente")
    print("="*70)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n[FIN]")
