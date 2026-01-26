# -*- coding: utf-8 -*-
"""
LOSA RECTANGULAR - USANDO TEMPLATE DE GRID
==========================================
Usar la funcion NewGridOnly para crear la geometria automaticamente.
"""

import comtypes.client
import math

print("="*70)
print("LOSA RECTANGULAR - GRID TEMPLATE")
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

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel
print(f"SAP2000 {SapModel.GetVersion()[0]}")

# Modelo con grid
print("\n--- NUEVO MODELO CON GRID ---")
SapModel.InitializeNewModel(6)

# NewGridOnly(NumberStorys, TypicalStoryHeight, BottomStoryHeight,
#             NumberLinesX, NumberLinesY, SpacingX, SpacingY)
ret = SapModel.File.NewGridOnly(1, 0, 0, n_a+1, n_b+1, a/n_a, b/n_b)
print(f"NewGridOnly: {ret}")

# Material
mat = "MAT"
SapModel.PropMaterial.SetMaterial(mat, 1)
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0)

# Shell
shell = "SHELL"
SapModel.PropArea.SetShell_1(shell, 1, False, mat, 0.0, t, t, 0, "", "")

# Ver nodos existentes
ret = SapModel.PointObj.GetNameList()
nodos = list(ret[1]) if ret[0] > 0 else []
print(f"\nNodos existentes: {len(nodos)}")

if not nodos:
    print("No hay nodos. Creandolos manualmente...")

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

    print(f"  {len(nodos)} nodos creados")

# Crear elementos
print("\n--- CREANDO ELEMENTOS ---")
a1 = a / n_a
b1 = b / n_b

# Primero crear diccionario de nodos
ret = SapModel.PointObj.GetNameList()
nodo_list = list(ret[1]) if ret[0] > 0 else []

nodo_coords = {}
for nodo in nodo_list:
    ret = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y = ret[0], ret[1]
    nodo_coords[(round(x, 3), round(y, 3))] = nodo

elementos = []
elem_id = 1

for i in range(n_a):
    for j in range(n_b):
        x1, y1 = i * a1, j * b1
        x2, y2 = (i+1) * a1, j * b1
        x3, y3 = (i+1) * a1, (j+1) * b1
        x4, y4 = i * a1, (j+1) * b1

        # Encontrar nodos por coordenadas
        n1 = nodo_coords.get((round(x1, 3), round(y1, 3)))
        n2 = nodo_coords.get((round(x2, 3), round(y2, 3)))
        n3 = nodo_coords.get((round(x3, 3), round(y3, 3)))
        n4 = nodo_coords.get((round(x4, 3), round(y4, 3)))

        if n1 and n2 and n3 and n4:
            pts = [n1, n2, n3, n4]
            name = f"E{elem_id}"
            ret = SapModel.AreaObj.AddByPoint(4, pts, name, shell, name)
            elementos.append(name)
        elem_id += 1

print(f"{len(elementos)} elementos creados")

# Restricciones - INTENTAR CON BODY CONSTRAINT
print("\n--- RESTRICCIONES ---")

# Primero, crear las restricciones normales
n_rest = 0
for nodo in nodo_list:
    ret = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y = ret[0], ret[1]

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

        ret = SapModel.PointObj.SetRestraint(nodo, restr)
        n_rest += 1

        # Verificar inmediatamente
        ret_check = SapModel.PointObj.GetRestraint(nodo)
        if list(ret_check[0]) != restr:
            print(f"  WARN: Nodo {nodo} - no se aplico correctamente")

print(f"{n_rest} restricciones aplicadas")

# Cargas
for elem in elementos:
    SapModel.AreaObj.SetLoadUniform(elem, "DEAD", q, 6, True, "Global", 0)
print(f"Carga: {q} kN/m2")

# Guardar
ModelPath = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Losa_Grid.sdb"
SapModel.File.Save(ModelPath)

# Analizar
SapModel.Analyze.SetRunCaseFlag("", False, True)
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)
ret = SapModel.Analyze.RunAnalysis()
print(f"\nRunAnalysis: {ret}")

# Resultados
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

print("\nResultados:")
U3_dict = {}
for nodo in nodo_list:
    ret = SapModel.Results.JointDispl(nodo, 0)
    if ret[0] > 0:
        ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
        x, y = ret_coord[0], ret_coord[1]
        U3_dict[(x, y, nodo)] = ret[9][0]

# Mostrar perfil en y=b/2
print(f"\nPerfil en y={b/2}m:")
for (x, y, nodo), uz in sorted(U3_dict.items()):
    if abs(y - b/2) < 0.01:
        print(f"  x={x:.1f}: UZ = {uz*1000:.4f} mm")

# Centro
for (x, y, nodo), uz in U3_dict.items():
    if abs(x - a/2) < 0.1 and abs(y - b/2) < 0.1:
        print(f"\nCentro: UZ = {uz*1000:.4f} mm")

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

print(f"Navier: {navier_w(a/2, b/2, a, b, q, D)*1000:.4f} mm")

print()
