# -*- coding: utf-8 -*-
"""
Modelo de losa usando Link Elements como apoyos
===============================================
Los Link elements permiten definir rigidez directamente.
"""

import comtypes.client
import math

print("="*70)
print("LOSA RECTANGULAR - APOYOS CON LINKS")
print("="*70)

# Datos
a = 6.0
b = 4.0
t = 0.1
q = 10.0
E = 35000000
nu = 0.15
n_a = 6
n_b = 4

print(f"Losa: {a}m x {b}m, t={t}m")
print(f"Carga: {q} kN/m2")

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

print(f"\nSAP2000 {SapModel.GetVersion()[0]}")

# Nuevo modelo
SapModel.InitializeNewModel(6)
SapModel.File.NewBlank()

# Material
mat = "MAT"
SapModel.PropMaterial.SetMaterial(mat, 1)
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0)

# Seccion Shell
shell = "SHELL"
SapModel.PropArea.SetShell_1(shell, 3, False, mat, 0.0, t, t, 0, "", "")

# Propiedad Link - Linear con alta rigidez en direccion vertical
link_prop = "APOYO_LINK"
# SetLinear(Name, DOF, Fixed, Ke, Ce, dj2, dj3, Notes, GUID)
# DOF: array de 6 booleanos [U1, U2, U3, R1, R2, R3]
# Fixed: array de 6 booleanos (si True, rigidez infinita)
# Ke: array de 6 valores de rigidez
DOF = [False, False, True, False, False, False]  # Solo U3 activo
Fixed = [False, False, True, False, False, False]  # U3 fijo (rigidez infinita)
Ke = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # No importa si Fixed=True
Ce = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # Sin amortiguamiento

ret = SapModel.PropLink.SetLinear(link_prop, DOF, Fixed, Ke, Ce, 0.0, 0.0, "", "")
print(f"SetLinear para link: {ret}")

# Crear nodos
print("\n=== CREANDO MODELO ===")
a1 = a / n_a
b1 = b / n_b
nodos = {}
nodo_id = 1

for i in range(n_a + 1):
    for j in range(n_b + 1):
        x = i * a1
        y = j * b1
        name = str(nodo_id)
        SapModel.PointObj.AddCartesian(x, y, 0.0, name)
        nodos[nodo_id] = (x, y)
        nodo_id += 1

print(f"Nodos: {len(nodos)}")

# Crear elementos
elementos = []
for i in range(n_a):
    for j in range(n_b):
        n1 = j + 1 + (n_b + 1) * i
        n2 = n1 + (n_b + 1)
        n3 = n2 + 1
        n4 = n1 + 1
        pts = [str(n1), str(n2), str(n3), str(n4)]
        name = f"E{len(elementos)+1}"
        SapModel.AreaObj.AddByPoint(4, pts, name, shell, name)
        elementos.append(name)

print(f"Elementos: {len(elementos)}")

# Crear links como apoyos puntuales (grounded springs)
print("\n=== CREANDO APOYOS CON LINKS ===")
nodos_borde = []

for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    if en_borde:
        nodos_borde.append(nodo)

        # Para evitar movimiento de cuerpo rigido, fijar esquinas
        esquina_00 = abs(x) < 0.001 and abs(y) < 0.001
        esquina_a0 = abs(x - a) < 0.001 and abs(y) < 0.001
        esquina_0b = abs(x) < 0.001 and abs(y - b) < 0.001

        if esquina_00:
            restr = [True, True, True, False, False, False]
            SapModel.PointObj.SetRestraint(str(nodo), restr)
        elif esquina_a0:
            restr = [False, True, True, False, False, False]
            SapModel.PointObj.SetRestraint(str(nodo), restr)
        elif esquina_0b:
            restr = [True, False, True, False, False, False]
            SapModel.PointObj.SetRestraint(str(nodo), restr)
        else:
            # Para los demas nodos, usar springs muy rigidos
            K_rigid = 1e12
            springs = [0.0, 0.0, K_rigid, 0.0, 0.0, 0.0]
            ret = SapModel.PointObj.SetSpring(str(nodo), springs)

print(f"Nodos de borde: {len(nodos_borde)}")

# Cargas
print("\n=== CARGAS ===")
for elem in elementos:
    SapModel.AreaObj.SetLoadUniform(elem, "DEAD", q, 6, True, "Global", 0)

# Guardar
ModelPath = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_LosaLinks.sdb"
SapModel.File.Save(ModelPath)
print(f"Guardado: {ModelPath}")

# Analizar
print("\n=== ANALIZANDO ===")
SapModel.Analyze.SetRunCaseFlag("", False, True)
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)
ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")
print(f"Bloqueado: {SapModel.GetModelIsLocked()}")

# Resultados
print("\n=== RESULTADOS ===")
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

U3_dict = {}
for nodo in nodos:
    ret = SapModel.Results.JointDispl(str(nodo), 0)
    if ret[0] > 0:
        U3_dict[nodo] = ret[9][0]

# Matriz
print(f"\nMatriz UZ (mm):")
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

# Centro
w_sap = 0
for nodo, (x, y) in nodos.items():
    if abs(x - a/2) < 0.1 and abs(y - b/2) < 0.1:
        w_sap = abs(U3_dict.get(nodo, 0))
        print(f"\nCentro ({nodo}): UZ = {-U3_dict.get(nodo, 0)*1000:.4f} mm")
        break

# Reacciones
print("\n=== REACCIONES ===")
total_F3 = 0
for nodo in nodos_borde:
    ret = SapModel.Results.JointReact(str(nodo), 0)
    if ret[0] > 0:
        total_F3 += ret[8][0]

print(f"Suma F3: {total_F3:.4f} kN (esperado: {-q*a*b:.0f} kN)")

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
print(f"\n=== COMPARACION ===")
print(f"w_centro (Navier): {w_navier*1000:.4f} mm")
print(f"w_centro (SAP2000): {w_sap*1000:.4f} mm")

if w_navier != 0 and w_sap != 0:
    error = abs(w_sap - w_navier) / w_navier * 100
    print(f"Error: {error:.2f}%")

print("\n" + "="*70)
