# -*- coding: utf-8 -*-
"""
LOSA RECTANGULAR - USANDO SPRINGS EN VEZ DE RESTRAINTS
======================================================
Intento alternativo usando resortes muy rigidos en lugar de restricciones.
"""

import comtypes.client
import math

print("="*70)
print("LOSA RECTANGULAR - CON SPRINGS")
print("="*70)

# Datos
a = 6.0
b = 4.0
t = 0.1
q = 10.0
E = 35000000  # kPa
nu = 0.15

n_a = 6
n_b = 4

print(f"Losa: {a}x{b}m, t={t}m, q={q}kN/m2")

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel
print(f"SAP2000 {SapModel.GetVersion()[0]}")

# Modelo
SapModel.InitializeNewModel(6)
SapModel.File.NewBlank()

# Material
mat = "MAT"
SapModel.PropMaterial.SetMaterial(mat, 1)
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0)

# Shell
shell = "SHELL"
SapModel.PropArea.SetShell_1(shell, 1, False, mat, 0.0, t, t, 0, "", "")

# Nodos
a1 = a / n_a
b1 = b / n_b
nodos = {}
nodo_id = 1

for i in range(n_a + 1):
    for j in range(n_b + 1):
        x = i * a1
        y = j * b1
        SapModel.PointObj.AddCartesian(x, y, 0.0, str(nodo_id))
        nodos[nodo_id] = (x, y)
        nodo_id += 1

print(f"{len(nodos)} nodos")

# Elementos
elementos = []
elem_id = 1
for i in range(n_a):
    for j in range(n_b):
        n1 = j + 1 + (n_b + 1) * i
        n2 = n1 + (n_b + 1)
        n3 = n2 + 1
        n4 = n1 + 1
        pts = [str(n1), str(n2), str(n3), str(n4)]
        name = f"E{elem_id}"
        SapModel.AreaObj.AddByPoint(4, pts, name, shell, name)
        elementos.append(name)
        elem_id += 1

print(f"{len(elementos)} elementos")

# RESTRICCIONES CON SPRINGS
# En lugar de SetRestraint, usar SetSpring con rigidez muy alta
print("\n--- RESTRICCIONES ---")

K_high = 1e12  # rigidez muy alta (kN/m)
K_spring = [K_high, K_high, K_high, 0, 0, 0]  # k1, k2, k3, k4, k5, k6

n_springs = 0

for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    if en_borde:
        # Aplicar spring vertical muy rigido
        # SetSpring(Name, k) donde k es array de 6 rigideces
        if abs(x) < 0.001 and abs(y) < 0.001:
            # Esquina (0,0): fijar todo
            k = [K_high, K_high, K_high, 0, 0, 0]
        elif abs(x - a) < 0.001 and abs(y) < 0.001:
            # Esquina (a,0): fijar Y, Z
            k = [0, K_high, K_high, 0, 0, 0]
        elif abs(x) < 0.001 and abs(y - b) < 0.001:
            # Esquina (0,b): fijar X, Z
            k = [K_high, 0, K_high, 0, 0, 0]
        else:
            # Resto del borde: solo Z
            k = [0, 0, K_high, 0, 0, 0]

        ret = SapModel.PointObj.SetSpring(str(nodo), k, 0, False, "")
        n_springs += 1

print(f"{n_springs} springs aplicados")

# Verificar
ret = SapModel.PointObj.GetSpring("1")
print(f"Spring nodo 1: {ret}")

# Cargas
for elem in elementos:
    SapModel.AreaObj.SetLoadUniform(elem, "DEAD", q, 6, True, "Global", 0)
print(f"Carga: {q} kN/m2")

# Guardar y analizar
ModelPath = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Losa_Springs.sdb"
SapModel.File.Save(ModelPath)

SapModel.Analyze.SetRunCaseFlag("", False, True)
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)
ret = SapModel.Analyze.RunAnalysis()
print(f"\nRunAnalysis: {ret}")

# Resultados
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

print("\nResultados:")
U3_dict = {}
for nodo in nodos:
    ret = SapModel.Results.JointDispl(str(nodo), 0)
    if ret[0] > 0:
        U3_dict[nodo] = ret[9][0]

# Centro
for nodo, (x, y) in nodos.items():
    if abs(x - a/2) < 0.01 and abs(y - b/2) < 0.01:
        print(f"  Centro: UZ = {U3_dict.get(nodo, 0)*1000:.4f} mm")
        break

# Maximo
if U3_dict:
    min_nodo = min(U3_dict, key=U3_dict.get)
    print(f"  Maximo: UZ = {U3_dict[min_nodo]*1000:.4f} mm")

# Verificar borde
print("\nBorde y=0:")
for nodo, (x, y) in sorted(nodos.items()):
    if abs(y) < 0.001:
        print(f"  x={x}: UZ = {U3_dict.get(nodo, 0)*1000:.6f} mm")

# Navier
D = E * t**3 / (12 * (1 - nu**2))
def navier_w(x, y, a, b, q, D, n=100):
    w = 0.0
    for m in range(1, n, 2):
        for nn in range(1, n, 2):
            coef = 16.0 * q / (math.pi**6 * m * nn)
            denom = D * (m**2/a**2 + nn**2/b**2)**2
            w += coef / denom * math.sin(m*math.pi*x/a) * math.sin(nn*math.pi*y/b)
    return w

w_navier = navier_w(a/2, b/2, a, b, q, D)
print(f"\nNavier: {w_navier*1000:.4f} mm")

print()
