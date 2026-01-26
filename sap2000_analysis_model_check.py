# -*- coding: utf-8 -*-
"""
Verificar el modelo de analisis de SAP2000
==========================================
Revisar si hay diferencias entre el modelo de objetos y el modelo de analisis.
"""

import comtypes.client

print("="*60)
print("VERIFICACION DEL MODELO DE ANALISIS")
print("="*60)

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

print(f"SAP2000 {SapModel.GetVersion()[0]}")
print(f"Archivo: {SapModel.GetModelFilename()}")

# Ver estado
print(f"\nModelo bloqueado: {SapModel.GetModelIsLocked()}")

# Intentar ver informacion del modelo de analisis
print("\n--- MODELO DE OBJETOS ---")
print(f"Nodos (PointObj): {SapModel.PointObj.Count()}")
print(f"Areas (AreaObj): {SapModel.AreaObj.Count()}")

# Ver restricciones de algunos nodos
ret = SapModel.PointObj.GetNameList()
nodos = list(ret[1]) if ret[0] > 0 else []

print("\nRestricciones de nodos (PointObj):")
for nodo in nodos[:5]:
    ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y = ret_coord[0], ret_coord[1]
    ret_restr = SapModel.PointObj.GetRestraint(nodo)
    restr = list(ret_restr[0])
    print(f"  Nodo {nodo} ({x:.1f},{y:.1f}): {restr}")

# Ver si hay resultados
if SapModel.GetModelIsLocked():
    print("\n--- MODELO DE ANALISIS ---")

    # Intento de obtener informacion del modelo de analisis
    # Esto puede variar segun la version de SAP2000

    # Ver numero de ecuaciones
    # ret = SapModel.Analyze.GetActiveDOFNum()

    # Ver resultados de un nodo especifico
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

    # Para cada nodo, ver si hay reaccion (si esta restringido, deberia tener reaccion)
    print("\nReacciones en nodos del borde (deben ser no-cero si estan restringidos):")

    ret = SapModel.Results.JointReact("", 2)
    if ret[0] > 0:
        nombres = list(ret[1])
        F3 = list(ret[8])  # Reaccion en Z

        for i in range(min(10, ret[0])):
            print(f"  {nombres[i]}: F3 = {F3[i]:.4f} kN")
    else:
        print("  No hay resultados de reacciones")

    # Verificar desplazamientos
    print("\nDesplazamientos de primeros nodos:")
    for nodo in nodos[:10]:
        ret = SapModel.Results.JointDispl(nodo, 0)
        if ret[0] > 0:
            ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
            x, y = ret_coord[0], ret_coord[1]
            uz = ret[9][0]
            print(f"  Nodo {nodo} ({x:.1f},{y:.1f}): UZ = {uz*1000:.4f} mm")

# Verificar si el problema es con elementos shell incompatibles
print("\n--- VERIFICACION DE ELEMENTOS ---")
ret = SapModel.AreaObj.GetNameList()
areas = list(ret[1]) if ret[0] > 0 else []

for area in areas[:2]:
    ret_prop = SapModel.AreaObj.GetProperty(area)
    sec = ret_prop[0]
    ret_shell = SapModel.PropArea.GetShell_1(sec)
    tipo = ret_shell[0]
    tipos = {1: "Shell-Thin", 2: "Shell-Thick", 3: "Plate-Thin",
             4: "Plate-Thick", 5: "Membrane", 6: "Layered"}
    print(f"  {area}: seccion={sec}, tipo={tipos.get(tipo, tipo)}")

# Ver si hay algun problema con el auto-mesh
print("\n--- AUTO-MESH ---")
for area in areas[:1]:
    ret = SapModel.AreaObj.GetAutoMesh(area)
    print(f"  {area}: AutoMesh = {ret}")

print()
