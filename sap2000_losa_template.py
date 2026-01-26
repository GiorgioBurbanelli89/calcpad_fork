# -*- coding: utf-8 -*-
"""
LOSA RECTANGULAR - USANDO TEMPLATE SIMPLIFICADO
===============================================
Intento con un modelo minimalista para verificar que funciona.
"""

import comtypes.client
import math

print("="*70)
print("LOSA RECTANGULAR - MODELO MINIMO")
print("="*70)

# Datos
a = 6.0   # m
b = 4.0   # m
t = 0.1   # m
q = 10.0  # kN/m2
E = 35000e3  # kPa
nu = 0.15

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel
print(f"SAP2000 {SapModel.GetVersion()[0]}")

# INTENTAR USAR EL MODELO DE TEMPLATE DE LOSA
print("\n--- CREANDO MODELO DESDE TEMPLATE ---")
SapModel.InitializeNewModel()

# Intentar crear modelo de losa directamente con NewSolidBlock o similar
# Primero, nuevo modelo en blanco
ret = SapModel.File.NewBlank()
print(f"NewBlank: {ret}")

# Unidades: kN, m, C
ret = SapModel.SetPresentUnits(6)
print(f"Unidades kN,m: {ret}")

# Crear un area object directamente con 4 esquinas
# En lugar de crear nodos y luego elementos, crear todo de una vez

# AddByCoord crea el area y los nodos automaticamente
# AddByCoord(NumberPoints, X, Y, Z, Name, PropName, UserName, CSys)
X = [0.0, a, a, 0.0]
Y = [0.0, 0.0, b, b]
Z = [0.0, 0.0, 0.0, 0.0]

# Primero necesito la seccion
mat = 'CONC'
SapModel.PropMaterial.SetMaterial(mat, 2)
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0)

shell = 'LOSA'
# Tipo 1 = Shell-Thin
SapModel.PropArea.SetShell_1(shell, 1, False, mat, 0.0, t, t, 0, "", "")
print(f"Seccion Shell-Thin creada")

# Crear area
name = ""
ret = SapModel.AreaObj.AddByCoord(4, X, Y, Z, name, shell, "LOSA1")
print(f"AddByCoord: {ret}")

# Subdividir el area
# SetAutoMesh(Name, MeshType, n1, n2, MaxSize1, MaxSize2, PointOnEdgeFromLine,
#             PointOnEdgeFromPoint, ExtendCookieCutLines, Rotation, MaxSizeGeneral,
#             LocalAxesOnEdge, LocalAxesOnFace, RestraintsOnEdge, RestraintsOnFace, Group, SubMesh, SubMeshSize)
# MeshType: 1=NoMesh, 2=CookieCut, 3=MaxSize, 4=General, 5=ByNumPts
ret = SapModel.AreaObj.SetAutoMesh("LOSA1", 5, 6, 4, 0, 0, False, False, False, 0, 0,
                                   False, False, False, False, "", False, 0)
print(f"SetAutoMesh (6x4): {ret}")

# Refrescar para que se generen los elementos
SapModel.View.RefreshView(0, False)

# Obtener los puntos que se crearon
ret = SapModel.PointObj.GetNameList()
puntos = list(ret[1]) if ret[0] > 0 else []
print(f"Puntos creados: {len(puntos)}")

# APLICAR RESTRICCIONES AL PERIMETRO
print("\n--- APLICANDO RESTRICCIONES ---")
n_apoyos = 0

for punto in puntos:
    ret = SapModel.PointObj.GetCoordCartesian(punto)
    x, y, z = ret[0], ret[1], ret[2]

    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    if en_borde:
        # Apoyo simple: solo UZ=0
        # Para membrana, restringir UX, UY en un nodo para estabilidad
        if abs(x) < 0.001 and abs(y) < 0.001:
            # Esquina (0,0): UX=UY=UZ=0
            SapModel.PointObj.SetRestraint(punto, [True, True, True, False, False, False])
        elif abs(x - a) < 0.001 and abs(y) < 0.001:
            # Esquina (a,0): UY=UZ=0
            SapModel.PointObj.SetRestraint(punto, [False, True, True, False, False, False])
        elif abs(x) < 0.001 and abs(y - b) < 0.001:
            # Esquina (0,b): UX=UZ=0
            SapModel.PointObj.SetRestraint(punto, [True, False, True, False, False, False])
        else:
            # Resto del borde: solo UZ=0
            SapModel.PointObj.SetRestraint(punto, [False, False, True, False, False, False])
        n_apoyos += 1

print(f"{n_apoyos} nodos apoyados en borde")

# Aplicar carga al area original
print("\n--- APLICANDO CARGA ---")
# SetLoadUniform(Name, LoadPat, Value, Dir, Replace, CSys, ItemType)
# Dir: 6=Gravity, 3=Local Z
# ItemType: 0=Object, 1=Group, 2=SelectedObjects
ret = SapModel.AreaObj.SetLoadUniform("LOSA1", "DEAD", q, 6, True, "Global", 0)
print(f"Carga uniforme q={q}kN/m2: {ret}")

# Guardar
ModelPath = r'C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Losa_Template.sdb'
SapModel.File.Save(ModelPath)
print(f"\nGuardado: {ModelPath}")

# Analizar
print("\n--- ANALIZANDO ---")
SapModel.Analyze.SetRunCaseFlag("", False, True)
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)
ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")

if ret != 0:
    print("ERROR en analisis")
    exit(1)

# Resultados
print("\n--- RESULTADOS ---")
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

# Desplazamientos
print("\nDesplazamientos:")
U3_dict = {}

for punto in puntos:
    ret_coord = SapModel.PointObj.GetCoordCartesian(punto)
    x, y = ret_coord[0], ret_coord[1]

    ret_disp = SapModel.Results.JointDispl(punto, 0)
    if ret_disp[0] > 0:
        uz = ret_disp[9][0]
        U3_dict[(x, y)] = uz

# Ordenar y mostrar
if U3_dict:
    # Centro aproximado
    centro_disp = None
    for (x, y), uz in U3_dict.items():
        if abs(x - a/2) < 0.6 and abs(y - b/2) < 0.6:
            print(f"  Centro aprox ({x:.1f}, {y:.1f}): UZ = {uz*1000:.4f} mm")
            if centro_disp is None or abs(x - a/2) + abs(y - b/2) < abs(centro_disp[0] - a/2) + abs(centro_disp[1] - b/2):
                centro_disp = (x, y, uz)

    # Maximo
    min_pos = min(U3_dict, key=U3_dict.get)
    min_uz = U3_dict[min_pos]
    print(f"  Maximo: ({min_pos[0]:.1f}, {min_pos[1]:.1f}): UZ = {min_uz*1000:.4f} mm")

    # Solucion de Navier
    D = E * t**3 / (12 * (1 - nu**2))

    def navier_w(x, y, a, b, q, D, n=100):
        w = 0
        for m in range(1, n, 2):
            for nn in range(1, n, 2):
                amn = 16 * q / (math.pi**6 * m * nn)
                denom = D * (m**2/a**2 + nn**2/b**2)**2
                w += amn / denom * math.sin(m*math.pi*x/a) * math.sin(nn*math.pi*y/b)
        return w

    w_navier = navier_w(a/2, b/2, a, b, q, D)
    print(f"\n  Navier (analitico): {w_navier*1000:.4f} mm")

    if centro_disp:
        w_sap = abs(centro_disp[2])
        error = abs(w_sap - w_navier) / w_navier * 100 if w_navier != 0 else 0
        print(f"  Error: {error:.1f}%")

else:
    print("Sin resultados de desplazamiento")

print("\n" + "="*70)
