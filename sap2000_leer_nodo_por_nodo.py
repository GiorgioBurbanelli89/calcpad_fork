# -*- coding: utf-8 -*-
"""
Leer desplazamientos nodo por nodo
==================================
"""

import comtypes.client

print("="*70)
print("LECTURA DE DESPLAZAMIENTOS NODO POR NODO")
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

# Nodos
ret = SapModel.PointObj.GetNameList()
nodos_list = list(ret[1]) if ret[0] > 0 else []
print(f"Nodos: {len(nodos_list)}")

nodos = {}
for nodo in nodos_list:
    ret = SapModel.PointObj.GetCoordCartesian(nodo)
    nodos[nodo] = (ret[0], ret[1])

# Seleccionar DEAD
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

# Leer desplazamientos NODO POR NODO con ObjectElm=0
print("\n=== DESPLAZAMIENTOS (ObjectElm=0, elemento a elemento) ===")
U3_dict = {}
for nodo in nodos_list:
    ret = SapModel.Results.JointDispl(nodo, 0)
    if ret[0] > 0:
        U3_dict[nodo] = ret[9][0]

print(f"Nodos con resultados: {len(U3_dict)}")

if U3_dict:
    xs = sorted(set(x for x, y in nodos.values()))
    ys = sorted(set(y for x, y in nodos.values()), reverse=True)

    print(f"\nMatriz UZ (mm):")
    print(f"{'y\\x':<6}", end="")
    for x in xs:
        print(f"{x:>8.1f}", end="")
    print()

    for y in ys:
        print(f"{y:<6.1f}", end="")
        for x in xs:
            for nodo, (nx, ny) in nodos.items():
                if abs(nx - x) < 0.001 and abs(ny - y) < 0.001:
                    uz = U3_dict.get(nodo, 0) * 1000
                    print(f"{uz:>8.3f}", end="")
                    break
        print()

    print(f"\nUZ min: {min(U3_dict.values())*1000:.4f} mm")
    print(f"UZ max: {max(U3_dict.values())*1000:.4f} mm")

    # Nodo central
    for nodo, (x, y) in nodos.items():
        if abs(x - 3.0) < 0.1 and abs(y - 2.0) < 0.1:
            print(f"UZ centro (nodo {nodo}): {U3_dict.get(nodo, 0)*1000:.4f} mm")
            break

# Verificar que los nodos de borde tienen UZ=0
print("\n=== VERIFICACION NODOS DE BORDE ===")
for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)
    if en_borde:
        uz = U3_dict.get(nodo, 0)
        if abs(uz) > 0.0001:  # Si UZ no es cero
            print(f"  PROBLEMA: Nodo {nodo} ({x:.1f},{y:.1f}) tiene UZ={uz*1000:.4f} mm (deberia ser 0)")

# Reacciones nodo por nodo
print("\n=== REACCIONES (nodo por nodo) ===")
total_F3 = 0
n_reac = 0
for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)
    if en_borde:
        ret = SapModel.Results.JointReact(nodo, 0)
        if ret[0] > 0:
            F3 = ret[8][0]
            total_F3 += F3
            n_reac += 1
            if abs(F3) > 0.001:  # Solo mostrar si hay reaccion significativa
                print(f"  Nodo {nodo} ({x:.1f},{y:.1f}): F3={F3:.4f} kN")

print(f"\nTotal reacciones encontradas: {n_reac}")
print(f"Suma F3: {total_F3:.4f} kN")
print(f"Carga esperada: {-10*a*b:.4f} kN")

print("\n" + "="*70)
