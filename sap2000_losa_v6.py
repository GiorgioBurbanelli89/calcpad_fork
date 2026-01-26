# -*- coding: utf-8 -*-
"""
LOSA RECTANGULAR - VERSION 6 (Corregida)
========================================
El problema anterior: la losa rotaba alrededor del eje central.
Solucion: restringir UX e UY en TODOS los nodos para simular
una placa que solo puede moverse verticalmente (flexion pura).
"""

import os
import comtypes.client
import math
import numpy as np
np.set_printoptions(precision=4, suppress=True)

print("="*70)
print("LOSA RECTANGULAR - CALCPAD vs SAP2000 (v6)")
print("="*70)

# Datos
a = 6.0
b = 4.0
t = 0.1
q = 10.0
E = 35000e3
nu = 0.15

n_a = 6
n_b = 4
a_1 = a / n_a
b_1 = b / n_b

print(f"\nLosa: {a}x{b}m, t={t}m, q={q}kN/m2")
print(f"E={E/1000}MPa, nu={nu}, Malla {n_a}x{n_b}")

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel
print(f"SAP2000 {SapModel.GetVersion()[0]}")

# Modelo
SapModel.InitializeNewModel()
SapModel.File.NewBlank()
SapModel.SetPresentUnits(6)  # kN, m, C

# Material
mat = 'CONC'
SapModel.PropMaterial.SetMaterial(mat, 2)
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0)

# Shell-Thin (Kirchhoff)
shell = 'LOSA'
SapModel.PropArea.SetShell_1(shell, 1, False, mat, 0.0, t, t, 0, "", "")
print(f"Shell-Thin (Kirchhoff), t={t}m")

# Nodos
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

# RESTRICCIONES CORREGIDAS
# Para simular flexion pura sin efecto membrana:
# - TODOS los nodos: UX=UY=0 (evita movimiento en plano)
# - Borde: UZ=0 (apoyo simple)
# - Interior: UZ libre
# - Rotaciones: libres en todos
print("\nRestricciones:")

n_borde = 0
n_interior = 0

for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    if en_borde:
        # Borde: UX=UY=UZ=0, rotaciones libres
        SapModel.PointObj.SetRestraint(str(nodo), [True, True, True, False, False, False])
        n_borde += 1
    else:
        # Interior: UX=UY=0, UZ libre, rotaciones libres
        SapModel.PointObj.SetRestraint(str(nodo), [True, True, False, False, False, False])
        n_interior += 1

print(f"  {n_borde} nodos en borde: UX=UY=UZ=0")
print(f"  {n_interior} nodos interior: UX=UY=0, UZ libre")

# Carga uniforme en direccion Z global negativa (gravedad)
# Dir=6 es Gravity (Z negativo)
for elem in elementos:
    SapModel.AreaObj.SetLoadUniform(elem, "DEAD", q, 6, True, "Global", 0)
print(f"\nCarga: q={q}kN/m2 (Gravity)")

SapModel.View.RefreshView(0, False)

# Guardar
ModelPath = r'C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Losa_v6.sdb'
SapModel.File.Save(ModelPath)
print(f"Guardado: {ModelPath}")

# Analizar
SapModel.Analyze.SetRunCaseFlag("", False, True)
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)
ret = SapModel.Analyze.RunAnalysis()
print(f"\nRunAnalysis: {ret}")

if ret != 0:
    print("ERROR")
    exit(1)

# Resultados
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

# Desplazamientos
U3_dict = {}
for nodo in nodos:
    ret = SapModel.Results.JointDispl(str(nodo), 0)
    if ret[0] > 0:
        U3_dict[nodo] = ret[9][0]

print("\n" + "="*70)
print("RESULTADOS SAP2000")
print("="*70)

if U3_dict:
    min_nodo = min(U3_dict, key=U3_dict.get)
    min_u3 = U3_dict[min_nodo]

    print(f"\nDesplazamiento maximo:")
    print(f"  w_max = {abs(min_u3)*1000:.4f} mm en nodo {min_nodo} {nodos[min_nodo]}")

    # Centro
    print(f"\nDesplazamiento en centro:")
    for nodo, (x, y) in nodos.items():
        if abs(x - a/2) < 0.1 and abs(y - b/2) < 0.1:
            print(f"  Nodo {nodo} ({x},{y}): w = {abs(U3_dict[nodo])*1000:.4f} mm")

    # Perfil en y=b/2
    print(f"\nPerfil en y={b/2}m:")
    print(f"{'x(m)':<8}{'w(mm)':<10}")
    for nodo, (x, y) in sorted(nodos.items()):
        if abs(y - b/2) < 0.01:
            print(f"{x:<8.1f}{abs(U3_dict.get(nodo, 0))*1000:<10.4f}")

# Momentos
M11_all = []
M22_all = []
M12_all = []

for elem in elementos:
    ret = SapModel.Results.AreaForceShell(elem, 0)
    if ret[0] > 0:
        M11_all.extend(list(ret[14]))
        M22_all.extend(list(ret[15]))
        M12_all.extend(list(ret[16]))

print(f"\nMomentos flectores:")
if M11_all:
    print(f"  M11: min={min(M11_all):.4f}, max={max(M11_all):.4f} kNm/m")
if M22_all:
    print(f"  M22: min={min(M22_all):.4f}, max={max(M22_all):.4f} kNm/m")
if M12_all:
    print(f"  M12: min={min(M12_all):.4f}, max={max(M12_all):.4f} kNm/m")

# Solucion de Navier
print("\n" + "="*70)
print("SOLUCION ANALITICA (NAVIER)")
print("="*70)

D = E * t**3 / (12 * (1 - nu**2))

def navier_w(x, y, a, b, q, D, n_terms=100):
    w = 0
    for m in range(1, n_terms, 2):
        for n in range(1, n_terms, 2):
            amn = 16 * q / (math.pi**6 * m * n)
            denom = D * (m**2/a**2 + n**2/b**2)**2
            w += amn / denom * math.sin(m*math.pi*x/a) * math.sin(n*math.pi*y/b)
    return w

w_centro_navier = navier_w(a/2, b/2, a, b, q, D)
print(f"\nRigidez D = {D:.2f} kNm")
print(f"w_centro (Navier, 100 terminos) = {w_centro_navier*1000:.4f} mm")

# Momentos teoricos en el centro
# Mx = q*b^2/8 * alpha_x (para relacion a/b=1.5, alpha_x ~ 0.087)
# My = q*a^2/8 * alpha_y (para relacion a/b=1.5, alpha_y ~ 0.047)
# Estos son valores aproximados para losa rectangular simplemente apoyada

# Comparacion
print("\n" + "="*70)
print("COMPARACION")
print("="*70)

nodo_centro = None
for n, (x, y) in nodos.items():
    if abs(x - a/2) < 0.1 and abs(y - b/2) < 0.1:
        nodo_centro = n
        break

if nodo_centro and nodo_centro in U3_dict:
    w_sap = abs(U3_dict[nodo_centro])
    error = abs(w_sap - w_centro_navier) / w_centro_navier * 100 if w_centro_navier != 0 else 0

    print(f"\nDesplazamiento en centro (x={a/2}, y={b/2}):")
    print(f"  Navier (analitico): {w_centro_navier*1000:.4f} mm")
    print(f"  SAP2000 (Shell-Thin): {w_sap*1000:.4f} mm")
    print(f"  Error: {error:.2f}%")

print("\n" + "="*70)
