# -*- coding: utf-8 -*-
"""
COMPARACION: Calcpad FEA vs SAP2000
Losa Rectangular 6x4m
"""
import sys
import os
import subprocess
import re

print("="*70)
print("COMPARACION: CALCPAD vs SAP2000")
print("Losa Rectangular 6x4m")
print("="*70)

# ============================================================
# DATOS DEL PROBLEMA
# ============================================================
a = 6.0       # dimension en X (m)
b = 4.0       # dimension en Y (m)
t = 0.1       # espesor (m)
q = 10.0      # carga (kN/m2)
E = 35000e3   # E en kPa (35000 MPa)
nu = 0.15     # Poisson

# Malla
n_a = 6       # elementos en X
n_b = 4       # elementos en Y
a_1 = a / n_a
b_1 = b / n_b

print("\n--- DATOS DEL PROBLEMA ---")
print(f"Losa: {a}m x {b}m, t={t}m")
print(f"Carga: q={q} kN/m2")
print(f"Material: E={E/1000} MPa, nu={nu}")
print(f"Malla: {n_a}x{n_b} elementos")

# ============================================================
# PARTE 1: EJECUTAR CALCPAD
# ============================================================
print("\n" + "="*70)
print("PARTE 1: EJECUTAR CALCPAD")
print("="*70)

calcpad_file = r"C:\Users\j-b-j\Documents\Calcpad\Examples\Mechanics\Finite Elements\Rectangular Slab FEA.cpd"
calcpad_exe = r"C:/Users/j-b-j/Documents/Calcpad-7.5.7/Calcpad.Cli/bin/Debug/net10.0/Cli.exe"
calcpad_output = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\calcpad_results.html"

if not os.path.exists(calcpad_exe):
    print(f"[ERROR] Calcpad.exe no encontrado: {calcpad_exe}")
    calcpad_results = None
else:
    try:
        print(f"Ejecutando Calcpad...")
        result = subprocess.run(
            [calcpad_exe, calcpad_file, calcpad_output],
            capture_output=True,
            text=True,
            timeout=30
        )

        if os.path.exists(calcpad_output):
            print(f"[OK] Resultados guardados en: {calcpad_output}")

            # Leer archivo HTML y extraer resultados
            with open(calcpad_output, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Buscar valores (esto es aproximado, necesitaria parsear mejor el HTML)
            print("\n[Calcpad] Archivo HTML generado correctamente")
            print("          Ver archivo para resultados detallados")

            calcpad_results = {"html": calcpad_output}
        else:
            print(f"[ERROR] No se genero el archivo de salida")
            calcpad_results = None

    except subprocess.TimeoutExpired:
        print(f"[ERROR] Timeout ejecutando Calcpad")
        calcpad_results = None
    except Exception as e:
        print(f"[ERROR] Error ejecutando Calcpad: {e}")
        calcpad_results = None

# ============================================================
# PARTE 2: EJECUTAR SAP2000
# ============================================================
print("\n" + "="*70)
print("PARTE 2: EJECUTAR SAP2000")
print("="*70)

try:
    import comtypes.client
    print("[OK] comtypes importado")
except:
    print("[ERROR] comtypes no esta instalado")
    print("Instalar con: pip install comtypes")
    sys.exit(1)

try:
    # Crear nueva instancia de SAP2000
    print("\nCreando instancia de SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject")
    mySapObject.ApplicationStart()
    SapModel = mySapObject.SapModel

    version = SapModel.GetVersion()
    print(f"[OK] SAP2000 Version: {version[0]}")

    # Unidades: kN, m, C
    SapModel.InitializeNewModel(6)
    SapModel.File.NewBlank()
    print("[OK] Modelo inicializado (kN, m, C)")

    # Material
    mat = "CONCRETO"
    G = E / (2 * (1 + nu))
    SapModel.PropMaterial.SetMaterial(mat, 2)  # 2 = Concrete
    SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0000099)
    print(f"[OK] Material: E={E/1000} MPa, nu={nu}")

    # Seccion shell - PLATE-THICK (Mindlin-Reissner)
    shell = "LOSA"
    # ShellType: 5 = Plate-Thick (Mindlin)
    SapModel.PropArea.SetShell_1(shell, 5, False, mat, 0.0, t, t, 0, "", "")
    print(f"[OK] Seccion: Plate-Thick (Mindlin), t={t}m")

    # Crear nodos
    print("\nCreando nodos...")
    nodo_num = 1
    nodos = {}  # {nodo_num: (x, y)}

    for i in range(n_a + 1):
        for j in range(n_b + 1):
            x = i * a_1
            y = j * b_1
            nombre = str(nodo_num)
            SapModel.PointObj.AddCartesian(x, y, 0.0, nombre)
            nodos[nodo_num] = (x, y)
            nodo_num += 1

    print(f"[OK] {len(nodos)} nodos creados")

    # Crear elementos
    print("Creando elementos...")
    elem_num = 1

    for i in range(n_a):
        for j in range(n_b):
            # Nodos del elemento (antihorario)
            j1 = j + 1 + (n_b + 1) * i
            j2 = j1 + (n_b + 1)
            j3 = j2 + 1
            j4 = j1 + 1

            pts = [str(j1), str(j2), str(j3), str(j4)]
            nombre = f"E{elem_num}"
            SapModel.AreaObj.AddByPoint(4, pts, nombre, shell, nombre)
            elem_num += 1

    print(f"[OK] {elem_num - 1} elementos creados")

    # CONDICIONES DE BORDE - CORREGIDO
    # PROBLEMA ANTERIOR: Se restringian TODOS los nodos en el borde
    # SOLUCION: Solo restringir U3 (deflexion vertical) en bordes
    print("\nAplicando condiciones de borde...")
    print("  Apoyo simple: Solo U3 restringido en bordes")

    apoyados = 0
    for nodo, (x, y) in nodos.items():
        # Verificar si esta en el borde
        en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                    abs(y) < 0.001 or abs(y - b) < 0.001)

        if en_borde:
            # Apoyo simple: SOLO U3 restringido
            # [U1, U2, U3, R1, R2, R3]
            # Para placa: liberar rotaciones, restringir solo deflexion
            SapModel.PointObj.SetRestraint(str(nodo), [False, False, True, False, False, False], 0)
            apoyados += 1

    print(f"[OK] {apoyados} nodos apoyados (solo U3 restringido)")

    # Carga uniforme
    print("\nAplicando carga...")
    for i in range(1, elem_num):
        nombre = f"E{i}"
        # Dir: 6 = Gravity direction (Z negativo)
        ret = SapModel.AreaObj.SetLoadUniform(nombre, "Dead", q, 6, True, "Global", 0)

    print(f"[OK] Carga q={q} kN/m2 aplicada")

    # Ejecutar analisis
    print("\nEjecutando analisis...")
    ret = SapModel.Analyze.RunAnalysis()
    print(f"[OK] Analisis completado (ret={ret})")

    # Extraer resultados
    print("\nExtrayendo resultados...")

    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    SapModel.Results.Setup.SetCaseSelectedForOutput("Dead")

    # Desplazamientos
    ret = SapModel.Results.JointDispl("", 2)

    max_desp = 0
    nodo_max = ""
    centro_x = a / 2
    centro_y = b / 2
    desp_centro = 0

    if ret[0] > 0:
        nombres = list(ret[2])
        U3 = list(ret[9])

        # Buscar desplazamiento maximo
        for i, nombre in enumerate(nombres):
            if abs(U3[i]) > abs(max_desp):
                max_desp = U3[i]
                nodo_max = nombre

        # Buscar desplazamiento en centro (aprox x=3, y=2)
        for i, nombre in enumerate(nombres):
            nodo_id = int(nombre)
            if nodo_id in nodos:
                x, y = nodos[nodo_id]
                if abs(x - centro_x) < 0.1 and abs(y - centro_y) < 0.1:
                    desp_centro = U3[i]
                    break

    print(f"\n[SAP2000] Desplazamiento maximo: {abs(max_desp)*1000:.4f} mm (nodo {nodo_max})")
    print(f"[SAP2000] Desplazamiento centro: {abs(desp_centro)*1000:.4f} mm")

    # Momentos flectores
    areas = [f"E{i}" for i in range(1, elem_num)]

    M11_max = 0
    M22_max = 0
    M12_max = 0

    for area in areas:
        ret = SapModel.Results.AreaForceShell(area, 0)
        if ret[0] > 0:
            M11 = list(ret[14])
            M22 = list(ret[15])
            M12 = list(ret[16])

            for m in M11:
                if abs(m) > abs(M11_max):
                    M11_max = m

            for m in M22:
                if abs(m) > abs(M22_max):
                    M22_max = m

            for m in M12:
                if abs(m) > abs(M12_max):
                    M12_max = m

    print(f"\n[SAP2000] M11 max: {abs(M11_max):.4f} kNm/m")
    print(f"[SAP2000] M22 max: {abs(M22_max):.4f} kNm/m")
    print(f"[SAP2000] M12 max: {abs(M12_max):.4f} kNm/m")

    # Guardar modelo
    ruta = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Comparacion.sdb"
    SapModel.File.Save(ruta)
    print(f"\n[OK] Modelo guardado: {ruta}")

    # Resultados SAP2000
    sap_results = {
        "desp_max": abs(max_desp) * 1000,  # mm
        "desp_centro": abs(desp_centro) * 1000,  # mm
        "M11_max": abs(M11_max),
        "M22_max": abs(M22_max),
        "M12_max": abs(M12_max)
    }

    # Preguntar si cerrar
    print("\nSAP2000 dejado abierto para inspeccion manual")
    print("Cierra SAP2000 manualmente cuando termines de revisar")

except Exception as e:
    print(f"\n[ERROR] Error en SAP2000: {e}")
    import traceback
    traceback.print_exc()
    sap_results = None

# ============================================================
# PARTE 3: COMPARACION
# ============================================================
print("\n" + "="*70)
print("PARTE 3: COMPARACION DE RESULTADOS")
print("="*70)

if sap_results:
    print("\n[SAP2000] Resultados obtenidos:")
    print(f"  Desp. maximo:  {sap_results['desp_max']:.4f} mm")
    print(f"  Desp. centro:  {sap_results['desp_centro']:.4f} mm")
    print(f"  M11 max:       {sap_results['M11_max']:.4f} kNm/m")
    print(f"  M22 max:       {sap_results['M22_max']:.4f} kNm/m")
    print(f"  M12 max:       {sap_results['M12_max']:.4f} kNm/m")

print("\n[CALCPAD] Revisar archivo HTML:")
if calcpad_results:
    print(f"  {calcpad_results['html']}")
else:
    print("  No disponible")

print("\n" + "="*70)
print("NOTAS IMPORTANTES:")
print("="*70)
print("1. Calcpad usa elementos de Kirchhoff (16 DOF, no incluye cortante)")
print("2. SAP2000 usa Shell-Thick Mindlin-Reissner (incluye cortante)")
print("3. Para placas delgadas (L/t > 20), resultados deben ser similares")
print("4. Para esta losa: a/t = 60, b/t = 40 (PLACA DELGADA)")
print("5. Se espera diferencia < 10% en desplazamientos")
print("6. CORRECCION APLICADA: Apoyos solo restringen U3, no U1/U2")
print("="*70)

print("\n[FIN]")
