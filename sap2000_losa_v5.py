# -*- coding: utf-8 -*-
"""
LOSA RECTANGULAR - VERSION 5
============================
Usando Shell-Thin y carga en direccion Z local negativa.
Aplicando restricciones correctas para estabilidad.
"""

import os
import comtypes.client
import numpy as np
import math
np.set_printoptions(precision=4, suppress=True)

print("="*70)
print("LOSA RECTANGULAR - CALCPAD vs SAP2000 (v5)")
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
SapModel.SetPresentUnits(6)

# Material
mat = 'CONC'
SapModel.PropMaterial.SetMaterial(mat, 2)
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0)

# Shell-Thin (tipo Kirchhoff, como Calcpad)
shell = 'LOSA'
# ShellType: 1=Shell-Thin, 2=Shell-Thick
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

# Restricciones
# Para Shell element en plano XY:
# - Bordes: apoyo simple = UZ restringido
# - Para estabilidad: necesitamos al menos 3 nodos con UX,UY restringidos
#   para evitar movimiento de cuerpo rigido en plano
print("\nRestricciones:")

# Nodo esquina (0,0): restringir UX, UY, UZ
SapModel.PointObj.SetRestraint("1", [True, True, True, False, False, False])
print("  Nodo 1 (0,0): UX=UY=UZ=0")

# Nodo esquina (a,0): restringir UY, UZ (permite expansion termica en X)
nodo_a0 = (n_b + 1) * n_a + 1  # Ultimo en y=0
# Encontrar nodo en (a, 0)
for n, (x, y) in nodos.items():
    if abs(x - a) < 0.001 and abs(y) < 0.001:
        SapModel.PointObj.SetRestraint(str(n), [False, True, True, False, False, False])
        print(f"  Nodo {n} ({x},{y}): UY=UZ=0")
        break

# Nodo esquina (0,b): restringir UX, UZ (permite expansion termica en Y)
for n, (x, y) in nodos.items():
    if abs(x) < 0.001 and abs(y - b) < 0.001:
        SapModel.PointObj.SetRestraint(str(n), [True, False, True, False, False, False])
        print(f"  Nodo {n} ({x},{y}): UX=UZ=0")
        break

# Resto de nodos en borde: solo UZ restringido
n_apoyos = 3
for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)
    # Ya procesamos las esquinas especiales
    es_esquina = ((abs(x) < 0.001 and abs(y) < 0.001) or
                  (abs(x - a) < 0.001 and abs(y) < 0.001) or
                  (abs(x) < 0.001 and abs(y - b) < 0.001))

    if en_borde and not es_esquina:
        SapModel.PointObj.SetRestraint(str(nodo), [False, False, True, False, False, False])
        n_apoyos += 1

print(f"  {n_apoyos} nodos con UZ=0 en perimetro")

# Carga uniforme
# Dir=3 es local Z, Dir=6 es Gravity
# Usar valor negativo para que vaya hacia abajo
for elem in elementos:
    SapModel.AreaObj.SetLoadUniform(elem, "DEAD", -q, 3, True, "Local", 0)
print(f"\nCarga: q={q}kN/m2 (Z local negativo)")

SapModel.View.RefreshView(0, False)

# Guardar
ModelPath = r'C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Losa_v5.sdb'
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

U3_dict = {}
for nodo in nodos:
    ret = SapModel.Results.JointDispl(str(nodo), 0)
    if ret[0] > 0:
        U3_dict[nodo] = ret[9][0]

print("\n--- RESULTADOS SAP2000 ---")

if U3_dict:
    # Encontrar maximo (mas negativo = mas hacia abajo)
    min_nodo = min(U3_dict, key=U3_dict.get)
    min_u3 = U3_dict[min_nodo]

    print(f"\nDesplazamiento maximo:")
    print(f"  w_max = {abs(min_u3)*1000:.4f} mm en nodo {min_nodo} {nodos[min_nodo]}")

    # Centro
    print(f"\nEn centro de la losa:")
    for nodo, (x, y) in nodos.items():
        if abs(x - a/2) < 0.1 and abs(y - b/2) < 0.1:
            print(f"  Nodo {nodo} ({x},{y}): w = {abs(U3_dict[nodo])*1000:.4f} mm")

    # Perfil
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

# Solucion analitica (Navier)
print("\n--- SOLUCION ANALITICA (Navier) ---")
D = E * t**3 / (12 * (1 - nu**2))

def navier_w(x, y, a, b, q, D, n_terms=100):
    w = 0
    for m in range(1, n_terms, 2):
        for n in range(1, n_terms, 2):
            amn = 16 * q / (math.pi**6 * m * n)
            denom = D * (m**2/a**2 + n**2/b**2)**2
            w += amn / denom * math.sin(m*math.pi*x/a) * math.sin(n*math.pi*y/b)
    return w

w_centro = navier_w(a/2, b/2, a, b, q, D)
print(f"D = {D:.2f} kNm")
print(f"w_centro (Navier) = {w_centro*1000:.4f} mm")

# Momento en centro (aproximacion)
# Mx = q*b^2/8 * coef (para losa cuadrada coef~0.0479)
# My = q*a^2/8 * coef

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
    error = abs(w_sap - w_centro) / w_centro * 100 if w_centro != 0 else 0
    print(f"\nDesplazamiento en centro:")
    print(f"  Navier:  {w_centro*1000:.4f} mm")
    print(f"  SAP2000: {w_sap*1000:.4f} mm")
    print(f"  Error:   {error:.2f}%")

print("\n" + "="*70)
