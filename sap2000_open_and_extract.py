# -*- coding: utf-8 -*-
"""
SAP2000 API - Abrir archivo existente y extraer resultados
"""
import sys
import comtypes.client
import os

print("="*70)
print("SAP2000 - ABRIR ARCHIVO Y EXTRAER RESULTADOS")
print("="*70)

# Archivo a abrir (del script anterior)
file_path = R"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_FINAL_AFTER.sdb"

if not os.path.exists(file_path):
    print(f"[ERROR] Archivo no existe: {file_path}")
    print("\nIntentando con otro archivo...")
    file_path = R"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_TABLES_TEST.sdb"

try:
    # Conectar a SAP2000
    print(f"\n[1] Conectando a SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    sap = helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject")
    sap.ApplicationStart()
    model = sap.SapModel
    print("    [OK] Conectado")

    # Abrir archivo existente
    print(f"\n[2] Abriendo archivo...")
    print(f"    {file_path}")
    ret = model.File.OpenFile(file_path)
    print(f"    [OK] Archivo abierto (ret={ret})")

    # Desbloquear modelo
    print("\n[3] Desbloqueando modelo...")
    model.SetModelIsLocked(False)
    print("    [OK] Desbloqueado")

    # Información del modelo
    print("\n[4] Información del modelo:")
    version = model.GetVersion()
    print(f"    Version: {version[0]}")

    # Contar objetos
    num_points = model.PointObj.Count()
    num_frames = model.FrameObj.Count()
    print(f"    Puntos: {num_points}")
    print(f"    Vigas: {num_frames}")

    # Listar casos de carga
    print("\n[5] Casos de carga:")
    num_cases = model.LoadCases.Count()
    print(f"    Total casos: {num_cases}")

    # IMPORTANTE: Seleccionar caso para output
    print("\n[6] Configurando casos para output...")
    model.Results.Setup.DeselectAllCasesAndCombosForOutput()
    model.Results.Setup.SetCaseSelectedForOutput("DEAD")
    print("    [OK] Caso DEAD seleccionado")

    # Intentar extraer resultados - METODO 1
    print("\n" + "="*70)
    print("EXTRACCION DE RESULTADOS")
    print("="*70)

    print("\n[Metodo 1] JointDispl - Todos los puntos")
    ret = model.Results.JointDispl("", 0)
    print(f"    ret[0] (num results) = {ret[0]}")

    if ret[0] > 0:
        num_results = ret[0]
        joint_names = ret[2]
        U1 = ret[7]
        U2 = ret[8]
        U3 = ret[9]

        print(f"    [OK] {num_results} resultados")
        print("\n    Primeros 5 resultados:")
        for i in range(min(5, num_results)):
            print(f"    Punto {joint_names[i]}: U3 = {U3[i]*1000:.4f} mm")
    else:
        print("    [WARN] Sin resultados")

    # Intentar con ItemTypeElm = 2 (Element)
    print("\n[Metodo 2] JointDispl - ItemTypeElm=2")
    ret = model.Results.JointDispl("", 2)
    print(f"    ret[0] (num results) = {ret[0]}")

    if ret[0] > 0:
        num_results = ret[0]
        print(f"    [OK] {num_results} resultados con ItemTypeElm=2")

    # Listar todos los puntos del modelo
    print("\n[7] Listando puntos del modelo:")
    for i in range(num_points):
        point_name = model.PointObj.GetNameList()[1][i]
        coords = model.PointObj.GetCoordCartesian(point_name)
        print(f"    Punto {point_name}: ({coords[0]:.2f}, {coords[1]:.2f}, {coords[2]:.2f})")

        # Intentar obtener desplazamiento de este punto específico
        ret_point = model.Results.JointDispl(point_name, 0)
        if ret_point[0] > 0:
            U3_point = ret_point[9][0]
            print(f"        -> U3 = {U3_point*1000:.4f} mm")

    # Intentar con FrameForce
    print("\n[8] Fuerzas en vigas:")
    if num_frames > 0:
        frame_names = model.FrameObj.GetNameList()[1]
        for i in range(min(3, num_frames)):
            frame_name = frame_names[i]
            ret_frame = model.Results.FrameForce(frame_name, 0)
            print(f"    Frame {frame_name}: num results = {ret_frame[0]}")

            if ret_frame[0] > 0:
                V2 = ret_frame[11]
                M3 = ret_frame[13]
                print(f"        V2 max = {max(abs(v) for v in V2):.4f} kN")
                print(f"        M3 max = {max(abs(m) for m in M3):.4f} kNm")

    print("\n" + "="*70)
    print("SAP2000 dejado abierto para inspeccion manual")
    print("="*70)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n[FIN]")
