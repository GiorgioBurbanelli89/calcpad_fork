# -*- coding: utf-8 -*-
"""
SAP2000 API - SINTAXIS CORRECTA según ejemplos oficiales CSI
Basado en Ejemplo_python.py (Example 7)
"""
import os
import sys
import comtypes.client

print("="*70)
print("SAP2000 - SINTAXIS OFICIAL CSI (CORRECTO)")
print("="*70)

# Path para guardar modelo
APIPath = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7'
ModelPath = os.path.join(APIPath, 'SAP2000_OFICIAL_TEST.sdb')

try:
    # Crear helper
    print("\n[1] Creando SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)

    # Crear instancia de SAP2000
    mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")

    # Iniciar aplicación
    mySapObject.ApplicationStart()

    # Obtener SapModel
    SapModel = mySapObject.SapModel
    print("    [OK] SAP2000 iniciado")

    # Inicializar modelo (unidades: kN, m, C)
    print("\n[2] Inicializando modelo...")
    SapModel.InitializeNewModel(6)  # 6 = kN_m_C

    # Crear modelo en blanco
    ret = SapModel.File.NewBlank()
    print("    [OK] Modelo creado")

    # Definir material
    print("\n[3] Definiendo material...")
    MATERIAL_CONCRETE = 2
    ret = SapModel.PropMaterial.SetMaterial('CONC', MATERIAL_CONCRETE)
    ret = SapModel.PropMaterial.SetMPIsotropic('CONC', 25000000, 0.2, 0.0000099)
    print("    [OK] Material CONC creado")

    # Definir sección de viga
    print("\n[4] Definiendo sección...")
    ret = SapModel.PropFrame.SetRectangle('R1', 'CONC', 0.3, 0.3)
    print("    [OK] Sección R1 (0.3x0.3m)")

    # Agregar vigas (pórtico simple)
    print("\n[5] Creando geometría...")
    FrameName1 = ' '
    FrameName2 = ' '

    # Columna vertical
    [FrameName1, ret] = SapModel.FrameObj.AddByCoord(0, 0, 0, 0, 0, 3, FrameName1, 'R1', '1', 'Global')

    # Viga horizontal (voladizo)
    [FrameName2, ret] = SapModel.FrameObj.AddByCoord(0, 0, 3, 3, 0, 3, FrameName2, 'R1', '2', 'Global')

    print(f"    [OK] Frame1: {FrameName1}")
    print(f"    [OK] Frame2: {FrameName2}")

    # Obtener puntos de las vigas
    PointName1 = ' '
    PointName2 = ' '

    # Puntos de la columna
    [PointName1, PointName2, ret] = SapModel.FrameObj.GetPoints(FrameName1, PointName1, PointName2)
    print(f"    Columna: {PointName1} -> {PointName2}")

    # Apoyo empotrado en la base
    Restraint = [True, True, True, True, True, True]
    ret = SapModel.PointObj.SetRestraint(PointName1, Restraint)
    print(f"    [OK] Apoyo empotrado en {PointName1}")

    # Puntos de la viga
    PointName3 = ' '
    PointName4 = ' '
    [PointName3, PointName4, ret] = SapModel.FrameObj.GetPoints(FrameName2, PointName3, PointName4)
    print(f"    Viga: {PointName3} -> {PointName4}")

    # Agregar patrón de carga
    print("\n[6] Creando patrón de carga...")
    LTYPE_OTHER = 8
    ret = SapModel.LoadPatterns.Add('DEAD', LTYPE_OTHER, 1, True)
    print("    [OK] Patrón DEAD creado")

    # Aplicar carga puntual en el extremo del voladizo
    print("\n[7] Aplicando carga...")
    PointLoadValue = [0, 0, -10, 0, 0, 0]  # 10 kN hacia abajo
    ret = SapModel.PointObj.SetLoadForce(PointName4, 'DEAD', PointLoadValue)
    print(f"    [OK] Carga de 10kN en punto {PointName4}")

    # Guardar modelo ANTES del análisis
    print(f"\n[8] Guardando modelo...")
    ret = SapModel.File.Save(ModelPath)
    print(f"    [OK] Guardado: {ModelPath}")

    # Ejecutar análisis (esto crea el modelo de análisis automáticamente)
    print("\n[9] Ejecutando análisis...")
    ret = SapModel.Analyze.RunAnalysis()
    print(f"    [OK] Análisis completado (ret={ret})")

    # ========== EXTRACCIÓN DE RESULTADOS ==========
    print("\n" + "="*70)
    print("EXTRACCIÓN DE RESULTADOS (SINTAXIS OFICIAL)")
    print("="*70)

    # Inicializar arrays para resultados
    print("\n[10] Extrayendo desplazamientos...")

    # Desseleccionar todos los casos
    ret = SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()

    # Seleccionar caso DEAD
    ret = SapModel.Results.Setup.SetCaseSelectedForOutput('DEAD')
    print("    [OK] Caso DEAD seleccionado")

    # Inicializar variables para JointDispl (SINTAXIS OFICIAL CSI)
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
    ObjectElm = 0  # 0 = Object

    # LLAMADA CORRECTA (según Example 7)
    [NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3, ret] = \
        SapModel.Results.JointDispl(PointName4, ObjectElm, NumberResults, Obj, Elm, ACase,
                                     StepType, StepNum, U1, U2, U3, R1, R2, R3)

    print(f"\n    NumberResults = {NumberResults}")

    if NumberResults > 0:
        print(f"\n    [OK] {NumberResults} resultados obtenidos!")
        print(f"\n    Punto: {Obj[0]}")
        print(f"    Caso: {ACase[0]}")
        print(f"    U1 (X) = {U1[0]*1000:.4f} mm")
        print(f"    U2 (Y) = {U2[0]*1000:.4f} mm")
        print(f"    U3 (Z) = {U3[0]*1000:.4f} mm")
        print(f"    R1 (RX) = {R1[0]} rad")
        print(f"    R2 (RY) = {R2[0]} rad")
        print(f"    R3 (RZ) = {R3[0]} rad")

        # Guardar resultado
        result_U3 = U3[0]
    else:
        print("    [ERROR] Sin resultados!")
        result_U3 = 0

    # Extraer TODOS los desplazamientos (todos los puntos)
    print("\n[11] Extrayendo todos los desplazamientos...")

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

    # Llamar con punto vacío para obtener todos
    [NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3, ret] = \
        SapModel.Results.JointDispl("", ObjectElm, NumberResults, Obj, Elm, ACase,
                                     StepType, StepNum, U1, U2, U3, R1, R2, R3)

    print(f"\n    Total puntos: {NumberResults}")

    if NumberResults > 0:
        print("\n    Todos los desplazamientos:")
        print(f"    {'Punto':<10} {'U1 (mm)':<12} {'U2 (mm)':<12} {'U3 (mm)':<12}")
        print("    " + "-"*50)
        for i in range(NumberResults):
            print(f"    {Obj[i]:<10} {U1[i]*1000:>11.4f} {U2[i]*1000:>11.4f} {U3[i]*1000:>11.4f}")

    # VERIFICACIÓN TEÓRICA
    print("\n" + "="*70)
    print("VERIFICACIÓN TEÓRICA")
    print("="*70)
    print("\nViga en voladizo:")
    print("  L = 3m")
    print("  P = 10 kN (en el extremo)")
    print("  E = 25000 MPa = 25000000 kN/m2")
    print("  I = bh^3/12 = 0.3*0.3^3/12 = 0.000675 m4")
    print("\n  Deflexión teórica = PL^3/(3EI)")
    E = 25000000  # kN/m2
    I = 0.000675  # m4
    L = 3  # m
    P = 10  # kN
    delta_teorico = (P * L**3) / (3 * E * I)
    print(f"  delta = {delta_teorico*1000:.4f} mm")

    if NumberResults > 0:
        error_pct = abs(result_U3 - delta_teorico) / delta_teorico * 100
        print(f"\n  SAP2000: {abs(result_U3)*1000:.4f} mm")
        print(f"  Teórico: {delta_teorico*1000:.4f} mm")
        print(f"  Error: {error_pct:.2f}%")

    # Cerrar SAP2000
    print("\n" + "="*70)
    print("COMPLETADO - SAP2000 se cerrará")
    print(f"Modelo guardado en: {ModelPath}")
    print("="*70)

    ret = mySapObject.ApplicationExit(False)
    SapModel = None
    mySapObject = None

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n[FIN]")
