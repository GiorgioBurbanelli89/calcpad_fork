# -*- coding: utf-8 -*-
"""
Investigar casos de carga y resultados en SAP2000
=================================================
"""

import comtypes.client

print("="*70)
print("INVESTIGACION DE CASOS DE CARGA Y RESULTADOS")
print("="*70)

# Conectar a SAP2000 existente
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

print(f"SAP2000 {SapModel.GetVersion()[0]}")
print(f"Archivo: {SapModel.GetModelFilename()}")
print(f"Modelo bloqueado: {SapModel.GetModelIsLocked()}")

# Datos del problema
a, b = 6.0, 4.0

# Obtener lista de nodos
ret = SapModel.PointObj.GetNameList()
nodos_list = list(ret[1]) if ret[0] > 0 else []
print(f"\nNodos: {len(nodos_list)}")

# Crear diccionario de coordenadas
nodos = {}
for nodo in nodos_list:
    ret = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y = ret[0], ret[1]
    nodos[nodo] = (x, y)

# Encontrar nodo central
nodo_centro = None
for nodo, (x, y) in nodos.items():
    if abs(x - 3.0) < 0.5 and abs(y - 2.0) < 0.5:
        nodo_centro = nodo
        print(f"Nodo central: {nodo} en ({x}, {y})")
        break

# Verificar restricciones en esquinas
print("\n=== RESTRICCIONES EN ESQUINAS ===")
esquinas = []
for nodo, (x, y) in nodos.items():
    es_esquina = ((abs(x) < 0.001 or abs(x-a) < 0.001) and
                  (abs(y) < 0.001 or abs(y-b) < 0.001))
    if es_esquina:
        esquinas.append(nodo)
        ret = SapModel.PointObj.GetRestraint(nodo)
        restr = list(ret[0])
        print(f"  Nodo {nodo} ({x:.1f},{y:.1f}): {restr}")

# Verificar restricciones en modelo de analisis
print("\n=== MODELO DE ANALISIS ===")
try:
    ret = SapModel.PointElm.CountRestraint()
    print(f"PointElm.CountRestraint: {ret}")
except Exception as e:
    print(f"Error: {e}")

# Seleccionar caso DEAD para output
print("\n=== SELECCIONAR CASO DEAD ===")
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
ret = SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")
print(f"SetCaseSelectedForOutput('DEAD'): {ret}")

# Leer desplazamientos de TODOS los nodos
print("\n=== DESPLAZAMIENTOS (TODOS LOS NODOS) ===")
ret = SapModel.Results.JointDispl("", 2)
print(f"JointDispl('', 2): {ret[0]} resultados")

if ret[0] > 0:
    nombres = list(ret[1])
    U3 = list(ret[9])

    # Crear matriz
    xs = sorted(set(x for x, y in nodos.values()))
    ys = sorted(set(y for x, y in nodos.values()), reverse=True)

    # Crear diccionario de desplazamientos
    U3_dict = {}
    for i, nombre in enumerate(nombres):
        U3_dict[nombre] = U3[i]

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

    # Estadisticas
    print(f"\nUZ min: {min(U3)*1000:.4f} mm")
    print(f"UZ max: {max(U3)*1000:.4f} mm")

    # Centro
    if nodo_centro and nodo_centro in U3_dict:
        print(f"UZ centro ({nodo_centro}): {U3_dict[nodo_centro]*1000:.4f} mm")

# Reacciones
print("\n=== REACCIONES ===")
ret = SapModel.Results.JointReact("", 2)
print(f"JointReact('', 2): {ret[0]} reacciones")

if ret[0] > 0:
    nombres = list(ret[1])
    F3 = list(ret[8])
    print(f"Suma F3: {sum(F3):.4f} kN")
    print(f"Carga total esperada: {-10*a*b:.4f} kN")
else:
    print("*** NO HAY REACCIONES - Las restricciones no estan funcionando ***")

# Intentar ver si hay otros apoyos (springs)
print("\n=== VERIFICAR SPRINGS ===")
hay_springs = False
for nodo in esquinas:
    try:
        ret = SapModel.PointObj.GetSpring(nodo)
        k = list(ret[0])
        if any(kk != 0 for kk in k):
            print(f"  Nodo {nodo}: K={k}")
            hay_springs = True
    except:
        pass

if not hay_springs:
    print("  No hay springs definidos")

# Verificar elementos de area
print("\n=== ELEMENTOS DE AREA ===")
ret = SapModel.AreaObj.GetNameList()
elementos = list(ret[1]) if ret[0] > 0 else []
print(f"Elementos: {len(elementos)}")

# Obtener fuerzas del primer elemento
if elementos:
    ret = SapModel.Results.AreaForceShell(elementos[0], 0)
    print(f"AreaForceShell('{elementos[0]}', 0): {ret[0]} resultados")
    if ret[0] > 0:
        M11 = list(ret[14])
        M22 = list(ret[15])
        print(f"  M11 rango: {min(M11):.4f} a {max(M11):.4f}")
        print(f"  M22 rango: {min(M22):.4f} a {max(M22):.4f}")

print("\n" + "="*70)
print("CONCLUSION:")
print("Si hay 0 reacciones y el patron es antisimetrico,")
print("las restricciones NO se aplicaron correctamente en el analisis.")
print("El usuario debe verificar manualmente en SAP2000 GUI si las")
print("restricciones estan activas.")
print("="*70)
