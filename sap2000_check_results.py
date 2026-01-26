# -*- coding: utf-8 -*-
"""
Verificar resultados del modelo SAP2000 ya analizado
"""

import comtypes.client

print("="*60)
print("VERIFICACION DE RESULTADOS SAP2000")
print("="*60)

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

print(f"SAP2000 {SapModel.GetVersion()[0]}")
print(f"Modelo bloqueado: {SapModel.GetModelIsLocked()}")

# Listar casos de carga
print("\n--- CASOS DE CARGA ---")
ret = SapModel.LoadCases.GetNameList()
casos = list(ret[1]) if ret[0] > 0 else []
print(f"Casos: {casos}")

# Ver tipo de cada caso
for caso in casos:
    ret = SapModel.LoadCases.GetTypeOAPI_1(caso)
    tipo = ret[0]
    tipo_str = {1: "LinearStatic", 2: "NonlinearStatic", 3: "Modal",
                4: "ResponseSpectrum", 5: "LinearHistory", 6: "NonlinearHistory",
                7: "LinearDirectInteg", 8: "NonlinearDirectInteg",
                9: "Moving Load", 10: "Buckling", 11: "SteadyState"}
    print(f"  {caso}: tipo={tipo_str.get(tipo, tipo)}")

# Ver patrones de carga
print("\n--- PATRONES DE CARGA ---")
ret = SapModel.LoadPatterns.GetNameList()
patrones = list(ret[1]) if ret[0] > 0 else []
print(f"Patrones: {patrones}")

# Intentar obtener resultados de cada caso
print("\n--- INTENTANDO OBTENER RESULTADOS ---")

for caso in casos:
    print(f"\nCaso: {caso}")

    # Seleccionar caso
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    ret = SapModel.Results.Setup.SetCaseSelectedForOutput(caso)
    print(f"  SetCaseSelectedForOutput: {ret}")

    # Intentar obtener desplazamientos
    ret = SapModel.Results.JointDispl("", 2)
    n = ret[0]
    print(f"  JointDispl: {n} resultados")

    if n > 0:
        nombres = list(ret[2])
        U3 = list(ret[9])
        print(f"    Primer nodo: {nombres[0]}, U3={U3[0]}")
        print(f"    U3 min={min(U3)*1000:.4f}mm, max={max(U3)*1000:.4f}mm")

# Intentar con nombre de nodo especifico
print("\n--- PROBANDO CON NODO ESPECIFICO ---")
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

# Obtener lista de nodos
ret = SapModel.PointObj.GetNameList()
nodos = list(ret[1]) if ret[0] > 0 else []
print(f"Nodos en modelo: {nodos[:5]}... (total {len(nodos)})")

# Probar con primer nodo
if nodos:
    nodo = nodos[0]
    print(f"\nProbando nodo '{nodo}':")
    ret = SapModel.Results.JointDispl(nodo, 0)  # ObjectElm = 0
    n = ret[0]
    print(f"  JointDispl('{nodo}', 0): {n} resultados")

    if n > 0:
        print(f"    U3 = {list(ret[9])}")

# Ver si hay combinaciones
print("\n--- COMBINACIONES ---")
ret = SapModel.RespCombo.GetNameList()
combos = list(ret[1]) if ret[0] > 0 else []
print(f"Combinaciones: {combos}")

# Verificar si DEAD tiene resultados disponibles
print("\n--- VERIFICAR DISPONIBILIDAD DE RESULTADOS ---")
ret = SapModel.Analyze.GetCaseStatus()
n_casos = ret[0]
if n_casos > 0:
    nombres_casos = list(ret[1])
    status = list(ret[2])
    status_str = {1: "Not run", 2: "Could not start", 3: "Not finished",
                  4: "Finished", 5: "Results exist"}
    for i in range(n_casos):
        print(f"  {nombres_casos[i]}: {status_str.get(status[i], status[i])}")

print("\n" + "="*60)
