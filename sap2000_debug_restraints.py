# -*- coding: utf-8 -*-
"""
Debug de restricciones en SAP2000
"""

import comtypes.client

print("="*60)
print("DEBUG RESTRICCIONES SAP2000")
print("="*60)

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

print(f"SAP2000 {SapModel.GetVersion()[0]}")
print(f"Bloqueado: {SapModel.GetModelIsLocked()}")

# Si esta bloqueado, desbloquear
if SapModel.GetModelIsLocked():
    SapModel.SetModelIsLocked(False)
    print("Modelo desbloqueado")

# Listar todos los nodos
ret = SapModel.PointObj.GetNameList()
nodos = list(ret[1]) if ret[0] > 0 else []

# Verificar restricciones
print("\n--- RESTRICCIONES ACTUALES ---")
print(f"{'Nodo':<6}{'X':<8}{'Y':<8}{'Restricciones'}")
print("-"*50)

for nodo in sorted(nodos, key=int):
    ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y = ret_coord[0], ret_coord[1]

    ret_restr = SapModel.PointObj.GetRestraint(nodo)
    restr = list(ret_restr[0])

    # Solo mostrar nodos con alguna restriccion o en borde
    en_borde = (abs(x) < 0.001 or abs(x - 6) < 0.001 or
                abs(y) < 0.001 or abs(y - 4) < 0.001)

    if any(restr) or en_borde:
        restr_str = "".join(["1" if r else "0" for r in restr])
        marker = "*" if en_borde else " "
        print(f"{nodo:<6}{x:<8.2f}{y:<8.2f}{restr_str} {marker}")

# Intentar aplicar restricciones de nuevo
print("\n--- RE-APLICANDO RESTRICCIONES ---")

# Primero, eliminar todas las restricciones
for nodo in nodos:
    ret = SapModel.PointObj.DeleteRestraint(nodo)

print("Restricciones eliminadas")

# Ahora aplicar las correctas
a = 6.0
b = 4.0
n_apoyados = 0

for nodo in nodos:
    ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y = ret_coord[0], ret_coord[1]

    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    if en_borde:
        # Esquina (0,0)
        if abs(x) < 0.001 and abs(y) < 0.001:
            restr = [True, True, True, False, False, False]
        # Esquina (a,0)
        elif abs(x - a) < 0.001 and abs(y) < 0.001:
            restr = [False, True, True, False, False, False]
        # Esquina (0,b)
        elif abs(x) < 0.001 and abs(y - b) < 0.001:
            restr = [True, False, True, False, False, False]
        # Esquina (a,b)
        elif abs(x - a) < 0.001 and abs(y - b) < 0.001:
            restr = [False, False, True, False, False, False]
        # Resto del borde
        else:
            restr = [False, False, True, False, False, False]

        ret = SapModel.PointObj.SetRestraint(nodo, restr)
        n_apoyados += 1

        # Verificar que se aplico
        ret_check = SapModel.PointObj.GetRestraint(nodo)
        if list(ret_check[0]) != restr:
            print(f"  ERROR: Nodo {nodo} - esperado {restr}, obtenido {list(ret_check[0])}")

print(f"Restricciones aplicadas a {n_apoyados} nodos")

# Verificar nuevamente
print("\n--- VERIFICACION POST-APLICACION ---")
print(f"{'Nodo':<6}{'X':<8}{'Y':<8}{'Restricciones'}")
print("-"*50)

for nodo in sorted(nodos, key=int):
    ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y = ret_coord[0], ret_coord[1]

    ret_restr = SapModel.PointObj.GetRestraint(nodo)
    restr = list(ret_restr[0])

    en_borde = (abs(x) < 0.001 or abs(x - 6) < 0.001 or
                abs(y) < 0.001 or abs(y - 4) < 0.001)

    if any(restr):
        restr_str = "".join(["1" if r else "0" for r in restr])
        print(f"{nodo:<6}{x:<8.2f}{y:<8.2f}{restr_str}")

# Guardar y re-analizar
print("\n--- RE-ANALIZANDO ---")

ModelPath = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Losa_Debug.sdb"
SapModel.File.Save(ModelPath)

SapModel.Analyze.SetRunCaseFlag("", False, True)
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)
ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")

# Resultados
print("\n--- RESULTADOS ---")
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

# Verificar desplazamientos en nodos del borde
print("\nDesplazamientos en nodos del borde (deben ser ~0):")
for nodo in sorted(nodos, key=int):
    ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y = ret_coord[0], ret_coord[1]

    en_borde = (abs(x) < 0.001 or abs(x - 6) < 0.001 or
                abs(y) < 0.001 or abs(y - 4) < 0.001)

    if en_borde:
        ret_disp = SapModel.Results.JointDispl(nodo, 0)
        if ret_disp[0] > 0:
            uz = ret_disp[9][0] * 1000
            print(f"  Nodo {nodo} ({x:.1f},{y:.1f}): UZ = {uz:.4f} mm")

print()
