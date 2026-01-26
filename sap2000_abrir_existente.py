# -*- coding: utf-8 -*-
"""
Abrir modelo existente y verificar estado
=========================================
El usuario dice que el modelo tiene resultados en GUI.
Vamos a abrir el archivo .sdb existente y ver su estado.
"""

import comtypes.client

print("="*70)
print("VERIFICAR MODELO EXISTENTE")
print("="*70)

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

print(f"SAP2000 {SapModel.GetVersion()[0]}")

# Abrir archivo existente
ModelPath = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_AnalysisModel.sdb"
print(f"\nAbriendo: {ModelPath}")
ret = SapModel.File.OpenFile(ModelPath)
print(f"OpenFile: {ret}")

print(f"Archivo: {SapModel.GetModelFilename()}")
print(f"Bloqueado: {SapModel.GetModelIsLocked()}")

# Datos
a, b = 6.0, 4.0

# Obtener nodos
ret = SapModel.PointObj.GetNameList()
nodos_list = list(ret[1]) if ret[0] > 0 else []
print(f"\nNodos: {len(nodos_list)}")

nodos = {}
for nodo in nodos_list:
    ret = SapModel.PointObj.GetCoordCartesian(nodo)
    nodos[nodo] = (ret[0], ret[1])

# Verificar restricciones actuales
print("\n=== RESTRICCIONES ACTUALES ===")
esquinas = []
for nodo, (x, y) in nodos.items():
    es_esquina = ((abs(x) < 0.001 or abs(x-a) < 0.001) and
                  (abs(y) < 0.001 or abs(y-b) < 0.001))
    if es_esquina:
        esquinas.append(nodo)
        ret = SapModel.PointObj.GetRestraint(nodo)
        print(f"  Nodo {nodo} ({x:.1f},{y:.1f}): {list(ret[0])}")

# Verificar springs
print("\n=== SPRINGS ACTUALES ===")
hay_springs = False
for nodo, (x, y) in nodos.items():
    ret = SapModel.PointObj.GetSpring(nodo)
    k = list(ret[0])
    if any(kk != 0 for kk in k):
        print(f"  Nodo {nodo} ({x:.1f},{y:.1f}): K={k}")
        hay_springs = True

if not hay_springs:
    print("  No hay springs")

# Elementos
ret = SapModel.AreaObj.GetNameList()
elementos = list(ret[1]) if ret[0] > 0 else []
print(f"\nElementos: {len(elementos)}")

# Seleccionar DEAD para resultados
print("\n=== RESULTADOS ===")
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
ret = SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")
print(f"SetCaseSelectedForOutput('DEAD'): {ret}")

# Intentar leer desplazamientos
print("\nDesplazamientos (nodo por nodo):")
U3_dict = {}
for nodo in nodos_list:
    ret = SapModel.Results.JointDispl(nodo, 0)
    if ret[0] > 0:
        U3_dict[nodo] = ret[9][0]

print(f"Nodos con resultados: {len(U3_dict)}")

if U3_dict:
    # Matriz
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

    # Centro
    for nodo, (x, y) in nodos.items():
        if abs(x - 3.0) < 0.1 and abs(y - 2.0) < 0.1:
            print(f"\nCentro ({nodo}): UZ = {U3_dict.get(nodo, 0)*1000:.4f} mm")
            break

# Reacciones
print("\n=== REACCIONES ===")
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

print(f"Reacciones: {n_reac}")
print(f"Suma F3: {total_F3:.4f} kN")
print(f"Carga esperada: -240.0 kN")

# Verificar modelo de analisis
print("\n=== MODELO DE ANALISIS ===")
try:
    ret = SapModel.PointElm.CountRestraint()
    print(f"PointElm.CountRestraint: {ret}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*70)
