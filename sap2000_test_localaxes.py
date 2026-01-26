# -*- coding: utf-8 -*-
"""
Test de ejes locales de puntos y restricciones
"""

import comtypes.client

print("="*60)
print("TEST DE EJES LOCALES Y RESTRICCIONES")
print("="*60)

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

print(f"SAP2000 {SapModel.GetVersion()[0]}")

# Si esta bloqueado, desbloquear
if SapModel.GetModelIsLocked():
    SapModel.SetModelIsLocked(False)
    print("Modelo desbloqueado")

# Ver ejes locales de algunos puntos
print("\n--- EJES LOCALES DE PUNTOS ---")

ret = SapModel.PointObj.GetNameList()
nodos = list(ret[1]) if ret[0] > 0 else []

for nodo in ['1', '6', '18']:  # Esquina, borde, interior
    ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y = ret_coord[0], ret_coord[1]

    # GetLocalAxes(Name) retorna los angulos de rotacion
    ret_axes = SapModel.PointObj.GetLocalAxes(nodo)
    print(f"Nodo {nodo} ({x},{y}): LocalAxes = {ret_axes}")

# Intentar con SetSpecialPoint para forzar el comportamiento
print("\n--- INTENTANDO CON CONSTRAINT DIAPHRAGM ---")

# Crear un grupo para los nodos del borde
ret = SapModel.GroupDef.SetGroup("BORDE")
print(f"SetGroup('BORDE'): {ret}")

# Agregar nodos del borde al grupo
for nodo in nodos:
    ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y = ret_coord[0], ret_coord[1]

    en_borde = (abs(x) < 0.001 or abs(x - 6) < 0.001 or
                abs(y) < 0.001 or abs(y - 4) < 0.001)

    if en_borde:
        ret = SapModel.PointObj.SetGroupAssign(nodo, "BORDE")

# Ver que hay en el grupo
ret = SapModel.GroupDef.GetAssignments("BORDE")
print(f"Objetos en grupo BORDE: {ret[0]} elementos")

# Intentar aplicar las restricciones al grupo directamente
print("\n--- APLICANDO RESTRICCIONES POR GRUPO ---")

# Primero quitar todas las restricciones
for nodo in nodos:
    SapModel.PointObj.DeleteRestraint(nodo)

# Aplicar restriccion UZ=0 a todo el grupo BORDE usando ItemType=1 (Group)
restr_uz = [False, False, True, False, False, False]
ret = SapModel.PointObj.SetRestraint("BORDE", restr_uz, 1)  # ItemType=1 para grupo
print(f"SetRestraint('BORDE', [F,F,T,F,F,F], Group): {ret}")

# Ahora las esquinas especiales
# Esquina (0,0)
ret = SapModel.PointObj.SetRestraint("1", [True, True, True, False, False, False], 0)
print(f"SetRestraint('1', [T,T,T,F,F,F]): {ret}")

# Esquina (6,0)
ret = SapModel.PointObj.SetRestraint("31", [False, True, True, False, False, False], 0)
print(f"SetRestraint('31', [F,T,T,F,F,F]): {ret}")

# Esquina (0,4)
ret = SapModel.PointObj.SetRestraint("5", [True, False, True, False, False, False], 0)
print(f"SetRestraint('5', [T,F,T,F,F,F]): {ret}")

# Verificar
print("\n--- VERIFICANDO RESTRICCIONES ---")
for nodo in ['1', '2', '6', '18', '31', '5']:
    ret = SapModel.PointObj.GetRestraint(nodo)
    restr = list(ret[0])
    ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y = ret_coord[0], ret_coord[1]
    print(f"  Nodo {nodo} ({x},{y}): {restr}")

# Guardar y analizar
print("\n--- GUARDANDO Y ANALIZANDO ---")
SapModel.View.RefreshView(0, False)
ModelPath = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Test_LocalAxes.sdb"
SapModel.File.Save(ModelPath)

SapModel.Analyze.SetRunCaseFlag("", False, True)
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)
ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")

# Resultados
print("\n--- RESULTADOS ---")
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

print("\nDesplazamientos en nodos clave:")
for nodo in ['1', '6', '16', '18', '20']:
    ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y = ret_coord[0], ret_coord[1]
    ret_disp = SapModel.Results.JointDispl(nodo, 0)
    uz = ret_disp[9][0] * 1000 if ret_disp[0] > 0 else 0
    print(f"  Nodo {nodo} ({x},{y}): UZ = {uz:.4f} mm")

print()
