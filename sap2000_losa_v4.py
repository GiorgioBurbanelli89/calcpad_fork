# -*- coding: utf-8 -*-
"""
LOSA RECTANGULAR - VERSION 4 (Corregida)
=========================================
Problema anterior: restricciones incorrectas causaban rotacion de cuerpo rigido.
Correccion: usar solo UZ restringido en bordes, sin restringir membrana en interior.
"""

import os
import comtypes.client
import numpy as np
np.set_printoptions(precision=4, suppress=True)

print("="*70)
print("LOSA RECTANGULAR - CALCPAD vs SAP2000 (v4)")
print("="*70)

# Datos del problema
a = 6.0       # dimension en X (m)
b = 4.0       # dimension en Y (m)
t = 0.1       # espesor (m)
q = 10.0      # carga (kN/m2)
E = 35000e3   # E en kPa (35000 MPa)
nu = 0.15

# Malla
n_a = 6
n_b = 4
a_1 = a / n_a
b_1 = b / n_b

print(f"\nDatos: Losa {a}x{b}m, t={t}m, q={q}kN/m2")
print(f"Material: E={E/1000}MPa, nu={nu}")
print(f"Malla: {n_a}x{n_b}")

# Conectar
print("\n--- CONECTANDO ---")
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel
print(f"SAP2000 {SapModel.GetVersion()[0]}")

# Crear modelo
print("\n--- CREANDO MODELO ---")
SapModel.InitializeNewModel()
SapModel.File.NewBlank()
SapModel.SetPresentUnits(6)  # kN, m, C

# Material
mat = 'CONC'
SapModel.PropMaterial.SetMaterial(mat, 2)
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0)

# Shell-Thick (Plate-Thick para solo flexion, sin membrana)
# ShellType: 1=Shell-Thin, 2=Shell-Thick, 3=Plate-Thin, 4=Plate-Thick
shell = 'LOSA'
SapModel.PropArea.SetShell_1(shell, 4, False, mat, 0.0, t, t, 0, "", "")
print(f"Seccion: Plate-Thick (solo flexion), t={t}m")

# Nodos
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

# Elementos
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

# Restricciones - SOLO apoyo simple en bordes (UZ=0)
# Para elemento tipo Plate, los DOF relevantes son: UZ, RX, RY
# Apoyo simple = UZ restringido, rotaciones libres
print("\n--- RESTRICCIONES ---")
n_apoyados = 0

for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    if en_borde:
        # Apoyo simple: SOLO UZ restringido
        # [UX, UY, UZ, RX, RY, RZ]
        SapModel.PointObj.SetRestraint(str(nodo), [False, False, True, False, False, False])
        n_apoyados += 1
    # Nodos interiores: sin restricciones

print(f"{n_apoyados} nodos con apoyo simple (UZ=0)")

# Carga
print("\n--- CARGA ---")
for elem in elementos:
    # Dir=6 es Gravity (Z negativo global)
    SapModel.AreaObj.SetLoadUniform(elem, "DEAD", q, 6, True, "Global", 0)
print(f"Carga q={q} kN/m2 aplicada")

# Refrescar
SapModel.View.RefreshView(0, False)

# Guardar
ModelPath = r'C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Losa_v4.sdb'
SapModel.File.Save(ModelPath)
print(f"\nModelo guardado: {ModelPath}")

# Analizar
print("\n--- ANALIZANDO ---")
SapModel.Analyze.SetRunCaseFlag("", False, True)
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)

ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")

if ret != 0:
    print("ERROR en analisis")
    # Ver log
    ret = SapModel.Analyze.GetCaseStatus()
    if ret[0] > 0:
        for i in range(ret[0]):
            print(f"  {ret[1][i]}: status={ret[2][i]}")
    exit(1)

# Resultados
print("\n--- RESULTADOS ---")
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

# Desplazamientos
U3_dict = {}
for nodo in nodos:
    ret = SapModel.Results.JointDispl(str(nodo), 0)
    if ret[0] > 0:
        U3_dict[nodo] = ret[9][0]

if U3_dict:
    min_nodo = min(U3_dict, key=U3_dict.get)
    min_u3 = U3_dict[min_nodo]

    print(f"\nDesplazamiento maximo:")
    print(f"  Nodo {min_nodo} {nodos[min_nodo]}: U3 = {min_u3*1000:.4f} mm")

    # Centro
    print(f"\nDesplazamiento en centro:")
    for nodo, (x, y) in nodos.items():
        if abs(x - a/2) < 0.1 and abs(y - b/2) < 0.1:
            print(f"  Nodo {nodo} ({x},{y}): U3 = {U3_dict[nodo]*1000:.4f} mm")

    # Perfil y=b/2
    print(f"\nPerfil en y={b/2}m:")
    print(f"{'x':<6} {'U3(mm)':<10}")
    for nodo, (x, y) in sorted(nodos.items()):
        if abs(y - b/2) < 0.01:
            print(f"{x:<6.1f} {U3_dict.get(nodo, 0)*1000:<10.4f}")

# Momentos
print("\nMomentos flectores:")
M11_all = []
M22_all = []

for elem in elementos:
    ret = SapModel.Results.AreaForceShell(elem, 0)
    if ret[0] > 0:
        M11_all.extend(list(ret[14]))
        M22_all.extend(list(ret[15]))

if M11_all:
    print(f"  M11: min={min(M11_all):.4f}, max={max(M11_all):.4f} kNm/m")
if M22_all:
    print(f"  M22: min={min(M22_all):.4f}, max={max(M22_all):.4f} kNm/m")

# Comparacion
print("\n" + "="*70)
print("COMPARACION CON SOLUCION ANALITICA")
print("="*70)

# Rigidez a flexion
D = E * t**3 / (12 * (1 - nu**2))

# Solucion de Navier (serie de Fourier) para losa simplemente apoyada
import math

def navier_displacement(x, y, a, b, q, D, n_terms=50):
    """Desplazamiento usando serie de Navier"""
    w = 0
    for m in range(1, n_terms, 2):  # solo impares
        for n in range(1, n_terms, 2):
            amn = 16 * q / (math.pi**6 * D * m * n)
            denom = (m**2/a**2 + n**2/b**2)**2
            w += amn / denom * math.sin(m*math.pi*x/a) * math.sin(n*math.pi*y/b)
    return w

w_centro_navier = navier_displacement(a/2, b/2, a, b, q, D)

print(f"\nRigidez D = {D:.2f} kNm")
print(f"\nSolucion de Navier (50 terminos):")
print(f"  w_centro = {w_centro_navier*1000:.4f} mm")

print(f"\nSAP2000 (Plate-Thick):")
centro_nodo = None
for nodo, (x, y) in nodos.items():
    if abs(x - a/2) < 0.1 and abs(y - b/2) < 0.1:
        centro_nodo = nodo
        break
if centro_nodo:
    print(f"  w_centro = {U3_dict.get(centro_nodo, 0)*1000:.4f} mm")

if centro_nodo and w_centro_navier != 0:
    error = abs(U3_dict.get(centro_nodo, 0) - w_centro_navier) / abs(w_centro_navier) * 100
    print(f"\nDiferencia: {error:.2f}%")

print("\n" + "="*70)
