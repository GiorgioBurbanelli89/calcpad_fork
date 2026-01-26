# -*- coding: utf-8 -*-
"""
COMPARACION - Abrir archivo Plate-6x4.s2k oficial
Este archivo usa Plate-Thin (Kirchhoff) - misma teoria que Calcpad
"""
import comtypes.client

print("="*70)
print("COMPARACION: Plate-6x4.s2k (KIRCHHOFF) vs CALCPAD")
print("="*70)

# Ruta al archivo .s2k original
s2k_file = R'C:\Users\j-b-j\Documents\Calcpad\Examples\Mechanics\Finite Elements\SAP 2000\Plate-6x4.s2k'
sdb_file = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\Plate-6x4_oficial.sdb'

try:
    # ========== INICIAR SAP2000 ==========
    print("\n[1] Iniciando SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    SapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
    SapObject.ApplicationStart()
    SapModel = SapObject.SapModel
    print("    [OK] Iniciado")

    # ========== ABRIR ARCHIVO .s2k ==========
    print(f"\n[2] Abriendo archivo .s2k...")
    print(f"    Archivo: {s2k_file}")
    ret = SapModel.File.OpenFile(s2k_file)
    print(f"    [OK] Archivo abierto (ret={ret})")

    # ========== REFRESCAR/ACTUALIZAR MODELO ==========
    print(f"\n[3] Actualizando modelo...")
    # Forzar actualizacion del modelo
    SapModel.View.RefreshView(0, False)
    # Intentar obtener nombres de objetos
    ret_names = SapModel.AreaObj.GetNameList()
    if ret_names[0] > 0:
        print(f"    [OK] Modelo actualizado - {ret_names[0]} areas detectadas")
        area_names = ret_names[1]
    else:
        print(f"    [AVISO] No se detectaron areas por nombre")
        area_names = []

    # ========== GUARDAR COMO .sdb ==========
    print(f"\n[4] Guardando como .sdb...")
    ret = SapModel.File.Save(sdb_file)
    print(f"    [OK] Guardado: {sdb_file}")

    # ========== VERIFICAR MODELO ==========
    print(f"\n[5] Verificando modelo...")
    num_points = SapModel.PointObj.Count()
    num_areas = len(area_names) if area_names else SapModel.AreaObj.Count()
    print(f"    Puntos: {num_points}")
    print(f"    Areas: {num_areas}")

    # ========== ANALIZAR ==========
    print("\n[6] Ejecutando analisis...")
    ret = SapModel.Analyze.RunAnalysis()
    print(f"    [OK] Analisis (ret={ret})")

    # ========== CONFIGURAR SALIDA ==========
    print("\n[7] Configurando output...")
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    # El archivo .s2k usa "LOAD1" como nombre del caso de carga
    SapModel.Results.Setup.SetCaseSelectedForOutput("LOAD1")
    print("    [OK] Caso LOAD1 seleccionado")

    # ========== EXTRAER DESPLAZAMIENTOS ==========
    print("\n[8] Extrayendo desplazamientos en el centro...")

    # Centro de la losa (coordenadas 0, 0)
    center_point = "18"  # Joint 18 está en X=0, Y=0

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

    w_center = 0.0
    if NumberResults > 0:
        w_center = abs(U3[0]) * 1000  # convertir a mm
        print(f"    Desplazamiento centro (Joint {center_point}): {w_center:.4f} mm")
    else:
        print(f"    [AVISO] No se obtuvieron desplazamientos")

    # ========== EXTRAER MOMENTOS DE TODAS LAS AREAS ==========
    print("\n[9] Extrayendo momentos de todas las areas...")

    all_M11 = []
    all_M22 = []
    all_M12 = []

    # Usar los nombres de areas obtenidos, o iterar por número si no hay nombres
    shells_to_process = area_names if area_names else [str(i) for i in range(1, 25)]

    for shell_name in shells_to_process:

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
            SapModel.Results.AreaForceShell(shell_name, 0, 0, [], [],
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
        print(f"\n    Total de resultados procesados: {len(all_M11)}")
    else:
        print("    [ERROR] No se obtuvieron momentos")
        global_max_m11 = 0
        global_max_m22 = 0
        global_max_m12 = 0

    # ========== CERRAR ==========
    print("\n[10] Cerrando...")
    SapObject.ApplicationExit(False)
    print("    [OK] Cerrado")

    # ========== RESUMEN ==========
    print("\n" + "="*70)
    print("RESULTADOS SAP2000 - Plate-6x4.s2k (PLATE-THIN/KIRCHHOFF)")
    print("="*70)
    print(f"Archivo original: Plate-6x4.s2k")
    print(f"Tipo de elemento: Plate-Thin (Kirchhoff)")
    print(f"Teoria: Misma que Calcpad")
    print("-"*70)
    print(f"Desplazamiento centro: {w_center:.4f} mm")
    print(f"M11 maximo global: {global_max_m11:.6f} kN-m/m")
    print(f"M22 maximo global: {global_max_m22:.6f} kN-m/m")
    print(f"M12 maximo global: {global_max_m12:.6f} kN-m/m")
    print("="*70)

    print("\nCOMPARACION CON CALCPAD:")
    print("-"*70)
    print("CALCPAD (Kirchhoff):")
    print("  Mx = 6.275 kN-m/m")
    print("  My = 12.744 kN-m/m")
    print("  Mxy = -8.378 kN-m/m")
    print("-"*70)
    print("SAP2000 Plate-Thin (Kirchhoff):")
    print(f"  M11 = {global_max_m11:.3f} kN-m/m")
    print(f"  M22 = {global_max_m22:.3f} kN-m/m")
    print(f"  M12 = {global_max_m12:.3f} kN-m/m")
    print("-"*70)

    # Calcular diferencias
    if global_max_m11 > 0:
        diff_m11 = abs(6.275 - global_max_m11) / 6.275 * 100
        diff_m22 = abs(12.744 - global_max_m22) / 12.744 * 100
        print(f"Diferencia M11 vs Mx: {diff_m11:.2f}%")
        print(f"Diferencia M22 vs My: {diff_m22:.2f}%")

        if diff_m11 < 5 and diff_m22 < 5:
            print("\n[EXCELENTE] Resultados coinciden (< 5% diferencia)")
        elif diff_m11 < 15 and diff_m22 < 15:
            print("\n[BUENO] Resultados cercanos (< 15% diferencia)")
        else:
            print("\n[ATENCION] Diferencias significativas")
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
