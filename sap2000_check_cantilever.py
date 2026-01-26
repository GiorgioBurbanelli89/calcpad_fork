# -*- coding: utf-8 -*-
"""
Verificar el modelo de cantilever
"""

import comtypes.client

print("="*60)
print("VERIFICACION CANTILEVER")
print("="*60)

helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

print(f"SAP2000 {SapModel.GetVersion()[0]}")
print(f"Archivo: {SapModel.GetModelFilename()}")
print(f"Bloqueado: {SapModel.GetModelIsLocked()}")

# Ver objetos
print(f"\nNodos: {SapModel.PointObj.Count()}")
print(f"Frames: {SapModel.FrameObj.Count()}")

# Nodos
ret = SapModel.PointObj.GetNameList()
nodos = list(ret[1]) if ret[0] > 0 else []
print(f"\nNodos: {nodos}")

for nodo in nodos:
    ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y, z = ret_coord[0], ret_coord[1], ret_coord[2]
    ret_restr = SapModel.PointObj.GetRestraint(nodo)
    restr = list(ret_restr[0])
    print(f"  {nodo}: ({x}, {y}, {z}), restr={restr}")

# Casos de carga
ret = SapModel.LoadCases.GetNameList()
casos = list(ret[1]) if ret[0] > 0 else []
print(f"\nCasos de carga: {casos}")

# Status
ret = SapModel.Analyze.GetCaseStatus()
if ret[0] > 0:
    status_map = {1: "NotRun", 2: "CouldNotStart", 3: "NotFinished", 4: "Finished"}
    for i in range(ret[0]):
        print(f"  {ret[1][i]}: {status_map.get(ret[2][i], ret[2][i])}")

# Si no esta analizado, analizar
print("\n--- ANALIZANDO ---")
SapModel.Analyze.SetRunCaseFlag("", False, True)
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)
ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")

# Resultados
print("\n--- RESULTADOS ---")
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

for nodo in nodos:
    ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
    x = ret_coord[0]
    ret_disp = SapModel.Results.JointDispl(nodo, 0)
    if ret_disp[0] > 0:
        uz = ret_disp[9][0]
        print(f"  Nodo {nodo} (x={x}m): UZ = {uz*1000:.6f} mm")

# Teorico
L = 10.0
P = 100.0
E = 200e6
I = 0.0001
delta = P * L**3 / (3 * E * I) * 1000
print(f"\nTeorico: {delta:.4f} mm")

print()
