# -*- coding: utf-8 -*-
"""
Verificar restricciones en el modelo de analisis
===============================================
"""

import comtypes.client
import math

print("="*70)
print("VERIFICACION DE RESTRICCIONES EN MODELO DE ANALISIS")
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

# Crear modelo
print("\n=== CREANDO MODELO ===")
SapModel.InitializeNewModel(6)
SapModel.File.NewBlank()

# Material y seccion
mat = "MAT"
SapModel.PropMaterial.SetMaterial(mat, 1)
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0)

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

print(f"Nodos: {len(nodos)}")

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

print(f"Elementos: {len(elementos)}")

# Restricciones
print("\n=== APLICANDO RESTRICCIONES ===")
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

        ret = SapModel.PointObj.SetRestraint(str(nodo), restr)
        n_rest += 1

print(f"Nodos restringidos: {n_rest}")

# Verificar restricciones en MODELO DE OBJETOS
print("\nRestricciones en MODELO DE OBJETOS:")
for nodo in [1, 6, 18]:
    ret = SapModel.PointObj.GetRestraint(str(nodo))
    restr = list(ret[0])
    x, y = nodos[nodo]
    print(f"  Nodo {nodo} ({x},{y}): {restr}")

# Cargas
for elem in elementos:
    SapModel.AreaObj.SetLoadUniform(elem, "DEAD", q, 6, True, "Global", 0)
print(f"\nCarga: {q} kN/m2")

# Guardar
ModelPath = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_AnalysisModel.sdb"
SapModel.File.Save(ModelPath)
print(f"Guardado: {ModelPath}")

# Crear modelo de analisis EXPLICITAMENTE
print("\n=== CREANDO MODELO DE ANALISIS ===")
ret = SapModel.Analyze.CreateAnalysisModel()
print(f"CreateAnalysisModel: {ret}")

# Verificar restricciones en MODELO DE ANALISIS
print("\nRestricciones en MODELO DE ANALISIS:")
try:
    # Obtener elementos de analisis (punto)
    ret = SapModel.PointElm.GetNameList()
    print(f"Elementos de punto en modelo de analisis: {ret[0]}")

    if ret[0] > 0:
        point_elms = list(ret[1])
        for elm in point_elms[:5]:
            ret_restr = SapModel.PointElm.GetRestraint(elm)
            print(f"  {elm}: {list(ret_restr[0])}")
except Exception as e:
    print(f"  Error: {e}")

# Intentar ver CountRestraint
print("\nConteo de restricciones:")
try:
    ret = SapModel.PointElm.CountRestraint()
    print(f"  PointElm.CountRestraint: {ret}")
except Exception as e:
    print(f"  Error: {e}")

# Analizar
print("\n=== ANALIZANDO ===")
SapModel.Analyze.SetRunCaseFlag("", False, True)
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)
ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")

# Reacciones
print("\n=== REACCIONES ===")
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

ret = SapModel.Results.JointReact("", 2)
print(f"Numero de reacciones: {ret[0]}")

if ret[0] > 0:
    nombres = list(ret[1])
    F3 = list(ret[8])
    print("\nReacciones F3:")
    for i in range(min(5, ret[0])):
        print(f"  {nombres[i]}: F3 = {F3[i]:.4f} kN")
    print(f"\n  Total F3: {sum(F3):.4f} kN")
    print(f"  Carga total: {q*a*b:.4f} kN")
else:
    print("  NO HAY REACCIONES")

# Desplazamientos clave
print("\n=== DESPLAZAMIENTOS ===")
for nodo in [1, 6, 16, 18]:
    ret = SapModel.Results.JointDispl(str(nodo), 0)
    if ret[0] > 0:
        x, y = nodos[nodo]
        uz = ret[9][0]
        print(f"  Nodo {nodo} ({x},{y}): UZ = {uz*1000:.4f} mm")

print()
