# -*- coding: utf-8 -*-
"""
SAP2000 Losa Rectangular - Python.NET (OFICIAL)
Basado en Example 8 de CSI OAPI Documentation
"""
import os
import sys
import clr

print("="*70)
print("SAP2000 LOSA RECTANGULAR - PYTHON.NET")
print("="*70)

# Agregar referencias
clr.AddReference("System.Runtime.InteropServices")
from System.Runtime.InteropServices import Marshal

# Ruta a SAP2000v1.dll
sap_dll_path = R'C:\Program Files\Computers and Structures\SAP2000 24\SAP2000v1.dll'
print(f"\nCargando DLL: {sap_dll_path}")

try:
    clr.AddReference(sap_dll_path)
    print("[OK] DLL cargada")
except Exception as e:
    print(f"[ERROR] No se pudo cargar DLL: {e}")
    print("\nVERIFICA la ruta correcta a SAP2000v1.dll")
    print("Buscar con: dir \"C:\\Program Files\\Computers and Structures\" /s /b | findstr SAP2000v1.dll")
    sys.exit(1)

from SAP2000v1 import *

# ============================================================
# CONFIGURACION
# ============================================================
AttachToInstance = False  # Crear nueva instancia
SpecifyPath = False       # Usar version instalada
Remote = False

# Crear helper
helper = cHelper(Helper())

if AttachToInstance:
    try:
        mySAPObject = cOAPI(helper.GetObject("CSI.SAP2000.API.SAPObject"))
        print("[OK] Conectado a instancia existente")
    except:
        print("[ERROR] No hay instancia activa")
        sys.exit(-1)
else:
    try:
        mySAPObject = cOAPI(helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject"))
        mySAPObject.ApplicationStart()
        print("[OK] Nueva instancia de SAP2000 creada")
    except Exception as e:
        print(f"[ERROR] No se pudo crear instancia: {e}")
        sys.exit(-1)

# Crear SapModel
SapModel = cSapModel(mySAPObject.SapModel)

# Obtener version
version_array = [""]
SapModel.GetVersion(version_array)
print(f"[OK] SAP2000 Version: {version_array[0]}")

# ============================================================
# DATOS DEL PROBLEMA - Losa 6x4m (ejemplo Calcpad)
# ============================================================
a = 6.0       # dimension X (m)
b = 4.0       # dimension Y (m)
t = 0.1       # espesor (m)
q = 10.0      # carga (kN/m2)
E = 35000000  # E en kPa (35000 MPa)
nu = 0.15     # Poisson
n_a = 6       # elementos en X
n_b = 4       # elementos en Y

print("\n--- DATOS DEL PROBLEMA ---")
print(f"Losa: {a}m x {b}m, t={t}m")
print(f"Carga: q={q} kN/m2")
print(f"Material: E={E/1000} MPa, nu={nu}")
print(f"Malla: {n_a}x{n_b} = {n_a*n_b} elementos")

# ============================================================
# CREAR MODELO
# ============================================================
print("\n--- CREANDO MODELO ---")

# Inicializar modelo (kN, m, C)
SapModel.InitializeNewModel(eUnits.kN_m_C)
print("[OK] Modelo inicializado (kN, m, C)")

# Nuevo archivo
File = cFile(SapModel.File)
ret = File.NewBlank()
print("[OK] Archivo nuevo creado")

# Material
PropMaterial = cPropMaterial(SapModel.PropMaterial)
ret = PropMaterial.SetMaterial('CONC', eMatType.Concrete)
ret = PropMaterial.SetMPIsotropic('CONC', E, nu, 0.0000099)
print(f"[OK] Material CONC: E={E/1000} MPa, nu={nu}")

# Propiedad de shell (Plate-Thick = Mindlin)
PropArea = cPropArea(SapModel.PropArea)
ret = PropArea.SetShell_1('LOSA', eShellType.PlateThick, False, 'CONC',
                           0.0, t, t, -1, "", "")
print(f"[OK] Shell property LOSA: Plate-Thick, t={t}m")

# ============================================================
# GEOMETRIA - Crear nodos
# ============================================================
print("\n--- CREANDO GEOMETRIA ---")
PointObj = cPointObj(SapModel.PointObj)

dx = a / n_a
dy = b / n_b

nodos = {}  # {(i,j): nombre}
nodo_num = 1

for i in range(n_a + 1):
    for j in range(n_b + 1):
        x = i * dx
        y = j * dy
        nombre = str(nodo_num)
        ret = PointObj.AddCartesian(x, y, 0.0, nombre)
        nodos[(i, j)] = nombre
        nodo_num += 1

print(f"[OK] {len(nodos)} nodos creados")

# Crear elementos
AreaObj = cAreaObj(SapModel.AreaObj)
elem_num = 1

for i in range(n_a):
    for j in range(n_b):
        # Nodos del elemento (antihorario)
        pts = [
            nodos[(i, j)],
            nodos[(i+1, j)],
            nodos[(i+1, j+1)],
            nodos[(i, j+1)]
        ]
        nombre = f"E{elem_num}"
        user_name = nombre
        ret = AreaObj.AddByPoint(4, pts, nombre, 'LOSA', user_name)
        elem_num += 1

print(f"[OK] {elem_num - 1} elementos creados")

# ============================================================
# CONDICIONES DE BORDE - Apoyo simple
# ============================================================
print("\n--- CONDICIONES DE BORDE ---")
apoyados = 0

for (i, j), nombre in nodos.items():
    x = i * dx
    y = j * dy

    # Verificar si está en el borde
    tol = 0.001
    en_borde = (abs(x) < tol or abs(x - a) < tol or
                abs(y) < tol or abs(y - b) < tol)

    if en_borde:
        # Apoyo simple: SOLO U3 restringido
        # [U1, U2, U3, R1, R2, R3]
        restraint = [False, False, True, False, False, False]
        ret = PointObj.SetRestraint(nombre, restraint, eItemType.Objects)
        apoyados += 1

print(f"[OK] {apoyados} nodos apoyados (solo U3 restringido)")

# ============================================================
# CARGAS
# ============================================================
print("\n--- APLICANDO CARGAS ---")

# Carga uniforme en todos los elementos
for i in range(1, elem_num):
    nombre = f"E{i}"
    # Dir: 6 = Gravity (local 3, hacia abajo)
    ret = AreaObj.SetLoadUniform(nombre, "DEAD", q, 6, False, eItemType.Objects)

print(f"[OK] Carga uniforme q={q} kN/m2 aplicada a {elem_num-1} elementos")

# Refresh view
View = cView(SapModel.View)
ret = View.RefreshView(0, False)

# ============================================================
# GUARDAR MODELO ANTES DE ANALIZAR
# ============================================================
model_path = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Losa_6x4_BEFORE.sdb'
ret = File.Save(model_path)
print(f"\n[OK] Modelo guardado (BEFORE): {model_path}")

# ============================================================
# ANALISIS
# ============================================================
print("\n--- EJECUTANDO ANALISIS ---")
Analyze = cAnalyze(SapModel.Analyze)
ret = Analyze.RunAnalysis()
print(f"[OK] Analisis completado (ret={ret})")

# Guardar modelo DESPUES de analizar
model_path_after = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Losa_6x4_AFTER.sdb'
ret = File.Save(model_path_after)
print(f"[OK] Modelo guardado (AFTER): {model_path_after}")

# ============================================================
# RESULTADOS
# ============================================================
print("\n" + "="*70)
print("EXTRAYENDO RESULTADOS")
print("="*70)

Results = cAnalysisResults(SapModel.Results)
Setup = cAnalysisResultsSetup(Results.Setup)

# Seleccionar caso DEAD
ret = Setup.DeselectAllCasesAndCombosForOutput()
ret = Setup.SetCaseSelectedForOutput("DEAD")
print("\n[OK] Caso DEAD seleccionado")

# Obtener desplazamientos
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
ObjectElm = eItemTypeElm.ObjectElm

print("\nObteniendo desplazamientos de todos los nodos...")
[ret, NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3] = \
    Results.JointDispl("", ObjectElm, NumberResults, Obj, Elm, ACase, StepType, StepNum,
                       U1, U2, U3, R1, R2, R3)

print(f"[OK] {NumberResults} resultados obtenidos")

if NumberResults > 0:
    # Buscar desplazamiento maximo
    max_u3 = 0
    max_idx = 0
    for i in range(NumberResults):
        if abs(U3[i]) > abs(max_u3):
            max_u3 = U3[i]
            max_idx = i

    # Buscar desplazamiento en centro (aprox x=3, y=2)
    centro_x = a / 2
    centro_y = b / 2
    desp_centro = 0

    for i in range(NumberResults):
        nodo_nombre = Obj[i]
        # Buscar coordenadas del nodo
        x_coord = 0.0
        y_coord = 0.0
        z_coord = 0.0
        [ret_coord, x_coord, y_coord, z_coord] = PointObj.GetCoordCartesian(nodo_nombre, x_coord, y_coord, z_coord)

        if abs(x_coord - centro_x) < 0.1 and abs(y_coord - centro_y) < 0.1:
            desp_centro = U3[i]
            break

    print("\n" + "-"*70)
    print("DESPLAZAMIENTOS")
    print("-"*70)
    print(f"Desplazamiento MAXIMO:   {abs(max_u3)*1000:.4f} mm (nodo {Obj[max_idx]})")
    print(f"Desplazamiento CENTRO:   {abs(desp_centro)*1000:.4f} mm")
else:
    print("[ERROR] No hay resultados de desplazamientos")

# Obtener fuerzas en shells
print("\n" + "-"*70)
print("MOMENTOS FLECTORES")
print("-"*70)

M11_total = []
M22_total = []
M12_total = []

for i in range(1, elem_num):
    nombre = f"E{i}"

    NumberResults = 0
    Obj_area = []
    Elm_area = []
    PointElm = []
    LoadCase = []
    StepType_area = []
    StepNum_area = []
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

    [ret, NumberResults, Obj_area, Elm_area, PointElm, LoadCase, StepType_area, StepNum_area,
     F11, F22, F12, FMax, FMin, FAngle, FVM, M11, M22, M12, MMax, MMin, MAngle,
     V13, V23, VMax, VAngle] = \
        Results.AreaForceShell(nombre, ObjectElm, NumberResults, Obj_area, Elm_area, PointElm,
                               LoadCase, StepType_area, StepNum_area,
                               F11, F22, F12, FMax, FMin, FAngle, FVM,
                               M11, M22, M12, MMax, MMin, MAngle,
                               V13, V23, VMax, VAngle)

    if NumberResults > 0:
        M11_total.extend(M11)
        M22_total.extend(M22)
        M12_total.extend(M12)

if len(M11_total) > 0:
    # Calcular maximos
    M11_max = max(abs(m) for m in M11_total)
    M22_max = max(abs(m) for m in M22_total)
    M12_max = max(abs(m) for m in M12_total)

    # Calcular promedios
    M11_avg = sum(abs(m) for m in M11_total) / len(M11_total)
    M22_avg = sum(abs(m) for m in M22_total) / len(M22_total)
    M12_avg = sum(abs(m) for m in M12_total) / len(M12_total)

    print(f"M11 MAXIMO:   {M11_max:.4f} kNm/m")
    print(f"M22 MAXIMO:   {M22_max:.4f} kNm/m")
    print(f"M12 MAXIMO:   {M12_max:.4f} kNm/m")
    print(f"\nM11 PROMEDIO: {M11_avg:.4f} kNm/m")
    print(f"M22 PROMEDIO: {M22_avg:.4f} kNm/m")
    print(f"M12 PROMEDIO: {M12_avg:.4f} kNm/m")
else:
    print("[ERROR] No hay resultados de momentos")

# ============================================================
# RESUMEN FINAL
# ============================================================
print("\n" + "="*70)
print("RESUMEN - SAP2000 LOSA 6x4m")
print("="*70)

if NumberResults > 0 and len(M11_total) > 0:
    print(f"\n[SAP2000] Desplazamiento maximo:  {abs(max_u3)*1000:.4f} mm")
    print(f"[SAP2000] Desplazamiento centro:  {abs(desp_centro)*1000:.4f} mm")
    print(f"[SAP2000] M11 maximo:             {M11_max:.4f} kNm/m")
    print(f"[SAP2000] M22 maximo:             {M22_max:.4f} kNm/m")

    print("\n[CALCPAD] Valores esperados (aproximados):")
    print("          Desplazamiento centro: ~3-4 mm")
    print("          Mx centro:             ~7-8 kNm/m")
    print("          My centro:             ~5-6 kNm/m")

    print("\n[OK] COMPARACION COMPLETA")
    print(f"\nModelos guardados:")
    print(f"  BEFORE: {model_path}")
    print(f"  AFTER:  {model_path_after}")
else:
    print("\n[ERROR] No se obtuvieron resultados validos")

print("\n[OK] SAP2000 dejado abierto para revision")
print("="*70)
