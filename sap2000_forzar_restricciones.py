# -*- coding: utf-8 -*-
"""
Forzar restricciones - Intentar diferentes metodos
==================================================
"""

import comtypes.client
import math
import time

print("="*70)
print("FORZAR RESTRICCIONES EN MODELO")
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

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

print(f"SAP2000 {SapModel.GetVersion()[0]}")

# Nuevo modelo
SapModel.InitializeNewModel(6)
SapModel.File.NewBlank()

# Material
mat = "MAT"
SapModel.PropMaterial.SetMaterial(mat, 1)
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0)

# Seccion - Plate-Thin (Kirchhoff)
shell = "SHELL"
SapModel.PropArea.SetShell_1(shell, 3, False, mat, 0.0, t, t, 0, "", "")
print("Seccion: Plate-Thin (tipo 3)")

# Nodos
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

# Elementos
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

# RESTRICCIONES - Usar diferentes metodos
print("\n=== METODO 1: SetRestraint normal ===")
nodos_borde = []

for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    if en_borde:
        nodos_borde.append(nodo)
        esquina_00 = abs(x) < 0.001 and abs(y) < 0.001
        esquina_a0 = abs(x - a) < 0.001 and abs(y) < 0.001
        esquina_0b = abs(x) < 0.001 and abs(y - b) < 0.001

        if esquina_00:
            restr = [True, True, True, False, False, False]
        elif esquina_a0:
            restr = [False, True, True, False, False, False]
        elif esquina_0b:
            restr = [True, False, True, False, False, False]
        else:
            restr = [False, False, True, False, False, False]

        # Metodo 1: SetRestraint normal
        SapModel.PointObj.SetRestraint(str(nodo), restr)

print(f"Restricciones aplicadas: {len(nodos_borde)}")

# Cargas
for elem in elementos:
    SapModel.AreaObj.SetLoadUniform(elem, "DEAD", q, 6, True, "Global", 0)

# Guardar
ModelPath = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Forzar.sdb"
SapModel.File.Save(ModelPath)

# Refrescar
SapModel.View.RefreshView(0, False)

# Crear modelo de analisis ANTES de correr
print("\n=== CREAR MODELO DE ANALISIS ===")
ret = SapModel.Analyze.CreateAnalysisModel()
print(f"CreateAnalysisModel: {ret}")

# Verificar restricciones en modelo de analisis
print("\n=== VERIFICAR EN MODELO DE ANALISIS ===")
try:
    ret = SapModel.PointElm.CountRestraint()
    print(f"PointElm.CountRestraint: {ret}")
except Exception as e:
    print(f"Error: {e}")

# Ahora intentar obtener info de un nodo de analisis
try:
    ret = SapModel.PointElm.GetNameList()
    print(f"Point Elements: {ret[0]}")

    # Ver restricciones de algunos elementos
    if ret[0] > 0:
        elms = list(ret[1])
        print("\nRestricciones en elementos de analisis:")
        for elm in elms[:5]:
            ret_r = SapModel.PointElm.GetRestraint(elm)
            print(f"  {elm}: {list(ret_r[0])}")
except Exception as e:
    print(f"Error: {e}")

# Analizar
print("\n=== ANALIZAR ===")
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
for nodo, (x, y) in nodos.items():
    if abs(x - a/2) < 0.1 and abs(y - b/2) < 0.1:
        print(f"\nCentro ({nodo}): UZ = {U3_dict.get(nodo, 0)*1000:.4f} mm")
        w_sap = abs(U3_dict.get(nodo, 0))
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
print(f"Navier: {w_navier*1000:.4f} mm")
print(f"SAP2000: {w_sap*1000:.4f} mm")

print("\n" + "="*70)
