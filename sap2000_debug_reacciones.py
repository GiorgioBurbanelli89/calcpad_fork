# -*- coding: utf-8 -*-
"""
Debug: Ver exactamente que nodos tienen reacciones
==================================================
"""

import comtypes.client

print("="*70)
print("DEBUG: REACCIONES DETALLADAS")
print("="*70)

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

print(f"SAP2000 {SapModel.GetVersion()[0]}")
print(f"Archivo: {SapModel.GetModelFilename()}")

# Datos
a, b = 6.0, 4.0

# Obtener nodos
ret = SapModel.PointObj.GetNameList()
nodos_list = list(ret[1]) if ret[0] > 0 else []

nodos = {}
for nodo in nodos_list:
    ret = SapModel.PointObj.GetCoordCartesian(nodo)
    nodos[nodo] = (ret[0], ret[1])

# Seleccionar DEAD
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

# Clasificar nodos por borde
print("\n=== NODOS POR BORDE ===")
borde_x0 = []  # x = 0
borde_xa = []  # x = a
borde_y0 = []  # y = 0
borde_yb = []  # y = b

for nodo, (x, y) in nodos.items():
    if abs(x) < 0.001:
        borde_x0.append(nodo)
    if abs(x - a) < 0.001:
        borde_xa.append(nodo)
    if abs(y) < 0.001:
        borde_y0.append(nodo)
    if abs(y - b) < 0.001:
        borde_yb.append(nodo)

print(f"Borde x=0: {len(borde_x0)} nodos")
print(f"Borde x=a: {len(borde_xa)} nodos")
print(f"Borde y=0: {len(borde_y0)} nodos")
print(f"Borde y=b: {len(borde_yb)} nodos")

# Reacciones en cada borde
print("\n=== REACCIONES POR BORDE ===")

def sumar_reacciones(nodos_lista, nombre):
    total_F3 = 0
    n_reac = 0
    print(f"\n{nombre}:")
    for nodo in nodos_lista:
        ret = SapModel.Results.JointReact(nodo, 0)
        if ret[0] > 0:
            F3 = ret[8][0]
            x, y = nodos[nodo]
            if abs(F3) > 0.0001:
                print(f"  Nodo {nodo} ({x:.1f},{y:.1f}): F3 = {F3:.4f} kN")
                total_F3 += F3
                n_reac += 1
    print(f"  Total: {n_reac} reacciones, suma F3 = {total_F3:.4f} kN")
    return total_F3

suma_x0 = sumar_reacciones(borde_x0, "BORDE x=0")
suma_xa = sumar_reacciones(borde_xa, "BORDE x=a")
suma_y0 = sumar_reacciones(borde_y0, "BORDE y=0")
suma_yb = sumar_reacciones(borde_yb, "BORDE y=b")

print(f"\n=== RESUMEN ===")
print(f"Borde x=0: {suma_x0:.4f} kN")
print(f"Borde x=a: {suma_xa:.4f} kN")
print(f"Borde y=0: {suma_y0:.4f} kN")
print(f"Borde y=b: {suma_yb:.4f} kN")
print(f"Total: {suma_x0 + suma_xa + suma_y0 + suma_yb:.4f} kN")
print(f"Esperado: -240.0 kN")

# Verificar desplazamientos en bordes
print("\n=== DESPLAZAMIENTOS EN BORDES ===")
for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)
    if en_borde:
        ret = SapModel.Results.JointDispl(nodo, 0)
        if ret[0] > 0:
            uz = ret[9][0] * 1000
            if abs(uz) > 0.001:  # Solo mostrar si UZ != 0
                print(f"  Nodo {nodo} ({x:.1f},{y:.1f}): UZ = {uz:.4f} mm (DEBERIA SER 0)")

print("\n" + "="*70)
