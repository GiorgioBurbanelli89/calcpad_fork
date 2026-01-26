# -*- coding: utf-8 -*-
"""
LOSA RECTANGULAR - COMPARACION CALCPAD vs SAP2000 (FINAL)
==========================================================
Basado en Example 7 (Python COM) de la documentacion CSI OAPI.
Replica el ejemplo "Rectangular Slab FEA.cpd" de Calcpad.
"""

import os
import comtypes.client
import numpy as np
np.set_printoptions(precision=4, suppress=True)

print("="*70)
print("LOSA RECTANGULAR - CALCPAD vs SAP2000")
print("="*70)

# ============================================================
# DATOS DEL PROBLEMA (del ejemplo Calcpad)
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

print(f"\n--- DATOS DEL PROBLEMA ---")
print(f"Losa: {a}m x {b}m, t={t}m")
print(f"Carga: q={q} kN/m2")
print(f"Material: E={E/1000} MPa, nu={nu}")
print(f"Malla: {n_a}x{n_b} elementos ({n_a*n_b} total)")
print(f"Elemento: {a_1}m x {b_1}m")

# Ruta del modelo
ModelPath = r'C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Losa_Final.sdb'

# ============================================================
# CONECTAR A SAP2000
# ============================================================
print("\n--- CONECTANDO A SAP2000 ---")
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel
print(f"SAP2000 {SapModel.GetVersion()[0]}")

# ============================================================
# CREAR MODELO
# ============================================================
print("\n--- CREANDO MODELO ---")
SapModel.InitializeNewModel()
SapModel.File.NewBlank()
SapModel.SetPresentUnits(6)  # kN, m, C
print("Modelo inicializado (kN, m, C)")

# Material
mat = 'CONC'
SapModel.PropMaterial.SetMaterial(mat, 2)
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0)
print(f"Material: E={E/1000} MPa, nu={nu}")

# Seccion Shell-Thick
shell = 'LOSA'
SapModel.PropArea.SetShell_1(shell, 2, False, mat, 0.0, t, t, 0, "", "")
print(f"Seccion Shell-Thick: t={t}m")

# ============================================================
# CREAR NODOS Y ELEMENTOS
# ============================================================
print("\n--- CREANDO MALLA ---")
nodos = {}
nodo_num = 1

for i in range(n_a + 1):
    for j in range(n_b + 1):
        x = i * a_1
        y = j * b_1
        SapModel.PointObj.AddCartesian(x, y, 0.0, str(nodo_num))
        nodos[nodo_num] = (x, y)
        nodo_num += 1

print(f"{len(nodos)} nodos")

elementos = []
elem_num = 1
for i in range(n_a):
    for j in range(n_b):
        j1 = j + 1 + (n_b + 1) * i
        j2 = j1 + (n_b + 1)
        j3 = j2 + 1
        j4 = j1 + 1
        pts = [str(j1), str(j2), str(j3), str(j4)]
        SapModel.AreaObj.AddByPoint(4, pts, f"E{elem_num}", shell, f"E{elem_num}")
        elementos.append(f"E{elem_num}")
        elem_num += 1

print(f"{len(elementos)} elementos")

# ============================================================
# RESTRICCIONES
# ============================================================
print("\n--- APLICANDO RESTRICCIONES ---")
n_apoyados = 0

for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    if en_borde:
        # Apoyo simple: UZ restringido, rotaciones libres
        SapModel.PointObj.SetRestraint(str(nodo), [True, True, True, False, False, True])
        n_apoyados += 1
    else:
        # Interior: membrana restringida
        SapModel.PointObj.SetRestraint(str(nodo), [True, True, False, False, False, True])

print(f"{n_apoyados} nodos apoyados en perimetro")

# ============================================================
# CARGAS
# ============================================================
print("\n--- APLICANDO CARGAS ---")

# Usar patron DEAD existente
for elem in elementos:
    SapModel.AreaObj.SetLoadUniform(elem, "DEAD", q, 6, True, "Global", 0)

print(f"Carga q={q} kN/m2 aplicada (dir=Gravity)")

# Refrescar vista
SapModel.View.RefreshView(0, False)

# ============================================================
# GUARDAR Y ANALIZAR
# ============================================================
print("\n--- GUARDANDO Y ANALIZANDO ---")
SapModel.File.Save(ModelPath)
print(f"Modelo guardado: {ModelPath}")

# Configurar y ejecutar analisis
SapModel.Analyze.SetRunCaseFlag("", False, True)
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)

ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")

if ret != 0:
    print("ERROR: Analisis fallo")
    exit(1)

print(f"Modelo bloqueado: {SapModel.GetModelIsLocked()}")

# ============================================================
# EXTRAER RESULTADOS
# ============================================================
print("\n--- RESULTADOS ---")

# Seleccionar caso DEAD para output
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

# Obtener desplazamientos nodo por nodo
print("\nDesplazamientos nodales:")
U3_dict = {}

for nodo in sorted(nodos.keys()):
    ret = SapModel.Results.JointDispl(str(nodo), 0)
    if ret[0] > 0:
        u3 = ret[9][0]
        U3_dict[nodo] = u3

if U3_dict:
    # Desplazamiento maximo
    min_nodo = min(U3_dict, key=U3_dict.get)
    max_nodo = max(U3_dict, key=U3_dict.get)
    min_u3 = U3_dict[min_nodo]
    max_u3 = U3_dict[max_nodo]

    print(f"  U3 min = {min_u3*1000:.4f} mm (nodo {min_nodo}, {nodos[min_nodo]})")
    print(f"  U3 max = {max_u3*1000:.4f} mm (nodo {max_nodo}, {nodos[max_nodo]})")

    # Nodo central (cerca de a/2, b/2)
    print(f"\nDesplazamiento en centro de la losa:")
    for nodo, (x, y) in nodos.items():
        if abs(x - a/2) < 0.1 and abs(y - b/2) < 0.1:
            print(f"  Nodo {nodo} ({x},{y}): U3 = {U3_dict[nodo]*1000:.4f} mm")

    # Perfil en linea central y=b/2
    print(f"\nPerfil de desplazamientos en y={b/2}m:")
    print(f"{'x (m)':<8} {'U3 (mm)':<12}")
    for nodo, (x, y) in sorted(nodos.items()):
        if abs(y - b/2) < 0.01:
            print(f"{x:<8.2f} {U3_dict.get(nodo, 0)*1000:<12.4f}")

# Momentos flectores
print("\nMomentos flectores:")
M11_all = []
M22_all = []
M12_all = []

for elem in elementos:
    ret = SapModel.Results.AreaForceShell(elem, 0)
    n = ret[0]
    if n > 0:
        M11_all.extend(list(ret[14]))
        M22_all.extend(list(ret[15]))
        M12_all.extend(list(ret[16]))

if M11_all:
    print(f"  M11: min={min(M11_all):.4f}, max={max(M11_all):.4f} kNm/m")
if M22_all:
    print(f"  M22: min={min(M22_all):.4f}, max={max(M22_all):.4f} kNm/m")
if M12_all:
    print(f"  M12: min={min(M12_all):.4f}, max={max(M12_all):.4f} kNm/m")

# Momento en elemento central
print("\nMomentos en elemento central:")
elem_central = f"E{n_a//2 * n_b + n_b//2 + 1}"
ret = SapModel.Results.AreaForceShell(elem_central, 0)
if ret[0] > 0:
    M11_centro = sum(ret[14]) / len(ret[14])
    M22_centro = sum(ret[15]) / len(ret[15])
    print(f"  {elem_central}: M11_avg={M11_centro:.4f}, M22_avg={M22_centro:.4f} kNm/m")

# ============================================================
# COMPARACION CON CALCPAD
# ============================================================
print("\n" + "="*70)
print("COMPARACION CALCPAD vs SAP2000")
print("="*70)

# Valores teoricos (solucion de Navier para placa simplemente apoyada)
D = E * t**3 / (12 * (1 - nu**2))  # rigidez a flexion

# Aproximacion Navier para el centro (primer termino)
import math
w_navier = 16 * q / (math.pi**6 * D) * (a**4 * b**4) / ((a**2 + b**2)**2)

# Momentos (aproximacion)
# Mx = -D * (d2w/dx2 + nu*d2w/dy2)
# Para carga uniforme, en el centro: Mx ~ q*b^2/8 * coef

print(f"""
VALORES DE REFERENCIA:

Rigidez a flexion D = {D:.2f} kNm

Solucion analitica (Navier, primer termino):
  w_centro ~ {w_navier*1000:.2f} mm (aproximacion)

SAP2000 (Shell-Thick, Mindlin):
  w_centro = {U3_dict.get(min_nodo, 0)*1000:.4f} mm
  M11_max = {max(M11_all):.4f} kNm/m
  M22_max = {max(M22_all):.4f} kNm/m

Para comparar con Calcpad:
- Ejecutar el archivo: Rectangular Slab FEA.cpd
- Verificar desplazamientos y momentos

NOTA: Diferencias esperadas debido a:
- Calcpad usa elemento Kirchhoff (sin deformacion por cortante)
- SAP2000 usa elemento Mindlin (incluye deformacion por cortante)
- Malla de 6x4 es relativamente gruesa
""")

print("="*70)
print("COMPLETADO")
print("="*70)
