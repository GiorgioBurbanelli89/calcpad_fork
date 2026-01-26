# -*- coding: utf-8 -*-
"""
Verificar mapeo de nodos y restricciones
========================================
"""

import comtypes.client

print("="*70)
print("VERIFICACION DE NODOS Y RESTRICCIONES")
print("="*70)

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

print(f"Archivo: {SapModel.GetModelFilename()}")

a, b = 6.0, 4.0

# Obtener todos los nodos
ret = SapModel.PointObj.GetNameList()
nodos_list = list(ret[1])
print(f"Nodos: {len(nodos_list)}")

# Mostrar todos los nodos y sus propiedades
print("\n=== TODOS LOS NODOS ===")
print(f"{'Nodo':<6} {'X':>6} {'Y':>6} {'En borde':>10} {'Restr UZ':>10} {'Restr'}")

for nodo in sorted(nodos_list, key=lambda x: int(x)):
    ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y = ret_coord[0], ret_coord[1]

    ret_restr = SapModel.PointObj.GetRestraint(nodo)
    restr = list(ret_restr[0])

    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    uz_restringido = restr[2]  # UZ es el tercer elemento

    marca_borde = "SI" if en_borde else ""
    marca_uz = "SI" if uz_restringido else "NO" if en_borde else ""

    print(f"{nodo:<6} {x:>6.1f} {y:>6.1f} {marca_borde:>10} {marca_uz:>10} {restr}")

# Contar
print("\n=== ESTADISTICAS ===")
n_borde = 0
n_uz_restringido = 0
n_borde_sin_uz = 0

for nodo in nodos_list:
    ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y = ret_coord[0], ret_coord[1]

    ret_restr = SapModel.PointObj.GetRestraint(nodo)
    restr = list(ret_restr[0])

    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    uz_restringido = restr[2]

    if en_borde:
        n_borde += 1
        if uz_restringido:
            n_uz_restringido += 1
        else:
            n_borde_sin_uz += 1
            print(f"  PROBLEMA: Nodo {nodo} ({x:.1f},{y:.1f}) en borde SIN UZ restringido")

print(f"\nNodos en borde: {n_borde}")
print(f"Nodos en borde con UZ restringido: {n_uz_restringido}")
print(f"Nodos en borde SIN UZ restringido: {n_borde_sin_uz}")

print("\n" + "="*70)
