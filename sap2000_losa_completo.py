# -*- coding: utf-8 -*-
"""
LOSA RECTANGULAR - MODELO COMPLETO CON VERIFICACION DE REACCIONES
================================================================
"""

import comtypes.client
import math

print("="*70)
print("LOSA RECTANGULAR - VERIFICACION COMPLETA")
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

print(f"\nDatos: {a}x{b}m, t={t}m, q={q}kN/m2, E={E/1000}MPa, nu={nu}")

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel
print(f"SAP2000 {SapModel.GetVersion()[0]}")

# Crear modelo
print("\n=== CREANDO MODELO ===")
SapModel.InitializeNewModel(6)  # kN, m, C
SapModel.File.NewBlank()

# Material
mat = "MAT"
SapModel.PropMaterial.SetMaterial(mat, 1)
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0)

# Shell-Thin
shell = "SHELL"
SapModel.PropArea.SetShell_1(shell, 1, False, mat, 0.0, t, t, 0, "", "")

# Crear nodos
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

print(f"Nodos: {len(nodos)}")

# Crear elementos
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

print(f"Elementos: {len(elementos)}")

# Restricciones
print("\n=== RESTRICCIONES ===")
n_rest = 0

for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    if en_borde:
        if abs(x) < 0.001 and abs(y) < 0.001:
            restr = [True, True, True, False, False, False]
        elif abs(x - a) < 0.001 and abs(y) < 0.001:
            restr = [False, True, True, False, False, False]
        elif abs(x) < 0.001 and abs(y - b) < 0.001:
            restr = [True, False, True, False, False, False]
        else:
            restr = [False, False, True, False, False, False]

        SapModel.PointObj.SetRestraint(str(nodo), restr)
        n_rest += 1

print(f"Nodos restringidos: {n_rest}")

# Cargas
for elem in elementos:
    SapModel.AreaObj.SetLoadUniform(elem, "DEAD", q, 6, True, "Global", 0)
print(f"Carga aplicada: {q} kN/m2")

# Guardar y analizar
ModelPath = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Losa_Completo.sdb"
SapModel.File.Save(ModelPath)
print(f"Guardado: {ModelPath}")

SapModel.Analyze.SetRunCaseFlag("", False, True)
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)
ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")

# RESULTADOS
print("\n=== RESULTADOS ===")
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

# REACCIONES - Esto nos dira si las restricciones estan funcionando
print("\n--- REACCIONES ---")
ret = SapModel.Results.JointReact("", 2)
n_reac = ret[0]
print(f"Numero de resultados de reacciones: {n_reac}")

if n_reac > 0:
    nombres = list(ret[1])
    F1 = list(ret[6])
    F2 = list(ret[7])
    F3 = list(ret[8])

    # Sumar reacciones verticales
    total_F3 = sum(F3)
    carga_total = q * a * b  # kN

    print(f"\nReacciones verticales (F3):")
    for i in range(min(5, n_reac)):
        nodo = nombres[i]
        ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
        x, y = ret_coord[0], ret_coord[1]
        print(f"  Nodo {nodo} ({x:.1f},{y:.1f}): F3 = {F3[i]:.4f} kN")

    print(f"\n  Suma total F3: {total_F3:.4f} kN")
    print(f"  Carga total aplicada: {carga_total:.4f} kN")
    print(f"  Diferencia: {abs(total_F3 - (-carga_total)):.4f} kN")
else:
    print("  NO HAY REACCIONES - Las restricciones no estan funcionando!")

# DESPLAZAMIENTOS
print("\n--- DESPLAZAMIENTOS ---")
U3_dict = {}

for nodo in nodos:
    ret = SapModel.Results.JointDispl(str(nodo), 0)
    if ret[0] > 0:
        U3_dict[nodo] = ret[9][0]

# Matriz
print(f"\nMatriz UZ (mm) [positivo=arriba, negativo=abajo]:")
print(f"{'y\\x':<6}", end="")
for i in range(n_a + 1):
    print(f"{i*a1:>8.1f}", end="")
print()

for j in range(n_b, -1, -1):
    y = j * b1
    print(f"{y:<6.1f}", end="")
    for i in range(n_a + 1):
        x = i * a1
        for nodo, (nx, ny) in nodos.items():
            if abs(nx - x) < 0.001 and abs(ny - y) < 0.001:
                uz = U3_dict.get(nodo, 0) * 1000
                print(f"{uz:>8.3f}", end="")
                break
    print()

# Centro y maximo
for nodo, (x, y) in nodos.items():
    if abs(x - a/2) < 0.01 and abs(y - b/2) < 0.01:
        print(f"\nCentro ({x},{y}): UZ = {U3_dict.get(nodo, 0)*1000:.4f} mm")

if U3_dict:
    min_nodo = min(U3_dict, key=U3_dict.get)
    max_nodo = max(U3_dict, key=U3_dict.get)
    print(f"Minimo: Nodo {min_nodo} {nodos[min_nodo]}: UZ = {U3_dict[min_nodo]*1000:.4f} mm")
    print(f"Maximo: Nodo {max_nodo} {nodos[max_nodo]}: UZ = {U3_dict[max_nodo]*1000:.4f} mm")

# Solucion analitica
print("\n=== SOLUCION ANALITICA (NAVIER) ===")
D = E * t**3 / (12 * (1 - nu**2))

def navier_w(x, y, a, b, q, D, n=100):
    w = 0.0
    for m in range(1, n, 2):
        for nn in range(1, n, 2):
            coef = 16.0 * q / (math.pi**6 * m * nn)
            denom = D * (m**2/a**2 + nn**2/b**2)**2
            w += coef / denom * math.sin(m*math.pi*x/a) * math.sin(nn*math.pi*y/b)
    return w

w_centro = navier_w(a/2, b/2, a, b, q, D)
print(f"D = {D:.2f} kNm")
print(f"w_centro (Navier) = {w_centro*1000:.4f} mm (hacia abajo = negativo)")

# DIAGNOSTICO
print("\n=== DIAGNOSTICO ===")
print("Si los desplazamientos son antisimetricos respecto a y=b/2,")
print("el modelo tiene un modo de cuerpo rigido rotacional.")
print("Esto significa que las restricciones UZ no estan funcionando")
print("correctamente en el analisis.")

# Verificar antisimetria
us_y0 = [U3_dict[n] for n, (x, y) in nodos.items() if abs(y) < 0.001]
us_yb = [U3_dict[n] for n, (x, y) in nodos.items() if abs(y - b) < 0.001]

antisimetrico = all(abs(u0 + ub) < 0.001 for u0, ub in zip(sorted(us_y0), sorted(us_yb, reverse=True)))
print(f"\nDesplazamientos antisimetricos: {antisimetrico}")

if antisimetrico:
    print("\n>>> PROBLEMA CONFIRMADO: El modelo esta rotando como cuerpo rigido.")
    print(">>> Las restricciones UZ=0 en el borde NO se estan aplicando en el analisis.")
    print(">>> Esto puede ser un bug del API o incompatibilidad de version.")

print("\n" + "="*70)
