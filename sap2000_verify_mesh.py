# -*- coding: utf-8 -*-
"""
Verificar la malla y desplazamientos del modelo actual
"""

import comtypes.client

print("="*60)
print("VERIFICACION DE MALLA Y RESULTADOS")
print("="*60)

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

# Resultados
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

# Parametros
a = 6.0
b = 4.0

# Obtener todos los nodos
ret = SapModel.PointObj.GetNameList()
nodos = list(ret[1])

# Crear diccionario de nodos
nodo_data = {}
for nodo in nodos:
    ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y, z = ret_coord[0], ret_coord[1], ret_coord[2]

    ret_restr = SapModel.PointObj.GetRestraint(nodo)
    uz_restr = ret_restr[0][2]  # UZ restringido?

    ret_disp = SapModel.Results.JointDispl(nodo, 0)
    uz = ret_disp[9][0] if ret_disp[0] > 0 else 0

    nodo_data[int(nodo)] = {'x': x, 'y': y, 'uz': uz, 'uz_restr': uz_restr}

# Mostrar matriz de desplazamientos
print("\nMatriz de desplazamientos (mm):")
print("Y\\X ", end="")
for x in [0, 1, 2, 3, 4, 5, 6]:
    print(f"{x:>8}", end="")
print()

for y in [4, 3, 2, 1, 0]:
    print(f"{y:<4}", end="")
    for x in [0, 1, 2, 3, 4, 5, 6]:
        # Buscar nodo en (x, y)
        found = False
        for nodo, data in nodo_data.items():
            if abs(data['x'] - x) < 0.01 and abs(data['y'] - y) < 0.01:
                uz_mm = data['uz'] * 1000
                marker = "*" if data['uz_restr'] else ""
                print(f"{uz_mm:>7.2f}{marker}", end="")
                found = True
                break
        if not found:
            print(f"{'--':>8}", end="")
    print()

print("\n* = UZ restringido (apoyo)")

# Verificar que el centro esta en (3, 2)
print(f"\nNodo en centro teorico (3, 2):")
for nodo, data in nodo_data.items():
    if abs(data['x'] - 3) < 0.01 and abs(data['y'] - 2) < 0.01:
        print(f"  Nodo {nodo}: x={data['x']}, y={data['y']}")
        print(f"  UZ restringido: {data['uz_restr']}")
        print(f"  UZ desplazamiento: {data['uz']*1000:.4f} mm")
        break

# El problema: todos los nodos en y=2 tienen UZ=0
# Verificar si hay algun problema con las restricciones
print(f"\nNodos en linea y={b/2}:")
for nodo, data in sorted(nodo_data.items()):
    if abs(data['y'] - b/2) < 0.01:
        print(f"  Nodo {nodo}: x={data['x']}, UZ_restr={data['uz_restr']}, UZ={data['uz']*1000:.4f}mm")

# Ver cuales nodos tienen desplazamiento significativo
print(f"\nNodos con |UZ| > 0.1mm:")
for nodo, data in sorted(nodo_data.items(), key=lambda x: abs(x[1]['uz']), reverse=True):
    if abs(data['uz']) > 0.0001:
        print(f"  Nodo {nodo}: ({data['x']}, {data['y']}), UZ={data['uz']*1000:.4f}mm, restr={data['uz_restr']}")

print()
