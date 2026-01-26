# -*- coding: utf-8 -*-
"""
Leer resultados del modelo SAP2000 existente
"""

import comtypes.client
import math

print("="*70)
print("LECTURA DE RESULTADOS - SAP2000_AnalysisModel.sdb")
print("="*70)

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

print(f"SAP2000 {SapModel.GetVersion()[0]}")
print(f"Archivo: {SapModel.GetModelFilename()}")
print(f"Bloqueado: {SapModel.GetModelIsLocked()}")

# Datos del problema
a = 6.0
b = 4.0
t = 0.1
q = 10.0
E = 35000000
nu = 0.15

# Obtener nodos
ret = SapModel.PointObj.GetNameList()
nodos_list = list(ret[1]) if ret[0] > 0 else []
print(f"\nNodos: {len(nodos_list)}")

# Crear diccionario de coordenadas
nodos = {}
for nodo in nodos_list:
    ret = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y = ret[0], ret[1]
    nodos[nodo] = (x, y)

# Seleccionar caso DEAD
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
ret = SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")
print(f"SetCaseSelectedForOutput('DEAD'): {ret}")

# REACCIONES
print("\n=== REACCIONES ===")
ret = SapModel.Results.JointReact("", 2)
n_reac = ret[0]
print(f"Numero de reacciones: {n_reac}")

if n_reac > 0:
    nombres = list(ret[1])
    F1 = list(ret[6])
    F2 = list(ret[7])
    F3 = list(ret[8])

    print("\nReacciones F3 (vertical):")
    for i in range(n_reac):
        nodo = nombres[i]
        x, y = nodos.get(nodo, (0, 0))
        print(f"  Nodo {nodo} ({x:.1f},{y:.1f}): F3 = {F3[i]:.4f} kN")

    print(f"\n  Suma total F3: {sum(F3):.4f} kN")
    print(f"  Carga total esperada: {-q*a*b:.4f} kN")

# DESPLAZAMIENTOS
print("\n=== DESPLAZAMIENTOS ===")
U3_dict = {}

for nodo in nodos_list:
    ret = SapModel.Results.JointDispl(nodo, 0)
    if ret[0] > 0:
        U3_dict[nodo] = ret[9][0]

if U3_dict:
    # Matriz de desplazamientos
    print("\nMatriz UZ (mm):")

    # Obtener valores unicos de x e y
    xs = sorted(set(x for x, y in nodos.values()))
    ys = sorted(set(y for x, y in nodos.values()), reverse=True)

    print(f"{'y\\x':<6}", end="")
    for x in xs:
        print(f"{x:>8.1f}", end="")
    print()

    for y in ys:
        print(f"{y:<6.1f}", end="")
        for x in xs:
            # Buscar nodo en (x, y)
            for nodo, (nx, ny) in nodos.items():
                if abs(nx - x) < 0.001 and abs(ny - y) < 0.001:
                    uz = U3_dict.get(nodo, 0) * 1000
                    print(f"{uz:>8.3f}", end="")
                    break
        print()

    # Centro
    print(f"\nDesplazamiento en centro (x={a/2}, y={b/2}):")
    for nodo, (x, y) in nodos.items():
        if abs(x - a/2) < 0.1 and abs(y - b/2) < 0.1:
            print(f"  Nodo {nodo}: UZ = {U3_dict.get(nodo, 0)*1000:.4f} mm")

    # Maximo
    min_nodo = min(U3_dict, key=U3_dict.get)
    max_nodo = max(U3_dict, key=U3_dict.get)
    print(f"\nDesplazamiento minimo (max deflexion hacia abajo):")
    print(f"  Nodo {min_nodo} {nodos[min_nodo]}: UZ = {U3_dict[min_nodo]*1000:.4f} mm")

# MOMENTOS
print("\n=== MOMENTOS FLECTORES ===")
ret = SapModel.AreaObj.GetNameList()
elementos = list(ret[1]) if ret[0] > 0 else []

M11_all = []
M22_all = []
M12_all = []

for elem in elementos:
    ret = SapModel.Results.AreaForceShell(elem, 0)
    if ret[0] > 0:
        M11_all.extend(list(ret[14]))
        M22_all.extend(list(ret[15]))
        M12_all.extend(list(ret[16]))

if M11_all:
    print(f"M11: min={min(M11_all):.4f}, max={max(M11_all):.4f} kNm/m")
if M22_all:
    print(f"M22: min={min(M22_all):.4f}, max={max(M22_all):.4f} kNm/m")
if M12_all:
    print(f"M12: min={min(M12_all):.4f}, max={max(M12_all):.4f} kNm/m")

# SOLUCION ANALITICA
print("\n=== COMPARACION CON SOLUCION ANALITICA ===")
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
print(f"D = {D:.2f} kNm")
print(f"w_centro (Navier) = {w_navier*1000:.4f} mm")

# Encontrar nodo central y comparar
for nodo, (x, y) in nodos.items():
    if abs(x - a/2) < 0.1 and abs(y - b/2) < 0.1:
        w_sap = abs(U3_dict.get(nodo, 0))
        if w_navier != 0:
            error = abs(w_sap - w_navier) / w_navier * 100
            print(f"\nComparacion centro:")
            print(f"  Navier:  {w_navier*1000:.4f} mm")
            print(f"  SAP2000: {w_sap*1000:.4f} mm")
            print(f"  Error:   {error:.2f}%")
        break

print("\n" + "="*70)
